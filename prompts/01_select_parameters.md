Analyze the following topic research and select the most appropriate writing parameters for content marketing.

**Context Summary**: You will be given: 1) batch diversity context, 2) voice definitions, 3) content marketing guidance, 4) topic research content, 5) title guidance, 6) detailed instructions and JSON schema.

**IMPORTANT**: Vary your parameter selections across different topics. Avoid selecting identical combinations unless truly warranted by the content. Consider how this topic differs from previous topics in the batch.
{batch_context}

Writing style descriptions:
New Yorker: {voice_new_yorker}
The Atlantic: {voice_atlantic}
Wired: {voice_wired}

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

Output ONLY the JSON object above with your selections.
