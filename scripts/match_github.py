#!/usr/bin/env python3
"""
GitHub Matcher - Match pain points to relevant GitHub repos.

Extracts keywords from titles and searches GitHub for relevant repos.
Supports: Hacker News (Ask HN, Show HN) and Product Hunt launches.
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# Stop words to filter out
STOP_WORDS = {
    # Common words
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "need", "dare",
    "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by",
    "from", "as", "into", "through", "during", "before", "after",
    "above", "below", "between", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "each",
    "few", "more", "most", "other", "some", "such", "no", "nor", "not",
    "only", "own", "same", "so", "than", "too", "very", "just", "and",
    "but", "if", "or", "because", "until", "while", "of", "at", "by",
    "about", "against", "between", "into", "through", "during", "before",
    "after", "above", "below", "to", "from", "up", "down", "in", "out",
    "on", "off", "over", "under", "again", "further", "then", "once",
    # HN specific
    "ask", "hn", "show", "tell", "what", "who", "which", "whom", "this",
    "that", "these", "those", "am", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "having", "do", "does", "did",
    "doing", "would", "should", "could", "ought", "i", "me", "my",
    "myself", "we", "our", "ours", "ourselves", "you", "your", "yours",
    "yourself", "yourselves", "he", "him", "his", "himself", "she", "her",
    "hers", "herself", "it", "its", "itself", "they", "them", "their",
    "theirs", "themselves", "what", "which", "who", "whom", "this", "that",
    "these", "those", "am", "is", "are", "was", "were", "be", "been",
    "being", "anyone", "everyone", "someone", "something", "anything",
    "everything", "nothing", "thing", "things", "way", "ways", "using",
    "use", "used", "get", "got", "getting", "make", "made", "making",
    "know", "known", "knowing", "think", "thought", "thinking", "want",
    "wanted", "wanting", "see", "seen", "seeing", "come", "came", "coming",
    "go", "went", "going", "take", "took", "taking", "find", "found",
    "finding", "give", "gave", "giving", "tell", "told", "telling",
    "work", "worked", "working", "call", "called", "calling", "try",
    "tried", "trying", "ask", "asked", "asking", "need", "needed",
    "needing", "feel", "felt", "feeling", "become", "became", "becoming",
    "leave", "left", "leaving", "put", "putting", "mean", "meant",
    "meaning", "keep", "kept", "keeping", "let", "letting", "begin",
    "began", "beginning", "seem", "seemed", "seeming", "help", "helped",
    "helping", "show", "showed", "showing", "hear", "heard", "hearing",
    "play", "played", "playing", "run", "ran", "running", "move", "moved",
    "moving", "live", "lived", "living", "believe", "believed", "believing",
    "hold", "held", "holding", "bring", "brought", "bringing", "happen",
    "happened", "happening", "write", "wrote", "writing", "provide",
    "provided", "providing", "sit", "sat", "sitting", "stand", "stood",
    "standing", "lose", "lost", "losing", "pay", "paid", "paying", "meet",
    "met", "meeting", "include", "included", "including", "continue",
    "continued", "continuing", "set", "setting", "learn", "learned",
    "learning", "change", "changed", "changing", "lead", "led", "leading",
    "understand", "understood", "understanding", "watch", "watched",
    "watching", "follow", "followed", "following", "stop", "stopped",
    "stopping", "create", "created", "creating", "speak", "spoke",
    "speaking", "read", "reading", "allow", "allowed", "allowing", "add",
    "added", "adding", "spend", "spent", "spending", "grow", "grew",
    "growing", "open", "opened", "opening", "walk", "walked", "walking",
    "win", "won", "winning", "offer", "offered", "offering", "remember",
    "remembered", "remembering", "love", "loved", "loving", "consider",
    "considered", "considering", "appear", "appeared", "appearing", "buy",
    "bought", "buying", "wait", "waited", "waiting", "serve", "served",
    "serving", "die", "died", "dying", "send", "sent", "sending", "expect",
    "expected", "expecting", "build", "built", "building", "stay", "stayed",
    "staying", "fall", "fell", "falling", "cut", "cutting", "reach",
    "reached", "reaching", "kill", "killed", "killing", "remain", "remained",
    "remaining", "suggest", "suggested", "suggesting", "raise", "raised",
    "raising", "pass", "passed", "passing", "sell", "sold", "selling",
    "require", "required", "requiring", "report", "reported", "reporting",
    "decide", "decided", "deciding", "pull", "pulled", "pulling",
    "best", "better", "good", "great", "new", "old", "long", "short",
    "big", "small", "high", "low", "right", "wrong", "next", "last",
    "first", "second", "third", "now", "today", "tomorrow", "yesterday",
    "year", "years", "month", "months", "week", "weeks", "day", "days",
    "hour", "hours", "minute", "minutes", "time", "times", "people",
    "person", "man", "woman", "child", "world", "life", "hand", "part",
    "place", "case", "week", "company", "system", "program", "question",
    "work", "government", "number", "night", "point", "home", "water",
    "room", "mother", "area", "money", "story", "fact", "month", "lot",
    "right", "study", "book", "eye", "job", "word", "business", "issue",
    "side", "kind", "head", "house", "service", "friend", "father",
    "power", "hour", "game", "line", "end", "member", "law", "car",
    "city", "community", "name", "president", "team", "minute", "idea",
    "kid", "body", "information", "back", "parent", "face", "others",
    "level", "office", "door", "health", "person", "art", "war",
    "history", "party", "result", "change", "morning", "reason", "research",
    "girl", "guy", "moment", "air", "teacher", "force", "education",
    "looking", "look", "really", "still", "even", "also", "much", "many",
    "well", "actually", "already", "always", "never", "ever", "yet",
    "probably", "maybe", "perhaps", "often", "usually", "sometimes",
    "definitely", "certainly", "clearly", "simply", "exactly", "especially",
    "basically", "generally", "specifically", "currently", "recently",
    "finally", "eventually", "immediately", "suddenly", "quickly", "slowly",
    "easily", "hard", "pretty", "quite", "rather", "almost", "enough",
    "less", "least", "most", "nearly", "around", "ago", "away", "back",
    "down", "forward", "home", "inside", "outside", "together", "alone",
}


def extract_keywords(title: str, min_length: int = 3) -> list[str]:
    """Extract meaningful keywords from a title."""
    # Remove "Ask HN:" or "Show HN:" prefix
    title = re.sub(r'^(Ask|Show)\s+HN:\s*', '', title, flags=re.IGNORECASE)

    # For Product Hunt "Name - Tagline" format, use the tagline part primarily
    if " - " in title:
        parts = title.split(" - ", 1)
        # Combine product name and tagline for keywords
        title = " ".join(parts)
    
    # Extract words
    words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9]*\b', title.lower())
    
    # Filter
    keywords = [
        w for w in words 
        if w not in STOP_WORDS and len(w) >= min_length
    ]
    
    # Dedupe while preserving order
    seen = set()
    unique = []
    for k in keywords:
        if k not in seen:
            seen.add(k)
            unique.append(k)
    
    return unique[:6]  # Top 6 keywords


def search_github(
    keywords: list[str],
    token: str,
    min_stars: int = 50,
    limit: int = 5,
) -> list[dict]:
    """Search GitHub for repos matching keywords."""
    
    if not keywords:
        return []
    
    # Build query
    query = " ".join(keywords)
    query += f" stars:>{min_stars}"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": limit,
    }
    
    try:
        resp = requests.get(
            "https://api.github.com/search/repositories",
            headers=headers,
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        
        repos = []
        for item in data.get("items", []):
            repos.append({
                "name": item["full_name"],
                "url": item["html_url"],
                "description": item.get("description") or "",
                "stars": item["stargazers_count"],
                "language": item.get("language"),
                "topics": item.get("topics", []),
                "updated_at": item.get("pushed_at"),
            })
        
        return repos
    
    except Exception as e:
        print(f"    GitHub search error: {e}")
        return []


def process_file(
    input_path: Path,
    output_path: Path,
    token: str,
    min_stars: int,
    repos_per_post: int,
    sleep: float,
    min_score: int,
):
    """Process a JSONL file and add GitHub matches."""
    
    records = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    
    print(f"  Loaded {len(records)} records")
    
    # Filter by minimum score
    if min_score > 0:
        records = [r for r in records if r.get("score", 0) >= min_score]
        print(f"  After score filter (>={min_score}): {len(records)}")
    
    matched = []
    
    for i, record in enumerate(records, 1):
        title = record.get("title", "")
        keywords = extract_keywords(title)
        
        print(f"  [{i}/{len(records)}] {title[:50]}...")
        print(f"    Keywords: {keywords}")
        
        repos = []
        if keywords:
            repos = search_github(keywords, token, min_stars, repos_per_post)
            print(f"    Found {len(repos)} repos")
        
        record["keywords"] = keywords
        record["github_repos"] = repos
        matched.append(record)
        
        if sleep > 0 and i < len(records):
            time.sleep(sleep)
    
    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        for r in matched:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    
    print(f"  Wrote {len(matched)} to {output_path}")
    return len(matched)


def main():
    parser = argparse.ArgumentParser(
        description="Match HN posts to GitHub repos",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input JSONL file or directory containing ask_hn.jsonl/show_hn.jsonl",
    )
    parser.add_argument(
        "--output",
        help="Output file/directory (default: same location with _matched suffix)",
    )
    parser.add_argument(
        "--min-stars",
        type=int,
        default=50,
        help="Minimum GitHub stars (default: 50)",
    )
    parser.add_argument(
        "--repos-per-post",
        type=int,
        default=5,
        help="Max repos per post (default: 5)",
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=10,
        help="Minimum HN score to process (default: 10)",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.5,
        help="Sleep between GitHub API calls (default: 0.5)",
    )
    
    args = parser.parse_args()
    
    # Load env
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("ERROR: GITHUB_TOKEN not set in .env")
        print("Create a token at: https://github.com/settings/tokens")
        sys.exit(1)
    
    input_path = Path(args.input)
    
    print("=" * 60)
    print("BUILD SIGNALS - GitHub Matcher")
    print("=" * 60)
    print(f"input:         {input_path}")
    print(f"min_stars:     {args.min_stars}")
    print(f"repos_per_post: {args.repos_per_post}")
    print(f"min_score:     {args.min_score}")
    print("=" * 60)
    print()
    
    total = 0
    
    if input_path.is_file():
        # Single file
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = input_path.with_name(
                input_path.stem + "_matched" + input_path.suffix
            )
        
        print(f"Processing {input_path.name}...")
        total += process_file(
            input_path, output_path, token,
            args.min_stars, args.repos_per_post, args.sleep, args.min_score
        )
    
    elif input_path.is_dir():
        # Directory - process HN and Product Hunt files
        for filename in ["ask_hn.jsonl", "show_hn.jsonl", "producthunt.jsonl"]:
            file_path = input_path / filename
            if file_path.exists():
                output_path = input_path / filename.replace(".jsonl", "_matched.jsonl")
                print(f"Processing {filename}...")
                total += process_file(
                    file_path, output_path, token,
                    args.min_stars, args.repos_per_post, args.sleep, args.min_score
                )
                print()
    
    else:
        print(f"ERROR: {input_path} not found")
        sys.exit(1)
    
    print("=" * 60)
    print(f"Finished. Processed {total} posts with GitHub matches.")
    print("=" * 60)


if __name__ == "__main__":
    main()
