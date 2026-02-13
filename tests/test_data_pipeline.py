from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.match_github import extract_keywords
from scripts.supabase_loader import load_jsonl_file, normalize_record


FIXTURES = Path(__file__).parent / "fixtures"


def test_extract_keywords_handles_hn_prefix_and_order():
    title = "Ask HN: Rust Kafka retry pipeline observability"

    assert extract_keywords(title) == [
        "rust",
        "kafka",
        "retry",
        "pipeline",
        "observability",
    ]


def test_extract_keywords_handles_producthunt_title_format_and_limit():
    title = "LaunchPad - AI agent for GitHub PR reviews and automation"

    assert extract_keywords(title) == [
        "launchpad",
        "agent",
        "github",
        "reviews",
        "automation",
    ]


def test_normalize_record_hn_mapping_from_fixture():
    hn_record = load_jsonl_file(FIXTURES / "hn_records.jsonl")[0]

    normalized = normalize_record(hn_record)

    assert normalized["id"] == "hn_ask:101"
    assert normalized["description"] == "We need better retries and tracing."
    assert normalized["score"] == 42
    assert normalized["comments"] == 12
    assert normalized["topics"] is None


def test_normalize_record_producthunt_mapping_from_fixture():
    ph_record = load_jsonl_file(FIXTURES / "producthunt_records.jsonl")[0]

    normalized = normalize_record(ph_record)

    assert normalized["id"] == "producthunt:ph_501"
    assert normalized["author"] == "maker1"
    assert normalized["score"] == 321
    assert normalized["comments"] == 18
    assert normalized["description"] == (
        "AI reviews for pull requests\n\nAutomated code review with clear feedback."
    )
    assert normalized["topics"] == ["Developer Tools", "Artificial Intelligence"]


def test_matcher_output_is_compatible_with_loader_schema():
    matched_record = load_jsonl_file(FIXTURES / "matcher_output.jsonl")[0]

    normalized = normalize_record(matched_record)

    assert normalized["github_url"] == "https://github.com/tokio-rs/tokio"
    assert isinstance(normalized["github_data"], list)
    assert normalized["github_data"][0]["name"] == "tokio-rs/tokio"

    expected_keys = {
        "id",
        "source",
        "source_id",
        "title",
        "description",
        "url",
        "external_url",
        "author",
        "score",
        "comments",
        "github_url",
        "github_data",
        "topics",
        "created_at",
    }
    assert set(normalized.keys()) == expected_keys
