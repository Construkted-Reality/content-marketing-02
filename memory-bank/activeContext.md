# Active Context

## Current Work
Successfully integrated both ScrapegraphAI web scraping and YouTube transcript extraction into the `02_generate_blog_drafts.py` script. The implementation now handles mixed source lists containing both web pages and YouTube videos, extracting actual content instead of passing URLs to the LLM.

## Recent Changes
- **Reference Context Field**: Added `reference_context` to the blog idea schema. `01_process_blog_ideas.py` now extracts this optional field from markdown sections, and `02_generate_blog_drafts.py` includes it in the LLM prompt via the updated `build_idea_context` helper function
- **Retry Mechanism Implementation**: Added robust retry logic to `utils/scrape_sources.py` for handling transient scraping failures
- **YouTube Transcript Integration**: Added YouTube video transcript extraction using yt-dlp via existing `extract_transcript.py` script
- **Mixed Source Processing**: Enhanced scraping workflow to handle both web pages (ScrapegraphAI) and YouTube videos (yt-dlp) in the same source list
- **ScrapegraphAI Integration**: Created `utils/scrape_sources.py` with SmartScraperGraph integration
- **Prompt Restructuring**: Replaced "Visit all URLs..." instructions with "Use the provided source excerpts"
- **Caching Implementation**: Added `scraped_sources` field to `blog_ideas.json` for persistent caching of both web content and video transcripts
- **Programmatic Sources**: Sources section now appended automatically outside LLM generation
- **Schema Updates**: Modified `01_process_blog_ideas.py` to include `scraped_sources: []` in new ideas

## Key Technical Concepts
- ScrapegraphAI SmartScraperGraph for LLM-assisted web scraping
- OpenAI-compatible API endpoint configuration for scraping
- Caching mechanism using JSON persistence
- Option A failure policy (continue on individual URL failures)
- Separation of content generation from source attribution
- Helper function architecture for modular scraping workflow

## Relevant Files and Code
- **File**: `utils/scrape_sources.py` (NEW)
  - Functions: `build_llm_env()`, `scrape_url()`, `scrape_urls()`
  - Uses local OpenAI endpoint (http://192.168.8.90:42069/v1) with model gpt-oss-120b
  - Implements comprehensive error handling and URL validation
  - **Retry Mechanism**: 3 attempts per URL with 1-second delays between retries
  - Returns structured ScrapedSource dictionaries with status, text, char_count

- **File**: `02_generate_blog_drafts.py` (EXTENSIVELY MODIFIED)
  - **NEW**: Added `extract_youtube_transcript()` function using subprocess to call `extract_transcript.py`
  - **ENHANCED**: Modified `get_or_build_scraped_sources()` to detect YouTube URLs and process them separately
  - Added helper functions: `build_source_excerpts()`, `build_idea_context()`, `add_sources_section_to_output()`
  - Modified `select_parameters()` and `generate_blog_post()` to use scraped excerpts
  - Updated `save_draft_and_update_json()` to append Sources section programmatically
  - Replaced manual idea content assembly with `build_idea_context()` function
  - **YouTube Detection**: Uses regex `r'(youtube\.com|youtu\.be)'` to identify video URLs
  - **Mixed Processing**: Handles both YouTube transcripts and web scraping in single workflow

- **File**: `extract_transcript.py` (EXISTING - LEVERAGED)
  - Used via subprocess call for YouTube transcript extraction
  - Handles yt-dlp integration and SRT parsing
  - Returns plain text transcripts from video subtitles

- **File**: `01_process_blog_ideas.py` (MINOR UPDATES)
  - Added 'scraped_sources' to enriched_fields list
  - Added default `scraped_sources: []` initialization in both processing methods

## Problem Solving
- **URL Injection Issue**: Solved by replacing URL lists with scraped text excerpts in prompts
- **Content Grounding**: Improved by providing actual web content instead of asking LLM to "visit" URLs
- **Caching Strategy**: Implemented to avoid repeated network calls and improve performance
- **Import Issues**: Resolved correct import path for ScrapegraphAI (`from scrapegraphai.graphs import SmartScraperGraph`)
- **Dependency Management**: Used pipenv for proper virtual environment package installation
- **Transient Scraping Failures**: Implemented retry mechanism with 3 attempts and 1-second delays to handle network glitches, rate limits, and temporary server issues

## Testing Results
- **Web Scraping**: Successfully tested with idea ID `2a2ab6040f05`
  - Scraped 3 source URLs and cached results in JSON
  - Generated blog post using scraped content instead of URLs
  - Programmatically added Sources section to final output
  - LLM correctly evaluated Construkted Reality's suitability for the use case

- **YouTube Transcript Extraction**: Successfully tested with ideas containing YouTube sources
  - **Idea ID `67448229cf6a`**: Extracted 1,051 character transcript from `https://www.youtube.com/watch?v=VtRLU2K7gyM`
  - **Idea ID `9ffbec2e6bd6`**: Extracted 63,057 character transcript from `https://www.youtube.com/watch?v=ZZut6f17Vtc`
  - Mixed source processing: Combined YouTube transcripts with web-scraped content seamlessly
  - Caching: Transcripts properly stored in `scraped_sources` field with status, char_count, and timestamps
  - Error handling: Gracefully handles videos without subtitles (returns error status)

- **Retry Mechanism Testing**: Verified retry functionality in production environment
  - Successfully tested with both failing and successful URLs
  - Confirmed 3-attempt retry logic with proper delays
  - Maintains existing error handling and "continue on error" policy
  - Integrates seamlessly with existing blog draft generation workflow

## Next Steps
- Monitor scraping performance and error rates in production use
- ~~Consider implementing retry logic for failed scrapes~~ ✅ **COMPLETED**: Retry mechanism implemented with 3 attempts and 1-second delays
- Evaluate need for rate limiting or request throttling
- Document scraping workflow for team members
