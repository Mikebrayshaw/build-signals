#!/usr/bin/env python3
"""
Google Trends Enrichment - Extract keywords from signals and query Google Trends.

Part of Build Signals: pain point discovery for vibe coders.

This is enrichment data — if Google blocks requests, we exit gracefully.
"""

import argparse
import json
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

try:
    from pytrends.request import TrendReq
except ImportError:
    print("ERROR: pytrends not installed. Run: pip install pytrends")
    sys.exit(1)


# Common stop words to filter out
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "it", "as", "are", "was", "were",
    "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might", "can", "shall",
    "not", "no", "nor", "so", "if", "then", "than", "too", "very",
    "just", "about", "up", "out", "how", "what", "when", "where", "who",
    "which", "why", "all", "each", "every", "both", "few", "more", "most",
    "other", "some", "such", "only", "own", "same", "that", "this",
    "these", "those", "i", "me", "my", "we", "our", "you", "your",
    "he", "him", "his", "she", "her", "they", "them", "their", "its",
    "ask", "hn", "show", "tell", "need", "want", "use", "using", "used",
    "new", "best", "get", "got", "make", "made", "like", "way", "one",
    "also", "any", "into", "over", "after", "before", "between", "under",
    "here", "there", "now", "still", "yet", "already", "much", "many",
}

# Source file names to skip (not signal data)
SKIP_FILES = {
    "scored_signals.jsonl",
    "tweet_drafts.jsonl",
    "google_trends.jsonl",
}


def generate_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def extract_keywords(signals: list[dict], max_keywords: int = 20) -> list[str]:
    """Extract top keywords from signal titles using frequency analysis."""
    word_counts = Counter()

    for signal in signals:
        title = signal.get("title", "")
        # Clean and tokenize
        words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]*[a-zA-Z0-9+#]|[a-zA-Z]", title.lower())

        # Build bigrams for multi-word terms
        filtered = [w for w in words if w not in STOP_WORDS and len(w) > 2]

        for word in filtered:
            word_counts[word] += 1

        # Bigrams
        for i in range(len(filtered) - 1):
            bigram = f"{filtered[i]} {filtered[i + 1]}"
            word_counts[bigram] += 1

    # Filter: must appear at least twice, prefer bigrams
    candidates = [
        (word, count) for word, count in word_counts.items()
        if count >= 2
    ]
    candidates.sort(key=lambda x: (-len(x[0].split()), -x[1]))

    # Remove single words that are part of a selected bigram
    selected = []
    selected_words = set()
    for word, count in candidates:
        if len(selected) >= max_keywords:
            break
        parts = word.split()
        # Skip single words already covered by bigrams
        if len(parts) == 1 and word in selected_words:
            continue
        selected.append(word)
        for p in parts:
            selected_words.add(p)

    return selected


def load_signals(input_dir: Path) -> list[dict]:
    """Load all signal records from JSONL files in input dir."""
    signals = []
    for jsonl_file in input_dir.glob("*.jsonl"):
        if jsonl_file.name in SKIP_FILES:
            continue
        with open(jsonl_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    record = json.loads(line)
                    signals.append(record)
    return signals


def fetch_trends(keywords: list[str], sleep: float = 5.0) -> list[dict]:
    """Query Google Trends for keyword interest over time."""
    pytrends = TrendReq(hl="en-US", tz=360)
    results = []
    now_iso = datetime.now(timezone.utc).isoformat()

    # Process in batches of 5 (pytrends limit)
    for i in range(0, len(keywords), 5):
        batch = keywords[i:i + 5]
        print(f"  Querying trends for: {batch}")

        try:
            pytrends.build_payload(batch, timeframe="today 12-m")
            iot = pytrends.interest_over_time()

            if iot.empty:
                print(f"  No interest data returned for batch")
                for kw in batch:
                    results.append({
                        "keyword": kw,
                        "source_signals": [],
                        "interest_over_time": [],
                        "current_interest": 0,
                        "year_ago_interest": 0,
                        "yoy_growth_pct": 0.0,
                        "is_rising": False,
                        "related_queries": [],
                        "fetched_at": now_iso,
                    })
                continue

            # Get related queries
            try:
                related = pytrends.related_queries()
            except Exception:
                related = {}

            for kw in batch:
                if kw not in iot.columns:
                    continue

                series = iot[kw]
                time_data = [
                    {"date": idx.strftime("%Y-%m-%d"), "value": int(val)}
                    for idx, val in series.items()
                ]

                current = int(series.iloc[-1]) if len(series) > 0 else 0
                year_ago = int(series.iloc[0]) if len(series) > 0 else 0

                if year_ago > 0:
                    yoy_growth = ((current - year_ago) / year_ago) * 100
                else:
                    yoy_growth = 100.0 if current > 0 else 0.0

                # Related queries
                rel_queries = []
                if kw in related and related[kw].get("top") is not None:
                    top_df = related[kw]["top"]
                    if not top_df.empty:
                        rel_queries = top_df["query"].head(5).tolist()

                results.append({
                    "keyword": kw,
                    "source_signals": [],
                    "interest_over_time": time_data,
                    "current_interest": current,
                    "year_ago_interest": year_ago,
                    "yoy_growth_pct": round(yoy_growth, 1),
                    "is_rising": yoy_growth > 50,
                    "related_queries": rel_queries,
                    "fetched_at": now_iso,
                })

        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "too many" in error_msg or "blocked" in error_msg:
                print(f"  WARNING: Google Trends rate limited/blocked. Stopping gracefully.")
                break
            print(f"  WARNING: Error querying trends: {e}")
            for kw in batch:
                results.append({
                    "keyword": kw,
                    "source_signals": [],
                    "interest_over_time": [],
                    "current_interest": 0,
                    "year_ago_interest": 0,
                    "yoy_growth_pct": 0.0,
                    "is_rising": False,
                    "related_queries": [],
                    "fetched_at": now_iso,
                })

        # Sleep between batches
        if i + 5 < len(keywords) and sleep > 0:
            print(f"  Sleeping {sleep}s...")
            time.sleep(sleep)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Enrich signals with Google Trends data",
    )
    parser.add_argument(
        "--input-dir",
        required=True,
        help="Input directory containing JSONL signal files",
    )
    parser.add_argument(
        "--out-dir",
        help="Output directory (default: same as input-dir)",
    )
    parser.add_argument(
        "--max-keywords",
        type=int,
        default=20,
        help="Max keywords to query (default: 20)",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=5.0,
        help="Sleep between pytrends batches (default: 5.0)",
    )

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    out_dir = Path(args.out_dir) if args.out_dir else input_dir

    if not input_dir.exists():
        print(f"ERROR: Input directory does not exist: {input_dir}")
        sys.exit(1)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Print config
    print("=" * 60)
    print("BUILD SIGNALS - Google Trends Enrichment")
    print("=" * 60)
    print(f"input:        {input_dir}")
    print(f"output:       {out_dir}")
    print(f"max_keywords: {args.max_keywords}")
    print(f"sleep:        {args.sleep}s")
    print("=" * 60)
    print()

    # Load signals
    print("[1] Loading signals...")
    signals = load_signals(input_dir)
    print(f"  Loaded {len(signals)} signals")
    print()

    if not signals:
        print("No signals found. Exiting.")
        sys.exit(0)

    # Extract keywords
    print("[2] Extracting keywords...")
    keywords = extract_keywords(signals, args.max_keywords)
    print(f"  Top {len(keywords)} keywords: {keywords}")
    print()

    if not keywords:
        print("No keywords extracted. Exiting.")
        sys.exit(0)

    # Fetch trends
    print("[3] Querying Google Trends...")
    trends = fetch_trends(keywords, args.sleep)
    print(f"  Got trends for {len(trends)} keywords")
    print()

    # Map source signals to keywords
    for trend in trends:
        kw = trend["keyword"].lower()
        sources = []
        for signal in signals:
            title = signal.get("title", "").lower()
            if kw in title:
                source = signal.get("source", "unknown")
                sid = str(signal.get("id", ""))
                sources.append(f"{source}:{sid}")
        trend["source_signals"] = sources[:10]  # cap at 10

    # Write output
    out_path = out_dir / "google_trends.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for t in trends:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

    # Summary
    rising = [t for t in trends if t["is_rising"]]
    print("=" * 60)
    print(f"Finished. {len(trends)} keywords, {len(rising)} rising (>50% YoY)")
    print(f"Output: {out_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
