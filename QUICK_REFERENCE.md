# Quick Reference: Translation + Audiobook Pipeline

## 🎯 Complete Workflow (100% Free)

```bash
# Navigate to project
cd /Users/thanhpt6/Documents/personal/translation
source .venv/bin/activate

# Install dependencies (one-time)
pip install -r requirements.txt
pip install edge-tts

# 1. Crawl (resumes automatically)
END_CHAPTER=1348 python main.py crawl

# 2. Extract characters
python main.py extract-characters

# 3. Translate (FREE)
python main.py translate-local

# 4. Export markdown
python main.py export

# 5. Generate audiobook (FREE)
python main.py generate-audio

# Check results
ls -lh output/full_book_vietnamese.md
ls -lh data/audio/
```

---

## ⚡ Optimization Quick Fixes

### Translation Too Slow? (7 min/chapter)

**Option 1: Optimize Current Model**
- LM Studio → Settings → GPU Layers: Max
- Context Length: 4096 (not 8192)
- Batch Size: 512-1024
- **Result**: 7 min → 4-5 min

**Option 2: Switch to Faster Model (Recommended)**
- Download: `Qwen2.5-7B-Instruct-Q5_K_M`
- Load in LM Studio
- Start server
- No code changes needed!
- **Result**: 7 min → 2-3 min

**Option 3: Smallest Fast Model**
- Download: `Qwen2.5-3B-Instruct-Q4_K_M`
- **Result**: 7 min → 1-1.5 min

See `OPTIMIZATION_GUIDE.md` for details.

---

## 🎙️ Audiobook Quick Commands

### Generate with Default (FREE Edge TTS)
```bash
pip install edge-tts
python main.py generate-audio
```

### Test Different Voices
```bash
# List Vietnamese voices
edge-tts --list-voices | grep vi-VN

# Test a voice
edge-tts --voice vi-VN-HoaiMyNeural --text "Chào bạn" --write-media test.mp3
open test.mp3

# Female voice (default)
# vi-VN-HoaiMyNeural

# Male voice
# vi-VN-NamMinhNeural
```

### Change Voice
```bash
# In .env:
TTS_VOICE=vi-VN-NamMinhNeural

# Then generate
python main.py generate-audio
```

### Merge All Chapters
```bash
# Install ffmpeg
brew install ffmpeg

# In .env:
TTS_MERGE_CHAPTERS=true

# Generate
python main.py generate-audio

# Result
open output/audiobook_full.mp3
```

---

## 📊 Status Checks

### Check Translation Progress
```bash
python main.py status
```

### Count Chapters
```bash
# Crawled
ls -1 data/raw/chapters/ | wc -l

# Translated
ls -1 data/translated/chapters/ | wc -l

# Audio generated
ls -1 data/audio/ | wc -l
```

### View Latest Chapter
```bash
# Latest crawled
ls -t data/raw/chapters/ | head -1

# Latest translated
ls -t data/translated/chapters/ | head -1

# Latest audio
ls -t data/audio/ | head -1
```

---

## 🐛 Common Issues

### Edge TTS: "No module named 'edge_tts'"
```bash
pip install edge-tts
```

### Translation: Empty output
```bash
# Check LM Studio is running
curl http://localhost:1234/v1/models

# Restart LM Studio server
```

### Crawling: SSL error
```bash
# Already handled in code - just run again
python main.py crawl
```

### Audio: ffmpeg not found
```bash
brew install ffmpeg
```

### Out of memory during translation
```bash
# Switch to smaller model: Qwen2.5-7B or 3B
# In LM Studio: Load smaller model
# No code changes needed
```

---

## 📈 Time Estimates

| Task | Time (1348 chapters) |
|------|---------------------|
| Crawl | 40-50 minutes |
| Extract characters | 30 seconds |
| Translate (Qwen 7B) | 35-50 hours |
| Export markdown | 1 minute |
| Generate audio (Edge TTS) | 13-27 hours |
| **TOTAL** | **~2-3 days** |

**Cost: $0** ✨

---

## 🔥 Tips for Best Results

### 1. Run in Background
```bash
# Translation
nohup python main.py translate-local > translate.log 2>&1 &

# Audio generation
nohup python main.py generate-audio > audio.log 2>&1 &

# Check logs
tail -f translate.log
tail -f audio.log
```

### 2. Prevent Sleep (macOS)
```bash
# Keep Mac awake during processing
caffeinate -i python main.py translate-local
```

### 3. Monitor GPU Usage
```bash
# Check if LM Studio is using GPU
sudo powermetrics --samplers gpu_power -i 1000
```

### 4. Speed Priority
```bash
# Use smallest model + Edge TTS
# Total time: ~25-35 hours
```

### 5. Quality Priority
```bash
# Use Qwen2.5-32B + OpenAI TTS
# Total time: ~100-110 hours
# Cost: ~$60 for audio
```

---

## 📁 Important Files

### Configuration
- `.env` - Your settings
- `config.py` - Default settings

### Data
- `data/raw/chapters/` - Chinese original
- `data/translated/chapters/` - Vietnamese translation
- `data/glossary/characters.json` - Character names
- `data/audio/` - Audio files

### Output
- `output/full_book_vietnamese.md` - Complete book
- `output/audiobook_full.mp3` - Full audiobook (if merged)

### Logs
- `logs/translation.log` - Detailed logs

---

## 🎯 Recommended Settings

### For Speed (Fastest, Good Quality)
```env
# .env file
AI_MODEL=local-model  # Using LM Studio
TTS_PROVIDER=edge-tts
TTS_VOICE=vi-VN-HoaiMyNeural
TTS_MERGE_CHAPTERS=false
```

**LM Studio**: Use Qwen2.5-7B-Instruct-Q5_K_M

### For Quality (Best, Slower)
```env
# .env file
AI_MODEL=local-model  # Using LM Studio
TTS_PROVIDER=edge-tts
TTS_VOICE=vi-VN-HoaiMyNeural
TTS_MERGE_CHAPTERS=false
```

**LM Studio**: Use Qwen2.5-32B-Instruct-Q4_K_M with GPU optimization

---

## 📖 Documentation

- `README.md` - Project overview
- `LOCAL_LLM_SETUP.md` - Free translation setup
- `OPTIMIZATION_GUIDE.md` - Speed optimization
- `AUDIOBOOK_GUIDE.md` - Audio generation
- `AUDIOBOOK_SUMMARY.md` - Feature summary
- This file - Quick reference

---

## ✅ Checklist

- [ ] Installed all dependencies
- [ ] LM Studio running with Qwen model
- [ ] Crawled all 1348 chapters
- [ ] Extracted character glossary
- [ ] Reviewed character names in JSON
- [ ] Started translation (running in background)
- [ ] Exported markdown after translation
- [ ] Installed edge-tts
- [ ] Generated audiobook
- [ ] Enjoyed your free Vietnamese novel! 🎉

---

**Need help?** Check the detailed guides in the documentation files above.
