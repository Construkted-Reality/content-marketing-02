# Blog Ideas Cleaner

A Python script that processes markdown files containing blog post ideas with references, cleaning them by removing extraneous content and integrating URL references directly into each blog post idea.

## Overview

This project was created to clean and reformat blog post idea files that contain:
- Extraneous content (logos, prompts, background information)
- Blog post ideas with numbered references `[^n]`
- URL references listed at the bottom of the file

The script transforms these files into a clean, consistent format suitable for parsing and further processing.

## Features

- **Automated Processing**: Processes multiple files with a single command
- **Reference Integration**: Automatically matches `[^n]` citations to their corresponding URLs
- **Content Cleaning**: Removes separators, fixes headers, and cleans text
- **Consistent Formatting**: Outputs standardized markdown structure
- **Error Handling**: Robust processing with detailed logging
- **Reusable**: Can process future files with similar structure

## File Structure

```
content-marketing-02/
├── blog_cleaner.py                                           # Main cleaning script
├── README.md                                                # This file
└── research_content/
    ├── mobile-lidar_blog_ideas-01Sept2025.md                # Original mobile LiDAR file
    ├── mobile-lidar_blog_ideas-01Sept2025_cleaned.md        # Cleaned mobile LiDAR file
    ├── photogrammetry_blog_ideas-02-01Sept2025.md           # Original photogrammetry file
    └── photogrammetry_blog_ideas-02-01Sept2025_cleaned.md   # Cleaned photogrammetry file
```

## Input Format

The script expects markdown files with:
- Blog post ideas separated by `\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#` patterns
- Each idea containing:
  - Title (with `## Blog Post Idea N:` format)
  - **Pain Point:** section
  - **Target Audience:** section  
  - **Content Details:** section
  - References in `[^n]` format within the content
- URL references at the bottom in `[^n]: https://url.com` format

## Output Format

The script produces clean markdown files where each blog post idea follows this structure:

```markdown
## [Blog Post Title]

**Pain Point:** [Description of user problem]

**Target Audience:** [Description of target users]

**Content Details:** [Detailed solution description]

**Sources:**
- https://url1.com
- https://url2.com
- https://url3.com

---
```

## Usage

### Basic Usage

Process one or more markdown files by specifying them as command line arguments:

```bash
python3 blog_cleaner.py file1.md file2.md
```

Example with the project files:

```bash
python3 blog_cleaner.py research_content/mobile-lidar_blog_ideas-01Sept2025.md research_content/photogrammetry_blog_ideas-02-01Sept2025.md
```

### Command Line Options

```bash
python3 blog_cleaner.py [OPTIONS] INPUT_FILES...
```

**Arguments:**
- `INPUT_FILES`: One or more markdown files to process (required)

**Options:**
- `-o, --output-suffix SUFFIX`: Suffix to add to output filenames (default: `_cleaned`)
- `--output-dir DIRECTORY`: Directory to save cleaned files (default: same as input file)
- `-h, --help`: Show help message and exit

### Usage Examples

**Process files with default settings:**
```bash
python3 blog_cleaner.py file1.md file2.md
```

**Use custom output suffix:**
```bash
python3 blog_cleaner.py -o _processed file1.md file2.md
```

**Save to specific directory:**
```bash
python3 blog_cleaner.py --output-dir ./cleaned_files file1.md file2.md
```

**Combine options:**
```bash
python3 blog_cleaner.py -o _final --output-dir ./output file1.md file2.md
```

## Requirements

- Python 3.6+
- Standard library modules only (no external dependencies)

## How It Works

1. **Reference Extraction**: Scans the file for `[^n]: URL` patterns and builds a reference mapping
2. **Content Parsing**: Identifies the blog posts section and splits individual posts
3. **Post Processing**: For each blog post:
   - Extracts title, pain point, target audience, and content details
   - Finds all `[^n]` references within the content
   - Maps references to their corresponding URLs
   - Removes reference markers from text
4. **Output Generation**: Formats each post in the standardized structure
5. **File Writing**: Saves cleaned content to new files with `_cleaned` suffix

## Example Transformation

### Before (Input):
```markdown
## Blog Post Idea 1: "Why Your Mobile LiDAR Scans Look Like a Mess"

**Pain Point**: Users encounter issues with data quality[^1][^2].

**Target Audience**: Mobile mapping operators

**Content Details**: Solutions include proper calibration[^1].

\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#

[^1]: https://example.com/solution1
[^2]: https://example.com/solution2
```

### After (Output):
```markdown
## Why Your Mobile LiDAR Scans Look Like a Mess

**Pain Point:** Users encounter issues with data quality.

**Target Audience:** Mobile mapping operators

**Content Details:** Solutions include proper calibration.

**Sources:**
- https://example.com/solution1
- https://example.com/solution2

---
```

## Results

The script successfully processed:
- **Mobile LiDAR file**: 20 blog post ideas with 70 references
- **Photogrammetry file**: 20 blog post ideas with 68 references

All references were properly matched and integrated into their respective blog posts.

## Error Handling

The script includes comprehensive error handling:
- Validates file existence before processing
- Handles malformed content gracefully
- Provides detailed logging of processing steps
- Continues processing other files if one fails

## Customization

### Adding New File Patterns

To support different input formats, modify these functions:
- `find_blog_posts_section()`: Adjust patterns for finding blog content
- `split_blog_posts()`: Modify separator patterns
- `parse_blog_post()`: Update section parsing logic

### Changing Output Format

Modify the `format_blog_post()` function to change the output structure.

## Troubleshooting

### Common Issues

1. **No blog posts found**: Check that the input file contains the expected header patterns
2. **Missing references**: Verify that URL references follow the `[^n]: URL` format
3. **Encoding errors**: Ensure input files are UTF-8 encoded

### Debug Mode

Add debug output by modifying the logging in the `process_file()` function:

```python
print(f"Debug: Found {len(blog_posts)} blog posts")
print(f"Debug: Blog section preview: {blog_section[:200]}...")
```

## Contributing

To extend this script for other file formats:
1. Add new pattern recognition in `find_blog_posts_section()`
2. Update parsing logic in `parse_blog_post()`
3. Test with sample files
4. Update this README with new usage examples

## License

This project is part of the content-marketing-02 repository and follows the same licensing terms.
