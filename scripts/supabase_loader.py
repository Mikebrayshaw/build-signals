#!/usr/bin/env python3
"""
Supabase Loader - Load matched HN posts to Supabase.

Reads *_matched.jsonl files and upserts to an "opportunities" table.
Uses Supabase REST API directly (no heavy SDK dependencies).
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


def load_matched_files(runs_dir: Path) -> list[dict]:
    """Load all *_matched.jsonl files from a runs directory."""
    records = []

    for pattern in ["ask_hn_matched.jsonl", "show_hn_matched.jsonl"]:
        file_path = runs_dir / pattern
        if file_path.exists():
            print(f"  Loading {pattern}...")
            count_before = len(records)
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))
            print(f"    Added {len(records) - count_before} records")

    return records


def transform_record(record: dict) -> dict:
    """Transform HN record to Supabase schema."""
    return {
        "hn_id": record.get("id"),
        "source": record.get("source", "unknown"),
        "title": record.get("title", ""),
        "url": record.get("url", ""),
        "external_url": record.get("external_url"),
        "author": record.get("by") or record.get("author"),
        "score": record.get("score", 0),
        "comments": record.get("descendants", 0),
        "text": record.get("text", ""),
        "keywords": record.get("keywords", []),
        "github_repos": record.get("github_repos", []),
        "created_at": record.get("created_iso") or datetime.fromtimestamp(
            record.get("created_utc", 0), tz=timezone.utc
        ).isoformat(),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


class SupabaseClient:
    """Lightweight Supabase client using REST API."""

    def __init__(self, url: str, key: str):
        self.base_url = url.rstrip("/")
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",  # Enables upsert
        }

    def upsert(self, table: str, records: list[dict], on_conflict: str = "hn_id") -> dict:
        """Upsert records to a table."""
        url = f"{self.base_url}/rest/v1/{table}"

        # Add on_conflict parameter for upsert behavior
        headers = self.headers.copy()
        headers["Prefer"] = f"resolution=merge-duplicates,return=minimal"

        resp = requests.post(
            url,
            headers=headers,
            json=records,
            params={"on_conflict": on_conflict},
            timeout=30,
        )

        if resp.status_code not in (200, 201, 204):
            raise Exception(f"Supabase error {resp.status_code}: {resp.text}")

        return {"status": "ok", "count": len(records)}


def upsert_records(
    client: SupabaseClient,
    records: list[dict],
    table: str = "opportunities",
    batch_size: int = 50,
) -> tuple[int, int]:
    """Upsert records to Supabase in batches."""

    success = 0
    failed = 0

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        transformed = [transform_record(r) for r in batch]

        try:
            client.upsert(table, transformed)
            success += len(batch)
            print(f"  Upserted batch {i // batch_size + 1}: {len(batch)} records")

        except Exception as e:
            failed += len(batch)
            print(f"  ERROR batch {i // batch_size + 1}: {e}")

    return success, failed


def main():
    parser = argparse.ArgumentParser(
        description="Load matched HN posts to Supabase",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input directory containing *_matched.jsonl files",
    )
    parser.add_argument(
        "--table",
        default="opportunities",
        help="Supabase table name (default: opportunities)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Batch size for upserts (default: 50)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be uploaded without actually uploading",
    )

    args = parser.parse_args()

    # Load env
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set in .env")
        print("Get these from your Supabase project settings > API")
        sys.exit(1)

    input_path = Path(args.input)

    print("=" * 60)
    print("BUILD SIGNALS - Supabase Loader")
    print("=" * 60)
    print(f"input:      {input_path}")
    print(f"table:      {args.table}")
    print(f"batch_size: {args.batch_size}")
    print(f"dry_run:    {args.dry_run}")
    print("=" * 60)
    print()

    # Load records
    print("[1] Loading matched files...")
    if not input_path.is_dir():
        print(f"ERROR: {input_path} is not a directory")
        sys.exit(1)

    records = load_matched_files(input_path)

    if not records:
        print("No records found to upload.")
        sys.exit(0)

    print(f"\nTotal records to upload: {len(records)}")
    print()

    # Dry run - show sample
    if args.dry_run:
        print("[DRY RUN] Sample transformed record:")
        sample = transform_record(records[0])
        for key, value in sample.items():
            if key == "github_repos":
                print(f"  {key}: [{len(value)} repos]")
            elif key == "text":
                text_preview = str(value)[:50] + "..." if len(str(value)) > 50 else value
                print(f"  {key}: {text_preview}")
            else:
                print(f"  {key}: {value}")
        print("\nNo data was uploaded. Remove --dry-run to upload.")
        sys.exit(0)

    # Connect and upload
    print("[2] Connecting to Supabase...")
    client = SupabaseClient(supabase_url, supabase_key)
    print("  Ready!")
    print()

    print("[3] Upserting records...")
    success, failed = upsert_records(client, records, args.table, args.batch_size)
    print()

    print("=" * 60)
    print(f"Finished. Success: {success}, Failed: {failed}")
    print("=" * 60)


if __name__ == "__main__":
    main()
