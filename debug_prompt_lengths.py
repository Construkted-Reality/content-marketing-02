#!/usr/bin/env python3
"""
Sanity‑check script for the two LLM prompts used in the blog‑draft pipeline.

It:
1. Loads a single idea (first in ``blog_ideas.json`` or the one specified via
   ``--idea-id``).
2. Builds the **first‑call** context (URL list only) and the **second‑call**
   context (full URL + text excerpts) using the same ``build_idea_context``
   helper from ``02_generate_blog_drafts.py``.
3. Constructs the exact prompts that are sent to the LLMs in
   ``select_parameters`` and ``generate_blog_post``.
4. Prints character counts and an approximate token estimate
   (≈ 0.75 token per word, matching the logic in ``call_llm``).
5. Flags any prompt that exceeds the model’s context window
   (64 k tokens for OpenAI, 28 k tokens for Ollama).

Usage:
    python debug_prompt_lengths.py            # checks the first idea
    python debug_prompt_lengths.py --idea-id <id>
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Import helpers from the main script – treat it as a module.
# The file is in the same directory, so we can modify sys.path.
SCRIPT_DIR = Path(__file__).parent
sys.path.append(str(SCRIPT_DIR))

from 02_generate_blog_drafts import (
    build_idea_context,
    read_file,
    get_batch_diversity_context,
    VOICE_DEFINITIONS,
    FORMATTING_RULES,
)

# Model limits (tokens)
OPENAI_LIMIT = 64000
OLLAMA_LIMIT = 28000  # the Ollama model used in the project (CTX28k)


def estimate_tokens(text: str) -> int:
    """Approximate token count using the same 0.75 tokens/word factor."""
    return int(len(text.split()) * 0.75)


def build_first_prompt(idea_content: str, context_content: str,
                       marketing_guidance: str, titles_content: str,
                       processed_ideas: list) -> str:
    """Re‑create the prompt used for the *first* LLM call."""
    batch_context = get_batch_diversity_context(processed_ideas)

    prompt = f"""Analyze the following topic research and select the most appropriate writing parameters for content marketing.

**Context Summary**: You will be given: 1) batch diversity context, 2) voice definitions, 3) content marketing guidance, 4) topic research content, 5) title guidance, 6) detailed instructions and JSON schema.
{batch_context}

Writing style descriptions:
New Yorker: {VOICE_DEFINITIONS["TheNewYorker"]}
The Atlantic: {VOICE_DEFINITIONS["TheAtlantic"]}
Wired: {VOICE_DEFINITIONS["Wired"]}

Content Marketing Context:
{marketing_guidance}

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
"""
    return prompt


def build_second_prompt(idea_content: str, context_content: str,
                        company_op_content: str, marketing_guidance: str,
                        selected: dict) -> str:
    """Re‑create the prompt used for the *second* LLM call."""
    voice_key = selected["voice"]
    voice_content = VOICE_DEFINITIONS.get(voice_key, "")

    system_prompt = (
        f"Reasoning: high "
        f"You are a content creator for Construkted Reality, tasked with writing a blog post. "
        f"Your writing style is that of a seasoned journalist at {voice_content}. "
        f"Content Marketing Context: {marketing_guidance}. "
        f"Extra context {context_content}. "
        f"Company operation details: {company_op_content}. Do **NOT** suggested ideas which do not align with company operation details."
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
    # In the real pipeline the system_prompt is sent separately; for token counting we
    # concatenate them as the LLM does.
    return system_prompt + "\n" + prompt


def main() -> None:
    parser = argparse.ArgumentParser(description="Check prompt sizes for the blog‑draft pipeline.")
    parser.add_argument("--idea-id", type=str, help="Process only the idea with this ID.")
    args = parser.parse_args()

    # Load ideas
    with open("blog_ideas.json", "r", encoding="utf-8") as f:
        ideas = json.load(f).get("ideas", [])

    if args.idea_id:
        ideas = [i for i in ideas if i.get("id") == args.idea_id]
        if not ideas:
            sys.stderr.write(f"No idea found with id '{args.idea_id}'.\n")
            sys.exit(1)

    if not ideas:
        sys.stderr.write("No ideas found in blog_ideas.json.\n")
        sys.exit(1)

    # Use the first (or only) idea for the sanity check
    idea = ideas[0]

    # Load static auxiliary files (same as the main script)
    context_content = read_file(Path("guidance/context.md"))
    titles_content = read_file(Path("guidance/crafting_compelling_titles.md"))
    company_op_content = read_file(Path("guidance/company_operation.md"))
    marketing_guidance_content = read_file(Path("guidance/content_marketing_guidance.md"))

    # ----------------------------------------------------------------------
    # First‑call prompt (URL list only)
    # ----------------------------------------------------------------------
    first_idea_content = build_idea_context(idea, for_first_call=True)
    first_prompt = build_first_prompt(
        first_idea_content,
        context_content,
        marketing_guidance_content,
        titles_content,
        processed_ideas=[],
    )
    first_char_len = len(first_prompt)
    first_token_est = estimate_tokens(first_prompt)

    print("=== First LLM Call (select_parameters) ===")
    print(f"Character count: {first_char_len}")
    print(f"Estimated tokens : {first_token_est}")
    limit = OPENAI_LIMIT if AI_PROVIDER == "openai" else OLLAMA_LIMIT
    print(f"Model token limit: {limit}")
    print("Status:", "OK" if first_token_est < limit else "EXCEEDS LIMIT")
    print()

    # ----------------------------------------------------------------------
    # Second‑call prompt (full excerpts)
    # ----------------------------------------------------------------------
    # For the second call we need a dummy “selected” dict – only fields that affect
    # the prompt length are used.
    dummy_selected = {
        "voice": "Wired",
        "title": "Placeholder Title",
        "piece_type": "tutorial",
        "primary_goal": "educate",
        "target_audience": "hobbyist",
        "technical_depth": "med",
        "length": "1500",
        "primary_seo_key_word": "placeholder",
        "secondary_seo_key_words": ["kw1", "kw2", "kw3"],
    }

    second_idea_content = build_idea_context(idea, for_first_call=False)
    second_prompt = build_second_prompt(
        second_idea_content,
        context_content,
        company_op_content,
        marketing_guidance_content,
        dummy_selected,
    )
    second_char_len = len(second_prompt)
    second_token_est = estimate_tokens(second_prompt)

    print("=== Second LLM Call (generate_blog_post) ===")
    print(f"Character count: {second_char_len}")
    print(f"Estimated tokens : {second_token_est}")
    print(f"Model token limit: {limit}")
    print("Status:", "OK" if second_token_est < limit else "EXCEEDS LIMIT")
    print()


if __name__ == "__main__":
    main()