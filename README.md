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

## Requirements

- Python 3.6+
- Standard library modules only (no external dependencies)

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
