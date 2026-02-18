#!/usr/bin/env python3
"""
GitHub Trending Scraper - Fetch trending repos from github.com/trending.

Part of Build Signals: pain point discovery for vibe coders.
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

TRENDING_URL = "https://github.com/trending"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}


def generate_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def parse_number(text: str) -> int:
    """Parse number strings like '1,234' or '12.5k' to int."""
    text = text.strip().replace(",", "")
    if not text:
        return 0
    if text.endswith("k"):
        return int(float(text[:-1]) * 1000)
    try:
        return int(text)
    except ValueError:
        return 0


def scrape_trending(since: str = "daily") -> list[dict]:
    """Scrape github.com/trending for a given time range."""
    url = f"{TRENDING_URL}?since={since}"
    print(f"  Fetching {url} ...")

    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    articles = soup.select("article.Box-row")

    if not articles:
        print(f"  WARNING: No trending repos found for since={since}")
        return []

    repos = []
    now_iso = datetime.now(timezone.utc).isoformat()

    for article in articles:
        # Repo name: h2 > a with href like /owner/repo
        h2 = article.select_one("h2")
        if not h2:
            continue
        link = h2.select_one("a")
        if not link:
            continue

        href = link.get("href", "").strip("/")
        parts = href.split("/")
        if len(parts) != 2:
            continue
        owner, repo_name = parts
        full_name = f"{owner}/{repo_name}"

        # Description
        desc_tag = article.select_one("p")
        description = desc_tag.get_text(strip=True) if desc_tag else ""

        # Language
        lang_tag = article.select_one("[itemprop='programmingLanguage']")
        language = lang_tag.get_text(strip=True) if lang_tag else ""

        # Stars (total)
        star_links = article.select("a.Link--muted")
        stars = 0
        forks = 0
        for sl in star_links:
            href_val = sl.get("href", "")
            text = sl.get_text(strip=True)
            if "/stargazers" in href_val:
                stars = parse_number(text)
            elif "/forks" in href_val:
                forks = parse_number(text)

        # Stars today/this week
        stars_today = 0
        span_tags = article.select("span.d-inline-block.float-sm-right")
        if span_tags:
            stars_text = span_tags[0].get_text(strip=True)
            # "350 stars today" or "1,200 stars this week"
            num_part = stars_text.split(" star")[0].strip()
            stars_today = parse_number(num_part)

        repos.append({
            "source": "github_trending",
            "id": full_name,
            "title": full_name,
            "description": description,
            "url": f"https://github.com/{full_name}",
            "external_url": None,
            "language": language,
            "stars": stars,
            "stars_today": stars_today,
            "forks": forks,
            "topics": [],
            "trending_since": since,
            "author": owner,
            "score": stars_today,
            "created_iso": now_iso,
        })

    return repos


def main():
    parser = argparse.ArgumentParser(
        description="Scrape GitHub Trending repos",
    )
    parser.add_argument(
        "--since",
        choices=["daily", "weekly", "both"],
        default="both",
        help="Trending period (default: both)",
    )
    parser.add_argument(
        "--out-dir",
        help="Output directory (default: runs/<run_id>)",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=2.0,
        help="Sleep between requests when fetching both periods (default: 2.0)",
    )

    args = parser.parse_args()

    # Setup output
    run_id = generate_run_id()
    if args.out_dir:
        out_dir = Path(args.out_dir)
    else:
        out_dir = Path("runs") / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    # Print config
    print("=" * 60)
    print("BUILD SIGNALS - GitHub Trending Scraper")
    print("=" * 60)
    print(f"run_id:  {run_id}")
    print(f"since:   {args.since}")
    print(f"output:  {out_dir}")
    print("=" * 60)
    print()

    all_repos = []
    seen_ids = set()

    periods = []
    if args.since in ("daily", "both"):
        periods.append("daily")
    if args.since in ("weekly", "both"):
        periods.append("weekly")

    for i, period in enumerate(periods):
        print(f"[{i + 1}] Fetching {period} trending...")
        try:
            repos = scrape_trending(period)
            print(f"  Found {len(repos)} repos")
        except Exception as e:
            print(f"  ERROR scraping {period}: {e}")
            repos = []

        # Dedup: daily takes priority over weekly
        for repo in repos:
            if repo["id"] not in seen_ids:
                seen_ids.add(repo["id"])
                all_repos.append(repo)

        # Sleep between requests
        if i < len(periods) - 1 and args.sleep > 0:
            print(f"  Sleeping {args.sleep}s...")
            time.sleep(args.sleep)

        print()

    if not all_repos:
        print("No repos found. Exiting gracefully.")
        sys.exit(0)

    # Write output
    out_path = out_dir / "github_trending.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for r in all_repos:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Update latest pointer
    latest_marker = Path("runs") / "latest"
    latest_marker.parent.mkdir(parents=True, exist_ok=True)
    latest_marker.write_text(out_dir.as_posix())

    # Summary
    print("=" * 60)
    print(f"Finished. Total repos: {len(all_repos)} (deduped)")
    print(f"Output: {out_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
