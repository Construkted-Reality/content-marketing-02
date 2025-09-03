# Implementation Plan: Fix Parameter Selection Diversity Issues

## Problem Summary
The blog draft generation script produces very similar parameters (all "Wired" voice, "tutorial" piece type, "Educational" marketing post type, etc.) across different blog ideas due to:
1. Triple content injection bug flooding the AI with repeated guidance
2. Structural bias toward educational/tutorial content
3. Missing diversity mechanisms
4. Poor prompt structure that doesn't encourage parameter variation

## Phase 1: Immediate Fixes (Critical Issues)

### 1. Fix Triple Content Injection Bug
**Problem**: Content marketing context appears 3 times in the prompt
**Solution**: Remove duplicate injections, keep only one strategically placed instance
**Code changes**:
- Remove the duplicate `Content Marketing Context: {content_marketing_guidance_content}` lines
- Keep one instance positioned after voice descriptions for balanced influence

### 2. Restructure Prompt Order for Better Decision Making
**Current order**: JSON format → Content context (3x) → Voice descriptions → Instructions
**New order**: Voice descriptions → Content context (1x) → Topic analysis → JSON format → Instructions
**Benefit**: Voices get equal consideration weight as content marketing guidance

### 3. Add Explicit Diversity Instructions
**Add to prompt**:
```
**IMPORTANT**: Vary your parameter selections across different topics. Avoid selecting identical combinations unless truly warranted by the content. Consider how this topic differs from previous topics in the batch.
```

### 4. Enhance Voice Selection Criteria
**Current**: Basic voice descriptions buried in prompt
**New**: Structured voice selection with topic-specific guidance:
- Technical troubleshooting → Wired (but not exclusively)
- Broader concepts → TheNewYorker 
- Policy/industry analysis → TheAtlantic
- Add explicit voice differentiation prompts

### 5. Fix Marketing Post Type Bias
**Problem**: Heavy emphasis on "Educational (TOFU)" 
**Solution**: Balance the options with equal weighting and clearer differentiation

## Phase 2: Parameter Diversity Mechanisms

### 1. Batch-Aware Selection
**Implementation**: Track previous selections within batch processing
**Mechanism**: Inject "previous selections" context into prompt for topics 2-5
```python
def get_batch_context(processed_ideas: list) -> str:
    if not processed_ideas:
        return ""
    selections = [idea.get('voice', ''), idea.get('piece_type', ''), ...]
    return f"Previous selections in this batch: {selections}. Aim for diversity unless content strongly suggests otherwise."
```

### 2. Topic Differentiation Logic
**Add topic analysis step**:
- Classify topic complexity (beginner vs advanced)
- Identify problem type (workflow vs technical vs equipment)
- Determine urgency level (critical vs optimization)
- Use these factors to influence parameter selection

### 3. Audience Refinement
**Current**: Basic audience categories
**Enhanced**: Add audience sophistication analysis:
- Beginner vs experienced users
- Budget constraints (startup vs enterprise)
- Use case complexity (simple scan vs complex project)

## Phase 3: Advanced Improvements

### 1. Dynamic Prompt Adjustment
**Smart prompting**: Adjust prompt emphasis based on:
- Topic similarity to previous processed items
- Content marketing funnel gaps (if all TOFU, suggest MOFU/BOFU)
- Voice distribution within batch

### 2. Content Clustering Analysis
**Pre-processing step**:
```python
def analyze_topic_clusters(ideas: list) -> dict:
    # Group similar topics
    # Identify differentiation opportunities
    # Suggest parameter diversity strategies
```

### 3. Quality Scoring System
**Add selection confidence scoring**:
- Rate how well parameters match content
- Flag when diversity is sacrificed for accuracy
- Provide feedback loop for prompt improvements

## Implementation Files to Modify

### Primary Changes: `generate_blog_drafts_from_ideas.py`
1. **select_parameters()** function
   - Fix prompt structure
   - Add diversity mechanisms
   - Enhance voice selection logic

2. **main()** function  
   - Add batch tracking
   - Implement topic clustering
   - Add selection history

### New Supporting Functions
```python
def get_batch_diversity_context(processed_selections: list) -> str
def analyze_topic_differentiation(topic1: dict, topic2: dict) -> dict
def enhance_voice_selection_prompt(topic_type: str) -> str
def validate_parameter_diversity(batch_selections: list) -> dict
```

## Testing Strategy

### 1. Immediate Testing
- Run same 5 topics with fixed prompt
- Verify parameter diversity increase
- Ensure quality doesn't degrade

### 2. Comprehensive Testing  
- Test with 20+ diverse topics
- Measure parameter distribution
- Validate content quality maintenance

### 3. Edge Case Testing
- All similar topics (should still vary some parameters)
- Very different topics (should show clear differentiation)
- Mixed technical levels

## Expected Outcomes

### Immediate Fixes (Phase 1)
- **Before**: 5/5 topics → identical parameters
- **After**: 5/5 topics → 3-4 different parameter combinations

### With Diversity Mechanisms (Phase 2)  
- **Target**: 80% parameter variation across batches
- **Quality**: Maintain or improve content relevance
- **Balance**: No single voice/type dominates unless warranted

### Advanced Implementation (Phase 3)
- **Smart selection**: Parameters optimally matched to content + diversity
- **Predictable variation**: Clear logic for why parameters differ
- **Scalability**: Works well with larger topic batches

## Progress Tracking

- [ ] Phase 1: Fix triple content injection bug
- [ ] Phase 1: Restructure prompt order
- [ ] Phase 1: Add explicit diversity instructions
- [ ] Phase 1: Enhance voice selection criteria
- [ ] Phase 1: Fix marketing post type bias
- [ ] Phase 2: Implement batch-aware selection
- [ ] Phase 2: Add topic differentiation logic
- [ ] Phase 2: Enhance audience refinement
- [ ] Phase 3: Dynamic prompt adjustment
- [ ] Phase 3: Content clustering analysis
- [ ] Phase 3: Quality scoring system
- [ ] Testing: Immediate fixes validation
- [ ] Testing: Comprehensive parameter distribution testing
- [ ] Testing: Edge case validation

## Implementation Priority
1. **Start with Phase 1** - Critical fixes that will immediately improve diversity
2. **Phase 2** - Add intelligence and batch awareness
3. **Phase 3** - Advanced features for optimal parameter selection

Last Updated: 2025-01-09
