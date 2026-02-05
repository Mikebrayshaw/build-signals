#!/usr/bin/env python3
"""
HN Listener - Fetch Ask HN and Show HN posts.

Part of Build Signals: pain point discovery for vibe coders.
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

HN_BASE = "https://hacker-news.firebaseio.com/v0"


def generate_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def fetch_story_ids(story_type: str) -> list[int]:
    """Fetch story IDs for ask/show HN."""
    url = f"{HN_BASE}/{story_type}stories.json"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_item(item_id: int) -> dict | None:
    """Fetch a single HN item."""
    url = f"{HN_BASE}/item/{item_id}.json"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  ERROR fetching {item_id}: {e}")
        return None


def item_to_record(item: dict, source: str) -> dict:
    """Convert HN item to our schema."""
    created_utc = item.get("time", 0)
    created_dt = datetime.fromtimestamp(created_utc, tz=timezone.utc)
    
    return {
        "source": source,
        "id": item.get("id"),
        "title": item.get("title", ""),
        "url": f"https://news.ycombinator.com/item?id={item.get('id')}",
        "external_url": item.get("url"),  # for Show HN links
        "author": item.get("by"),
        "score": item.get("score", 0),
        "descendants": item.get("descendants", 0),  # comment count
        "text": item.get("text", ""),  # self-post body
        "created_utc": created_utc,
        "created_iso": created_dt.isoformat(),
    }


def fetch_stories(
    story_type: str,
    source_name: str,
    cutoff_ts: float,
    limit: int,
    sleep: float = 0.1,
) -> list[dict]:
    """Fetch and filter stories by type."""
    
    print(f"Fetching {story_type} story IDs...")
    story_ids = fetch_story_ids(story_type)
    print(f"  Found {len(story_ids)} IDs")
    
    if limit:
        story_ids = story_ids[:limit]
    
    records = []
    seen = 0
    kept = 0
    
    for i, sid in enumerate(story_ids, 1):
        item = fetch_item(sid)
        seen += 1
        
        if not item:
            continue
        
        # Filter by date
        if item.get("time", 0) < cutoff_ts:
            continue
        
        record = item_to_record(item, source_name)
        records.append(record)
        kept += 1
        
        # Progress
        if kept % 25 == 0:
            print(f"  kept {kept} (seen {seen})...")
        
        # Rate limiting
        if sleep > 0:
            time.sleep(sleep)
    
    print(f"  Done: kept={kept} seen={seen}")
    return records


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Ask HN and Show HN posts",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Fetch posts from last N days (default: 7)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=200,
        help="Max posts to fetch per type (default: 200)",
    )
    parser.add_argument(
        "--out-dir",
        help="Output directory (default: runs/<run_id>)",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.05,
        help="Sleep between API calls (default: 0.05)",
    )
    parser.add_argument(
        "--type",
        choices=["ask", "show", "both"],
        default="both",
        help="Which stories to fetch (default: both)",
    )
    
    args = parser.parse_args()
    
    # Calculate cutoff
    now = datetime.now(timezone.utc)
    cutoff_ts = now.timestamp() - (args.days * 24 * 60 * 60)
    cutoff_iso = datetime.fromtimestamp(cutoff_ts, tz=timezone.utc).isoformat()
    
    # Setup output
    run_id = generate_run_id()
    if args.out_dir:
        out_dir = Path(args.out_dir)
    else:
        out_dir = Path("runs") / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Print config
    print("=" * 60)
    print("BUILD SIGNALS - HN Listener")
    print("=" * 60)
    print(f"run_id:    {run_id}")
    print(f"days:      {args.days}")
    print(f"cutoff:    {cutoff_iso}")
    print(f"limit:     {args.limit}")
    print(f"type:      {args.type}")
    print(f"output:    {out_dir}")
    print("=" * 60)
    print()
    
    total_written = 0
    
    # Fetch Ask HN
    if args.type in ("ask", "both"):
        print("[1] Fetching Ask HN...")
        ask_records = fetch_stories(
            "ask", "hn_ask", cutoff_ts, args.limit, args.sleep
        )
        
        ask_path = out_dir / "ask_hn.jsonl"
        with open(ask_path, "w", encoding="utf-8") as f:
            for r in ask_records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"  Wrote {len(ask_records)} to {ask_path}")
        total_written += len(ask_records)
        print()
    
    # Fetch Show HN
    if args.type in ("show", "both"):
        print("[2] Fetching Show HN...")
        show_records = fetch_stories(
            "show", "hn_show", cutoff_ts, args.limit, args.sleep
        )
        
        show_path = out_dir / "show_hn.jsonl"
        with open(show_path, "w", encoding="utf-8") as f:
            for r in show_records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"  Wrote {len(show_records)} to {show_path}")
        total_written += len(show_records)
        print()
    
    # Summary
    print("=" * 60)
    print(f"Finished. Total posts: {total_written}")
    print(f"Output directory: {out_dir}")
    print("=" * 60)
    
    # Write a latest symlink/marker
    latest_marker = Path("runs") / "latest"
    latest_marker.write_text(str(out_dir))


if __name__ == "__main__":
    main()
