#!/usr/bin/env python3
"""
Opportunity Validator - Cross-reference scored signals against multiple sources.

Takes top scored HN signals, classifies the opportunity type, generates targeted
search queries, executes them against Google Trends / Product Hunt / GitHub,
then synthesizes a validation narrative with confidence scoring.

Part of Build Signals: pain point discovery for vibe coders.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-20250514"

OPPORTUNITY_TYPES = [
    "developer-tooling",
    "demographic-market-gap",
    "infrastructure-need",
    "workflow-inefficiency",
    "emerging-category",
]

CLASSIFY_PROMPT = """You are a signal analyst classifying startup/builder opportunities and generating buyer-intent search queries.

For each signal, provide:
1. **opportunity_types**: A list with 1-2 items chosen from:
   - developer-tooling
   - demographic-market-gap
   - infrastructure-need
   - workflow-inefficiency
   - emerging-category
2. **opportunity_title**: A short 4-8 word title describing the opportunity (NOT the HN title).
3. **queries**: An object with three keys, each containing a list of 3-5 search query strings:
   - **google_trends**: buyer intent keyword phrases (2-6 words, no special chars)
   - **producthunt**: product search queries (what someone would search on Product Hunt)
   - **github**: GitHub repository search queries (technical terms, tool categories)

Be specific and varied. Each query should probe a different angle of the opportunity.

Input signals:

{signals_text}

Respond with a JSON array. Each element:
{{
  "signal_index": 0,
  "opportunity_types": ["developer-tooling", "infrastructure-need"],
  "opportunity_title": "Secure AI coding environments",
  "queries": {{
    "google_trends": ["query1", "query2", "query3", "query4"],
    "producthunt": ["query1", "query2", "query3"],
    "github": ["query1", "query2", "query3", "query4", "query5"]
  }}
}}

ONLY output the JSON array."""

SYNTHESIZE_PROMPT = """You are writing validation narratives for builder opportunities. You've been given a signal and evidence summaries from Google Trends, Product Hunt, and GitHub.

For each signal, write:
1. **narrative**: 3-5 sentences summarizing the validation evidence. Be specific about what was found. If evidence is weak or missing, say so honestly. Reference actual numbers or product names when provided.
2. End with an explicit assessment sentence using the provided confidence label, e.g. "Assessment: Open market with validated demand. High confidence opportunity."

Use the provided confidence label and source count. Do NOT change them.

Input:

{evidence_text}

Respond with a JSON array. Each element:
{{
  "signal_index": 0,
  "narrative": "3-5 sentence validation narrative..."
}}

ONLY output the JSON array."""


def load_scored_signals(input_dir: Path, top_n: int) -> list[dict]:
    """Load top N scored signals sorted by combined score."""
    scored_path = input_dir / "scored_signals.jsonl"
    if not scored_path.exists():
        return []

    signals = []
    with open(scored_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                signals.append(json.loads(line))

    signals.sort(
        key=lambda s: s.get("relevance_score", 0) + s.get("content_potential", 0),
        reverse=True,
    )
    return signals[:top_n]


def format_signal_for_classify(signal: dict, index: int) -> str:
    """Format signal for the classification prompt."""
    title = signal.get("title", "")
    description = signal.get("description", signal.get("text", ""))
    if description and len(description) > 400:
        description = description[:400] + "..."

    return (
        f"[Signal {index}]\n"
        f"Source: {signal.get('source', 'unknown')}\n"
        f"Title: {title}\n"
        f"Score: {signal.get('score', 0)}\n"
        f"Comments: {signal.get('descendants', signal.get('comments', 0))}\n"
        f"Category: {signal.get('category', '')}\n"
        f"Hook: {signal.get('one_line_hook', '')}\n"
        f"Insight: {signal.get('key_insight', '')}\n"
        f"Description: {description}\n"
    )


def classify_batch(client, signals: list[dict], batch_indices: list[int]) -> list[dict]:
    """Classify opportunity types and generate queries for a batch."""
    signal_texts = []
    for i, idx in enumerate(batch_indices):
        signal_texts.append(format_signal_for_classify(signals[idx], i))

    prompt = CLASSIFY_PROMPT.format(signals_text="\n---\n".join(signal_texts))

    for attempt in range(2):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()

            if text.startswith("["):
                return json.loads(text)
            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            if attempt == 0:
                print("    Malformed classify response, retrying...")
                continue
            print("    WARNING: Could not parse classify response")
            return []
        except json.JSONDecodeError:
            if attempt == 0:
                print("    JSON parse error in classify, retrying...")
                continue
            print("    WARNING: JSON parse failed in classify")
            return []
        except Exception as e:
            print(f"    ERROR in classify API call: {e}")
            return []
    return []


def _coerce_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        parts = [p.strip() for p in value.replace("/", ",").split(",")]
        return [p for p in parts if p]
    return []


def _normalize_opportunity_types(raw_types) -> list[str]:
    types = _coerce_list(raw_types)
    normalized = []
    for t in types:
        t = t.strip().lower().replace("_", "-")
        if t in OPPORTUNITY_TYPES and t not in normalized:
            normalized.append(t)
    return normalized[:2]


def _normalize_queries(queries: dict) -> dict:
    normalized = {}
    for key in ("google_trends", "producthunt", "github"):
        vals = _coerce_list((queries or {}).get(key, []))
        deduped = []
        seen = set()
        for v in vals:
            v = v.strip()
            if not v or v in seen:
                continue
            seen.add(v)
            deduped.append(v)
        normalized[key] = deduped[:5]
    return normalized


def _hn_strength(signal: dict) -> bool:
    score = signal.get("score", 0) or 0
    comments = signal.get("descendants", signal.get("comments", 0)) or 0
    return (score >= 30) or (comments >= 20) or (score >= 15 and comments >= 10)


def _fallback_opportunity_title(signal: dict) -> str:
    hook = (signal.get("one_line_hook") or "").strip().strip('"')
    if hook:
        return hook[:80]
    title = (signal.get("title") or "").strip()
    return title[:80] if title else "Untitled opportunity"


def _chunks(items: list[str], size: int) -> list[list[str]]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def execute_google_trends(queries: list[str], sleep: float = 2.0) -> dict:
    """Query Google Trends for interest data. Returns evidence dict."""
    try:
        from pytrends.request import TrendReq
    except ImportError:
        return {"status": "skipped", "reason": "pytrends not installed", "results": []}

    pytrends = TrendReq(hl="en-US", tz=360)
    results = []

    # pytrends accepts up to 5 keywords per batch
    for batch in _chunks(queries[:5], 5):
        try:
            pytrends.build_payload(batch, timeframe="today 12-m")
            iot = pytrends.interest_over_time()

            if iot.empty:
                for q in batch:
                    results.append({"query": q, "interest": 0, "yoy_growth": 0})
                continue

            for kw in batch:
                if kw not in iot.columns:
                    results.append({"query": kw, "interest": 0, "yoy_growth": 0})
                    continue

                series = iot[kw]
                current = int(series.iloc[-1]) if len(series) > 0 else 0
                year_ago = int(series.iloc[0]) if len(series) > 0 else 0

                if year_ago > 0:
                    yoy = round(((current - year_ago) / year_ago) * 100, 1)
                else:
                    yoy = 100.0 if current > 0 else 0.0

                results.append({"query": kw, "interest": current, "yoy_growth": yoy})

            if sleep > 0:
                time.sleep(sleep)

        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "too many" in error_msg or "blocked" in error_msg:
                return {"status": "rate_limited", "results": results}
            return {"status": "error", "reason": str(e)[:200], "results": results}

    return {"status": "ok", "results": results}


def execute_github_search(queries: list[str], token: str, sleep: float = 2.0) -> dict:
    """Search GitHub repos via REST API. Returns evidence dict."""
    if not token:
        return {"status": "skipped", "reason": "no GITHUB_TOKEN", "results": []}

    import requests

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    results = []

    for q in queries[:5]:
        try:
            resp = requests.get(
                "https://api.github.com/search/repositories",
                params={"q": q, "sort": "stars", "per_page": 5},
                headers=headers,
                timeout=10,
            )
            if resp.status_code == 403:
                results.append({"query": q, "status": "rate_limited", "repos": []})
                break
            resp.raise_for_status()
            data = resp.json()
            repos = []
            for item in data.get("items", [])[:5]:
                repos.append({
                    "name": item.get("full_name", ""),
                    "stars": item.get("stargazers_count", 0),
                    "description": (item.get("description") or "")[:150],
                    "url": item.get("html_url", ""),
                    "language": item.get("language"),
                    "updated": (item.get("updated_at") or "")[:10],
                })
            results.append({"query": q, "total_count": data.get("total_count", 0), "repos": repos})
        except Exception as e:
            results.append({"query": q, "status": "error", "reason": str(e)[:150], "repos": []})

        if sleep > 0:
            time.sleep(sleep)

    return {"status": "ok", "results": results}


def execute_producthunt_search(queries: list[str], token: str, fallback_file: Path | None = None) -> dict:
    """Search Product Hunt via GraphQL API, with fallback to local JSONL."""
    results = []

    if token:
        import requests

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        graphql_query = """
        query SearchPosts($query: String!) {
          posts(order: VOTES, search: $query, first: 5) {
            edges {
              node {
                id
                name
                tagline
                votesCount
                url
                createdAt
              }
            }
          }
        }
        """

        for q in queries[:5]:
            try:
                resp = requests.post(
                    "https://api.producthunt.com/v2/api/graphql",
                    json={"query": graphql_query, "variables": {"query": q}},
                    headers=headers,
                    timeout=10,
                )
                if resp.status_code != 200:
                    results.append({"query": q, "status": "error", "products": []})
                    continue

                data = resp.json()
                edges = data.get("data", {}).get("posts", {}).get("edges", [])
                products = []
                for edge in edges[:5]:
                    node = edge.get("node", {})
                    products.append({
                        "name": node.get("name", ""),
                        "tagline": node.get("tagline", ""),
                        "votes": node.get("votesCount", 0),
                        "url": node.get("url", ""),
                        "created_at": (node.get("createdAt") or "")[:10],
                    })
                results.append({"query": q, "total": len(products), "products": products})
            except Exception as e:
                results.append({"query": q, "status": "error", "reason": str(e)[:150], "products": []})

        # If API returned some results, use them
        if any(r.get("total", 0) > 0 for r in results):
            return {"status": "ok", "results": results}

    # Fallback: keyword-match local producthunt.jsonl
    if fallback_file and fallback_file.exists():
        local_products = []
        with open(fallback_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    local_products.append(json.loads(line))

        fallback_results = []
        for q in queries[:5]:
            q_lower = q.lower()
            matches = []
            for p in local_products:
                title = (p.get("title", "") + " " + p.get("tagline", "")).lower()
                if any(word in title for word in q_lower.split()):
                    matches.append({
                        "name": p.get("title", p.get("name", "")),
                        "tagline": p.get("tagline", ""),
                        "votes": p.get("votes", p.get("score", 0)),
                        "url": p.get("url", ""),
                        "created_at": (p.get("created_iso") or "")[:10],
                    })
            fallback_results.append({
                "query": q,
                "total": len(matches),
                "products": matches[:5],
                "source": "local_fallback",
            })

        return {"status": "ok", "source": "local_fallback", "results": fallback_results}

    if not token:
        return {"status": "skipped", "reason": "no PH_TOKEN", "results": []}

    return {"status": "ok", "results": results}


def summarize_trends(evidence: dict) -> dict:
    results = evidence.get("results", []) or []
    if evidence.get("status") != "ok" or not results:
        return {"summary": "No Google Trends data available.", "supporting": False}

    supporting = []
    for r in results:
        interest = r.get("interest", 0) or 0
        yoy = r.get("yoy_growth", 0) or 0
        if (interest >= 10 and yoy > 0) or interest >= 20:
            supporting.append(r)

    top = max(results, key=lambda r: (r.get("interest", 0), r.get("yoy_growth", 0)), default=None)
    if supporting:
        summary = (
            f"Search demand present. Top query '{top.get('query', '')}' "
            f"shows interest {top.get('interest', 0)} and YoY {top.get('yoy_growth', 0):+.0f}%."
        )
        return {"summary": summary, "supporting": True}

    if top:
        summary = (
            f"Search demand weak or flat. Top query '{top.get('query', '')}' "
            f"has interest {top.get('interest', 0)} and YoY {top.get('yoy_growth', 0):+.0f}%."
        )
        return {"summary": summary, "supporting": False}

    return {"summary": "Search demand unclear (no usable Trends signal).", "supporting": False}


def summarize_producthunt(evidence: dict) -> dict:
    results = evidence.get("results", []) or []
    total_products = sum(len(r.get("products", [])) for r in results)
    if evidence.get("status") != "ok" or not results:
        return {"summary": "No Product Hunt data available.", "supporting": False}
    if total_products == 0:
        return {"summary": "No relevant products found on Product Hunt.", "supporting": False}

    top_product = None
    for r in results:
        for p in r.get("products", []):
            if not top_product or (p.get("votes", 0) or 0) > (top_product.get("votes", 0) or 0):
                top_product = p

    if top_product:
        summary = (
            f"Found {total_products} related products. "
            f"Top: {top_product.get('name', '')} ({top_product.get('votes', 0)} votes)."
        )
    else:
        summary = f"Found {total_products} related products on Product Hunt."
    return {"summary": summary, "supporting": True}


def summarize_github(evidence: dict) -> dict:
    results = evidence.get("results", []) or []
    total_repos = sum(len(r.get("repos", [])) for r in results)
    if evidence.get("status") != "ok" or not results:
        return {"summary": "No GitHub data available.", "supporting": False}
    if total_repos == 0:
        return {"summary": "No relevant repos found on GitHub search.", "supporting": False}

    # Collect all repos, dedupe by name, sort by stars
    seen = set()
    all_repos = []
    for r in results:
        for repo in r.get("repos", []):
            name = repo.get("name", "")
            if name and name not in seen:
                seen.add(name)
                all_repos.append(repo)
    all_repos.sort(key=lambda r: r.get("stars", 0) or 0, reverse=True)

    top_repo = all_repos[0] if all_repos else None

    support = False
    if top_repo and (top_repo.get("stars", 0) or 0) >= 50:
        support = True
    if total_repos >= 3:
        support = True

    # Build narrative with top 3 repos
    top3 = all_repos[:3]
    parts = [f"Found {len(all_repos)} unique repos across {len(results)} queries."]
    for repo in top3:
        name = repo.get("name", "")
        stars = repo.get("stars", 0) or 0
        desc = (repo.get("description") or "").strip()
        lang = repo.get("language") or ""
        detail = f"{name} ({stars:,} stars"
        if lang:
            detail += f", {lang}"
        detail += ")"
        if desc:
            detail += f" - {desc}"
        parts.append(detail)

    summary = " | ".join(parts)
    return {"summary": summary, "supporting": support}


def compute_confidence(signal: dict, gt_support: bool, ph_support: bool, gh_support: bool) -> tuple[str, int]:
    hn_support = _hn_strength(signal)
    total_sources = (1 if hn_support else 0) + sum([gt_support, ph_support, gh_support])

    if total_sources >= 3:
        confidence = "high"
    elif total_sources == 2:
        confidence = "medium"
    else:
        confidence = "low"

    return confidence, total_sources


def fallback_narrative(signal: dict, evidence: dict) -> str:
    hook = signal.get("one_line_hook") or ""
    score = signal.get("score", 0) or 0
    comments = signal.get("descendants", signal.get("comments", 0)) or 0
    confidence = (evidence.get("confidence") or "low").lower()
    sources = evidence.get("sources_confirming", 0)

    parts = []
    if hook:
        parts.append(f"HN signal highlights: {hook}")
    else:
        parts.append(f"HN signal shows interest ({score} upvotes, {comments} comments).")

    parts.append(evidence.get("summary_trends", "No Google Trends data available."))
    parts.append(evidence.get("summary_products", "No Product Hunt data available."))
    parts.append(evidence.get("summary_github", "No GitHub data available."))

    parts.append(
        f"Assessment: {sources} sources confirming, {confidence.title()} confidence opportunity."
    )
    return " ".join(parts)


def synthesize_batch(client, signals: list[dict], evidence_list: list[dict], batch_indices: list[int]) -> list[dict]:
    """Generate narrative + confidence for a batch of signals with evidence."""
    evidence_texts = []
    for i, idx in enumerate(batch_indices):
        sig = signals[idx]
        ev = evidence_list[idx]

        text = (
            f"[Signal {i}]\n"
            f"Title: {sig.get('title', '')}\n"
            f"Source: {sig.get('source', '')}\n"
            f"Hook: {sig.get('one_line_hook', '')}\n"
            f"Opportunity Title: {ev.get('opportunity_title', '')}\n"
            f"Types: {ev.get('opportunity_type', '')}\n"
            f"Confidence: {ev.get('confidence', '').upper()} ({ev.get('sources_confirming', 0)} sources confirming, incl HN)\n\n"
            f"Trends Summary: {ev.get('summary_trends', '')}\n"
            f"Products Summary: {ev.get('summary_products', '')}\n"
            f"GitHub Summary: {ev.get('summary_github', '')}\n\n"
            f"Trends Evidence (short): {json.dumps(ev.get('evidence_google_trends', {}), indent=2)[:400]}\n\n"
            f"Product Hunt Evidence (short): {json.dumps(ev.get('evidence_producthunt', {}), indent=2)[:400]}\n\n"
            f"GitHub Evidence (short): {json.dumps(ev.get('evidence_github', {}), indent=2)[:400]}\n"
        )
        evidence_texts.append(text)

    prompt = SYNTHESIZE_PROMPT.format(evidence_text="\n===\n".join(evidence_texts))

    for attempt in range(2):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()

            if text.startswith("["):
                return json.loads(text)
            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            if attempt == 0:
                print("    Malformed synthesize response, retrying...")
                continue
            print("    WARNING: Could not parse synthesize response")
            return []
        except json.JSONDecodeError:
            if attempt == 0:
                print("    JSON parse error in synthesize, retrying...")
                continue
            print("    WARNING: JSON parse failed in synthesize")
            return []
        except Exception as e:
            print(f"    ERROR in synthesize API call: {e}")
            return []
    return []


def main():
    parser = argparse.ArgumentParser(
        description="Validate top scored signals against multiple sources",
    )
    parser.add_argument(
        "--input-dir",
        required=True,
        help="Input directory containing scored_signals.jsonl",
    )
    parser.add_argument(
        "--out-dir",
        help="Output directory (default: same as input-dir)",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=15,
        help="Number of top signals to validate (default: 15)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Signals per Claude API call (default: 5)",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=2.0,
        help="Sleep between API calls (default: 2.0)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be validated without calling APIs",
    )

    args = parser.parse_args()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key and not args.dry_run:
        print("WARNING: ANTHROPIC_API_KEY not set. Skipping validation.")
        sys.exit(0)

    github_token = os.getenv("GITHUB_TOKEN")
    ph_token = os.getenv("PH_TOKEN")

    input_dir = Path(args.input_dir)
    out_dir = Path(args.out_dir) if args.out_dir else input_dir

    if not input_dir.exists():
        print(f"ERROR: Input directory does not exist: {input_dir}")
        sys.exit(1)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("BUILD SIGNALS - Opportunity Validator")
    print("=" * 60)
    print(f"input:      {input_dir}")
    print(f"output:     {out_dir}")
    print(f"top_n:      {args.top_n}")
    print(f"batch_size: {args.batch_size}")
    print(f"github:     {'yes' if github_token else 'no token (skipped)'}")
    print(f"producthunt:{'yes' if ph_token else 'no token (local fallback)'}")
    print(f"mode:       {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60)
    print()

    # Load signals
    print("[1] Loading scored signals...")
    signals = load_scored_signals(input_dir, args.top_n)
    print(f"  Loaded {len(signals)} top signals")
    print()

    if not signals:
        print("No scored signals found. Run score_signals.py first.")
        sys.exit(0)

    for i, s in enumerate(signals):
        rel = s.get("relevance_score", 0)
        cp = s.get("content_potential", 0)
        print(f"  {i + 1}. [{rel}+{cp}={rel + cp}] {s.get('title', '')[:60]}")
    print()

    if args.dry_run:
        print("[DRY RUN] Would validate the above signals.")
        print(f"  Estimated Claude calls: {2 * ((len(signals) + args.batch_size - 1) // args.batch_size)}")
        print(f"  Estimated GitHub API calls: {len(signals) * 5}")
        print(f"  Estimated pytrends batches: {len(signals)}")
        return

    # Initialize Anthropic
    try:
        from anthropic import Anthropic
    except ImportError:
        print("ERROR: anthropic package not installed. Run: pip install anthropic")
        sys.exit(1)

    client = Anthropic(api_key=api_key)

    # Step 2: Classify + generate queries
    print("[2] Classifying opportunities and generating queries...")
    classifications = [None] * len(signals)
    total_batches = (len(signals) + args.batch_size - 1) // args.batch_size

    for batch_num in range(total_batches):
        start_idx = batch_num * args.batch_size
        end_idx = min(start_idx + args.batch_size, len(signals))
        batch_indices = list(range(start_idx, end_idx))

        print(f"  Batch {batch_num + 1}/{total_batches} (signals {start_idx}-{end_idx - 1})...")
        results = classify_batch(client, signals, batch_indices)

        for r in results:
            signal_idx = r.get("signal_index", 0)
            actual_idx = start_idx + signal_idx
            if actual_idx < len(signals):
                opp_types = _normalize_opportunity_types(
                    r.get("opportunity_types") or r.get("opportunity_type")
                )
                queries = _normalize_queries(r.get("queries", {}))
                opp_title = (r.get("opportunity_title") or "").strip()
                if not opp_title:
                    opp_title = _fallback_opportunity_title(signals[actual_idx])

                classifications[actual_idx] = {
                    "opportunity_types": opp_types,
                    "opportunity_title": opp_title,
                    "queries": queries,
                }
                print(f"    Signal {actual_idx}: type={','.join(opp_types) or '?'}")

        if batch_num < total_batches - 1 and args.sleep > 0:
            time.sleep(args.sleep)

    print()

    # Step 3: Execute queries against sources
    print("[3] Executing queries against sources...")
    evidence_list = []
    ph_fallback = input_dir / "producthunt.jsonl"

    for i, sig in enumerate(signals):
        cls = classifications[i] or {}
        queries = cls.get("queries", {})
        opp_types = cls.get("opportunity_types", [])
        opp_type = " / ".join(opp_types) if opp_types else "unknown"
        opp_title = cls.get("opportunity_title") or _fallback_opportunity_title(sig)

        print(f"  Signal {i + 1}/{len(signals)}: {sig.get('title', '')[:50]}...")

        # Google Trends
        gt_queries = queries.get("google_trends", [])
        if gt_queries:
            print(f"    Google Trends: {gt_queries}")
            gt_evidence = execute_google_trends(gt_queries)
            print(f"    -> {gt_evidence.get('status', '?')}")
        else:
            gt_evidence = {"status": "no_queries", "results": []}
        gt_summary = summarize_trends(gt_evidence)
        gt_evidence["summary"] = gt_summary["summary"]
        gt_evidence["supporting"] = gt_summary["supporting"]

        # GitHub
        gh_queries = queries.get("github", [])
        if gh_queries:
            print(f"    GitHub: {gh_queries}")
            gh_evidence = execute_github_search(gh_queries, github_token, sleep=args.sleep)
            print(f"    -> {gh_evidence.get('status', '?')}")
        else:
            gh_evidence = {"status": "no_queries", "results": []}
        gh_summary = summarize_github(gh_evidence)
        gh_evidence["summary"] = gh_summary["summary"]
        gh_evidence["supporting"] = gh_summary["supporting"]

        # Product Hunt
        ph_queries = queries.get("producthunt", [])
        if ph_queries:
            print(f"    Product Hunt: {ph_queries}")
            ph_evidence = execute_producthunt_search(
                ph_queries, ph_token,
                fallback_file=ph_fallback if ph_fallback.exists() else None,
            )
            print(f"    -> {ph_evidence.get('status', '?')}")
        else:
            ph_evidence = {"status": "no_queries", "results": []}
        ph_summary = summarize_producthunt(ph_evidence)
        ph_evidence["summary"] = ph_summary["summary"]
        ph_evidence["supporting"] = ph_summary["supporting"]

        confidence, sources_confirming = compute_confidence(
            sig,
            gt_summary["supporting"],
            ph_summary["supporting"],
            gh_summary["supporting"],
        )

        evidence_list.append({
            "opportunity_type": opp_type,
            "opportunity_title": opp_title,
            "queries": queries,
            "evidence_google_trends": gt_evidence,
            "evidence_github": gh_evidence,
            "evidence_producthunt": ph_evidence,
            "summary_trends": gt_summary["summary"],
            "summary_products": ph_summary["summary"],
            "summary_github": gh_summary["summary"],
            "confidence": confidence,
            "sources_confirming": sources_confirming,
            "supporting_sources": {
                "hn": _hn_strength(sig),
                "trends": gt_summary["supporting"],
                "producthunt": ph_summary["supporting"],
                "github": gh_summary["supporting"],
            },
        })

        # Brief pause between signals
        if i < len(signals) - 1:
            time.sleep(0.5)

    print()

    # Step 4: Synthesize narratives
    print("[4] Synthesizing validation narratives...")
    narratives = [None] * len(signals)

    for batch_num in range(total_batches):
        start_idx = batch_num * args.batch_size
        end_idx = min(start_idx + args.batch_size, len(signals))
        batch_indices = list(range(start_idx, end_idx))

        print(f"  Batch {batch_num + 1}/{total_batches} (signals {start_idx}-{end_idx - 1})...")
        results = synthesize_batch(client, signals, evidence_list, batch_indices)

        for r in results:
            signal_idx = r.get("signal_index", 0)
            actual_idx = start_idx + signal_idx
            if actual_idx < len(signals):
                narratives[actual_idx] = r
                conf = evidence_list[actual_idx].get("confidence", "?")
                sources = evidence_list[actual_idx].get("sources_confirming", 0)
                print(f"    Signal {actual_idx}: confidence={conf}, sources={sources}")

        if batch_num < total_batches - 1 and args.sleep > 0:
            time.sleep(args.sleep)

    print()

    # Step 5: Assemble output
    print("[5] Writing validated opportunities...")
    now_iso = datetime.now(timezone.utc).isoformat()
    validated = []

    for i, sig in enumerate(signals):
        source = sig.get("source", "unknown")
        source_id = str(sig.get("id", ""))
        if ":" in source_id:
            signal_id = source_id
        else:
            signal_id = f"{source}:{source_id}"

        ev = evidence_list[i] if i < len(evidence_list) else {}
        narr = narratives[i] or {}
        narrative_text = (narr.get("narrative") or "").strip()
        if not narrative_text:
            narrative_text = fallback_narrative(sig, ev)

        record = {
            "id": f"val:{signal_id}",
            "signal_id": signal_id,
            "signal_title": ev.get("opportunity_title", sig.get("title", "")),
            "signal_url": sig.get("url", ""),
            "signal_source": source,
            "signal_score": sig.get("score", 0),
            "signal_comments": sig.get("descendants", sig.get("comments", 0)),
            "relevance_score": sig.get("relevance_score"),
            "content_potential": sig.get("content_potential"),
            "opportunity_type": ev.get("opportunity_type", "unknown"),
            "queries": ev.get("queries", {}),
            "evidence_google_trends": ev.get("evidence_google_trends", {}),
            "evidence_producthunt": ev.get("evidence_producthunt", {}),
            "evidence_github": ev.get("evidence_github", {}),
            "sources_confirming": ev.get("sources_confirming", 0),
            "confidence": ev.get("confidence", "low"),
            "narrative": narrative_text,
            "one_line_hook": sig.get("one_line_hook", ""),
            "key_insight": sig.get("key_insight", ""),
            "validated_at": now_iso,
            "model_used": MODEL,
        }
        validated.append(record)

    out_path = out_dir / "validated_opportunities.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for v in validated:
            f.write(json.dumps(v, ensure_ascii=False) + "\n")

    # Summary
    high = sum(1 for v in validated if v["confidence"] == "high")
    medium = sum(1 for v in validated if v["confidence"] == "medium")
    low = sum(1 for v in validated if v["confidence"] == "low")

    print()
    print("=" * 60)
    print(f"Finished. {len(validated)} opportunities validated")
    print(f"  High confidence: {high}")
    print(f"  Medium confidence: {medium}")
    print(f"  Low confidence: {low}")
    print(f"Output: {out_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
