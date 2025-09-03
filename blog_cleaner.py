#!/usr/bin/env python3
"""
Blog Ideas Cleaner Script

This script processes markdown files containing blog post ideas with references,
cleaning them by removing extraneous content and integrating URL references
directly into each blog post idea.
"""

import re
import os
import sys
import argparse
from typing import Dict, List, Tuple, Any


def extract_references(content: str) -> Dict[int, str]:
    """Extract reference mappings from the bottom of the file."""
    references = {}
    
    # Find all reference patterns like [^1]: https://url.com
    ref_pattern = r'\[\^(\d+)\]:\s*(https?://[^\s\n]+)'
    matches = re.findall(ref_pattern, content)
    
    for ref_num, url in matches:
        references[int(ref_num)] = url.strip()
    
    return references


def find_blog_posts_section(content: str) -> str:
    """Find and extract the main blog posts section."""
    # Look for the start of blog post ideas (after the background info)
    # Usually starts with "## Blog Post Idea" or similar
    
    # Find the first blog post idea
    blog_start_pattern = r'## Blog Post Idea \d+:'
    match = re.search(blog_start_pattern, content)
    
    if not match:
        # Alternative pattern for different formats
        blog_start_pattern = r'### \d+\.'
        match = re.search(blog_start_pattern, content)
    
    if match:
        # Extract from first blog post to end of content
        blog_section = content[match.start():]
        
        # Remove the reference section at the bottom
        # Look for the divider before references
        ref_divider_pattern = r'<div style="text-align: center">⁂</div>'
        ref_match = re.search(ref_divider_pattern, blog_section)
        
        if ref_match:
            blog_section = blog_section[:ref_match.start()]
        
        return blog_section.strip()
    
    return content


def parse_blog_post(blog_text: str, references: Dict[int, str]) -> Dict[str, Any]:
    """Parse a single blog post and extract its components."""
    # Remove hidden HTML content before processing
    # This filters out content in <span style="display:none"> tags that contain extra references
    cleaned_blog_text = re.sub(r'<span style="display:none">.*?</span>', '', blog_text, flags=re.DOTALL)
    
    lines = cleaned_blog_text.strip().split('\n')
    
    # Extract title (first line, remove ## and clean up)
    title = lines[0] if lines else ""
    title = re.sub(r'^#+\s*', '', title)  # Remove markdown headers
    title = re.sub(r'^Blog Post Idea \d+:\s*', '', title)  # Remove "Blog Post Idea N:"
    title = re.sub(r'^\d+\.\s*', '', title)  # Remove "N. " at the beginning
    title = title.strip('"')  # Remove quotes if present
    
    # Find sections
    pain_point = ""
    target_audience = ""
    content_details = ""
    
    current_section = None
    current_content = []
    
    for line in lines[1:]:
        line = line.strip()
        
        if line.startswith('**Pain Point'):
            if current_section and current_content:
                if current_section == 'pain_point':
                    pain_point = ' '.join(current_content)
                elif current_section == 'target_audience':
                    target_audience = ' '.join(current_content)
                elif current_section == 'content_details':
                    content_details = ' '.join(current_content)
            
            current_section = 'pain_point'
            current_content = [line.replace('**Pain Point:**', '').replace('**Pain Point**:', '').strip()]
            
        elif line.startswith('**Target Audience'):
            if current_section and current_content:
                if current_section == 'pain_point':
                    pain_point = ' '.join(current_content)
                elif current_section == 'target_audience':
                    target_audience = ' '.join(current_content)
                elif current_section == 'content_details':
                    content_details = ' '.join(current_content)
            
            current_section = 'target_audience'
            current_content = [line.replace('**Target Audience:**', '').replace('**Target Audience**:', '').strip()]
            
        elif line.startswith('**Content Details'):
            if current_section and current_content:
                if current_section == 'pain_point':
                    pain_point = ' '.join(current_content)
                elif current_section == 'target_audience':
                    target_audience = ' '.join(current_content)
                elif current_section == 'content_details':
                    content_details = ' '.join(current_content)
            
            current_section = 'content_details'
            current_content = [line.replace('**Content Details:**', '').replace('**Content Details**:', '').strip()]
            
        elif line and current_section:
            current_content.append(line)
    
    # Handle the last section
    if current_section and current_content:
        if current_section == 'pain_point':
            pain_point = ' '.join(current_content)
        elif current_section == 'target_audience':
            target_audience = ' '.join(current_content)
        elif current_section == 'content_details':
            content_details = ' '.join(current_content)
    
    # Extract references from the content and get corresponding URLs
    ref_pattern = r'\[\^(\d+)\]'
    ref_numbers = set()
    
    for text in [pain_point, target_audience, content_details]:
        matches = re.findall(ref_pattern, text)
        ref_numbers.update(int(num) for num in matches)
    
    # Get URLs for found references
    sources = []
    for ref_num in sorted(ref_numbers):
        if ref_num in references:
            sources.append(references[ref_num])
    
    # Clean reference markers and separators from text
    separator_cleanup = r'\\?#\\?#\\?#\\?#\\?#\\?#\\?#\\?#\\?#\\?#\\?#\\?#\\?#\\?#\\?#\\?#\\?#\\?#\\?#\\?#\\?#\\?#\\?#\\?#\\?#\\?#'
    
    for text_field in ['pain_point', 'target_audience', 'content_details']:
        if text_field == 'pain_point':
            pain_point = re.sub(ref_pattern, '', pain_point)
            pain_point = re.sub(separator_cleanup, '', pain_point)
        elif text_field == 'target_audience':
            target_audience = re.sub(ref_pattern, '', target_audience)
            target_audience = re.sub(separator_cleanup, '', target_audience)
        elif text_field == 'content_details':
            content_details = re.sub(ref_pattern, '', content_details)
            content_details = re.sub(separator_cleanup, '', content_details)
    
    return {
        'title': title,
        'pain_point': pain_point.strip(),
        'target_audience': target_audience.strip(),
        'content_details': content_details.strip(),
        'sources': sources
    }


def split_blog_posts(blog_section: str) -> List[str]:
    """Split the blog section into individual blog posts."""
    # First try splitting by the actual separator pattern (without escaping)
    separator_pattern = r'\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#'
    
    if separator_pattern in blog_section:
        parts = blog_section.split(separator_pattern)
        return [part.strip() for part in parts if part.strip()]
    
    # Try alternative splitting by blog post headers
    parts = re.split(r'(?=## Blog Post Idea \d+:)', blog_section)
    if len(parts) > 1:
        return [part.strip() for part in parts if part.strip()]
    
    # Try alternative format for numbered sections
    parts = re.split(r'(?=### \d+\.)', blog_section)
    if len(parts) > 1:
        return [part.strip() for part in parts if part.strip()]
    
    # If no clear separation found, return the whole section
    return [blog_section]


def format_blog_post(blog_data: Dict[str, str]) -> str:
    """Format a blog post in the new clean format."""
    output = []
    
    output.append(f"## {blog_data['title']}")
    output.append("")
    output.append(f"**Pain Point:** {blog_data['pain_point']}")
    output.append("")
    output.append(f"**Target Audience:** {blog_data['target_audience']}")
    output.append("")
    output.append(f"**Content Details:** {blog_data['content_details']}")
    output.append("")
    
    if blog_data['sources']:
        output.append("**Sources:**")
        for source in blog_data['sources']:
            output.append(f"- {source}")
        output.append("")
    
    output.append("---")
    output.append("")
    
    return '\n'.join(output)


def process_file(input_path: str, output_path: str) -> None:
    """Process a single markdown file."""
    print(f"Processing {input_path}...")
    
    # Read the input file
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract references
    references = extract_references(content)
    print(f"Found {len(references)} references")
    
    # Find blog posts section
    blog_section = find_blog_posts_section(content)
    
    # Split into individual blog posts
    blog_posts = split_blog_posts(blog_section)
    print(f"Found {len(blog_posts)} blog posts")
    
    # Process each blog post
    formatted_posts = []
    for i, blog_text in enumerate(blog_posts, 1):
        try:
            blog_data = parse_blog_post(blog_text, references)
            if blog_data['title']:  # Only include if we found a title
                formatted_post = format_blog_post(blog_data)
                formatted_posts.append(formatted_post)
                print(f"  Processed blog post {i}: {blog_data['title'][:50]}...")
        except Exception as e:
            print(f"  Error processing blog post {i}: {e}")
            continue
    
    # Write output file
    output_content = '\n'.join(formatted_posts)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print(f"Wrote {len(formatted_posts)} cleaned blog posts to {output_path}")


def main():
    """Main function to process files specified via command line arguments."""
    parser = argparse.ArgumentParser(
        description='Clean and reformat blog post idea markdown files by removing extraneous content and integrating URL references.',
        epilog='Example: python3 blog_cleaner.py file1.md file2.md'
    )
    
    parser.add_argument(
        'input_files',
        nargs='+',
        help='One or more markdown files to process'
    )
    
    parser.add_argument(
        '-o', '--output-suffix',
        default='_cleaned',
        help='Suffix to add to output filenames (default: _cleaned)'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Directory to save cleaned files (default: same as input file)'
    )
    
    args = parser.parse_args()
    
    if not args.input_files:
        print("Error: No input files specified")
        parser.print_help()
        sys.exit(1)
    
    processed_count = 0
    
    for input_file in args.input_files:
        if os.path.exists(input_file):
            # Generate output filename
            base_name = os.path.splitext(input_file)[0]
            extension = os.path.splitext(input_file)[1]
            
            if args.output_dir:
                # Use specified output directory
                filename = os.path.basename(base_name)
                output_file = os.path.join(args.output_dir, f"{filename}{args.output_suffix}{extension}")
                # Create output directory if it doesn't exist
                os.makedirs(args.output_dir, exist_ok=True)
            else:
                # Use same directory as input file
                output_file = f"{base_name}{args.output_suffix}{extension}"
            
            try:
                process_file(input_file, output_file)
                print(f"✓ Successfully processed {input_file}")
                print(f"  Output: {output_file}")
                print()
                processed_count += 1
            except Exception as e:
                print(f"✗ Error processing {input_file}: {e}")
                print()
        else:
            print(f"✗ File not found: {input_file}")
            print()
    
    print(f"Processing complete. Successfully processed {processed_count} of {len(args.input_files)} files.")


if __name__ == "__main__":
    main()
