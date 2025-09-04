# Active Context

## Current Work
Enhanced the `02_generate_blog_drafts.py` script with a new `--ideas_id` command-line flag that allows users to process a single idea from `blog_ideas.json` by its ID. Also added the `--force_article_gen` flag for regenerating articles.

## Key Technical Concepts
- Command-line argument parsing using `argparse`
- Conditional processing logic based on flag state
- JSON field checking for article generation status
- User feedback and status messaging for different execution modes
- Error handling for missing IDs and already-generated articles

## Relevant Files and Code
- **File**: `02_generate_blog_drafts.py`
- **Changes**: 
  - Added `argparse` import and argument parser with `--force_article_gen` and `--ideas_id` flags
  - Implemented filtering logic to process single idea when `--ideas_id` is provided
  - Added error handling for non-existent IDs and already-generated articles
  - Implemented skip logic in main processing loop to check `article_generated` field
  - Added status messages for different execution modes
  - Maintained backward compatibility with existing functionality

## Problem Solving
- Implemented selective processing based on `article_generated` flag in `blog_ideas.json`
- Created clear user feedback for different execution modes
- Added comprehensive error handling for edge cases
- Ensured existing file naming and collision handling logic remains intact
- Preserved all existing API call functionality and JSON update behavior
- Added proper exit behavior after single idea processing

## Next Steps
- Test the new flag functionality with both enabled and disabled states
- Verify that `article_generated` flags are properly maintained in JSON
- Document the new features in project documentation
