# Implementation Plan

## Overview
Create a Python script that ingests markdown files containing blog post ideas, processes them using "---" separators, performs deduplication against existing records, and stores all ideas in a JSON file with rich metadata support for content tracking.

## Types
The system will use these data structures:
- **BlogPost Idea**: A complete blog post idea with all metadata fields including title, pain_point, and comprehensive metadata
- **Metadata Schema**: Structured definition of all supported fields with validation rules and predefined options
- **Duplicate Detection**: Title and pain point comparison mechanism using hash-based comparison
- **Storage Format**: JSON structure optimized for querying and tracking article status

## Files
- **New file**: `blog_idea_unified_processor.py` - Main processing script
- **New file**: `blog_ideas.json` - Storage file for processed blog ideas  
- **New file**: `metadata_config.json` - Configuration for metadata fields and options
- **New file**: `implementation_plan.md` - Documentation of the implementation plan

## Functions
- `process_markdown_file()`: Parse markdown files with "---" separators
- `extract_blog_post_data()`: Extract structured data from individual blog posts
- `validate_metadata()`: Validate all metadata fields against configured options
- `check_duplicates()`: Compare new ideas against existing database using title and pain point
- `store_blog_ideas()`: Save processed ideas to JSON file with proper structure
- `load_existing_ideas()`: Load existing ideas for duplicate checking
- `generate_id()`: Generate unique identifiers for blog posts
- `main()`: Coordinate the entire processing workflow

## Classes
- **BlogPostProcessor**: Main class managing the processing workflow
- **MetadataValidator**: Class handling metadata validation and configuration
- **DuplicateDetector**: Class handling duplicate detection logic

## Dependencies
Standard Python libraries only (json, os, re, argparse, hashlib, datetime) - No external dependencies required

## Testing
- Unit tests for metadata validation
- Integration tests for duplicate detection
- End-to-end tests for file processing
- Test data files for validation

## Implementation Order
1. Create metadata configuration schema
2. Implement core processing functions
3. Build duplicate detection system
4. Create main processor class
5. Add command-line interface
6. Implement JSON storage and loading
7. Add comprehensive testing
8. Final integration and validation
