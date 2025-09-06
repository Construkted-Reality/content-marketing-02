#!/usr/bin/env python3
""" 
This script:
1. Reads blog post ideas from `blog_ideas.json`.
2. Calls an LLM API twice per idea:
   - First to select writing parameters (voice, piece type, etc.).
   - Second to generate the full blog draft using the selected parameters.
3. Saves the generated draft (with metadata) into `blog_post_drafts/`,
   handling naming collisions by appending a two‑digit suffix (e.g., `-01.md`).
"""

import os
import sys
import json
import pathlib
import re
import argparse
import subprocess
import tempfile
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    sys.stderr.write("Error: The Python `requests` library is required. Install it with `pip install requests`.\n")
    sys.exit(1)

# Import scraping utilities
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from utils.scrape_sources import scrape_urls
except ImportError:
    sys.stderr.write("Error: Could not import scraping utilities. Make sure utils/scrape_sources.py exists.\n")
    sys.exit(1)

# --- Configuration -----------------------------------------------------------
AI_PROVIDER = "openai"   # Change between "ollama" and "openai" compatible API

# OLLAMA API configuration
OLLAMA_HOST = "192.168.8.90"
OLLAMA_PORT = "11434"
OLLAMA_API_PATH = "/api/generate"
OLLAMA_MODEL = "gpt-oss-120b-CTX28k"

# OpenAI API configuration
OPENAI_HOST_IP = "192.168.8.90"
OPENAI_PORT = "42069"
OPENAI_API_PATH = "/v1/chat/completions"
OPENAI_AUTH_KEY = "outsider"
OPENAI_MODEL = "gpt-oss-120b"
#OPENAI_MODEL = "qwen3-think-30b-awq8"

# --- Main execution ---
if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Generate blog drafts from blog_ideas.json. "
                    "Use --force_article_gen to regenerate drafts for ideas that already have an article."
    )
    parser.add_argument(
        "--force_article_gen",
        action="store_true",
        help="Regenerate drafts even if `article_generated` is true."
    )
    parser.add_argument(
        "--ideas_id",
        type=str,
        help="Process only the idea with the given id."
    )
    args = parser.parse_args()
    force_article_gen = args.force_article_gen
    
    if force_article_gen:
        print("Force article generation enabled – all ideas will be processed.")
    else:
        print("Skipping ideas with article_generated=True. Use --force_article_gen to override.")
    
    print(f"AI Provider set to: {AI_PROVIDER}")

DESTINATION_FOLDER = pathlib.Path("blog_post_drafts")

CONTEXT_FILE = pathlib.Path("guidance/context.md")
TITLES_FILE = pathlib.Path("guidance/crafting_compelling_titles.md")
COMPANY_OPERATION_FILE = pathlib.Path("guidance/company_operation.md")
CONTENT_MARKETING_GUIDANCE_FILE = pathlib.Path("guidance/content_marketing_guidance.md")

# Voice definitions (mirroring the associative array in the Bash script)
VOICE_DEFINITIONS: Dict[str, str] = {
    "TheNewYorker": (
        "New Yorker "
        "- Tone: sophisticated, witty, introspective, and conversational, yet authoritative. "
        "- Rhythm: mix short, punchy sentences with longer, meandering ones; allow occasional asides and minor tangents. "
        "- Style: sprinkle in idioms, slang, and light‑hearted rhetorical questions (e.g., “Who hasn’t…?”) to keep it authentic. "
        "- Personality: let the narrator’s sharp curiosity and dry humor shine through; don’t be afraid of a subtle imperfection or a fleeting digression. "
        "- Purpose: inform, entertain, and provoke thought—think of a column that educates while it delights and challenges the reader."
    ),
    "TheAtlantic": (
        "The Atlantic "
        "- Personality: Thought‑provoking, long‑form, measured, policy‑savvy. "
        "- Signature tricks: Structured arguments, data‑driven evidence, historical context, calm but persuasive tone, minimal slang. "
        "- Prompt cheat‑sheet: Write in the voice of an Atlantic columnist: analytical, well‑researched, balanced, with a calm persuasive tone and ample historical context."
    ),
    "Wired": (
        "Wired "
        "- Personality: Futurist, tech‑obsessed, fast‑paced, jargon‑light. "
        "- Signature tricks: Short, punchy sentences; use of bold tech metaphors ('the internet is a nervous system'); occasional emojis or meme references (when appropriate); 'what‑it‑means‑for‑you' framing. "
        "- Prompt cheat‑sheet: Write like a Wired feature: tech‑forward, fast‑paced, with vivid metaphors and a ‘what it means for the reader’ angle."
    ),
}

FORMATTING_RULES = (
    "**Formatting rules** "
    "- Do **not** use any tables, ASCII‑art tables, or Markdown tables. "
    "- Keep the output strictly in paragraph form (or simple bullet points if a list is needed). "
    "- Avoid other “grid‑like” structures; use prose instead. "
    "- Deliver a piece that fulfills the voice and purpose while respecting the formatting rules."
)

# --- Helper functions ---------------------------------------------------------

def read_file(path: pathlib.Path) -> str:
    """Read a file and return its content as a string."""
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        sys.stderr.write(f"Error reading {path}: {e}\n")
        sys.exit(1)

def post_api(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Unified API request function that handles both Ollama and OpenAI APIs."""
    if AI_PROVIDER == "openai":
        # OpenAI API compatibility
        headers = {
            "Authorization": f"Bearer {OPENAI_AUTH_KEY}",
            "Content-Type": "application/json"
        }
        # Build the full URL from IP, port, and path for OpenAI Compliant API
        url = f"http://{OPENAI_HOST_IP}:{OPENAI_PORT}{OPENAI_API_PATH}"
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=300)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            sys.stderr.write(f"Error contacting OpenAI API at {url}: {e}\n")
            sys.exit(1)
    else:
        # Build the full URL from IP, port, and path for Ollama compliant API
        url = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}{OLLAMA_API_PATH}"
        try:
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            sys.stderr.write(f"Error contacting OLLAMA at {url}: {e}\n")
            sys.exit(1)


def call_llm(prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
    """
    Unified LLM call function that handles both OpenAI and Ollama APIs.
    
    Args:
        prompt: The user prompt to send to the LLM
        system_prompt: Optional system prompt (for OpenAI) or system context (for Ollama)
        **kwargs: Additional parameters to override defaults
        
    Returns:
        The text content from the LLM response
    """
    # Set standard defaults for all LLM calls
    defaults = {
        "temperature": 1,
        "reasoning_effort": "high",
        "max_tokens": 64000,
        "top_p": 1,
    }
    # Override defaults with any provided kwargs
    defaults.update(kwargs)
    
    if AI_PROVIDER == "openai":
        # Build OpenAI chat completions format
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": OPENAI_MODEL,
            "messages": messages,
            "stream": False,
        }
        # Add the standardized parameters
        payload.update(defaults)
        
        result = post_api(payload)
        
        # Extract content from OpenAI response
        try:
            return result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        except (IndexError, KeyError) as e:
            sys.stderr.write(f"Failed to extract content from OpenAI response: {e}\n")
            sys.stderr.write(f"Raw response: {result}\n")
            return ""
    else:
        # Build Ollama format
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt
            
        result = post_api(payload)
        
        # Extract content from Ollama response
        return result.get("response", "")


def get_batch_diversity_context(processed_ideas: list) -> str:
    """Generate context about previous selections to encourage diversity."""
    if not processed_ideas:
        return ""
    
    # Extract previous selections
    voices = [idea.get('voice', '') for idea in processed_ideas if idea.get('voice')]
    piece_types = [idea.get('piece_type', '') for idea in processed_ideas if idea.get('piece_type')]
    marketing_types = [idea.get('marketing_post_type', '') for idea in processed_ideas if idea.get('marketing_post_type')]
    goals = [idea.get('primary_goal', '') for idea in processed_ideas if idea.get('primary_goal')]
    audiences = [idea.get('target_audience', '') for idea in processed_ideas if idea.get('target_audience')]
    
    context_parts = []
    if voices:
        context_parts.append(f"Previous voices used: {', '.join(voices)}")
    if piece_types:
        context_parts.append(f"Previous piece types: {', '.join(piece_types)}")
    if marketing_types:
        context_parts.append(f"Previous marketing types: {', '.join(marketing_types)}")
    if goals:
        context_parts.append(f"Previous goals: {', '.join(goals)}")
    if audiences:
        context_parts.append(f"Previous audiences: {', '.join(audiences)}")
    
    if context_parts:
        return f"\n**BATCH DIVERSITY CONTEXT**: {'; '.join(context_parts)}. Aim for diversity in your selections unless the content strongly suggests otherwise.\n"
    return ""


def extract_youtube_transcript(url: str, lang: str = "en") -> Dict[str, Any]:
    """
    Uses yt-dlp (via the existing extract_transcript.py script) to download
    the auto-generated subtitles for a YouTube video and returns a ScrapedSource
    dict compatible with the rest of the pipeline.
    
    Args:
        url: YouTube video URL
        lang: Language code for subtitles (default: "en")
        
    Returns:
        ScrapedSource dict with url, status, text, char_count, last_scraped_at, and optional error
    """
    # Create a temporary file for the transcript output
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        output_path = tmp.name

    # Build command: python extract_transcript.py <url> --lang <lang> --output <tmpfile>
    cmd = [
        sys.executable,
        os.path.join(os.path.dirname(__file__), "extract_transcript.py"),
        url,
        "--lang",
        lang,
        "--output",
        output_path,
    ]

    try:
        # Run the command, suppressing stdout; errors go to stderr
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        # Clean up temporary file on error
        try:
            os.remove(output_path)
        except OSError:
            pass
        
        return {
            "url": url,
            "status": "error",
            "text": "",
            "char_count": 0,
            "last_scraped_at": datetime.now().isoformat(),
            "error": f"yt-dlp failed: {e.stderr.strip()}",
        }

    # Read the transcript file generated by extract_transcript.py
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            transcript = f.read().strip()
    except Exception as e:
        return {
            "url": url,
            "status": "error",
            "text": "",
            "char_count": 0,
            "last_scraped_at": datetime.now().isoformat(),
            "error": f"Failed to read transcript file: {str(e)}",
        }
    finally:
        # Clean up temporary file
        try:
            os.remove(output_path)
        except OSError:
            pass

    if not transcript:
        return {
            "url": url,
            "status": "error",
            "text": "",
            "char_count": 0,
            "last_scraped_at": datetime.now().isoformat(),
            "error": "No subtitles found for this video.",
        }

    return {
        "url": url,
        "status": "ok",
        "text": transcript,
        "char_count": len(transcript),
        "last_scraped_at": datetime.now().isoformat(),
    }


def get_or_build_scraped_sources(idea: dict) -> List[Dict[str, Any]]:
    """
    Get cached scraped sources or scrape URLs and cache the results.
    Handles both regular web pages (via scrapegraphai) and YouTube videos (via yt-dlp).
    
    Args:
        idea: The idea dictionary that may contain cached scraped_sources
        
    Returns:
        List of ScrapedSource dictionaries
    """
    # Check if we have cached scraped sources
    cached_sources = idea.get('scraped_sources', [])
    if cached_sources:
        print(f"  Using cached scraped sources ({len(cached_sources)} sources)")
        return cached_sources
    
    # Get URLs to scrape
    urls = idea.get('sources', [])
    if not urls:
        print("  No source URLs to scrape")
        return []
    
    print(f"  Processing {len(urls)} source URLs...")
    
    # Separate YouTube URLs from regular URLs
    youtube_urls = []
    regular_urls = []
    
    for url in urls:
        if re.search(r'(youtube\.com|youtu\.be)', url):
            youtube_urls.append(url)
        else:
            regular_urls.append(url)
    
    scraped_sources = []
    
    # Process YouTube URLs with transcript extraction
    if youtube_urls:
        print(f"  Extracting transcripts from {len(youtube_urls)} YouTube video(s)...")
        for youtube_url in youtube_urls:
            transcript_result = extract_youtube_transcript(youtube_url)
            scraped_sources.append(transcript_result)
            if transcript_result['status'] == 'ok':
                print(f"    ✓ YouTube transcript extracted: {transcript_result['char_count']} characters")
            else:
                print(f"    ✗ YouTube transcript failed: {transcript_result.get('error', 'Unknown error')}")
    
    # Process regular URLs with web scraping
    if regular_urls:
        print(f"  Scraping {len(regular_urls)} web page(s)...")
        try:
            web_scraped = scrape_urls(regular_urls)
            scraped_sources.extend(web_scraped)
        except Exception as e:
            sys.stderr.write(f"Error scraping web sources: {e}\n")
    
    # Update the idea with scraped sources
    idea['scraped_sources'] = scraped_sources
    
    # Persist to JSON file immediately
    try:
        with open("blog_ideas.json", "r", encoding="utf-8") as f:
            json_data = json.load(f)
        
        # Find and update the corresponding idea in the JSON data
        idea_id = idea.get('id')
        if idea_id:
            for json_idea in json_data.get('ideas', []):
                if json_idea.get('id') == idea_id:
                    json_idea['scraped_sources'] = scraped_sources
                    break
        
        # Save updated JSON file
        with open("blog_ideas.json", "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        successful_count = len([s for s in scraped_sources if s.get('status') == 'ok'])
        print(f"  Processed and cached {len(scraped_sources)} sources ({successful_count} successful)")
        
    except Exception as e:
        sys.stderr.write(f"Warning: Could not cache scraped sources: {e}\n")
    
    return scraped_sources


def build_source_excerpts(scraped_sources: List[Dict[str, Any]]) -> str:
    """
    Build a text block from scraped sources, including each source's URL and extracted text.
    
    Args:
        scraped_sources: List of ScrapedSource dictionaries
        
    Returns:
        Concatenated excerpts with URLs from successful scrapes
    """
    if not scraped_sources:
        return ""
    
    excerpts = []
    successful_scrapes = 0
    
    for source in scraped_sources:
        if source.get('status') == 'ok' and source.get('text'):
            url = source.get('url', '')
            text = source['text'].strip()
            if text:
                if url:
                    excerpts.append(f"Source URL: {url}\n\n{text}")
                else:
                    excerpts.append(text)
                successful_scrapes += 1
    
    if not excerpts:
        return ""
    
    print(f"  Built source excerpts from {successful_scrapes}/{len(scraped_sources)} successful scrapes")
    
    # Join excerpts with separators
    return "\n\n---\n\n".join(excerpts)


def build_idea_context(idea: dict) -> str:
    """Build idea context without URL lists, including scraped source excerpts.

    This function now also includes the optional ``reference_context`` field from
    the ``blog_ideas.json`` entry, if present. The field provides additional
    background that the LLM can use when selecting parameters and drafting the
    blog post.
    """
    idea_content_parts = []

    # Add title if available
    if idea.get("title"):
        idea_content_parts.append(f"Title: {idea['title']}")

    # Add pain point
    if idea.get("pain_point"):
        idea_content_parts.append(f"Pain Point: {idea['pain_point']}")

    # Add target audience
    if idea.get("target_audience"):
        idea_content_parts.append(f"Target Audience: {idea['target_audience']}")

    # Add content details if available
    if idea.get("content_details"):
        idea_content_parts.append(f"Content Details: {idea['content_details']}")

    # Get scraped source excerpts instead of URL list
    scraped_sources = get_or_build_scraped_sources(idea)
    source_excerpts = build_source_excerpts(scraped_sources)

    if source_excerpts:
        idea_content_parts.append(f"Source Excerpts:\n{source_excerpts}")

    # Add reference_context if present
    if idea.get("reference_context"):
        idea_content_parts.append(f"Reference Context:\n{idea['reference_context']}")

    return "\n\n".join(idea_content_parts)


def add_sources_section_to_output(idea: dict, response: str) -> str:
    """
    Append a Sources section to the blog post output programmatically.
    
    Args:
        idea: The idea dictionary containing sources
        response: The LLM-generated blog post content
        
    Returns:
        Blog post content with Sources section appended
    """
    sources = idea.get('sources', [])
    if not sources:
        return response
    
    sources_section = "\n\n## Sources\n\n"
    for i, source in enumerate(sources, 1):
        sources_section += f"{i}. {source}\n"
    
    return response + sources_section


def select_parameters(idea_content: str, context_content: str, content_marketing_guidance_content: str, titles_content: str, processed_ideas: Optional[List[dict]] = None) -> Dict[str, str]:
    """First API call – ask the model to choose voice, piece type, etc. and generate a title."""
    if processed_ideas is None:
        processed_ideas = []
    
    batch_context = get_batch_diversity_context(processed_ideas)
    
    first_prompt = f"""Analyze the following topic research and select the most appropriate writing parameters for content marketing.

**Context Summary**: You will be given: 1) batch diversity context, 2) voice definitions, 3) content marketing guidance, 4) topic research content, 5) title guidance, 6) detailed instructions and JSON schema.

**IMPORTANT**: Vary your parameter selections across different topics. Avoid selecting identical combinations unless truly warranted by the content. Consider how this topic differs from previous topics in the batch.
{batch_context}

Writing style descriptions:
New Yorker: {VOICE_DEFINITIONS["TheNewYorker"]}
The Atlantic: {VOICE_DEFINITIONS["TheAtlantic"]}
Wired: {VOICE_DEFINITIONS["Wired"]}

Content Marketing Context:
{content_marketing_guidance_content}

Title Guidance:
{titles_content}

Topic research content:
{idea_content}
Use the provided source excerpts to extract the pain points and guide your research.

Use ONLY this JSON format for output (no other text):
{{
  "voice": "Your chosen voice option (e.g., TheNewYorker)",
  "piece_type": "Your chosen piece type (e.g., explainer)",
  "marketing_post_type": "Your chosen marketing post type (e.g., educational)",
  "primary_goal": "Your chosen primary goal (e.g., educate)",
  "target_audience": "Your chosen target audience (e.g., enterprise)",
  "technical_depth": "Your chosen technical depth (e.g., med)",
  "justification": "Explanation of why these choices were made",
  "pain_point": "Summary of the main pain point users are experiencing",
  "length": "Estimated number of words for the final article",
  "primary_seo_key_word": "Primary SEO keyword for the article",
  "secondary_seo_key_words": ["Secondary keyword 1", "Secondary keyword 2", "Secondary keyword 3"],
  "title": "A compelling, reader-focused title following the guidance provided"
}}

Instructions:
1. **Voice Selection**: Choose the most appropriate voice based on content type and audience:
   - Technical troubleshooting/how-to guides → Consider Wired (but evaluate other options)
   - Broader conceptual topics → Consider TheNewYorker
   - Policy/industry analysis → Consider TheAtlantic
   - Evaluate which voice truly fits the content and audience best

2. **Piece Type Selection** from: explainer, tutorial, methods deep dive, case study, product update, standards/policy analysis, news reaction
   - Match the piece type to the content structure and user needs
   - Consider variety across the batch

3. **Marketing Post Type** - Balance across funnel positions:
   - Educational (TOFU): For awareness and education - foundational knowledge
   - Comparison (MOFU): For consideration and evaluation - benefits vs competitors
   - Conversion-focused (BOFU): For decision-making and purchase - drive action, emphasize ROI
   - Case Study: For trust-building - showcase real-world results
   - Product Update: For awareness and conversion - announce new features
   - Standards/Policy Analysis: For thought leadership - industry insights
   - News Reaction: For engagement - commentary on trends

4. **Primary Goal** from: educate, persuade, announce, compare, troubleshoot
   - Match to the core user need and content purpose

5. **Target Audience** from: enterprise, public sector, academic, hobbyist
   - Consider user sophistication, budget constraints, and use case complexity

6. **Technical Depth** from: low, med, high
   - Match to audience expertise and content complexity

7. **Justification**: Explain your specific choices and how this topic differs from typical selections

8. **Pain Point**: Extract detailed, specific pain points from the research content and URLs with concrete examples

9. **Length**: Integer value between 800 and 3000
   - Estimate an article length based on the amount of source material, the amount that should be said 
     regarding the topic that was researched and the complexity of the pain point/problem being resolved by the article
   - 600-900 words: For simple problems that can be answered with a quick list, a straightforward definition, or a few direct steps. The solution is not deeply nuanced.
   - 1200-1800 words: For multi-faceted problems that require more detailed explanations, examples, comparisons, or a step-by-step process. This is for topics that require evidence and elaboration to be truly helpful.
   - 2500-3000 words: For complex, high-stakes problems that require a comprehensive, in-depth guide. These articles often cover a topic from every angle, include multiple sub-sections, and aim to be the definitive resource on the subject.

10. **primary seo key word**: Select one primary SEO key word which will be used later in the crafting of the blog post for the company marketing website.

11. **secondary seo key words**: Select three to five (2-5) secondary SEO key words which will be used later in the crafting of the blog post for the company marketing website.

12. **Title**: Generate a compelling, reader-focused title following the guidance above:
    - Write the title from the reader's point of view
    - Include one concrete benefit or goal
    - Keep under 15 words if possible
    - Be truthful and specific
    - Optionally add target audience or constraint for relevance

Output ONLY the JSON object above with your selections."""
    # Use the unified LLM call function
    response_text = call_llm(prompt=first_prompt)
    
    # Parse the JSON response
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Fallback: extract the longest {...} block using regex
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not match:
            sys.stderr.write("Failed to locate JSON object in LLM response.\n")
            sys.exit(1)
        json_candidate = match.group(0)
        try:
            return json.loads(json_candidate)
        except json.JSONDecodeError as exc:
            sys.stderr.write(f"JSON parsing error after regex extraction: {exc}\n")
            sys.exit(1)


def generate_blog_post(
    idea_content: str,
    context_content: str,
    company_operation_content: str,
    content_marketing_guidance_content: str,  # New parameter
    selected: Dict[str, str],
) -> str:
    """Second API call – generate the full blog post using the chosen parameters."""
    voice_key = selected["voice"]
    voice_content = VOICE_DEFINITIONS.get(voice_key, "")
    voice_prompt = f"Write in the voice of a seasoned journalist at {voice_content}"

    system_prompt = (
        f"Reasoning: high "
        f"You are a content creator for Construkted Reality, tasked with writing a blog post. "
        f"Your writing style is that of a seasoned journalist at {voice_content}. "
        f"Content Marketing Context: {content_marketing_guidance_content}. "
        f"Extra context {context_content}. "
        f"Company operation details: {company_operation_content}. Do **NOT** suggested ideas which do not align with company operation details."
        f"Article title is: {selected['title']}."
        f"Piece Type: {selected['piece_type']}. "
        f"Primary Goal: {selected['primary_goal']}. "
        f"Target Audience: {selected['target_audience']}. "
        f"Technical Depth: {selected['technical_depth']}. "
        f"Article target word count length: {selected['length']} words.\n"
        f"\n\n**Core Instructions**:\n- Incorporate the primary SEO keyword (`{selected.get('primary_seo_key_word','')}`) prominently in the title and early sections, and naturally weave the secondary SEO keywords (`{', '.join(selected.get('secondary_seo_key_words', []))}`) throughout the article for SEO optimization.\n"
        f"- Mention our product, Construkted Reality, where it naturally fits as a solution to the problems discussed. Do not force it.\n"
        f"- Do not fabricate information about how Construkted Reality works or its features.\n"
        f"- For images, create numeric placeholders in the body of the post (e.g., [IMAGE 1], [IMAGE 2]). At the end of the article, create an 'Image Prompt Summary' section with detailed prompts for an image generation LLM for each placeholder.\n"
        f"- Follow these formatting rules: {FORMATTING_RULES}\n"
        f"- When referencing information from the provided source excerpts, include the source URL as an inline citation and weave the URLs naturally into the body of the article for credibility and SEO optimization."
    )

    prompt = (
        f"Using the provided research, write a full blog post. \n"
        f"The primary goal is to validate and suggest solutions to the user pain points identified in the research.\n"
        f"The secondary goal is to position Construkted Reality as the solution to the user pain point.\n"
        f"**Article Research and Draft Content**:\n{idea_content}\n\n"
        f"**Instructions**:\n"
        f"1. Use the provided source excerpts to deepen your understanding of the pain points.\n"
        f"2. Evaluate if Construkted Reality is a suitable solution to the pain point/problem statement based on the 'Company operation details' provided. Be conservative: if a capability isn’t explicitly supported, assume it’s not available. \n" 
        f"   If Construkted Reality cannot provide a direct solution, write a statement in bold under the title describing why Construkted Reality cannot provide a solution to the problem/pain point. and continue writing the blog post. \n"
        f"   Also if Construkted Reality does not provide a direct solution, frame Construkted Reality as a tool after the pain point/problem is resolved. Suggestion for positioning Constructed Reality should be in line with 'Company operation details'. Present the most appropriate use of Construkted Reality at the end of the blog post. \n"
        f"3. Write the full blog post, addressing the extracted pain points and integrating solutions."
        
    )


    # Use the unified LLM call function
    return call_llm(prompt=prompt, system_prompt=system_prompt)


def make_output_path(base_name: str) -> pathlib.Path:
    """Determine a non‑colliding output path inside DESTINATION_FOLDER."""
    dest = DESTINATION_FOLDER / f"{base_name}.md"
    if not dest.parent.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)

    if not dest.exists():
        return dest

    # Find highest existing numeric suffix
    pattern = re.compile(rf"^{re.escape(base_name)}-(\d{{2}})\.md$")
    max_counter = 0
    for p in dest.parent.iterdir():
        m = pattern.match(p.name)
        if m:
            try:
                num = int(m.group(1))
                if num > max_counter:
                    max_counter = num
            except ValueError:
                pass

    counter = max_counter + 1
    while True:
        suffix = f"{counter:02d}"
        candidate = dest.parent / f"{base_name}-{suffix}.md"
        if not candidate.exists():
            return candidate
        counter += 1


def load_blog_ideas_from_json() -> list:
    """Load blog ideas from the JSON file."""
    try:
        with open("blog_ideas.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("ideas", [])
    except FileNotFoundError:
        sys.stderr.write("Error: blog_ideas.json file not found.\n")
        sys.exit(1)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Error: Invalid JSON in blog_ideas.json: {e}\n")
        sys.exit(1)


def update_idea_with_api_response(idea: dict, selected: dict) -> None:
    """Update the idea dictionary with fields from the API response."""
    # Only update fields that were returned by the API call
    for field in ["voice", "piece_type", "marketing_post_type", "primary_goal", "target_audience",
                  "technical_depth", "justification", "pain_point", "keywords", "length",
                  "sections", "call_to_action", "title",
                  "primary_seo_key_word", "secondary_seo_key_words"]:
        if field in selected and selected[field]:  # Only update if field has data
            idea[field] = selected[field]

def set_seo_fields(idea: dict, selected: dict) -> None:
    """Utility to set primary/secondary SEO fields from LLM response (optional)."""
    # The LLM may return these fields; if present, store them; otherwise keep defaults.
    if "primary_seo_key_word" in selected and selected["primary_seo_key_word"]:
        idea["primary_seo_key_word"] = selected["primary_seo_key_word"]
    if "secondary_seo_key_words" in selected and isinstance(selected["secondary_seo_key_words"], list):
        idea["secondary_seo_key_words"] = selected["secondary_seo_key_words"]


def update_modified_at(idea: dict) -> None:
    """
    Set the `modified_at` key of the given idea dict to the current UTC
    timestamp in ISO‑8601 format with microseconds (e.g. 2025-09-03T12:34:56.123456).
    """
    now_iso = datetime.now().isoformat()
    idea["modified_at"] = now_iso


def save_draft_and_update_json(idea: dict, response: str, selected: dict) -> None:
    """Save the draft and update the JSON file with article path."""
    # Load the existing JSON file to update it
    try:
        with open("blog_ideas.json", "r", encoding="utf-8") as f:
            json_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        sys.stderr.write("Error: Could not load blog_ideas.json for updating.\n")
        return
    
    # Update the idea with API response data
    update_idea_with_api_response(idea, selected)
    
    # Create output filename: idea ID + title
    base_name = f"{idea.get('id', 'unknown')}_{idea.get('title', 'untitled').replace('/', '_').replace('\\', '_')}"
    # Sanitize the base name to remove invalid characters for filenames
    base_name = re.sub(r'[<>:"/\\|?*]', '_', base_name)
    # Limit length to avoid filesystem issues
    base_name = base_name[:100]
    
    # Determine output file name with collision handling
    output_path = make_output_path(base_name)
    
    # Add Sources section programmatically to the response
    response_with_sources = add_sources_section_to_output(idea, response)
    
    # Append metadata
    metadata = f""" 
---
### Content Creation Metadata
- **Voice**: {selected.get('voice', '')}
- **Piece Type**: {selected.get('piece_type', '')}
- **Marketing Post Type**: {selected.get('marketing_post_type', '')}
- **Primary Goal**: {selected.get('primary_goal', '')}
- **Target Audience**: {selected.get('target_audience', '')}
- **Technical Depth**: {selected.get('technical_depth', '')}
- **Justification**: {selected.get('justification', '')}
- **Pain Point**: {selected.get('pain_point', '')}
---
"""
    full_content = response_with_sources + metadata
    
    # Write out
    output_path.write_text(full_content, encoding="utf-8")
    print(f"  Saved draft to {output_path}")
    
    # Update the article field in the JSON idea
    idea["article"] = str(output_path.relative_to("."))
    
    # Set the article_generated flag to True
    idea["article_generated"] = True
    
    # Find and update the corresponding idea in the JSON data
    idea_id = idea.get('id')
    if idea_id:
        for json_idea in json_data.get('ideas', []):
            if json_idea.get('id') == idea_id:
                # Update this idea with all the new data
                json_idea.update(idea)
                break
    
    # Save updated JSON file
    try:
        with open("blog_ideas.json", "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print(f"  Updated JSON file with API response data")
    except Exception as e:
        sys.stderr.write(f"Error saving updated JSON: {e}\n")


def main() -> None:
    # Load blog ideas from JSON file
    ideas = load_blog_ideas_from_json()
    
    if not ideas:
        sys.stderr.write("No blog ideas found in the JSON file.\n")
        sys.exit(0)
    
    # If --ideas_id is specified, filter ideas to only process that one
    if args.ideas_id:
        matching = [idea for idea in ideas if idea.get("id") == args.ideas_id]
        if not matching:
            sys.stderr.write(f"Error: No idea found with id '{args.ideas_id}'.\n")
            sys.exit(1)
        ideas = matching  # Restrict processing to the single idea
    
    # Process only first 5 ideas for testing 
#    ideas = ideas[:5]  # Comment this line when ready for full processing
    
    # Load static auxiliary files once
    context_content = read_file(CONTEXT_FILE)
    titles_content = read_file(TITLES_FILE)
    company_operation_content = read_file(COMPANY_OPERATION_FILE)

    # Track processed ideas for batch diversity
    processed_ideas = []

    # Process each idea
    for idx, idea in enumerate(ideas, start=1):
        # Skip ideas that have already been generated (unless force mode is enabled)
        if not force_article_gen and idea.get("article_generated"):
            # Check if this is a single idea request and it's already generated
            if args.ideas_id and idea.get("article_generated"):
                print(f"Idea id '{args.ideas_id}' already has an article written.")
                sys.exit(0)
            print(f"  Skipping – article already generated (use --force_article_gen to override)")
            continue
            
        print(f"[{idx}/{len(ideas)}] Processing idea: {idea.get('title', 'Untitled')}")
        
        # Build idea content with scraped source excerpts (no URL lists)
        idea_content = build_idea_context(idea)
        
        # --- First API call -------------------------------------------------
        content_marketing_guidance_content = read_file(CONTENT_MARKETING_GUIDANCE_FILE)
        selected = select_parameters(idea_content, context_content, content_marketing_guidance_content, titles_content, processed_ideas)

        # Verify we got a voice; otherwise skip
        if not selected.get("voice"):
            print(f"  Warning: Voice selection failed for idea; skipping.")
            continue

        # Echo selected parameters (mirrors Bash script output)
        print("  Selected parameters:")
        for key in ["voice", "title", "piece_type", "marketing_post_type", "primary_goal", "target_audience", "technical_depth", "length"]:
            print(f"    {key.replace('_', ' ').title()}: {selected.get(key, '')}")

        # Update JSON file with API response data immediately after first API call
        update_idea_with_api_response(idea, selected)
        # Optional: capture SEO fields from the LLM response
        set_seo_fields(idea, selected)
        
        # ---------------------------------------------------------------
        # STEP 3: Refresh modified_at timestamp now that the idea has been
        #         processed (parameters selected)
        # ---------------------------------------------------------------
        update_modified_at(idea)
        
        # Add this idea to processed list for future diversity context
        processed_ideas.append(idea)
        try:
            with open("blog_ideas.json", "r", encoding="utf-8") as f:
                json_data = json.load(f)
            
            # Find and update the corresponding idea in the JSON data
            idea_id = idea.get('id')
            if idea_id:
                for json_idea in json_data.get('ideas', []):
                    if json_idea.get('id') == idea_id:
                        # Update this idea with the API response data
                        json_idea.update(idea)
                        break
            
            # Save updated JSON file
            with open("blog_ideas.json", "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            print("  Updated JSON file")
        except Exception as e:
            sys.stderr.write(f"Error updating JSON after first API call: {e}\n")

        # --- Second API call -----------------------------------------------
        content_marketing_guidance_content = read_file(CONTENT_MARKETING_GUIDANCE_FILE)
        response = generate_blog_post(
            idea_content,
            context_content,
            company_operation_content,
            content_marketing_guidance_content,
            selected,
        )

        # Save draft and update JSON
        save_draft_and_update_json(idea, response, selected)
        print()
    
    # If we processed a single idea, exit after completion
    if args.ideas_id:
        sys.exit(0)


if __name__ == "__main__":
    main()
