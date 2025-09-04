# Implementation Plan

[Overview]
Integrate ScrapegraphAI SmartScraperGraph to fetch readable text from each research source URL and inject that text (not the URLs) into LLM prompts, while caching scraped results in blog_ideas.json and removing any URL list injection from prompts.

This change replaces the current behavior of passing URL lists to the LLM with pre-scraped source excerpts. Scraped content will be cached to avoid repeated network calls and to ensure reproducibility. 02_generate_blog_drafts.py will build prompts from structured idea metadata plus the scraped text excerpts; it will no longer instruct the LLM to "visit" URLs nor include the URL list in prompts. Source lists will be appended programmatically to the final markdown output (outside the LLM response) to preserve attribution without violating the "no URLs in prompts" requirement.

[Types]  
Introduce a cached source payload structure stored per idea.

- ScrapedSource (object)
  - url: string (required)
  - status: "ok" | "error" (required)
  - text: string (required if status="ok"; empty if "error")
  - char_count: integer (number of characters in text; 0 if error)
  - last_scraped_at: string (ISO 8601)
  - error: string (optional; present if status="error")

- Idea (extension)
  - scraped_sources: ScrapedSource[] (optional; defaults to [])
    - Caching strategy: if present and non-empty, re-use unless a refresh flag is introduced later.
    - Failure policy: continue on individual URL failures (Option A).

[Files]
Modify one script and one generator; add one small utility for scraping.

- New:
  - utils/scrape_sources.py
    - Purpose: Encapsulate ScrapegraphAI SmartScraperGraph configuration and scraping logic for a list of URLs; returns ScrapedSource[] with status and metadata. Handles Option A failure policy.

- Modified:
  - 02_generate_blog_drafts.py
    - Remove injecting URL lists into prompts.
    - Add scraped text injection from cached/newly-scraped sources.
    - Adjust prompts to reference "source excerpts" rather than telling the model to visit URLs.
    - Remove "Display all sources…" instruction from system prompt; append Sources section programmatically after LLM response.
    - Add cache read/write to idea.scraped_sources with timestamps.
  - 01_process_blog_ideas.py
    - Add 'scraped_sources' default to enriched fields and JSON output schema (initialized to []) to preserve schema stability for downstream code.

- Unchanged:
  - guidance/* files and existing research_content markdown.

[Functions]
Add scraper helpers; extend main flow to use cache + scraping; adjust prompt construction.

- New functions
  - utils/scrape_sources.py
    - build_llm_env(): None
      - Sets OPENAI_API_KEY and OPENAI_BASE_URL/OPENAI_API_BASE env vars using existing OPENAI_AUTH_KEY and host/port from 02_generate_blog_drafts.py.
    - scrape_url(url: str) -> ScrapedSource
      - Uses SmartScraperGraph with a generic prompt: "Extract main readable page text, excluding navigation, ads, comments; return markdown/plain text."
      - Returns { url, status, text, char_count, last_scraped_at, error? }.
    - scrape_urls(urls: List[str]) -> List[ScrapedSource]
      - Iterates scrape_url with Option A policy (continue on errors).
  - 02_generate_blog_drafts.py
    - get_or_build_scraped_sources(idea: dict) -> List[ScrapedSource]
      - If idea.scraped_sources exists and non-empty, return as cache.
      - Else scrape via utils/scrape_sources and persist to blog_ideas.json for this idea.
    - build_source_excerpts(scraped: List[ScrapedSource]) -> str
      - Concatenate text from status="ok" entries into a single string. No URL list or headings containing URLs. Respect "no caps" requirement (no local truncation).
    - build_idea_context(idea: dict) -> str
      - Compose idea metadata (title, pain_point, target_audience, content_details) without any URL list.
    - add_sources_section_to_output(idea: dict, response: str) -> str
      - Append a formatted "Sources" section to the output with the idea.sources list programmatically, not passed to LLM.

- Modified functions
  - select_parameters(...)
    - Replace "Visit all URLs…" paragraph with "Use the provided source excerpts."
    - Add a "Source Excerpts" block containing text only (no URLs).
  - generate_blog_post(...)
    - Remove instruction to visit URLs; replace with "Use the provided source excerpts."
    - Remove "Display all sources…" instruction; rely on post-processing to append Sources list.
  - save_draft_and_update_json(...)
    - After obtaining response, call add_sources_section_to_output to include Sources in the saved markdown output.

- Removed/Adjusted
  - Idea content assembly no longer includes a "Sources:" list in the prompt payload.

[Classes]
No class additions; functional utilities suffice.

- None new
- None removed
- N/A modifications to existing classes

[Dependencies]
Use existing scrapegraphai via Pipfile; rely on OpenAI-compatible local endpoint.

- scrapegraphai already present in Pipfile.
- Environment:
  - OPENAI_API_KEY: use existing OPENAI_AUTH_KEY ("outsider").
  - OPENAI_BASE_URL (or OPENAI_API_BASE): http://192.168.8.90:42069/v1
  - Model: gpt-oss-120b (from existing OPENAI_MODEL)
- Note: SmartScraperGraph will be configured to provider "openai" and to prefer plain HTTP via base URL. Unsupported content (e.g., YouTube) will likely yield empty text; handled by Option A (continue).

[Testing]
Validate scraping, caching, and prompt changes without exceeding token budgets by provider limits.

- Unit-style checks (informal):
  - Run 02_generate_blog_drafts.py with --ideas_id 2a2ab6040f05 and confirm:
    - First run: scraped_sources is created, article generated, Sources appended programmatically.
    - Second run: skips network, reuses cached scraped_sources.
  - Verify prompts no longer include URL lists or "visit URLs" instructions.
  - Confirm 01_process_blog_ideas.py adds scraped_sources: [] for new entries and doesn't break.

[Implementation Order]
Implement utility, wire caching, remove URL injections, then update prompts and output handling.

1) Add utils/scrape_sources.py with SmartScraperGraph integration and env setup.
2) Update 01_process_blog_ideas.py to include scraped_sources default (empty list) in enriched fields and JSON output structure.
3) In 02_generate_blog_drafts.py:
   - Implement get_or_build_scraped_sources, build_source_excerpts, build_idea_context, add_sources_section_to_output.
   - Remove URL list injection in idea_content and prompt text.
   - Update select_parameters and generate_blog_post prompts to use "Source Excerpts".
   - Persist scraped_sources back into blog_ideas.json for the processed idea (with last_scraped_at).
4) Run a single-idea test to validate scrape + cache + generation + Sources appending.
5) Run a batch test (with/without --force_article_gen) as needed.
6) Commit changes.
