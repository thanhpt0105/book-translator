# Audiobook Generation Guide

## Overview
Convert your translated Vietnamese text to natural storytelling audio using Text-to-Speech (TTS).

## TTS Providers Comparison

| Provider | Cost | Quality | Vietnamese Support | Speed | Recommendation |
|----------|------|---------|-------------------|-------|----------------|
| **Edge TTS** | FREE | Very Good | Excellent ✅ | Fast | **Best for free** |
| OpenAI TTS | $15/1M chars | Excellent | Good | Very Fast | Best paid option |
| ElevenLabs | $5-99/month | Outstanding | Good | Fast | Best quality |
| Google Cloud | $4/1M chars | Very Good | Excellent | Fast | Good alternative |

## Quick Start (Free with Edge TTS)

### 1. Install Dependencies
```bash
cd /Users/thanhpt6/Documents/personal/translation
source .venv/bin/activate
pip install edge-tts
```

### 2. Generate Audiobook
```bash
# Generate audio for all translated chapters
python main.py generate-audio
```

**Default settings:**
- Provider: Microsoft Edge TTS (FREE)
- Voice: `vi-VN-HoaiMyNeural` (Female Vietnamese narrator)
- Output: Separate MP3 file per chapter
- Location: `data/audio/chapter_XXXX/`

### 3. Output Structure
```
data/audio/
├── chapter_0001/
│   └── full_chapter.mp3
├── chapter_0002/
│   └── full_chapter.mp3
└── ...
```

---

## Available Vietnamese Voices (Edge TTS)

Test voices to find your favorite:

```bash
# List all Vietnamese voices
edge-tts --list-voices | grep vi-VN

# Test a voice
edge-tts --voice vi-VN-HoaiMyNeural --text "Xin chào, đây là giọng đọc truyện tiếng Việt" --write-media test.mp3
```

**Recommended Vietnamese voices:**
- `vi-VN-HoaiMyNeural` - Female, natural, warm (storytelling) ⭐
- `vi-VN-NamMinhNeural` - Male, deep, serious

---

## Configuration Options

Edit `.env` or `config.py`:

```bash
# TTS Settings
TTS_PROVIDER=edge-tts          # edge-tts, openai, elevenlabs, google
TTS_VOICE=vi-VN-HoaiMyNeural   # Voice ID
TTS_MERGE_CHAPTERS=false       # true = merge all into single file
```

### Merge All Chapters into Single Audiobook

To create one large audio file for the entire book:

```bash
# In .env file:
TTS_MERGE_CHAPTERS=true

# Then run:
python main.py generate-audio
```

**Output:** `output/audiobook_full.mp3`

**Note:** Requires `ffmpeg`:
```bash
brew install ffmpeg
```

---

## Advanced: Using Paid TTS Services

### OpenAI TTS (Excellent Quality)

**Cost:** ~$15 per million characters
- 1348 chapters × ~3000 chars/chapter = ~4M characters
- **Total cost: ~$60**

**Setup:**
```bash
# Install
pip install openai

# In .env:
OPENAI_API_KEY=your_key_here
TTS_PROVIDER=openai
TTS_VOICE=nova  # Voices: alloy, echo, fable, onyx, nova, shimmer

# Generate
python main.py generate-audio
```

**Voices:**
- `nova` - Female, expressive, great for storytelling ⭐
- `shimmer` - Female, warm, friendly
- `onyx` - Male, deep, narrator

### ElevenLabs (Best Quality)

**Cost:** $5-99/month subscription
- Professional plan: $99/month = unlimited characters
- Free tier: 10K characters/month

**Setup:**
```bash
# Install
pip install elevenlabs

# In .env:
ELEVENLABS_API_KEY=your_key_here
TTS_PROVIDER=elevenlabs
TTS_VOICE=21m00Tcm4TlvDq8ikWAM  # Rachel voice

# Generate
python main.py generate-audio
```

**Features:**
- Voice cloning capability
- Most natural-sounding TTS
- Good with Vietnamese (multilingual v2 model)

### Google Cloud TTS

**Cost:** ~$4 per million characters = **~$16 total**

**Setup:**
```bash
# Install
pip install google-cloud-texttospeech

# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# In .env:
TTS_PROVIDER=google
TTS_VOICE=vi-VN-Standard-A  # or vi-VN-Wavenet-A (better quality)

# Generate
python main.py generate-audio
```

---

## Performance Estimates

### Edge TTS (FREE)
- Speed: ~50-100 chapters/hour
- Total time: **13-27 hours** for 1348 chapters
- Cost: **$0**

### OpenAI TTS
- Speed: ~200-300 chapters/hour
- Total time: **4-7 hours**
- Cost: **~$60**

### ElevenLabs
- Speed: ~100-150 chapters/hour
- Total time: **9-14 hours**
- Cost: **$99/month** (cancel after first month)

---

## Customization

### Split by Paragraphs (More Control)

Edit `tts_generator.py` line ~150:
```python
audio_files = await tts.generate_chapter_audio(
    chapter, 
    split_paragraphs=True  # Generate separate audio per paragraph
)
```

**Output:**
```
chapter_0001/
├── 00_title.mp3
├── 001_paragraph.mp3
├── 002_paragraph.mp3
└── ...
```

### Adjust Speaking Rate/Pitch (Google TTS)

Edit `tts_generator.py` line ~135:
```python
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=1.1,  # 1.0 = normal, 1.2 = faster
    pitch=2.0,          # -20.0 to 20.0
)
```

### Adjust Speed (OpenAI TTS)

Edit `tts_generator.py` line ~100:
```python
response = self.openai_client.audio.speech.create(
    model="tts-1-hd",
    voice=self.voice,
    input=text,
    speed=1.1  # 0.25 to 4.0, 1.0 = normal
)
```

---

## Workflow Example

### Complete pipeline from crawl to audiobook:

```bash
# 1. Crawl all chapters (if not done)
END_CHAPTER=1348 python main.py crawl

# 2. Extract characters
python main.py extract-characters

# 3. Translate with local LLM
python main.py translate-local

# 4. Export to markdown
python main.py export

# 5. Generate audiobook
python main.py generate-audio

# Check output
ls -lh data/audio/
ls -lh output/audiobook_full.mp3  # If merged
```

---

## Troubleshooting

### Edge TTS: "No audio generated"
```bash
# Test connection
edge-tts --voice vi-VN-HoaiMyNeural --text "test" --write-media test.mp3

# If fails, check internet connection (Edge TTS requires online access)
```

### OpenAI TTS: Rate limits
```bash
# Add delay between chapters in tts_generator.py
import time
time.sleep(1)  # After each chapter
```

### Audio quality issues
- Edge TTS: Try different voices (vi-VN-NamMinhNeural)
- OpenAI: Use "tts-1-hd" model instead of "tts-1"
- Google: Use "Wavenet" voices instead of "Standard"

### Merge fails (ffmpeg error)
```bash
# Install ffmpeg
brew install ffmpeg

# Verify installation
ffmpeg -version
```

---

## Tips for Best Results

1. **Preview before full generation:**
   - Test with 1-2 chapters first
   - Try different voices
   - Adjust speed if needed

2. **Background processing:**
   ```bash
   nohup python main.py generate-audio > tts.log 2>&1 &
   ```

3. **Resume capability:**
   - Script automatically skips already-generated chapters
   - Safe to stop and restart

4. **Storage requirements:**
   - ~1-2 MB per chapter
   - Total: ~1.5-2.5 GB for 1348 chapters

5. **Quality vs Speed:**
   - Edge TTS: Best free option, good quality
   - OpenAI TTS-1-HD: Best paid quality/speed balance
   - ElevenLabs: Best absolute quality (but slower)

---

## Recommended: Start with Edge TTS

**Why:**
- Completely FREE
- Excellent Vietnamese voices
- Good quality for audiobooks
- Fast generation
- No API keys needed

**Upgrade to paid if:**
- You need even more natural voices (ElevenLabs)
- You want faster generation (OpenAI)
- You're willing to pay for convenience

**Command to start:**
```bash
pip install edge-tts
python main.py generate-audio
```

That's it! Your audiobook will be in `data/audio/` folder.
