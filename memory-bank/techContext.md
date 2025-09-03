# Technical Context: Blog Post Generation System

## Technologies Used
- **Python 3.x**: Primary implementation language for blog draft generation
- **JSON**: Data storage format for blog ideas database (80+ entries)
- **OLLAMA API**: External AI service for content generation via HTTP requests
- **Requests Library**: HTTP client for API communication
- **Pathlib**: Modern file path handling and directory operations
- **Regular Expressions**: JSON parsing and content validation
- **Logging**: System monitoring and debugging

## Development Setup
- **Python 3.6+**: Required for f-string formatting and pathlib features
- **OLLAMA Server**: External AI service running on 192.168.8.90:11434
- **Local File System**: blog_ideas.json database and blog_post_drafts/ output
- **Supporting Files**: context.md, crafting_compelling_titles.md, company_operation.md, content_marketing_guidance.md
- **No Additional Dependencies**: Uses only Python standard library plus requests

## Technical Constraints
- **API Dependency**: Requires OLLAMA server availability for content generation
- **Network Connectivity**: Must maintain stable connection to AI service
- **File System Access**: Requires read/write permissions for JSON and markdown files
- **Memory Efficiency**: Must handle large JSON datasets (80+ blog ideas) efficiently
- **Error Resilience**: Must gracefully handle API failures and network issues
- **Cross-platform Compatibility**: Works on Linux, macOS, Windows

## Dependencies
- **Python 3.6+**: Core runtime environment
- **Standard Library**: json, os, sys, pathlib, re, typing
- **Requests Library**: HTTP client for OLLAMA API communication
- **OLLAMA API**: External AI service for content generation
- **File System**: Local storage for JSON database and markdown outputs

## Tool Usage Patterns
- **Script Execution**: `python3 02_generate_blog_drafts.py`
- **JSON Processing**: Load blog_ideas.json → Process ideas → Update JSON with results
- **API Workflow**: Two-stage OLLAMA calls (parameter selection → content generation)
- **File Generation**: Create markdown files with ID+title naming convention
- **Error Handling**: Comprehensive logging and graceful failure recovery

## Integration Points
- **OLLAMA API**: HTTP POST requests to /api/generate endpoint
- **JSON Database**: blog_ideas.json serves as persistent data store
- **File System**: blog_post_drafts/ directory for markdown output
- **Configuration Files**: Supporting prompt templates and guidance documents
- **Future Integrations**: Publishing platforms, CMS systems, analytics dashboards

## Performance Considerations
- **API Rate Limiting**: Sequential processing to avoid overwhelming OLLAMA service
- **Memory Management**: Efficient JSON loading and processing for large datasets
- **File I/O Optimization**: Minimal disk operations with batch updates
- **Network Resilience**: Timeout handling and retry logic for API calls
- **Processing Limits**: Testing constraints (first 5 ideas) for validation
- **Concurrent Safety**: Single-threaded processing to maintain data integrity

## API Configuration
- **OLLAMA Host**: 192.168.8.90 (configurable)
- **Model**: gpt-oss-120b-CTX28k (high-capacity model for quality content)
- **Timeout**: 300 seconds for complex content generation
- **Request Format**: JSON payload with model, prompt, and system parameters
- **Response Handling**: JSON parsing with fallback regex extraction

## Data Flow Architecture
1. **Input**: blog_ideas.json (80 structured blog post ideas)
2. **Processing**: Sequential idea processing with API calls
3. **Stage 1**: Parameter selection API call → JSON update
4. **Stage 2**: Content generation API call → File creation
5. **Output**: Markdown files + updated JSON database
6. **Tracking**: Article paths stored in JSON for reference

## Security Considerations
- **API Access**: Internal network communication to OLLAMA service
- **File Permissions**: Appropriate read/write access for data files
- **Error Exposure**: Sanitized error messages to prevent information leakage
- **Data Validation**: Input validation for JSON structure and API responses
