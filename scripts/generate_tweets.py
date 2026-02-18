#!/usr/bin/env python3
"""
Tweet Generator - Generate tweet drafts from scored signals using Claude API.

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

TWEET_PROMPT = """You are writing a tweet draft (200-280 words) based on a signal about what people are building, what problems exist, or what tools are trending.

VOICE RULES (follow these exactly):
- lowercase throughout
- contractions always (don't, can't, won't, you're, i'm)
- mix sentence lengths. short. then longer flowing ones. fragments.
- specific numbers, not vague claims
- second person where natural
- personality: parenthetical asides, "look," "yeah," starting paragraphs with "and" or "but"
- position yourself as peer sharing discoveries, not expert lecturing

FORBIDDEN WORDS (never use these):
delve, landscape, realm, utilize, moreover, furthermore, additionally, "it's worth noting", "in today's digital age", navigate, tapestry, multifaceted, cornerstone, robust, paradigm, synergy, leverage

STRUCTURE:
- Open with a hook that makes someone stop scrolling
- Build with specific details, numbers, examples
- Close with insight or provocation, not a call to action
- 200-280 words total

Output ONLY a JSON object:
{
  "hook": "the opening line that makes people stop scrolling",
  "full_draft": "the complete 200-280 word tweet text including the hook as the first line"
}"""


def load_scored_signals(input_dir: Path) -> list[dict]:
    """Load scored signals from scored_signals.jsonl."""
    scored_path = input_dir / "scored_signals.jsonl"
    if not scored_path.exists():
        return []

    signals = []
    with open(scored_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                signals.append(json.loads(line))
    return signals


def generate_tweet(client, signal: dict) -> dict | None:
    """Generate a tweet draft for a single signal."""
    source = signal.get("source", "unknown")
    title = signal.get("title", "")
    description = signal.get("description", signal.get("text", ""))
    score = signal.get("score", 0)
    url = signal.get("url", "")
    category = signal.get("category", "")
    one_line_hook = signal.get("one_line_hook", "")
    key_insight = signal.get("key_insight", "")
    relevance = signal.get("relevance_score", 0)
    content_potential = signal.get("content_potential", 0)

    if description and len(description) > 800:
        description = description[:800] + "..."

    user_message = (
        f"Write a tweet draft based on this signal:\n\n"
        f"Source: {source}\n"
        f"Title: {title}\n"
        f"Score/Votes: {score}\n"
        f"URL: {url}\n"
        f"Category: {category}\n"
        f"Hook idea: {one_line_hook}\n"
        f"Key insight: {key_insight}\n"
        f"Description: {description}\n"
    )

    for attempt in range(2):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": TWEET_PROMPT + "\n\n" + user_message}
                ],
            )

            text = response.content[0].text.strip()

            # Parse JSON
            if text.startswith("{"):
                result = json.loads(text)
            else:
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    result = json.loads(text[start:end])
                else:
                    if attempt == 0:
                        print(f"    Malformed response, retrying...")
                        continue
                    return None

            full_draft = result.get("full_draft", "")
            word_count = len(full_draft.split())

            # Validate word count, retry if out of range
            if (word_count < 200 or word_count > 280) and attempt == 0:
                print(f"    Word count {word_count} out of range, retrying...")
                continue

            # Build signal_id
            source_id = str(signal.get("id", ""))
            if ":" in source_id:
                signal_id = source_id
            else:
                signal_id = f"{source}:{source_id}"

            now_iso = datetime.now(timezone.utc).isoformat()

            return {
                "signal_id": signal_id,
                "source": source,
                "category": category,
                "hook": result.get("hook", ""),
                "full_draft": full_draft,
                "word_count": word_count,
                "generated_at": now_iso,
                "status": "draft",
                "notes": "",
                "model_used": MODEL,
                "signal_title": title,
                "signal_url": url,
                "relevance_score": relevance,
                "content_potential": content_potential,
            }

        except json.JSONDecodeError:
            if attempt == 0:
                print(f"    JSON parse error, retrying...")
                continue
            return None
        except Exception as e:
            print(f"    ERROR calling Claude API: {e}")
            return None

    return None


def main():
    parser = argparse.ArgumentParser(
        description="Generate tweet drafts from scored signals",
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
        default=5,
        help="Number of top signals to generate tweets for (default: 5)",
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
        help="Show which signals would be used without calling API",
    )

    args = parser.parse_args()

    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key and not args.dry_run:
        print("WARNING: ANTHROPIC_API_KEY not set. Skipping tweet generation.")
        sys.exit(0)

    input_dir = Path(args.input_dir)
    out_dir = Path(args.out_dir) if args.out_dir else input_dir

    if not input_dir.exists():
        print(f"ERROR: Input directory does not exist: {input_dir}")
        sys.exit(1)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Print config
    print("=" * 60)
    print("BUILD SIGNALS - Tweet Generator")
    print("=" * 60)
    print(f"input:   {input_dir}")
    print(f"output:  {out_dir}")
    print(f"top_n:   {args.top_n}")
    print(f"mode:    {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60)
    print()

    # Load scored signals
    print("[1] Loading scored signals...")
    signals = load_scored_signals(input_dir)
    print(f"  Loaded {len(signals)} scored signals")
    print()

    if not signals:
        print("No scored signals found. Run score_signals.py first.")
        sys.exit(0)

    # Sort by combined score, take top N
    signals.sort(
        key=lambda s: s.get("relevance_score", 0) + s.get("content_potential", 0),
        reverse=True,
    )
    top_signals = signals[:args.top_n]

    print(f"[2] Top {len(top_signals)} signals for tweet generation:")
    for i, s in enumerate(top_signals):
        rel = s.get("relevance_score", 0)
        cp = s.get("content_potential", 0)
        print(f"  {i + 1}. [{rel}+{cp}={rel + cp}] {s.get('title', '')[:60]}")
    print()

    if args.dry_run:
        print("[DRY RUN] Would generate tweets for the above signals.")
        return

    # Initialize Anthropic client
    try:
        from anthropic import Anthropic
    except ImportError:
        print("ERROR: anthropic package not installed. Run: pip install anthropic")
        sys.exit(1)

    client = Anthropic(api_key=api_key)

    # Generate tweets
    print("[3] Generating tweet drafts...")
    drafts = []

    for i, signal in enumerate(top_signals):
        title = signal.get("title", "")[:50]
        print(f"  Generating draft {i + 1}/{len(top_signals)}: {title}...")

        draft = generate_tweet(client, signal)
        if draft:
            drafts.append(draft)
            print(f"    OK ({draft['word_count']} words)")
        else:
            print(f"    FAILED")

        if i < len(top_signals) - 1 and args.sleep > 0:
            time.sleep(args.sleep)

    # Write output
    out_path = out_dir / "tweet_drafts.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for d in drafts:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    print()
    print("=" * 60)
    print(f"Finished. Generated {len(drafts)} tweet drafts")
    print(f"Output: {out_path}")
    print("=" * 60)

    # Print drafts for review
    if drafts:
        print()
        print("=" * 60)
        print("DRAFT PREVIEWS")
        print("=" * 60)
        for i, d in enumerate(drafts):
            print(f"\n--- Draft {i + 1} ({d['word_count']} words) ---")
            print(f"Hook: {d['hook']}")
            print(f"Category: {d['category']}")
            print()
            print(d["full_draft"])
            print()


if __name__ == "__main__":
    main()
