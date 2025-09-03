# System Patterns: Blog Post Generation System

## System Architecture
The system has evolved into a comprehensive blog post generation pipeline with advanced parameter diversity mechanisms:

1. **Data Source Layer**: JSON-based blog idea storage (blog_ideas.json) with 80+ structured ideas
2. **Processing Layer**: generate_blog_drafts_from_ideas.py orchestrates the entire workflow with batch-aware selection
3. **API Integration Layer**: Two-stage OLLAMA API workflow with optimized prompt engineering
4. **Parameter Selection Layer**: Intelligent diversity-aware parameter selection system
5. **Content Generation Layer**: Structured blog post creation with diverse parameters and metadata
6. **Storage Layer**: Markdown file output with JSON database updates
7. **Configuration Layer**: Supporting files for prompts and guidance

## Key Technical Decisions
- **JSON-First Architecture**: Single source of truth for all blog ideas with rich metadata
- **Two-Stage API Processing**: Separate parameter selection and content generation for quality
- **Batch-Aware Selection**: System tracks previous selections to encourage parameter diversity
- **Prompt Engineering**: Strategic ordering of content to balance AI decision-making influences
- **ID-Based File Naming**: Uses idea ID + title for clear traceability and conflict prevention
- **Dynamic Field Population**: API responses automatically populate JSON metadata fields
- **Incremental Processing**: Testing limits allow safe validation before full production runs
- **Error Handling**: Comprehensive error handling with graceful degradation

## Design Patterns Used
- **Pipeline Pattern**: Sequential processing through parameter selection → content generation → storage
- **Template Method Pattern**: Consistent API call structure with customizable prompts
- **Observer Pattern**: JSON database updates notify about processing progress
- **Strategy Pattern**: Different voice and content type strategies based on API responses and batch context
- **Factory Pattern**: Dynamic file naming and path generation
- **Memento Pattern**: Batch context tracking for diversity-aware selection
- **Command Pattern**: Structured parameter selection with explicit diversity instructions

## Component Relationships
- **02_generate_blog_drafts.py** reads from blog_ideas.json and writes to blog_post_drafts/
- **get_batch_diversity_context()** tracks previous selections and generates diversity context
- **select_parameters()** uses batch context for intelligent parameter selection
- **OLLAMA API** provides AI-powered content generation with optimized prompts
- **Supporting Files** (context.md, crafting_compelling_titles.md, etc.) provide prompt context
- **JSON Database** maintains state and metadata for all blog ideas
- **Output Files** are markdown with embedded metadata for publishing workflows
- **implementation_plan.md** documents systematic improvement approach

## Critical Implementation Paths
1. **JSON Loading** → Idea Selection → Batch Context Generation → API Parameter Selection → JSON Update
2. **Parameter Diversity** → Previous Selection Tracking → Context Injection → Diverse Selection
3. **Content Generation** → API Content Creation → File Writing → JSON Path Update
4. **Error Handling** → Validation → Logging → Graceful Recovery
5. **File Management** → Naming Convention → Directory Creation → Collision Handling

## Data Flow
1. **Input**: blog_ideas.json loaded with 80 structured blog post ideas
2. **Selection**: Ideas processed sequentially with batch tracking (currently first 5 for testing)
3. **Batch Context**: Previous selections analyzed for diversity context generation
4. **Stage 1 API**: Parameter selection with diversity-aware prompting (voice, piece_type, marketing_post_type, etc.)
5. **JSON Update**: Selected parameters written back to JSON database
6. **Batch Tracking**: Current idea added to processed list for future diversity context
7. **Stage 2 API**: Full blog post content generation using selected parameters
8. **File Output**: Markdown files created in blog_post_drafts/ with ID+title naming
9. **Final Update**: Article paths written back to JSON database for tracking

## Integration Points
- **OLLAMA API**: External AI service for content generation with optimized prompts
- **File System**: Markdown output files for publishing workflows
- **JSON Database**: Persistent storage for idea tracking and metadata
- **Configuration Files**: Prompt templates and guidance documents
- **Batch Processing**: In-memory tracking of selections for diversity
- **Future Integrations**: Publishing platforms, CMS systems, analytics tools

## Quality Assurance Patterns
- **Two-Stage Validation**: Parameter selection validates before content generation
- **Parameter Diversity Metrics**: Measuring variation across all parameter categories
- **Field Verification**: Script expectations match JSON structure perfectly
- **Testing Limits**: Conservative processing limits for validation
- **Error Recovery**: Graceful handling of API failures and file system issues
- **Data Integrity**: JSON updates maintain consistency and prevent corruption
- **Prompt Structure Validation**: Ensuring balanced influence of different prompt elements

## Parameter Diversity Architecture
- **Batch Context Tracking**: `processed_ideas` list maintains selection history
- **Diversity Context Generation**: `get_batch_diversity_context()` creates awareness prompts
- **Strategic Prompt Ordering**: Voice descriptions before content guidance for balanced influence
- **Explicit Diversity Instructions**: Clear guidance for parameter variation
- **Content Marketing Balance**: Encourages variation across TOFU/MOFU/BOFU funnel positions
- **Voice Selection Logic**: Enhanced criteria for appropriate voice matching based on content type

## Performance Metrics
- **Voice Diversity**: Achieved 60% variation (improved from 0%)
- **Marketing Post Types**: Achieved 60% variation (improved from 0%)
- **Primary Goals**: Achieved 60% variation (improved from 0%)
- **Piece Types**: Achieved 80% variation
- **Overall Parameter Diversity**: Increased from ~20% to ~60% while maintaining content quality
