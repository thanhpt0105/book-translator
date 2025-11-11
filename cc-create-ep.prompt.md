# Chinese-to-Vietnamese Book Translation System - Implementation Proposal

## Project Overview

This system will crawl a multi-chapter Chinese novel from ixdzs.tw and translate it to Vietnamese using AI, maintaining character consistency and narrative context throughout.

**Target Website**: https://ixdzs.tw/read/273426/
**Sample Chapter**: https://ixdzs.tw/read/273426/p1211.html (Chapter 1212)

---

## System Architecture

### 1. Web Crawler Module
**Purpose**: Extract chapter content from the Chinese novel website

**Key Features**:
- Incremental crawling with chapter navigation detection
- Robust error handling and retry mechanism
- Rate limiting to respect website resources
- Content extraction (chapter title, body text, metadata)
- Progress tracking and resumable crawling

**Technical Approach**:
- Use `requests` + `BeautifulSoup4` or `Scrapy` for web scraping
- Extract chapter navigation links (next/previous)
- Parse chapter structure: title, content, chapter number
- Save raw Chinese content to structured format (JSON/Markdown)

**Chapter URL Pattern Analysis**:
```
Base URL: https://ixdzs.tw/read/273426/
Chapter pattern: /read/273426/p{chapter_number}.html
Navigation: Links contain "上一章" (previous) and "下一章" (next)
```

---

### 2. Translation Module
**Purpose**: Translate Chinese text to Vietnamese with context awareness

**Key Features**:
- Context-aware translation using AI (GPT-4, Claude, or similar)
- Character name consistency tracking
- Glossary management for recurring terms
- Batch processing with context windows
- Quality assurance and post-editing support

**Context Management Strategy**:

1. **Character Registry**:
   - Extract and maintain a glossary of character names
   - Ensure consistent translation across all chapters
   - Store name mappings: Chinese → Vietnamese

2. **Translation with Context**:
   - Include previous chapter summary or character list in prompts
   - Use sliding context window (e.g., previous 2 paragraphs)
   - Maintain narrative consistency

3. **AI Prompt Structure**:
   ```
   System: You are a professional Chinese-to-Vietnamese translator specializing in novels.
   
   Context:
   - Character glossary: {name_mappings}
   - Previous context: {recent_context}
   
   Task: Translate the following Chinese text to Vietnamese, maintaining:
   - Character name consistency
   - Narrative tone and style
   - Cultural nuances
   
   Text to translate: {chunk}
   ```

**Recommended AI Services**:
- OpenAI GPT-4 (via API)
- Anthropic Claude (via API)
- Google Gemini Pro
- Local LLM option: Qwen 2.5 (Chinese-specialized model)

---

### 3. Storage & Data Management
**Purpose**: Organize crawled and translated content

**Data Structure**:
```
translation/
├── data/
│   ├── raw/                 # Original Chinese text
│   │   ├── metadata.json    # Book info, total chapters
│   │   └── chapters/
│   │       ├── chapter_0001.json
│   │       ├── chapter_0002.json
│   │       └── ...
│   ├── translated/          # Vietnamese translations
│   │   └── chapters/
│   │       ├── chapter_0001.json
│   │       └── ...
│   └── glossary/
│       ├── characters.json  # Character name mappings
│       └── terms.json       # Recurring terms/phrases
├── output/
│   ├── full_book_chinese.md
│   ├── full_book_vietnamese.md
│   └── full_book_vietnamese.epub (optional)
```

**JSON Schema for Chapters**:
```json
{
  "chapter_number": 1212,
  "title_chinese": "第1212章 我們不是兇手！",
  "title_vietnamese": "Chương 1212: Chúng tôi không phải là kẻ giết người!",
  "content_chinese": "...",
  "content_vietnamese": "...",
  "metadata": {
    "crawled_at": "2025-11-11T10:00:00Z",
    "translated_at": "2025-11-11T11:00:00Z",
    "word_count": 2500,
    "url": "https://ixdzs.tw/read/273426/p1211.html"
  }
}
```

---

### 4. Character Consistency Engine
**Purpose**: Track and maintain consistent character translations

**Implementation**:

1. **Character Name Extraction**:
   - Use NER (Named Entity Recognition) for Chinese text
   - Extract recurring character names
   - Build initial glossary from first 5-10 chapters

2. **Translation Consistency**:
   - Maintain a `characters.json` mapping file
   - Pre-translate character names before chapter translation
   - Validate translations against glossary
   - Allow manual review and corrections

3. **Example Glossary Entry**:
```json
{
  "characters": [
    {
      "chinese": "葉陽",
      "vietnamese": "Diệp Dương",
      "pinyin": "Yè Yáng",
      "role": "protagonist",
      "first_appearance": 1
    },
    {
      "chinese": "陶興旺",
      "vietnamese": "Đào Hưng Vượng",
      "pinyin": "Táo Xīngwàng",
      "role": "supporting",
      "first_appearance": 1212
    }
  ]
}
```

---

## Implementation Phases

### Phase 1: Setup & Infrastructure (2-3 days)
- [ ] Project structure setup
- [ ] Install dependencies (requests, beautifulsoup4, openai, etc.)
- [ ] Configuration file for API keys, URLs, settings
- [ ] Database/file storage setup

### Phase 2: Web Crawler Development (3-4 days)
- [ ] Implement chapter discovery and navigation
- [ ] Content extraction and parsing
- [ ] Save raw Chinese content
- [ ] Error handling and logging
- [ ] Test with first 10 chapters

### Phase 3: Character Extraction & Glossary (2-3 days)
- [ ] Implement NER for character name extraction
- [ ] Build initial character glossary
- [ ] Manual review interface for name mappings
- [ ] Consistency validation system

### Phase 4: Translation Engine (4-5 days)
- [ ] AI API integration (OpenAI/Claude)
- [ ] Context-aware translation prompts
- [ ] Character name substitution
- [ ] Batch processing pipeline
- [ ] Quality checks and validation

### Phase 5: Testing & Quality Assurance (3-4 days)
- [ ] Translate sample chapters
- [ ] Human review of quality
- [ ] Refine prompts and glossary
- [ ] Performance optimization

### Phase 6: Full Deployment & Monitoring (Ongoing)
- [ ] Crawl all chapters
- [ ] Translate all content
- [ ] Generate final output formats
- [ ] Review and corrections

---

## Technology Stack

### Core Dependencies
```
Python 3.10+
├── Web Scraping
│   ├── requests
│   ├── beautifulsoup4
│   └── lxml
├── AI Translation
│   ├── openai (GPT-4 API)
│   ├── anthropic (Claude API)
│   └── tiktoken (token counting)
├── NLP Processing
│   ├── jieba (Chinese text segmentation)
│   └── spacy (optional, for NER)
├── Data Management
│   ├── pydantic (data validation)
│   └── sqlite3 / json (storage)
└── Utilities
    ├── tqdm (progress bars)
    ├── python-dotenv (config)
    └── loguru (logging)
```

---

## Configuration File Structure

**`.env` file**:
```env
# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Crawler Settings
BASE_URL=https://ixdzs.tw/read/273426/
START_CHAPTER=1
END_CHAPTER=auto  # or specific number
CRAWL_DELAY=2  # seconds between requests

# Translation Settings
AI_MODEL=gpt-4-turbo-preview
MAX_TOKENS_PER_REQUEST=4000
TRANSLATION_BATCH_SIZE=5
CONTEXT_WINDOW_PARAGRAPHS=3

# Storage
OUTPUT_FORMAT=json,markdown,epub
```

---

## Cost Estimation

### AI Translation Costs (OpenAI GPT-4)
- Average chapter: ~2,500 Chinese characters
- Estimated tokens: ~4,000 input + 4,000 output = 8,000 tokens/chapter
- GPT-4 Turbo pricing: $0.01/1K input, $0.03/1K output
- Cost per chapter: ~$0.16
- **Total for 1000 chapters: ~$160**

### Alternative: Claude 3 Sonnet
- Similar token usage
- Pricing: $3/$15 per million tokens (in/out)
- Cost per chapter: ~$0.07
- **Total for 1000 chapters: ~$70**

---

## Quality Assurance Strategy

1. **Translation Quality**:
   - Spot-check every 10th chapter
   - Human review for first 20 chapters
   - Feedback loop for prompt improvement

2. **Consistency Checks**:
   - Automated character name validation
   - Cross-chapter terminology consistency
   - Narrative flow assessment

3. **Post-Processing**:
   - Proofreading interface
   - Correction tracking
   - Version control for translations

---

## Risk Mitigation

| Risk | Mitigation Strategy |
|------|-------------------|
| Website blocking crawler | Rate limiting, user-agent rotation, respectful crawling |
| API rate limits/costs | Batch processing, caching, budget monitoring |
| Translation quality | Human review, feedback loops, prompt refinement |
| Character name inconsistency | Automated validation, glossary management |
| Data loss | Incremental saves, version control, backups |

---

## Success Metrics

- **Crawling**: Successfully extract 100% of chapters
- **Translation**: Maintain 95%+ character name consistency
- **Quality**: Human review scores >4/5 for readability
- **Efficiency**: Process 50+ chapters/day
- **Cost**: Stay within budget estimate

---

## Next Steps

1. **Approve this proposal** and confirm AI service preference
2. **Set up development environment** with required dependencies
3. **Implement crawler prototype** and test with first 10 chapters
4. **Build character glossary** from initial chapters
5. **Test translation pipeline** with sample content
6. **Iterate and refine** based on quality review

---

## Timeline Estimate

- **Total Duration**: 15-20 working days
- **Part-time effort (2-3 hours/day)**: 6-8 weeks
- **Full-time effort**: 3-4 weeks

---

## Questions to Address

1. **AI Service Preference**: OpenAI GPT-4, Claude, or local LLM?
2. **Budget**: What's the maximum acceptable cost for translation?
3. **Output Format**: Markdown, EPUB, PDF, or web format?
4. **Quality vs Speed**: Prioritize translation quality or faster completion?
5. **Manual Review**: How much human review is feasible?

---

*End of Proposal*
