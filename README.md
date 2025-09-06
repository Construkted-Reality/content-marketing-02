# Blog Idea Processor

A Python script that processes markdown files containing blog post ideas, extracts structured data, performs deduplication, and stores everything in a JSON file with rich metadata support.

## Enhanced Version

An enhanced version of the processor has been created to handle enriched JSON files and provide improved compatibility with the content marketing workflow. This version maintains backward compatibility while adding new features for importing and consolidating blog ideas.

## Overview

This project implements a system for collecting, processing, and storing blog post ideas from various research sources. The system ingests markdown files containing blog post ideas separated by "---" separators, extracts structured data, detects and prevents duplicates, and stores all ideas in a persistent JSON database.

## Features

- **Automated Processing**: Process multiple markdown files with a single command
- **Structured Data Extraction**: Automatically parses title, pain point, target audience, content details, and sources
- **Duplicate Detection**: Prevents processing the same blog post ideas multiple times
- **Metadata Validation**: Validates all fields against predefined configuration
- **Persistent Storage**: Stores processed ideas in JSON format for easy access
- **Timestamp Tracking**: Tracks both creation and modification times for blog ideas
- **Command-line Interface**: Simple, intuitive CLI with clear usage examples
- **Extensible Design**: Modular architecture that's easy to extend and maintain

## Files

```
content-marketing-02/
├── 01_process_blog_ideas.py       # Main processing script
├── 02_generate_blog_drafts.py     # Blog draft generation script (NEW)
├── metadata_config.json           # Configuration for metadata fields
├── blog_ideas.json                # Storage file for processed blog ideas
├── README.md                      # This file
├── implementation_plan.md         # Implementation documentation
└── memory-bank/                   # Project documentation
    ├── projectbrief.md            # Project overview
    ├── productContext.md          # Product context and requirements
    ├── activeContext.md           # Current work focus
    ├── systemPatterns.md          # System architecture patterns
    ├── techContext.md             # Technical details
    └── progress.md                # Current status and progress
```

## Usage

### Basic Usage

Process one or more markdown files by specifying them as command line arguments:

```bash
python3 01_process_blog_ideas.py file1.md file2.md
```

Example with the project files:

```bash
python3 01_process_blog_ideas.py research_content/*.md
```

### Enhanced Usage

The enhanced processor supports importing from enriched JSON files:

```bash
python3 01_process_blog_ideas.py --enriched-json blog_ideas.json
```

Process markdown files and import existing ideas:

```bash
python3 01_process_blog_ideas.py research_content/*.md --enriched-json blog_ideas.json
```

### Command Line Options

```bash
python3 01_process_blog_ideas.py [OPTIONS] INPUT_FILES...
```

**Arguments:**
- `INPUT_FILES`: One or more markdown files to process (required)

### Usage Examples

**Process files with duplicate detection (default):**
```bash
python3 01_process_blog_ideas.py research_content/*.md
```

**Process files without duplicate detection:**
```bash
python3 01_process_blog_ideas.py research_content/*.md --skip-duplicates False
```

**Use custom output file:**
```bash
python3 01_process_blog_ideas.py research_content/*.md --output-file my_blog_ideas.json
```

## Blog Draft Generation

The system now includes a second script for generating blog drafts from processed ideas with integrated web scraping:

```bash
python3 02_generate_blog_drafts.py
```

This script:
- Reads from `blog_ideas.json`
- **Scrapes source URLs** using ScrapegraphAI to extract actual web content
- Caches scraped content in `blog_ideas.json` to avoid repeated network calls
- Calls an LLM API twice per idea:
  - First to select writing parameters (voice, piece type, etc.)
  - Second to generate the full blog draft using scraped content instead of URL lists
- Saves drafts to `blog_post_drafts/` directory with programmatic Sources section
- Updates the JSON database with article paths and metadata

### Web Scraping and YouTube Transcript Integration

The script now uses **ScrapegraphAI** for web scraping and **yt-dlp** for YouTube transcript extraction to provide actual content to the LLM instead of asking it to "visit URLs." This provides better content grounding and more accurate blog posts.

**Key Features:**
- **Mixed Source Processing**: Handles both web pages and YouTube videos in the same source list
- **YouTube Transcript Extraction**: Uses existing `extract_transcript.py` script with yt-dlp to download video subtitles
- **Web Scraping**: Uses ScrapegraphAI with local OpenAI-compatible endpoint (http://192.168.8.90:42069/v1)
- **Intelligent URL Detection**: Automatically detects YouTube URLs (`youtube.com` or `youtu.be`) and processes them separately
- **Unified Caching**: Both web content and video transcripts cached in `scraped_sources` field
- **Robust Error Handling**: Continues processing on individual URL failures (Option A failure policy)
- **No Content Limits**: No caps on scraped text or transcript length
- **Programmatic Sources**: Sources section added automatically to final blog posts

**Production Status:**
- ✅ **Fully tested and working** - Successfully scraped real URLs with 6,158+ characters of content
- ✅ **YouTube Integration Working** - Successfully extracted transcripts up to 63,057 characters
- ✅ **Mixed Source Processing** - Handles YouTube videos + web pages in single workflow
- ✅ **Robust error handling** - Continues processing when individual URLs fail
- ✅ **Persistent caching** - All content saved in `blog_ideas.json` under `scraped_sources` field
- ✅ **Content verification** - Sample content includes both web articles and video transcripts

**Dependencies:**
- Requires `scrapegraphai` package: `pipenv install scrapegraphai`
- Requires `yt-dlp` package: `pipenv install yt-dlp` (already installed)
- Requires Playwright browsers: `pipenv run playwright install`
- Uses local OpenAI-compatible LLM endpoint for content extraction
- Leverages existing `extract_transcript.py` script for YouTube processing

### Command Line Options

```bash
python3 02_generate_blog_drafts.py [OPTIONS]
```

**Options:**
- `--force_article_gen`: Regenerate drafts even if `article_generated` is true
- `--ideas_id ID`: Process only the idea with the given ID

### Usage Examples

**Generate drafts for all ideas (default behavior):**
```bash
python3 02_generate_blog_drafts.py
```

**Force regeneration of all drafts:**
```bash
python3 02_generate_blog_drafts.py --force_article_gen
```

**Process a single idea by ID:**
```bash
python3 02_generate_blog_drafts.py --ideas_id "2a2ab6040f05"
```

**Force regeneration of a single idea:**
```bash
python3 02_generate_blog_drafts.py --ideas_id "2a2ab6040f05" --force_article_gen
```

The script automatically skips ideas that have already been processed (where `article_generated` is `true`) to prevent redundant processing. Use the `--force_article_gen` flag to override this behavior and regenerate all drafts.

## Input Format

The script expects markdown files with blog post ideas separated by `---` patterns:

```markdown
## Blog Post 1: "Title of the Blog Post"

**Pain Point:** Description of the user problem

**Target Audience:** Description of target users

**Content Details:** Detailed solution description

**Sources:**
- https://url1.com
- https://url2.com

---

## Blog Post 2: "Another Blog Post Title"

**Pain Point:** Another user problem description

**Target Audience:** Another target audience

**Content Details:** Another solution description

**Sources:**
- https://url3.com

---
```

## Output Format

The script produces a JSON file with the following structure:

```json
{
  "ideas": [
    {
      "title": "Blog Post Title",
      "pain_point": "User problem description",
      "target_audience": "Target audience description",
      "content_details": "Solution description",
      "sources": ["https://url1.com", "https://url2.com"],
      "id": "unique_hash_id",
      "created_at": "2025-01-01T12:00:00"
    }
  ],
  "last_updated": "2025-01-01T12:00:00",
  "total_count": 80
}
```

## Metadata Configuration

The system supports rich metadata fields defined in `metadata_config.json`. These include:

- **article**: The finished article
- **voice**: Stylistic identity (TheNewYorker, TheAtlantic, Wired)
- **piece_type**: Structural format (explainer, tutorial, etc.)
- **marketing_post_type**: Marketing angle (educational, promotional, etc.)
- **primary_goal**: Article objective (educate, persuade, etc.)
- **target_audience**: Reader type (enterprise, public sector, etc.)
- **technical_depth**: Technical detail level (low, med, high)
- **title**: Blog post headline
- **keywords**: SEO terms
- **length**: Word count or section count
- **sections**: Major headings
- **call_to_action**: Reader action request
- **pain_point**: Core user problem
+
+ **primary seo key word**: Primary SEO keyword for the article (string, optional)
+ **secondary seo key words**: List of secondary SEO keywords (list of strings, optional)

## Requirements

### Core Requirements
- Python 3.12+ (specified in Pipfile)
- pipenv (for virtual environment management)

### Dependencies
The project uses pipenv for dependency management. All dependencies are captured in `Pipfile` and `Pipfile.lock` files.

**Main Dependencies:**
- `scrapegraphai` - Web scraping with LLM assistance
- `requests` - HTTP library (used by blog generation script)
- Standard library modules for core functionality

### Environment Recreation

To recreate the Python environment on another computer:

1. **Install pipenv** (if not already installed):
   ```bash
   pip install pipenv
   ```

2. **Clone the repository and navigate to the project directory**:
   ```bash
   git clone <repository-url>
   cd content-marketing-02
   ```

3. **Install all dependencies from Pipfile.lock** (ensures exact versions):
   ```bash
   pipenv install
   ```

4. **Install Playwright browsers** (required for web scraping):
   ```bash
   pipenv run playwright install
   ```

5. **Activate the virtual environment**:
   ```bash
   pipenv shell
   ```

6. **Verify installation**:
   ```bash
   python3 02_generate_blog_drafts.py --help
   ```

**Alternative: Manual Installation**
If you prefer not to use pipenv:
```bash
pip install scrapegraphai requests
playwright install
```

**Note:** The `Pipfile.lock` contains exact dependency versions for reproducible builds. Using `pipenv install` ensures you get the exact same environment that was used for development and testing.

## How It Works

1. **File Processing**: Reads markdown files and splits them by "---" separators
2. **Data Extraction**: Parses each blog post into structured data fields
3. **Validation**: Validates all fields against metadata configuration
4. **Duplicate Detection**: Checks against existing database using title and pain point hashes
5. **Import Functionality**: Can import from enriched JSON files with deduplication
6. **Storage**: Saves valid, non-duplicate ideas to JSON file
7. **Reporting**: Logs processing results and statistics

## Error Handling

The script includes comprehensive error handling:
- Validates file existence before processing
- Handles malformed content gracefully
- Provides detailed logging of processing steps
- Continues processing other files if one fails
- Maintains data integrity throughout the process

## Customization

### Adding New Fields

To add new metadata fields, modify `metadata_config.json` with the appropriate field definition including:
- Type specification (string, etc.)
- Required flag
- Allowed options (if applicable)
- Description for documentation

### Changing Storage Location

Use the `--output-file` option to specify a different output file name and location.

## Contributing

The system is designed to be extensible. Future enhancements could include:
- Unit testing framework
- Export functionality to CSV/Excel
- Web interface for browsing ideas
- Advanced duplicate detection algorithms
- Bulk processing capabilities

## License

This project is part of the content-marketing-02 repository and follows the same licensing terms.
