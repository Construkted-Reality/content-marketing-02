# Project Brief: Blog Post Idea Library System

## Overview
This project implements a system for collecting, processing, and storing blog post ideas from various research sources. The system ingests markdown files containing blog post ideas, processes them using "---" separators, performs deduplication, and stores all ideas in a structured JSON format with rich metadata support.

## Key Requirements
- Process markdown files with "---" separators
- Extract structured data (title, pain point, target audience, content details, sources)
- Perform deduplication based on title and pain point
- Store ideas in JSON format with metadata
- Support all specified metadata fields (article, voice, piece_type, marketing_post_type, etc.)
- Maintain a persistent database of blog ideas

## Technical Approach
- Python-based solution with no external dependencies
- Command-line interface for easy usage
- Modular design with separate classes for processing, validation, and storage
- Comprehensive logging and error handling
- JSON-based storage for easy integration and querying

## Files Created
- blog_idea_processor.py: Main processing script
- metadata_config.json: Configuration for metadata fields
- blog_ideas.json: Storage file for processed blog ideas
- implementation_plan.md: Documentation of implementation approach
