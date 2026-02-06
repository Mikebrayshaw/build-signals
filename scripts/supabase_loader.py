#!/usr/bin/env python3
"""
Supabase Loader - Upsert opportunities to Supabase.

Part of Build Signals: pain point discovery for vibe coders.
"""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

try:
    from supabase import create_client, Client
except ImportError:
    print("ERROR: supabase package not installed")
    print("Run: pip install supabase")
    sys.exit(1)


def get_supabase_client() -> Client:
    """Create Supabase client from environment."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set")
        sys.exit(1)

    return create_client(url, key)


def normalize_record(record: dict) -> dict:
    """
    Normalize record to match Supabase opportunities table schema.

    Expected schema:
    - id: text (primary key, composite of source + source_id)
    - source: text (hn_ask, hn_show, producthunt)
    - source_id: text (original ID from source)
    - title: text
    - description: text
    - url: text
    - external_url: text
    - author: text
    - score: int
    - comments: int
    - github_url: text (nullable)
    - github_data: jsonb (nullable)
    - topics: text[] (nullable)
    - created_at: timestamptz
    - fetched_at: timestamptz
    """
    source = record.get("source", "unknown")
    source_id = str(record.get("id", ""))

    # Create composite ID
    composite_id = f"{source}:{source_id}"

    # Normalize fields based on source
    if source in ("hn_ask", "hn_show"):
        return {
            "id": composite_id,
            "source": source,
            "source_id": source_id,
            "title": record.get("title", ""),
            "description": record.get("text", ""),  # HN uses 'text'
            "url": record.get("url", ""),
            "external_url": record.get("external_url"),
            "author": record.get("author"),
            "score": record.get("score", 0),
            "comments": record.get("descendants", 0),  # HN uses 'descendants'
            "github_url": record.get("github_url"),
            "github_data": record.get("github"),
            "topics": None,
            "created_at": record.get("created_iso"),
        }
    elif source == "producthunt":
        # Combine tagline and description
        tagline = record.get("tagline", "")
        desc = record.get("description", "")
        full_desc = f"{tagline}\n\n{desc}".strip() if tagline else desc

        # Get maker as author
        makers = record.get("makers", [])
        author = makers[0].get("username") if makers else None

        return {
            "id": composite_id,
            "source": source,
            "source_id": source_id,
            "title": record.get("title", ""),
            "description": full_desc,
            "url": record.get("url", ""),
            "external_url": record.get("external_url"),
            "author": author,
            "score": record.get("votes", 0),
            "comments": record.get("comments", 0),
            "github_url": record.get("github_url"),
            "github_data": record.get("github"),
            "topics": record.get("topics"),
            "created_at": record.get("created_iso"),
        }
    else:
        # Generic fallback
        return {
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
            "github_data": record.get("github"),
            "topics": record.get("topics"),
            "created_at": record.get("created_iso"),
        }


def upsert_records(client: Client, records: list[dict], table: str = "opportunities") -> int:
    """
    Upsert records to Supabase table.

    Returns number of records upserted.
    """
    if not records:
        return 0

    # Normalize all records
    normalized = [normalize_record(r) for r in records]

    # Upsert in batches
    batch_size = 100
    upserted = 0

    for i in range(0, len(normalized), batch_size):
        batch = normalized[i:i + batch_size]

        try:
            result = client.table(table).upsert(
                batch,
                on_conflict="id",
            ).execute()

            upserted += len(batch)
            print(f"    Upserted batch {i // batch_size + 1}: {len(batch)} records")

        except Exception as e:
            print(f"    ERROR upserting batch: {e}")
            # Continue with next batch

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
        description="Load opportunities to Supabase",
    )
    parser.add_argument(
        "--input-dir",
        required=True,
        help="Input directory containing JSONL files",
    )
    parser.add_argument(
        "--table",
        default="opportunities",
        help="Supabase table name (default: opportunities)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse files but don't upload to Supabase",
    )

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"ERROR: Input directory does not exist: {input_dir}")
        sys.exit(1)

    print("=" * 60)
    print("BUILD SIGNALS - Supabase Loader")
    print("=" * 60)
    print(f"input: {input_dir}")
    print(f"table: {args.table}")
    print(f"mode:  {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60)
    print()

    # Find all JSONL files
    jsonl_files = list(input_dir.glob("*.jsonl"))
    if not jsonl_files:
        print("No JSONL files found in input directory")
        sys.exit(0)

    # Load all records
    all_records = []
    for jsonl_file in jsonl_files:
        print(f"[*] Loading {jsonl_file.name}...")
        records = load_jsonl_file(jsonl_file)
        all_records.extend(records)
        print(f"    Loaded {len(records)} records")

    print()
    print(f"Total records to upload: {len(all_records)}")
    print()

    if args.dry_run:
        print("DRY RUN - skipping Supabase upload")
        # Print sample normalized record
        if all_records:
            sample = normalize_record(all_records[0])
            print("\nSample normalized record:")
            print(json.dumps(sample, indent=2, default=str))
    else:
        print("[*] Uploading to Supabase...")
        client = get_supabase_client()
        upserted = upsert_records(client, all_records, args.table)
        print()
        print(f"Successfully upserted {upserted} records")

    print()
    print("=" * 60)
    print("Finished.")
    print("=" * 60)


if __name__ == "__main__":
    main()
