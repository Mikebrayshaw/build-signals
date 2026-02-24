#!/usr/bin/env python3
"""
Supabase Loader - Upsert opportunities, tweet drafts, and Google Trends to Supabase.

Part of Build Signals: pain point discovery for vibe coders.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / "app" / ".env.local")

try:
    from supabase import create_client, Client
except ImportError:
    print("ERROR: supabase package not installed")
    print("Run: pip install supabase")
    sys.exit(1)


def get_supabase_client() -> Client:
    """Create Supabase client from environment."""
    url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        print("ERROR: SUPABASE_URL/NEXT_PUBLIC_SUPABASE_URL and SUPABASE_KEY/SUPABASE_SERVICE_ROLE_KEY must be set")
        sys.exit(1)

    return create_client(url, key)


def normalize_hn_record(record: dict) -> dict:
    """Normalize HN record to opportunities schema."""
    source = record.get("source", "unknown")
    source_id = str(record.get("id", ""))
    composite_id = f"{source}:{source_id}"

    return {
        "id": composite_id,
        "source": source,
        "source_id": source_id,
        "title": record.get("title", ""),
        "description": record.get("text", ""),
        "url": record.get("url", ""),
        "external_url": record.get("external_url"),
        "author": record.get("author"),
        "score": record.get("score", 0),
        "comments": record.get("descendants", 0),
        "github_url": record.get("github_url"),
        "github_data": record.get("github_repos"),
        "topics": None,
        "created_at": record.get("created_iso"),
    }


def normalize_producthunt_record(record: dict) -> dict:
    """Normalize Product Hunt record to opportunities schema."""
    source_id = str(record.get("id", ""))
    composite_id = f"producthunt:{source_id}"

    tagline = record.get("tagline", "")
    desc = record.get("description", "")
    full_desc = f"{tagline}\n\n{desc}".strip() if tagline else desc

    makers = record.get("makers", [])
    author = makers[0].get("username") if makers else None

    return {
        "id": composite_id,
        "source": "producthunt",
        "source_id": source_id,
        "title": record.get("title", ""),
        "description": full_desc,
        "url": record.get("url", ""),
        "external_url": record.get("external_url"),
        "author": author,
        "score": record.get("votes", 0),
        "comments": record.get("comments", 0),
        "github_url": record.get("github_url"),
        "github_data": record.get("github_repos"),
        "topics": record.get("topics"),
        "created_at": record.get("created_iso"),
    }


def normalize_github_trending(record: dict) -> dict:
    """Normalize GitHub Trending record to opportunities schema."""
    full_name = record.get("id", "")
    composite_id = f"github_trending:{full_name}"

    return {
        "id": composite_id,
        "source": "github_trending",
        "source_id": full_name,
        "title": full_name,
        "description": record.get("description", ""),
        "url": record.get("url", f"https://github.com/{full_name}"),
        "external_url": None,
        "author": record.get("author", ""),
        "score": record.get("stars_today", record.get("score", 0)),
        "comments": 0,
        "github_url": record.get("url", f"https://github.com/{full_name}"),
        "github_data": json.dumps({
            "language": record.get("language", ""),
            "stars": record.get("stars", 0),
            "forks": record.get("forks", 0),
            "stars_today": record.get("stars_today", 0),
            "trending_since": record.get("trending_since", ""),
        }),
        "topics": record.get("topics"),
        "created_at": record.get("created_iso"),
    }


def normalize_scored_signal(record: dict) -> dict:
    """Normalize scored signal to opportunities schema with scoring columns."""
    source = record.get("source", "unknown")
    source_id = str(record.get("id", ""))

    # Build composite ID if not already composite
    if ":" in source_id:
        composite_id = source_id
    else:
        composite_id = f"{source}:{source_id}"

    # Start with base normalization based on source
    if source in ("hn_ask", "hn_show"):
        base = normalize_hn_record(record)
    elif source == "producthunt":
        base = normalize_producthunt_record(record)
    elif source == "github_trending":
        base = normalize_github_trending(record)
    else:
        base = {
            "id": composite_id,
            "source": source,
            "source_id": source_id,
            "title": record.get("title", ""),
            "description": record.get("description", ""),
            "url": record.get("url", ""),
            "external_url": record.get("external_url"),
            "author": record.get("author"),
            "score": record.get("score", 0),
            "comments": record.get("comments", 0),
            "github_url": record.get("github_url"),
            "github_data": record.get("github_repos"),
            "topics": record.get("topics"),
            "created_at": record.get("created_iso"),
        }

    # Add scoring columns
    base["relevance_score"] = record.get("relevance_score")
    base["content_potential"] = record.get("content_potential")
    base["category"] = record.get("category")
    base["one_line_hook"] = record.get("one_line_hook")
    base["key_insight"] = record.get("key_insight")
    base["scored_at"] = record.get("scored_at")
    base["model_used"] = record.get("model_used")

    return base


def normalize_tweet_draft(record: dict) -> dict:
    """Normalize tweet draft for tweet_drafts table."""
    signal_id = record.get("signal_id", "")
    timestamp = record.get("generated_at", datetime.now(timezone.utc).isoformat())
    # Create a stable ID from signal_id
    draft_id = f"draft:{signal_id}:{timestamp[:19].replace(':', '-')}"

    return {
        "id": draft_id,
        "signal_id": signal_id,
        "source": record.get("source", ""),
        "category": record.get("category"),
        "hook": record.get("hook"),
        "full_draft": record.get("full_draft", ""),
        "word_count": record.get("word_count"),
        "generated_at": timestamp,
        "status": record.get("status", "draft"),
        "notes": record.get("notes", ""),
        "model_used": record.get("model_used"),
        "signal_title": record.get("signal_title"),
        "signal_url": record.get("signal_url"),
        "relevance_score": record.get("relevance_score"),
        "content_potential": record.get("content_potential"),
    }


def normalize_google_trend(record: dict) -> dict:
    """Normalize Google Trends record for google_trends table."""
    keyword = record.get("keyword", "")
    trend_id = f"trend:{keyword}"

    return {
        "id": trend_id,
        "keyword": keyword,
        "source_signals": json.dumps(record.get("source_signals", [])),
        "interest_over_time": json.dumps(record.get("interest_over_time", [])),
        "current_interest": record.get("current_interest"),
        "year_ago_interest": record.get("year_ago_interest"),
        "yoy_growth_pct": record.get("yoy_growth_pct"),
        "is_rising": record.get("is_rising", False),
        "related_queries": json.dumps(record.get("related_queries", [])),
        "fetched_at": record.get("fetched_at", datetime.now(timezone.utc).isoformat()),
    }


def normalize_validated_opportunity(record: dict) -> dict:
    """Normalize validated opportunity for validated_opportunities table."""
    return {
        "id": record.get("id", ""),
        "signal_id": record.get("signal_id", ""),
        "signal_title": record.get("signal_title", ""),
        "signal_url": record.get("signal_url"),
        "signal_source": record.get("signal_source", ""),
        "signal_score": record.get("signal_score", 0),
        "signal_comments": record.get("signal_comments", 0),
        "relevance_score": record.get("relevance_score"),
        "content_potential": record.get("content_potential"),
        "opportunity_type": record.get("opportunity_type", "unknown"),
        "queries": json.dumps(record.get("queries", {})) if isinstance(record.get("queries"), dict) else record.get("queries", "{}"),
        "evidence_google_trends": json.dumps(record.get("evidence_google_trends", {})) if isinstance(record.get("evidence_google_trends"), dict) else record.get("evidence_google_trends", "{}"),
        "evidence_producthunt": json.dumps(record.get("evidence_producthunt", {})) if isinstance(record.get("evidence_producthunt"), dict) else record.get("evidence_producthunt", "{}"),
        "evidence_github": json.dumps(record.get("evidence_github", {})) if isinstance(record.get("evidence_github"), dict) else record.get("evidence_github", "{}"),
        "sources_confirming": record.get("sources_confirming", 0),
        "confidence": record.get("confidence", "low"),
        "narrative": record.get("narrative"),
        "one_line_hook": record.get("one_line_hook"),
        "key_insight": record.get("key_insight"),
        "validated_at": record.get("validated_at", datetime.now(timezone.utc).isoformat()),
        "model_used": record.get("model_used"),
    }


def normalize_record(record: dict) -> dict:
    """Legacy normalize for raw source files (backward compat)."""
    source = record.get("source", "unknown")

    if source in ("hn_ask", "hn_show"):
        return normalize_hn_record(record)
    elif source == "producthunt":
        return normalize_producthunt_record(record)
    elif source == "github_trending":
        return normalize_github_trending(record)
    else:
        source_id = str(record.get("id", ""))
        return {
            "id": f"{source}:{source_id}",
            "source": source,
            "source_id": source_id,
            "title": record.get("title", ""),
            "description": record.get("description", ""),
            "url": record.get("url", ""),
            "external_url": record.get("external_url"),
            "author": record.get("author"),
            "score": record.get("score", 0),
            "comments": record.get("comments", 0),
            "github_url": record.get("github_url"),
            "github_data": record.get("github_repos"),
            "topics": record.get("topics"),
            "created_at": record.get("created_iso"),
        }


def upsert_records(client: Client, records: list[dict], table: str, normalize_fn) -> int:
    """Upsert records to Supabase table. Returns count upserted."""
    if not records:
        return 0

    # Normalize and deduplicate
    seen = {}
    for r in records:
        n = normalize_fn(r)
        seen[n["id"]] = n
    normalized = list(seen.values())
    print(f"    Deduplicated: {len(records)} -> {len(normalized)} unique records")

    # Upsert in batches
    batch_size = 100
    upserted = 0

    for i in range(0, len(normalized), batch_size):
        batch = normalized[i:i + batch_size]

        try:
            client.table(table).upsert(
                batch,
                on_conflict="id",
            ).execute()

            upserted += len(batch)
            print(f"    Upserted batch {i // batch_size + 1}: {len(batch)} records")

        except Exception as e:
            print(f"    ERROR upserting batch: {e}")

    return upserted


def load_jsonl_file(path: Path) -> list[dict]:
    """Load records from JSONL file."""
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def main():
    parser = argparse.ArgumentParser(
        description="Load opportunities, tweet drafts, and trends to Supabase",
    )
    parser.add_argument(
        "--input-dir",
        help="Input directory containing JSONL files",
    )
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Use the latest run directory from runs/latest pointer file",
    )
    parser.add_argument(
        "--table",
        default="opportunities",
        help="Default Supabase table name (default: opportunities)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse files but don't upload to Supabase",
    )

    args = parser.parse_args()

    if args.latest:
        latest_marker = Path("runs") / "latest"
        if not latest_marker.exists():
            print("ERROR: runs/latest pointer file not found")
            sys.exit(1)
        input_dir = Path(latest_marker.read_text().strip())
    elif args.input_dir:
        input_dir = Path(args.input_dir)
    else:
        print("ERROR: provide --input-dir or --latest")
        sys.exit(1)

    if not input_dir.exists():
        print(f"ERROR: Input directory does not exist: {input_dir}")
        sys.exit(1)

    print("=" * 60)
    print("BUILD SIGNALS - Supabase Loader")
    print("=" * 60)
    print(f"input: {input_dir}")
    print(f"mode:  {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60)
    print()

    # Find all JSONL files
    jsonl_files = {f.name: f for f in input_dir.glob("*.jsonl")}
    if not jsonl_files:
        print("No JSONL files found in input directory")
        sys.exit(0)

    print(f"Found files: {', '.join(sorted(jsonl_files.keys()))}")
    print()

    # Determine what to load based on file names
    has_scored = "scored_signals.jsonl" in jsonl_files

    # Route files into load groups
    # Group 1: Opportunities (load first due to FK dependency)
    opp_files = []
    if has_scored:
        # Use scored signals as primary opportunities source
        opp_files.append(("scored_signals.jsonl", normalize_scored_signal))
    # Also load raw source files (scored signals may not cover all records)
    raw_source_files = {
        "ask_hn.jsonl": normalize_record,
        "show_hn.jsonl": normalize_record,
        "producthunt.jsonl": normalize_record,
        "github_trending.jsonl": normalize_record,
    }
    for fname, norm_fn in raw_source_files.items():
        if fname in jsonl_files:
            opp_files.append((fname, norm_fn))

    # Group 2: Tweet drafts (needs signal_id FK)
    tweet_files = []
    if "tweet_drafts.jsonl" in jsonl_files:
        tweet_files.append(("tweet_drafts.jsonl", normalize_tweet_draft))

    # Group 3: Google Trends (independent)
    trend_files = []
    if "google_trends.jsonl" in jsonl_files:
        trend_files.append(("google_trends.jsonl", normalize_google_trend))

    # Group 4: Validated opportunities (needs signal_id FK)
    validated_files = []
    if "validated_opportunities.jsonl" in jsonl_files:
        validated_files.append(("validated_opportunities.jsonl", normalize_validated_opportunity))

    if args.dry_run:
        print("DRY RUN - showing what would be loaded:\n")

        for fname, norm_fn in opp_files:
            records = load_jsonl_file(jsonl_files[fname])
            print(f"[opportunities] {fname}: {len(records)} records")
            if records:
                sample = norm_fn(records[0])
                print(f"  Sample: {json.dumps(sample, indent=2, default=str)[:500]}")
            print()

        for fname, norm_fn in tweet_files:
            records = load_jsonl_file(jsonl_files[fname])
            print(f"[tweet_drafts] {fname}: {len(records)} records")
            if records:
                sample = norm_fn(records[0])
                print(f"  Sample: {json.dumps(sample, indent=2, default=str)[:500]}")
            print()

        for fname, norm_fn in trend_files:
            records = load_jsonl_file(jsonl_files[fname])
            print(f"[google_trends] {fname}: {len(records)} records")
            if records:
                sample = norm_fn(records[0])
                print(f"  Sample: {json.dumps(sample, indent=2, default=str)[:500]}")
            print()

        for fname, norm_fn in validated_files:
            records = load_jsonl_file(jsonl_files[fname])
            print(f"[validated_opportunities] {fname}: {len(records)} records")
            if records:
                sample = norm_fn(records[0])
                print(f"  Sample: {json.dumps(sample, indent=2, default=str)[:500]}")
            print()

        return

    # Live mode
    client = get_supabase_client()
    total_upserted = 0

    # Load opportunities first (FK dependency)
    if opp_files:
        print("[1] Loading to opportunities table...")
        all_opp_records = []
        for fname, norm_fn in opp_files:
            print(f"  Loading {fname}...")
            records = load_jsonl_file(jsonl_files[fname])
            # Normalize each record individually using the correct function
            for r in records:
                all_opp_records.append(norm_fn(r))
            print(f"    Loaded {len(records)} records")

        # Deduplicate (scored signals override raw)
        seen = {}
        for r in all_opp_records:
            rid = r["id"]
            # Scored signals (with relevance_score) take priority
            if rid in seen and r.get("relevance_score") is None:
                continue
            seen[rid] = r
        deduped = list(seen.values())
        print(f"  Total: {len(all_opp_records)} -> {len(deduped)} unique")

        # Upsert
        batch_size = 100
        upserted = 0
        for i in range(0, len(deduped), batch_size):
            batch = deduped[i:i + batch_size]
            try:
                client.table("opportunities").upsert(batch, on_conflict="id").execute()
                upserted += len(batch)
                print(f"    Upserted batch {i // batch_size + 1}: {len(batch)} records")
            except Exception as e:
                print(f"    ERROR: {e}")
        total_upserted += upserted
        print()

    # Load tweet drafts (after opportunities due to FK)
    if tweet_files:
        print("[2] Loading to tweet_drafts table...")
        for fname, norm_fn in tweet_files:
            records = load_jsonl_file(jsonl_files[fname])
            print(f"  {fname}: {len(records)} records")
            count = upsert_records(client, records, "tweet_drafts", norm_fn)
            total_upserted += count
        print()

    # Load Google Trends
    if trend_files:
        print("[3] Loading to google_trends table...")
        for fname, norm_fn in trend_files:
            records = load_jsonl_file(jsonl_files[fname])
            print(f"  {fname}: {len(records)} records")
            count = upsert_records(client, records, "google_trends", norm_fn)
            total_upserted += count
        print()

    # Load validated opportunities (after opportunities due to FK)
    if validated_files:
        print("[4] Loading to validated_opportunities table...")
        for fname, norm_fn in validated_files:
            records = load_jsonl_file(jsonl_files[fname])
            print(f"  {fname}: {len(records)} records")
            count = upsert_records(client, records, "validated_opportunities", norm_fn)
            total_upserted += count
        print()

    print("=" * 60)
    print(f"Finished. Total records upserted: {total_upserted}")
    print("=" * 60)


if __name__ == "__main__":
    main()
