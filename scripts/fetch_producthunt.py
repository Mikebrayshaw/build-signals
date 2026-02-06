#!/usr/bin/env python3
"""
Product Hunt Listener - Fetch recent Product Hunt launches with traction.

Part of Build Signals: validated idea discovery for vibe coders.

Requires a PH Developer Token from:
https://www.producthunt.com/v2/oauth/applications
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

PH_API_URL = "https://api.producthunt.com/v2/api/graphql"


def generate_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def fetch_posts(
    token: str,
    days: int = 7,
    min_votes: int = 50,
    limit: int = 100,
) -> list[dict]:
    """Fetch recent Product Hunt posts using GraphQL API."""

    # Calculate date filter
    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    # GraphQL query to get posts with engagement
    query = """
    query GetPosts($first: Int!, $postedAfter: DateTime) {
        posts(first: $first, postedAfter: $postedAfter, order: VOTES) {
            edges {
                node {
                    id
                    name
                    tagline
                    description
                    url
                    votesCount
                    commentsCount
                    createdAt
                    featuredAt
                    website
                    slug
                    topics {
                        edges {
                            node {
                                name
                                slug
                            }
                        }
                    }
                    makers {
                        id
                        name
                        username
                    }
                }
            }
        }
    }
    """

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    variables = {
        "first": min(limit, 100),  # API max is usually 100 per request
        "postedAfter": cutoff_date,
    }

    try:
        resp = requests.post(
            PH_API_URL,
            headers=headers,
            json={"query": query, "variables": variables},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        if "errors" in data:
            print(f"  GraphQL errors: {data['errors']}")
            return []

        posts = []
        edges = data.get("data", {}).get("posts", {}).get("edges", [])

        for edge in edges:
            node = edge["node"]
            votes = node.get("votesCount", 0)

            # Filter by minimum votes
            if votes < min_votes:
                continue

            # Extract topics
            topics = [
                t["node"]["name"]
                for t in node.get("topics", {}).get("edges", [])
            ]

            # Extract makers
            makers = [
                {"name": m.get("name"), "username": m.get("username")}
                for m in node.get("makers", [])
            ]

            posts.append({
                "source": "producthunt",
                "id": node.get("id"),
                "name": node.get("name", ""),
                "title": f"{node.get('name', '')} - {node.get('tagline', '')}",
                "tagline": node.get("tagline", ""),
                "description": node.get("description", ""),
                "url": f"https://www.producthunt.com/posts/{node.get('slug', '')}",
                "external_url": node.get("website"),
                "score": votes,
                "votes": votes,
                "comments": node.get("commentsCount", 0),
                "topics": topics,
                "makers": makers,
                "created_iso": node.get("createdAt"),
                "featured_at": node.get("featuredAt"),
            })

        return posts

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("  ERROR: Invalid or expired PH token")
            print("  Get a new token at: https://www.producthunt.com/v2/oauth/applications")
        else:
            print(f"  ERROR: HTTP {e.response.status_code}: {e}")
        return []
    except Exception as e:
        print(f"  ERROR fetching PH posts: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Product Hunt launches with traction",
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
        default=100,
        help="Max posts to fetch (default: 100)",
    )
    parser.add_argument(
        "--min-votes",
        type=int,
        default=50,
        help="Minimum votes to include (default: 50)",
    )
    parser.add_argument(
        "--out-dir",
        help="Output directory (default: runs/<run_id>)",
    )

    args = parser.parse_args()

    # Load env
    load_dotenv()
    token = os.getenv("PH_TOKEN")

    if not token:
        print("WARNING: PH_TOKEN not set in .env")
        print("Product Hunt fetch will be skipped.")
        print("Get a token at: https://www.producthunt.com/v2/oauth/applications")
        sys.exit(0)  # Exit gracefully, not an error

    # Setup output
    run_id = generate_run_id()
    if args.out_dir:
        out_dir = Path(args.out_dir)
    else:
        out_dir = Path("runs") / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    # Print config
    print("=" * 60)
    print("BUILD SIGNALS - Product Hunt Listener")
    print("=" * 60)
    print(f"run_id:     {run_id}")
    print(f"days:       {args.days}")
    print(f"limit:      {args.limit}")
    print(f"min_votes:  {args.min_votes}")
    print(f"output:     {out_dir}")
    print("=" * 60)
    print()

    print("[1] Fetching Product Hunt posts...")
    posts = fetch_posts(token, args.days, args.min_votes, args.limit)
    print(f"  Found {len(posts)} posts with {args.min_votes}+ votes")
    print()

    # Write output
    ph_path = out_dir / "producthunt.jsonl"
    with open(ph_path, "w", encoding="utf-8") as f:
        for p in posts:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"  Wrote {len(posts)} to {ph_path}")

    # Update latest marker
    latest_marker = Path("runs") / "latest"
    latest_marker.write_text(str(out_dir))

    print()
    print("=" * 60)
    print(f"Finished. Total posts: {len(posts)}")
    print(f"Output directory: {out_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
