# Audiobook Feature Summary

## ✅ What's Been Added

### 1. New Module: `tts_generator.py`
Complete Text-to-Speech system supporting multiple providers:
- **Edge TTS** (FREE) - Microsoft's Vietnamese voices
- **OpenAI TTS** (Paid) - Premium quality
- **ElevenLabs** (Paid) - Best quality
- **Google Cloud TTS** (Paid) - Alternative

### 2. New Command: `generate-audio`
```bash
python main.py generate-audio
```

Generates natural storytelling audio from Vietnamese translations.

### 3. Configuration Updates
New settings in `config.py`:
```python
tts_provider: str = "edge-tts"
tts_voice: str = "vi-VN-HoaiMyNeural"
tts_merge_chapters: bool = False
```

### 4. Documentation
- **AUDIOBOOK_GUIDE.md** - Complete audiobook generation guide
- Updated README.md with audiobook features
- Updated requirements.txt with TTS dependencies

---

## 🎯 Recommended Workflow

### Complete Pipeline (Crawl → Translate → Audiobook)

```bash
# 1. Crawl all chapters
END_CHAPTER=1348 python main.py crawl

# 2. Extract characters
python main.py extract-characters

# 3. Translate (FREE with local LLM)
python main.py translate-local

# 4. Export to markdown
python main.py export

# 5. Generate audiobook (FREE with Edge TTS)
pip install edge-tts
python main.py generate-audio
```

---

## 🎙️ TTS Provider Comparison

| Provider | Cost | Setup | Quality | Speed |
|----------|------|-------|---------|-------|
| **Edge TTS** ⭐ | FREE | `pip install edge-tts` | Very Good | Fast |
| OpenAI TTS | ~$60 | API key needed | Excellent | Very Fast |
| ElevenLabs | $99/mo | API key + subscription | Outstanding | Fast |
| Google Cloud | ~$16 | Credentials JSON | Very Good | Fast |

**Recommendation: Start with Edge TTS (FREE)**

---

## 📊 Output Structure

```
data/audio/
├── chapter_0001/
│   └── full_chapter.mp3
├── chapter_0002/
│   └── full_chapter.mp3
├── chapter_0003/
│   └── full_chapter.mp3
└── ...

output/
├── full_book_vietnamese.md
└── audiobook_full.mp3  # If merged
```

---

## ⚡ Performance Estimates

### Edge TTS (FREE)
- **Speed**: 50-100 chapters/hour
- **Time for 1348 chapters**: 13-27 hours
- **Cost**: $0
- **Storage**: ~1.5-2.5 GB

### OpenAI TTS
- **Speed**: 200-300 chapters/hour
- **Time for 1348 chapters**: 4-7 hours
- **Cost**: ~$60
- **Storage**: ~1.5-2.5 GB

---

## 🔧 How It Works

### Architecture
```
Translated Chapter (JSON)
    ↓
TTSGenerator.generate_chapter_audio()
    ↓
Edge TTS API / OpenAI API / etc.
    ↓
MP3 Audio File
```

### Features
✅ **Resume capability** - Skips already-generated chapters
✅ **Natural voices** - Vietnamese storytelling narrators
✅ **Chapter merging** - Optional single-file audiobook
✅ **Paragraph splitting** - Better control over audio segments
✅ **Multiple voices** - Choose male/female narrators

---

## 🎯 Next Steps

### For Free Audiobook (Recommended)
```bash
# Install dependency
pip install edge-tts

# Test a single chapter translation first
python main.py translate-local

# Generate audio
python main.py generate-audio

# Listen to result
open data/audio/chapter_0001/full_chapter.mp3
```

### For Premium Quality
```bash
# Use OpenAI TTS
pip install openai

# In .env:
OPENAI_API_KEY=your_key
TTS_PROVIDER=openai
TTS_VOICE=nova

# Generate
python main.py generate-audio
```

---

## 💡 Tips

1. **Test voices first:**
   ```bash
   edge-tts --list-voices | grep vi-VN
   edge-tts --voice vi-VN-HoaiMyNeural --text "Xin chào" --write-media test.mp3
   ```

2. **Merge all chapters into one file:**
   ```bash
   # In .env:
   TTS_MERGE_CHAPTERS=true
   
   # Requires ffmpeg:
   brew install ffmpeg
   ```

3. **Run in background:**
   ```bash
   nohup python main.py generate-audio > tts.log 2>&1 &
   ```

4. **Check progress:**
   ```bash
   ls -1 data/audio/ | wc -l  # Count completed chapters
   ```

---

## 🚀 Complete Example: Zero to Audiobook

```bash
# Setup
cd /Users/thanhpt6/Documents/personal/translation
source .venv/bin/activate
pip install -r requirements.txt
pip install edge-tts

# Workflow
END_CHAPTER=1348 python main.py crawl           # ~40-50 min
python main.py extract-characters                # ~30 sec
python main.py translate-local                   # ~35-50 hours with Qwen2.5-7B
python main.py export                            # ~1 min
python main.py generate-audio                    # ~13-27 hours with Edge TTS

# Result
open output/full_book_vietnamese.md
open data/audio/chapter_0001/full_chapter.mp3
```

**Total time**: ~2-3 days of background processing
**Total cost**: **$0** ✨

---

## 📚 Documentation Files

1. **AUDIOBOOK_GUIDE.md** - Complete TTS setup and usage
2. **OPTIMIZATION_GUIDE.md** - Speed up translation
3. **LOCAL_LLM_SETUP.md** - Free translation setup
4. **README.md** - Updated with audiobook features

All documentation is ready to use!
