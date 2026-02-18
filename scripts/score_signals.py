#!/usr/bin/env python3
"""
Signal Scorer - Score signals using Claude API for relevance and content potential.

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

SKIP_FILES = {
    "scored_signals.jsonl",
    "tweet_drafts.jsonl",
    "google_trends.jsonl",
}

MODEL = "claude-sonnet-4-20250514"

SCORING_PROMPT = """You are a skeptical signal analyst for a content engine that discovers what people are building, what problems exist, and what tools are trending.

Score each signal on TWO dimensions (1-10 scale):

1. **relevance_score**: How relevant is this to builders, indie hackers, and vibe coders?
   - 1-3: Generic tech news, company announcements, no actionable insight
   - 4-6: Somewhat interesting but common knowledge or vague
   - 7-8: Clear signal of unmet need, growing trend, or validated opportunity
   - 9-10: Exceptional — specific gap in the market with evidence of demand

2. **content_potential**: How good would this be as the basis for a tweet/thread?
   - 1-3: Boring, already well-covered, no hook
   - 4-6: Could be interesting but needs heavy lifting to make compelling
   - 7-8: Strong hook, specific data points, natural story arc
   - 9-10: Irresistible — the kind of thing people screenshot and share

BE SKEPTICAL. Most signals are 4-6. Only genuinely interesting ones score 7+. I'd rather have 3 great signals than 20 mediocre ones.

For each signal, also provide:
- **category**: One of: market-gap, trending-tool, exit-story, emerging-trend, pain-point, vibe-coding-opportunity
- **one_line_hook**: A compelling one-line hook for content (lowercase, conversational, specific)
- **key_insight**: 2-3 sentences on why this matters for builders

Respond with a JSON array. Each element must have:
{
  "signal_index": 0,
  "relevance_score": 7,
  "content_potential": 8,
  "category": "market-gap",
  "one_line_hook": "47 people asked for invoice automation this month. nobody's built it.",
  "key_insight": "2-3 sentence explanation..."
}

ONLY output the JSON array, no other text."""


def load_signals(input_dir: Path) -> list[dict]:
    """Load all signal records from JSONL files, skipping output files."""
    signals = []
    for jsonl_file in sorted(input_dir.glob("*.jsonl")):
        if jsonl_file.name in SKIP_FILES:
            continue
        with open(jsonl_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    signals.append(json.loads(line))
    return signals


def format_signal_for_prompt(signal: dict, index: int) -> str:
    """Format a signal for the Claude prompt."""
    source = signal.get("source", "unknown")
    title = signal.get("title", "")
    description = signal.get("description", signal.get("text", ""))
    score = signal.get("score", 0)
    url = signal.get("url", "")
    author = signal.get("author", "")

    # Truncate long descriptions
    if description and len(description) > 500:
        description = description[:500] + "..."

    return (
        f"[Signal {index}]\n"
        f"Source: {source}\n"
        f"Title: {title}\n"
        f"Score/Votes: {score}\n"
        f"Author: {author}\n"
        f"URL: {url}\n"
        f"Description: {description}\n"
    )


def score_batch(client, signals: list[dict], batch_indices: list[int]) -> list[dict]:
    """Score a batch of signals using Claude API."""
    signal_texts = []
    for i, idx in enumerate(batch_indices):
        signal_texts.append(format_signal_for_prompt(signals[idx], i))

    user_message = (
        "Score the following signals:\n\n"
        + "\n---\n".join(signal_texts)
    )

    for attempt in range(2):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": SCORING_PROMPT + "\n\n" + user_message}
                ],
            )

            text = response.content[0].text.strip()

            # Try to extract JSON from response
            if text.startswith("["):
                scores = json.loads(text)
            else:
                # Try to find JSON array in response
                start = text.find("[")
                end = text.rfind("]") + 1
                if start >= 0 and end > start:
                    scores = json.loads(text[start:end])
                else:
                    if attempt == 0:
                        print(f"    Malformed response, retrying...")
                        continue
                    print(f"    WARNING: Could not parse response, skipping batch")
                    return []

            return scores

        except json.JSONDecodeError:
            if attempt == 0:
                print(f"    JSON parse error, retrying...")
                continue
            print(f"    WARNING: JSON parse failed after retry, skipping batch")
            return []
        except Exception as e:
            print(f"    ERROR calling Claude API: {e}")
            return []

    return []


def main():
    parser = argparse.ArgumentParser(
        description="Score signals using Claude AI",
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
        "--batch-size",
        type=int,
        default=5,
        help="Signals per Claude API call (default: 5)",
    )
    parser.add_argument(
        "--min-relevance",
        type=int,
        default=7,
        help="Minimum relevance score to include (default: 7)",
    )
    parser.add_argument(
        "--min-content",
        type=int,
        default=7,
        help="Minimum content potential to include (default: 7)",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=1.0,
        help="Sleep between API calls (default: 1.0)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show prompts without calling Claude API",
    )

    args = parser.parse_args()

    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key and not args.dry_run:
        print("WARNING: ANTHROPIC_API_KEY not set. Skipping scoring.")
        sys.exit(0)

    input_dir = Path(args.input_dir)
    out_dir = Path(args.out_dir) if args.out_dir else input_dir

    if not input_dir.exists():
        print(f"ERROR: Input directory does not exist: {input_dir}")
        sys.exit(1)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Print config
    print("=" * 60)
    print("BUILD SIGNALS - Claude AI Scorer")
    print("=" * 60)
    print(f"input:          {input_dir}")
    print(f"output:         {out_dir}")
    print(f"batch_size:     {args.batch_size}")
    print(f"min_relevance:  {args.min_relevance}")
    print(f"min_content:    {args.min_content}")
    print(f"mode:           {'DRY RUN' if args.dry_run else 'LIVE'}")
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

    if args.dry_run:
        print("[DRY RUN] Sample prompt for first batch:")
        print("-" * 40)
        batch = signals[:args.batch_size]
        for i, s in enumerate(batch):
            print(format_signal_for_prompt(s, i))
        print("-" * 40)
        print(f"\nWould process {len(signals)} signals in {(len(signals) + args.batch_size - 1) // args.batch_size} batches")
        return

    # Initialize Anthropic client
    try:
        from anthropic import Anthropic
    except ImportError:
        print("ERROR: anthropic package not installed. Run: pip install anthropic")
        sys.exit(1)

    client = Anthropic(api_key=api_key)

    # Score in batches
    print("[2] Scoring signals...")
    scored = []
    now_iso = datetime.now(timezone.utc).isoformat()
    total_batches = (len(signals) + args.batch_size - 1) // args.batch_size

    for batch_num in range(total_batches):
        start_idx = batch_num * args.batch_size
        end_idx = min(start_idx + args.batch_size, len(signals))
        batch_indices = list(range(start_idx, end_idx))

        print(f"  Batch {batch_num + 1}/{total_batches} (signals {start_idx}-{end_idx - 1})...")

        scores = score_batch(client, signals, batch_indices)

        for score_data in scores:
            signal_idx = score_data.get("signal_index", 0)
            actual_idx = start_idx + signal_idx

            if actual_idx >= len(signals):
                continue

            rel = score_data.get("relevance_score", 0)
            content = score_data.get("content_potential", 0)

            if rel >= args.min_relevance and content >= args.min_content:
                # Merge original signal with scores
                merged = dict(signals[actual_idx])
                merged["relevance_score"] = rel
                merged["content_potential"] = content
                merged["category"] = score_data.get("category", "")
                merged["one_line_hook"] = score_data.get("one_line_hook", "")
                merged["key_insight"] = score_data.get("key_insight", "")
                merged["scored_at"] = now_iso
                merged["model_used"] = MODEL
                scored.append(merged)
                print(f"    Signal {actual_idx}: rel={rel} content={content} -> KEPT")
            else:
                print(f"    Signal {actual_idx}: rel={rel} content={content} -> filtered")

        # Sleep between batches
        if batch_num < total_batches - 1 and args.sleep > 0:
            time.sleep(args.sleep)

    # Write output
    out_path = out_dir / "scored_signals.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for s in scored:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    print()
    print("=" * 60)
    print(f"Finished. {len(scored)}/{len(signals)} signals scored 7+ on both dimensions")
    print(f"Output: {out_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
