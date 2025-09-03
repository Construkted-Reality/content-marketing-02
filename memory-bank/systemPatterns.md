# System Patterns: Blog Post Idea Library System

## System Architecture
The system follows a modular architecture pattern with clear separation of concerns:

1. **Processor Layer**: BlogPostProcessor class orchestrates the entire workflow
2. **Validation Layer**: MetadataValidator handles field validation against configuration
3. **Detection Layer**: DuplicateDetector manages duplicate identification logic
4. **Storage Layer**: JSON-based persistence with automatic deduplication
5. **Interface Layer**: Command-line interface for user interaction

## Key Technical Decisions
- **File Processing**: Uses regex pattern matching for "---" separators
- **Data Extraction**: Implements state machine approach for parsing structured content
- **Duplicate Detection**: MD5 hash of title + pain point for efficient comparison
- **Storage Format**: JSON for human-readable persistence and easy integration
- **Error Handling**: Comprehensive logging with graceful degradation

## Design Patterns Used
- **Strategy Pattern**: Separate validation logic in MetadataValidator
- **Observer Pattern**: Logging system notifies about processing events
- **Factory Pattern**: Configuration-driven metadata field handling
- **Singleton Pattern**: MetadataValidator instance reused across processing

## Component Relationships
- BlogPostProcessor depends on MetadataValidator and DuplicateDetector
- MetadataValidator loads configuration from metadata_config.json
- DuplicateDetector works with data structures from BlogPostProcessor
- All components interact through well-defined interfaces

## Critical Implementation Paths
1. File reading and parsing → Data extraction → Validation → Storage
2. Duplicate detection workflow → Comparison logic → Filtering → Storage
3. Command-line argument parsing → Processor initialization → File processing → Output

## Data Flow
1. Input files are read and split by "---" separators
2. Each blog post is parsed into structured data
3. Data is validated against metadata configuration
4. Duplicate detection compares against existing database
5. Valid, non-duplicate data is stored in JSON format
6. Processing results are logged and reported to user
