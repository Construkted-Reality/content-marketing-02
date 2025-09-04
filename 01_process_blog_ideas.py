#!/usr/bin/env python3
"""
Unified Blog Idea Processor

A single script that processes all markdown files in the research_content directory
and generates a complete, enriched blog_ideas.json file in one run.
"""

import json
import os
import re
import argparse
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MetadataValidator:
    """Handles validation of metadata fields against configuration."""
    
    def __init__(self, config_file: str = "metadata_config.json"):
        """Initialize the validator with metadata configuration."""
        self.config = self._load_config(config_file)
    
    def _load_config(self, config_file: str) -> Dict:
        """Load metadata configuration from JSON file."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Metadata config file {config_file} not found")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in metadata config: {e}")
            raise
    
    def validate_field(self, field_name: str, value: Any) -> tuple[bool, str]:
        """Validate a single field value against configuration."""
        if field_name not in self.config['fields']:
            return True, ""  # Unknown field, skip validation
        
        field_config = self.config['fields'][field_name]
        field_type = field_config.get('type', 'string')
        required = field_config.get('required', False)
        options = field_config.get('options', [])
        
        # Check required fields
        if required and (value is None or value == ""):
            return False, f"Required field '{field_name}' is missing"
        
        # Type validation
        if field_type == 'string' and not isinstance(value, str):
            return False, f"Field '{field_name}' must be a string"
        
        # Options validation
        if options and value not in options:
            return False, f"Field '{field_name}' value '{value}' is not in allowed options: {options}"
        
        return True, ""
    
    def validate_all_fields(self, data: Dict) -> List[str]:
        """Validate all fields in the data dictionary."""
        errors = []
        for field_name, value in data.items():
            is_valid, error_msg = self.validate_field(field_name, value)
            if not is_valid:
                errors.append(error_msg)
        return errors


class DuplicateDetector:
    """Handles duplicate detection logic."""
    
    @staticmethod
    def _create_hash(title: str, pain_point: str) -> str:
        """Create a hash of title and pain point for duplicate detection."""
        combined = f"{title.strip().lower()}|{pain_point.strip().lower()}"
        return hashlib.md5(combined.encode('utf-8')).hexdigest()
    
    @staticmethod
    def is_duplicate(new_idea: Dict, existing_ideas: List[Dict]) -> bool:
        """Check if a new idea is a duplicate of any existing idea."""
        if not existing_ideas:
            return False
        
        new_title = new_idea.get('title', '')
        new_pain_point = new_idea.get('pain_point', '')
        new_hash = DuplicateDetector._create_hash(new_title, new_pain_point)
        
        for existing_idea in existing_ideas:
            existing_title = existing_idea.get('title', '')
            existing_pain_point = existing_idea.get('pain_point', '')
            existing_hash = DuplicateDetector._create_hash(existing_title, existing_pain_point)
            
            if new_hash == existing_hash:
                return True
        
        return False


class BlogPostProcessor:
    """Unified class for processing blog post ideas from multiple sources."""
    
    def __init__(self, metadata_config: str = "metadata_config.json"):
        """Initialize the processor."""
        self.validator = MetadataValidator(metadata_config)
        self.duplicate_detector = DuplicateDetector()
        self.storage_file = "blog_ideas.json"
        # Default enriched fields that should be included
        self.enriched_fields = [
            'article', 'voice', 'piece_type', 'marketing_post_type', 
            'primary_goal', 'technical_depth', 'keywords', 'length', 
            'sections', 'call_to_action', 'scraped_sources'
        ]
    
    def process_markdown_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a markdown file and extract blog post ideas."""
        logger.info(f"Processing markdown file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return []
        
        # Split by the separator
        separator_pattern = r'---\s*$'
        blog_posts = re.split(separator_pattern, content, flags=re.MULTILINE)
        
        # Filter out empty sections and strip whitespace
        blog_posts = [post.strip() for post in blog_posts if post.strip()]
        
        processed_posts = []
        for i, post_content in enumerate(blog_posts):
            try:
                blog_data = self.extract_blog_post_data(post_content)
                if blog_data:
                    # Add metadata
                    blog_data['id'] = self.generate_id(blog_data)
                    blog_data['created_at'] = datetime.now().isoformat()
                    blog_data['modified_at'] = datetime.now().isoformat()
                    processed_posts.append(blog_data)
            except Exception as e:
                logger.warning(f"Error processing blog post {i+1} in {file_path}: {e}")
                continue
        
        logger.info(f"Processed {len(processed_posts)} blog posts from {file_path}")
        return processed_posts
    
    def extract_blog_post_data(self, post_content: str) -> Optional[Dict[str, Any]]:
        """Extract structured data from a single blog post."""
        # Split into lines
        lines = post_content.strip().split('\n')
        
        # Extract title (first line, remove markdown headers)
        title = ""
        if lines:
            title_line = lines[0].strip()
            # Remove markdown headers and any prefix
            title = re.sub(r'^#+\s*', '', title_line)
            title = re.sub(r'^Blog Post Idea \d+:\s*', '', title)
            title = re.sub(r'^\d+\.\s*', '', title)
            title = title.strip('"')
        
        # Find sections
        pain_point = ""
        target_audience = ""
        content_details = ""
        sources = []
        
        current_section = None
        current_content = []
        
        # Process lines to find sections
        for line in lines[1:]:
            line = line.strip()
            
            # Check for section headers
            if line.startswith('**Pain Point:'):
                if current_section and current_content:
                    if current_section == 'pain_point':
                        pain_point = ' '.join(current_content)
                    elif current_section == 'target_audience':
                        target_audience = ' '.join(current_content)
                    elif current_section == 'content_details':
                        content_details = ' '.join(current_content)
                
                current_section = 'pain_point'
                current_content = [line.replace('**Pain Point:**', '').replace('**Pain Point**:', '').strip()]
            
            elif line.startswith('**Target Audience:'):
                if current_section and current_content:
                    if current_section == 'pain_point':
                        pain_point = ' '.join(current_content)
                    elif current_section == 'target_audience':
                        target_audience = ' '.join(current_content)
                    elif current_section == 'content_details':
                        content_details = ' '.join(current_content)
                
                current_section = 'target_audience'
                current_content = [line.replace('**Target Audience:**', '').replace('**Target Audience**:', '').strip()]
            
            elif line.startswith('**Content Details:'):
                if current_section and current_content:
                    if current_section == 'pain_point':
                        pain_point = ' '.join(current_content)
                    elif current_section == 'target_audience':
                        target_audience = ' '.join(current_content)
                    elif current_section == 'content_details':
                        content_details = ' '.join(current_content)
                
                current_section = 'content_details'
                current_content = [line.replace('**Content Details:**', '').replace('**Content Details**:', '').strip()]
            
            elif line.startswith('**Sources:'):
                # Sources section - collect URLs
                current_section = 'sources'
                current_content = []
            
            elif line.startswith('- ') and current_section == 'sources':
                # Collect source URLs
                url = line[2:].strip()  # Remove "- "
                if url:
                    sources.append(url)
            
            elif line and current_section:
                # Add content to current section
                current_content.append(line)
        
        # Handle the last section
        if current_section and current_content:
            if current_section == 'pain_point':
                pain_point = ' '.join(current_content)
            elif current_section == 'target_audience':
                target_audience = ' '.join(current_content)
            elif current_section == 'content_details':
                content_details = ' '.join(current_content)
        
        # Create the blog post data structure
        blog_data = {
            'title': title,
            'pain_point': pain_point,
            'target_audience': target_audience,
            'content_details': content_details,
            'sources': sources
        }
        
        # Validate required fields
        required_fields = ['title', 'pain_point']
        for field in required_fields:
            if not blog_data.get(field, '').strip():
                logger.warning(f"Missing required field '{field}' in blog post")
                return None
        
        return blog_data
    
    def generate_id(self, data: Dict) -> str:
        """Generate a unique ID for a blog post."""
        combined = f"{data.get('title', '')}|{data.get('pain_point', '')}"
        return hashlib.md5(combined.encode('utf-8')).hexdigest()[:12]
    
    def load_existing_ideas(self) -> List[Dict]:
        """Load existing blog ideas from storage file."""
        if not os.path.exists(self.storage_file):
            return []
        
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('ideas', []) if isinstance(data, dict) else []
        except Exception as e:
            logger.error(f"Error loading existing ideas: {e}")
            return []
    
    def save_ideas(self, ideas: List[Dict]) -> None:
        """Save blog ideas to storage file."""
        existing_ideas = self.load_existing_ideas()
        
        # Combine existing and new ideas
        all_ideas = existing_ideas + ideas
        
        # Remove duplicates (keeping the first occurrence)
        seen_ids = set()
        unique_ideas = []
        for idea in all_ideas:
            idea_id = idea.get('id', '')
            if idea_id not in seen_ids:
                seen_ids.add(idea_id)
                unique_ideas.append(idea)
        
        # Save to file
        try:
            data = {
                'ideas': unique_ideas,
                'last_updated': datetime.now().isoformat(),
                'total_count': len(unique_ideas)
            }
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(unique_ideas)} blog ideas to {self.storage_file}")
        except Exception as e:
            logger.error(f"Error saving ideas: {e}")
            raise
    
    def process_all_research_files(self, research_dir: str = "research_content") -> int:
        """Process all markdown files in the research directory."""
        if not os.path.exists(research_dir):
            logger.error(f"Research directory {research_dir} does not exist")
            return 0
        
        # Find all markdown files
        markdown_files = []
        for filename in os.listdir(research_dir):
            if filename.endswith('.md') and not filename.startswith('.'):
                markdown_files.append(os.path.join(research_dir, filename))
        
        if not markdown_files:
            logger.warning(f"No markdown files found in {research_dir}")
            return 0
        
        logger.info(f"Found {len(markdown_files)} markdown files to process")
        
        total_processed = 0
        all_new_ideas = []
        
        # Load existing ideas for duplicate checking
        existing_ideas = self.load_existing_ideas()
        
        for file_path in markdown_files:
            try:
                processed_posts = self.process_markdown_file(file_path)
                total_processed += len(processed_posts)
                
                # Add enriched metadata fields to each idea
                enriched_posts = []
                for post in processed_posts:
                    # Add default enriched fields if they don't exist
                    for field in self.enriched_fields:
                        if field not in post:
                            post[field] = ""
                    
                    # Set default values for common fields
                    if 'voice' not in post:
                        post['voice'] = "TheNewYorker"
                    if 'piece_type' not in post:
                        post['piece_type'] = "explainer"
                    if 'marketing_post_type' not in post:
                        post['marketing_post_type'] = "Educational (TOFU): For awareness and education - focus on answering general questions, providing foundational knowledge"
                    if 'primary_goal' not in post:
                        post['primary_goal'] = "educate"
                    if 'technical_depth' not in post:
                        post['technical_depth'] = "med"
                    
                    # Add article_generated flag
                    if 'article_generated' not in post:
                        post['article_generated'] = False
                    
                    # Add scraped_sources default
                    if 'scraped_sources' not in post:
                        post['scraped_sources'] = []
                    
                    enriched_posts.append(post)
                
                # Filter out duplicates
                filtered_posts = []
                for post in enriched_posts:
                    if not self.duplicate_detector.is_duplicate(post, existing_ideas + all_new_ideas):
                        filtered_posts.append(post)
                        # Add to existing ideas for subsequent checks
                        existing_ideas.append(post)
                    else:
                        logger.info(f"Skipping duplicate: {post.get('title', 'Unknown')}")
                
                all_new_ideas.extend(filtered_posts)
                
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                continue
        
        # Save all new ideas
        if all_new_ideas:
            self.save_ideas(all_new_ideas)
            logger.info(f"Successfully processed {total_processed} blog posts, added {len(all_new_ideas)} new ideas")
        else:
            logger.info(f"Processed {total_processed} blog posts, no new ideas to add")
        
        return len(all_new_ideas)
    
    def process_files(self, file_paths: List[str], skip_duplicates: bool = True) -> int:
        """Process multiple markdown files (backward compatibility)."""
        total_processed = 0
        new_ideas = []
        
        # Load existing ideas for duplicate checking
        existing_ideas = self.load_existing_ideas() if skip_duplicates else []
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                continue
            
            try:
                processed_posts = self.process_markdown_file(file_path)
                total_processed += len(processed_posts)
                
                # Add enriched metadata fields to each idea
                enriched_posts = []
                for post in processed_posts:
                    # Add default enriched fields if they don't exist
                    for field in self.enriched_fields:
                        if field not in post:
                            post[field] = ""
                    
                    # Set default values for common fields
                    if 'voice' not in post:
                        post['voice'] = "TheNewYorker"
                    if 'piece_type' not in post:
                        post['piece_type'] = "explainer"
                    if 'marketing_post_type' not in post:
                        post['marketing_post_type'] = "Educational (TOFU): For awareness and education - focus on answering general questions, providing foundational knowledge"
                    if 'primary_goal' not in post:
                        post['primary_goal'] = "educate"
                    if 'technical_depth' not in post:
                        post['technical_depth'] = "med"
                    
                    # Add scraped_sources default
                    if 'scraped_sources' not in post:
                        post['scraped_sources'] = []
                    
                    enriched_posts.append(post)
                
                # Filter out duplicates if requested
                if skip_duplicates:
                    filtered_posts = []
                    for post in enriched_posts:
                        if not self.duplicate_detector.is_duplicate(post, existing_ideas + new_ideas):
                            filtered_posts.append(post)
                            # Add to existing ideas for subsequent checks
                            existing_ideas.append(post)
                        else:
                            logger.info(f"Skipping duplicate: {post.get('title', 'Unknown')}")
                    processed_posts = filtered_posts
                
                new_ideas.extend(processed_posts)
                
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                continue
        
        # Save all new ideas
        if new_ideas:
            self.save_ideas(new_ideas)
            logger.info(f"Successfully processed {total_processed} blog posts, added {len(new_ideas)} new ideas")
        else:
            logger.info(f"Processed {total_processed} blog posts, no new ideas to add")
        
        return len(new_ideas)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Unified blog post idea processor that handles all research_content files',
        epilog='Example: python3 blog_idea_unified_processor.py'
    )
    
    parser.add_argument(
        '--research-dir',
        default='research_content',
        help='Directory containing markdown files to process (default: research_content)'
    )
    
    parser.add_argument(
        '--files',
        nargs='+',
        help='Specific markdown files to process (alternative to --research-dir)'
    )
    
    parser.add_argument(
        '--skip-duplicates',
        action='store_true',
        help='Skip duplicate blog posts based on title and pain point'
    )
    
    parser.add_argument(
        '--output-file',
        default='blog_ideas.json',
        help='Output JSON file name (default: blog_ideas.json)'
    )
    
    args = parser.parse_args()
    
    # Create processor and process files
    processor = BlogPostProcessor()
    
    # Update storage file path
    processor.storage_file = args.output_file
    
    try:
        # Check if specific files were provided
        if args.files:
            # Process specific files provided via command line
            logger.info(f"Processing specific files: {args.files}")
            new_count = processor.process_files(args.files, args.skip_duplicates)
        else:
            # Process all files in the research directory (original behavior)
            logger.info(f"Processing all files in directory: {args.research_dir}")
            new_count = processor.process_all_research_files(args.research_dir)
        
        logger.info(f"Unified processing complete. Added {new_count} new blog ideas.")
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return


if __name__ == "__main__":
    main()
