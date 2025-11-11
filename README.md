# Chinese-to-Vietnamese Novel Translation System

A comprehensive system for crawling Chinese novels from web sources and translating them to Vietnamese using AI, with intelligent character name consistency management.

## Features

- **Web Crawler**: Automatically extracts chapters from Chinese novel websites
- **AI Translation**: Context-aware translation using GPT-4 or Claude
- **Character Consistency**: Maintains consistent character name translations across all chapters
- **Batch Processing**: Efficient processing of large novels with hundreds of chapters
- **Progress Tracking**: Resume capability for interrupted operations
- **Multiple Export Formats**: Markdown, JSON, and optional EPUB output

## Project Structure

```
translation/
├── main.py                   # CLI entry point
├── config.py                 # Configuration management
├── models.py                 # Data models
├── crawler.py                # Web crawler
├── translator.py             # AI translation engine
├── character_extractor.py    # Character name extraction
├── requirements.txt          # Python dependencies
├── .env                      # Configuration (create from .env.example)
├── data/                     # Data storage
│   ├── raw/chapters/         # Original Chinese chapters
│   ├── translated/chapters/  # Translated Vietnamese chapters
│   └── glossary/             # Character name glossary
├── output/                   # Final output files
└── logs/                     # Application logs
```

## Installation

1. **Clone or navigate to this directory**

2. **Create virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

## Configuration

Edit `.env` file with your settings:

```env
# Required: API key for AI translation
OPENAI_API_KEY=sk-your-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Choose AI provider
AI_PROVIDER=openai  # or "anthropic"
AI_MODEL=gpt-4-turbo-preview  # or "claude-3-sonnet-20240229"

# Crawler settings
BASE_URL=https://ixdzs.tw/read/273426/
START_CHAPTER=1
END_CHAPTER=auto
CRAWL_DELAY=2.0
```

## Usage

### Complete Workflow

```bash
# 1. Crawl chapters from website
python main.py crawl

# 2. Extract character names and build glossary
python main.py extract-characters

# 3. Review and edit the glossary (optional but recommended)
#    Edit: data/glossary/characters.json
#    Add Vietnamese translations for character names

# 4. Translate all chapters
python main.py translate

# 5. Export to readable format
python main.py export

# Check status anytime
python main.py status
```

### Individual Commands

- **`python main.py crawl`** - Download all chapters from the website
- **`python main.py extract-characters`** - Build character name database
- **`python main.py translate`** - Translate chapters to Vietnamese
- **`python main.py export`** - Generate final output files
- **`python main.py status`** - Show progress statistics

## Character Glossary

The system automatically extracts character names and builds a glossary in `data/glossary/characters.json`:

```json
{
  "characters": [
    {
      "chinese": "葉陽",
      "vietnamese": "Diệp Dương",
      "role": "protagonist",
      "first_appearance": 1
    }
  ]
}
```

You can manually edit this file to:
- Correct Vietnamese name translations
- Add character descriptions
- Mark important characters

## Cost Estimation

**Using GPT-4 Turbo:**
- ~$0.16 per chapter
- For 1000 chapters: ~$160

**Using Claude 3 Sonnet:**
- ~$0.07 per chapter
- For 1000 chapters: ~$70

## Output Files

After running `export`, you'll find:
- `output/full_book_vietnamese.md` - Complete translated book in Markdown
- Each chapter also saved individually in `data/translated/chapters/`

## Troubleshooting

**Import errors when running:**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

**Crawler can't find chapters:**
- Check the BASE_URL in .env
- Verify the website is accessible
- Adjust CRAWL_DELAY if getting rate limited

**Translation quality issues:**
- Review and improve character glossary
- Try different AI models
- Adjust TEMPERATURE in .env (lower = more consistent)

## Advanced Configuration

See `config.py` for all available settings including:
- Context window size
- Batch processing size
- Token limits
- Output formats

## License

This tool is for personal educational use. Respect copyright laws when translating published works.

## Contributing

Contributions welcome! Key areas:
- Better character name extraction
- Additional export formats (EPUB, PDF)
- Translation quality improvements
- Support for more novel websites
