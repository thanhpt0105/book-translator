# Chinese-to-Vietnamese Novel Translation System

A comprehensive system for crawling Chinese novels from web sources and translating them to Vietnamese using AI, with intelligent character name consistency management.

## Features

- **Web Crawler**: Automatically extracts chapters from Chinese novel websites
- **AI Translation**: Context-aware translation using GPT-4, Claude, or **Local LLM**
- **Character Consistency**: Maintains consistent character name translations across all chapters
- **Batch Processing**: Efficient processing of large novels with hundreds of chapters
- **Progress Tracking**: Resume capability for interrupted operations
- **Multiple Export Formats**: Markdown, JSON, and optional EPUB output
- **💰 Free Local LLM Support**: Translate unlimited chapters for $0 using LM Studio!
- **🎙️ Audiobook Generation**: Convert translated text to natural Vietnamese storytelling audio

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

### macOS/Linux

1. **Clone or navigate to this directory**

2. **Create virtual environment** (recommended)
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env and add your API keys if using cloud AI
   ```

5. **Test installation**
   ```bash
   python test_setup.py
   ```

### Windows

👉 **Quick Fix for "No module named 'loguru'" error: [WINDOWS_QUICK_START.md](WINDOWS_QUICK_START.md)**

👉 **Full setup guide: [WINDOWS_SETUP.md](WINDOWS_SETUP.md)**

**Quick setup (PowerShell):**
```powershell
# Run automated setup script
.\setup_windows.ps1

# OR manual setup:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python test_setup.py
```

**Common issue:** "No module named 'loguru'" after `pip install`
- **Cause:** `pip` and `python` using different Python installations
- **Solution:** Use virtual environment (run `setup_windows.ps1` script)



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

# 4a. Translate using local LLM (FREE, recommended!)
python main.py translate-local

# OR 4b. Translate using cloud AI (costs money)
python main.py translate

# 5. Export to readable format
python main.py export

# 6. Generate audiobook (FREE with Edge TTS!)
python main.py generate-audio

# Check status anytime
python main.py status
```

### Using Local LLM (FREE Translation!)

For **free unlimited translation** using LM Studio:

👉 **See detailed guide: [LOCAL_LLM_SETUP.md](LOCAL_LLM_SETUP.md)**

Quick start:
1. Install [LM Studio](https://lmstudio.ai/)
2. Download Qwen2.5 model (7B or 32B)
3. Start the local server
4. Run: `python main.py translate-local`

**Translation optimization:**
👉 **See speed optimization guide: [OPTIMIZATION_GUIDE.md](OPTIMIZATION_GUIDE.md)**

### Audiobook Generation (FREE!)

For **free Vietnamese audiobook** generation:

👉 **See detailed guide: [AUDIOBOOK_GUIDE.md](AUDIOBOOK_GUIDE.md)**

Quick start:
1. Install Edge TTS: `pip install edge-tts`
2. Run: `python main.py generate-audio`
3. Audio files saved to `data/audio/`

**Voice quality:**
- Free: Edge TTS (Microsoft) - Excellent Vietnamese voices
- Paid: OpenAI/ElevenLabs - Premium quality

**Cost comparison:**
- GPT-4o: ~$500-700 for 1348 chapters
- Local LLM: **$0** ✨

### Individual Commands

- **`python main.py crawl`** - Download all chapters from the website
- **`python main.py extract-characters`** - Build character name database
- **`python main.py translate`** - Translate chapters using cloud AI (OpenAI/Anthropic)
- **`python main.py translate-local`** - Translate using local LLM (FREE)
- **`python main.py export`** - Generate markdown output file
- **`python main.py generate-audio`** - Convert to audiobook (Vietnamese narrator)
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

**Using GPT-4o:**
- ~$0.40-0.50 per chapter
- For 1348 chapters: ~$500-700

**Using Claude 3.5 Sonnet:**
- ~$0.10-0.15 per chapter
- For 1348 chapters: ~$135-200

**Using Local LLM (LM Studio):**
- ~$0 per chapter ✨
- For 1348 chapters: **FREE**
- See [LOCAL_LLM_SETUP.md](LOCAL_LLM_SETUP.md) for setup guide

**Audiobook Generation:**
- **Edge TTS**: FREE (Microsoft) - Excellent Vietnamese voices ✨
- **OpenAI TTS**: ~$60 for full book
- **ElevenLabs**: $99/month (best quality)
- See [AUDIOBOOK_GUIDE.md](AUDIOBOOK_GUIDE.md) for details

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
