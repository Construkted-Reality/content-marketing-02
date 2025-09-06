# Active Context

## Current Work
Successfully completed comprehensive refactoring of the `02_generate_blog_drafts.py` script to eliminate code duplication and standardize LLM API calls. The refactoring created a unified `call_llm` helper function with built-in defaults, significantly improving code maintainability and consistency.

## Recent Changes
- **Complete Code Refactoring**: Created unified `call_llm` helper function with standardized defaults
- **Parameter Standardization**: Built standardized parameters directly into the function (temperature=0.7, reasoning_effort="high", max_tokens=6400, top_p=1)
- **Function Simplification**: Reduced complex API calls to simple one-liners
- **Code Elimination**: Removed ~80 lines of duplicated OpenAI/Ollama API handling code
- **Enhanced Maintainability**: Centralized all LLM parameter management in single location
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
- Unified LLM interface pattern with built-in parameter defaults
- DRY (Don't Repeat Yourself) principle implementation with centralized configuration
- Function parameter standardization and default value management
- API abstraction layer with provider-agnostic interface
- ScrapegraphAI SmartScraperGraph for LLM-assisted web scraping
- OpenAI-compatible API endpoint configuration for scraping
- Caching mechanism using JSON persistence
- Option A failure policy (continue on individual URL failures)
- Separation of content generation from source attribution
- Helper function architecture for modular scraping workflow

## Relevant Files and Code
- **File**: `02_generate_blog_drafts.py` (COMPLETELY REFACTORED)
  - **NEW**: Added `call_llm()` function as unified LLM interface with built-in defaults
    - Handles both OpenAI and Ollama API formats
    - Built-in standardized parameters: temperature=0.7, reasoning_effort="high", max_tokens=6400, top_p=1
    - Supports flexible parameter overrides via **kwargs
    - Centralizes response parsing logic
    - Returns clean text content from LLM responses
  - **REFACTORED**: Modified `select_parameters()` function
    - Removed ~40 lines of duplicated OpenAI/Ollama handling code
    - Now uses simple `call_llm(prompt=first_prompt)` call
    - Simplified JSON parsing with fallback regex extraction
  - **REFACTORED**: Modified `generate_blog_post()` function
    - Removed ~40 lines of duplicated OpenAI/Ollama handling code
    - Now uses clean `call_llm(prompt=prompt, system_prompt=system_prompt)` call
    - Eliminated complex parameter passing
  - **ENHANCED**: Modified `get_or_build_scraped_sources()` to detect YouTube URLs and process them separately
  - Added helper functions: `build_source_excerpts()`, `build_idea_context()`, `add_sources_section_to_output()`
  - **YouTube Detection**: Uses regex `r'(youtube\.com|youtu\.be)'` to identify video URLs
  - **Mixed Processing**: Handles both YouTube transcripts and web scraping in single workflow

- **File**: `utils/scrape_sources.py` (EXISTING)
  - Functions: `build_llm_env()`, `scrape_url()`, `scrape_urls()`
  - Uses local OpenAI endpoint (http://192.168.8.90:42069/v1) with model gpt-oss-120b
  - Implements comprehensive error handling and URL validation
  - **Retry Mechanism**: 3 attempts per URL with 1-second delays between retries
  - Returns structured ScrapedSource dictionaries with status, text, char_count

- **File**: `extract_transcript.py` (EXISTING - LEVERAGED)
  - Used via subprocess call for YouTube transcript extraction
  - Handles yt-dlp integration and SRT parsing
  - Returns plain text transcripts from video subtitles

- **File**: `01_process_blog_ideas.py` (MINOR UPDATES)
  - Added 'scraped_sources' to enriched_fields list
  - Added default `scraped_sources: []` initialization in both processing methods

## Problem Solving
- **Code Duplication**: Completely eliminated ~80 lines of duplicated OpenAI API handling code by creating unified `call_llm` function with built-in defaults
- **Parameter Inconsistency**: Solved by centralizing all LLM parameters in single function with standardized defaults
- **Maintainability**: Dramatically improved by creating single point of control for all LLM interactions
- **Function Complexity**: Reduced complex multi-parameter API calls to simple one-liners
- **Configuration Management**: Centralized parameter control makes future changes trivial
- **URL Injection Issue**: Previously solved by replacing URL lists with scraped text excerpts in prompts
- **Content Grounding**: Improved by providing actual web content instead of asking LLM to "visit" URLs
- **Caching Strategy**: Implemented to avoid repeated network calls and improve performance
- **Import Issues**: Resolved correct import path for ScrapegraphAI (`from scrapegraphai.graphs import SmartScraperGraph`)
- **Dependency Management**: Used pipenv for proper virtual environment package installation
- **Transient Scraping Failures**: Implemented retry mechanism with 3 attempts and 1-second delays to handle network glitches, rate limits, and temporary server issues

## Testing Results
- **Code Refactoring**: Successfully completed comprehensive refactoring
  - Verified `call_llm` function works with both OpenAI and Ollama providers
  - Confirmed both `select_parameters` and `generate_blog_post` maintain identical functionality
  - Reduced codebase complexity while preserving all existing features
  - No breaking changes to existing API or functionality
  - Standardized parameters now applied consistently across all LLM calls
  - Function calls simplified from complex multi-parameter to clean one-liners

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
- Monitor refactored code performance and ensure no regressions in production
- Consider applying similar refactoring patterns to other parts of the codebase
- Evaluate opportunities for further code consolidation and standardization
- ~~Consider implementing retry logic for failed scrapes~~ ✅ **COMPLETED**: Retry mechanism implemented with 3 attempts and 1-second delays
- Evaluate need for rate limiting or request throttling
- Document scraping workflow for team members

## Refactoring Achievements
- **Eliminated Code Duplication**: Removed ~80 lines of duplicated API handling code
- **Standardized Parameters**: All LLM calls now use identical settings automatically
- **Simplified Function Calls**: Reduced complex API calls to simple one-liners
- **Centralized Configuration**: Single point of control for all LLM parameters
- **Enhanced Maintainability**: Future changes require updates in only one location
- **Improved Consistency**: Guaranteed identical behavior across all LLM calls
- **Better Readability**: Clean, self-documenting function interfaces
- **Future-Proof Architecture**: Easy to add new parameters or LLM providers
