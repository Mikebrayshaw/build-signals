# Lessons Learned

Claude updates this file after every correction or mistake. Each entry captures the pattern to avoid repeating it.

## Format
**[Date] - Category**: What went wrong → What to do instead

---

**2026-02-09 - Dependency Management**: Ran `pip install --upgrade supabase` which pulled in `pyiceberg` → `pyroaring` (C extension) and failed without MSVC. → Diagnose the actual broken package first (httpx version), upgrade only that.

**2026-02-09 - Schema Assumptions**: Loader script had column names in comments (`description`, `github_data`) that didn't match the actual Supabase table (`text`, `github_repos`). → Always `SELECT * LIMIT 1` from the real table before writing migration or loader code.

**2026-02-09 - Batch Upserts**: Loading overlapping JSONL files (base + matched) caused duplicate IDs in the same batch, which Postgres ON CONFLICT rejects. → Deduplicate by PK in-memory before batching.

**2026-02-09 - Env File Loading**: `load_dotenv()` with no arguments only checks CWD. The actual `.env.local` was in `app/`, and the var names were `NEXT_PUBLIC_SUPABASE_URL` not `SUPABASE_URL`. → Always verify both the file path and the var names.

**2026-02-09 - API Complexity Limits**: Product Hunt GraphQL API has a 500k complexity limit. Fetching 100 posts with nested topics/makers blows past it. → Use small page sizes (20) with cursor pagination instead of one big request.

**2026-02-09 - Windows Console Encoding**: Python on Windows defaults to cp1252, which crashes on non-Latin characters (Cyrillic, CJK, etc) in print(). → Use `.encode('ascii', 'replace').decode()` for user-facing strings, or set `PYTHONIOENCODING=utf-8`.

**2026-02-09 - Token Expiry**: GitHub PATs expire silently. The match_github script had no clear error for 401 beyond a generic "search error". → Check token validity before running a long batch, and surface auth errors early.

**2026-02-18 - Streamlit Secrets**: `st.secrets.get("KEY")` throws `StreamlitSecretNotFoundError` if no `secrets.toml` file exists at all. The `or` short-circuit in `os.getenv("X") or st.secrets.get("X")` doesn't help because the exception fires before returning. → Wrap `st.secrets` access in try/except, or check for file existence first.

**2026-02-18 - Supabase JSON Text Columns**: Supabase stores JSON/JSONB columns but the Python client returns them as strings, not parsed objects. Dashboard code that calls `.get()` on these values crashes with `'str' object has no attribute 'get'`. → Always `json.loads()` fields that contain JSON arrays/objects when reading from Supabase.
