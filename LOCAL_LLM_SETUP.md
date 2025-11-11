# Local LLM Translation Setup Guide

## Using LM Studio for Free Translation

### Step 1: Install LM Studio

1. Download from: https://lmstudio.ai/
2. Install and launch LM Studio

### Step 2: Download a Model

**Recommended models** (choose based on your hardware):

| Model | RAM Required | Quality | Download in LM Studio |
|-------|-------------|---------|---------------------|
| **Qwen2.5-32B-Instruct-Q4_K_M** | 20GB | Excellent | ⭐ Recommended |
| Qwen2.5-14B-Instruct-Q4_K_M | 10GB | Very Good | For lower-end systems |
| Qwen2.5-72B-Instruct-Q4_K_M | 48GB | Best | For high-end systems |

**How to download:**
1. Click the **"Search"** icon in LM Studio
2. Search for: `Qwen2.5-32B-Instruct`
3. Find the GGUF version
4. Download the **Q4_K_M** quantization (best balance of quality/speed)

### Step 3: Start Local Server

1. Click the **"Local Server"** tab in LM Studio
2. Select your downloaded Qwen model from the dropdown
3. **Configure settings**:
   - Context Length: 8192 or higher
   - GPU Offload: Max (if you have GPU)
4. Click **"Start Server"**
5. Server will start at: `http://localhost:1234`

### Step 4: Test the Connection

Run this test script:

```bash
python -c "
import requests
response = requests.post(
    'http://localhost:1234/v1/chat/completions',
    json={
        'model': 'local-model',
        'messages': [{'role': 'user', 'content': '你好'}],
        'temperature': 0.3
    }
)
print('Status:', response.status_code)
print('Response:', response.json()['choices'][0]['message']['content'])
"
```

If you see a response, it's working! ✅

### Step 5: Run Translation

```bash
# Translate using local LLM
python main.py translate-local
```

That's it! The translation will now use your local LLM.

## Performance Tips

### 1. Speed Optimization

In LM Studio settings:
- **GPU Layers**: Set to maximum if you have a GPU
- **Batch Size**: Increase to 512 or 1024
- **Threads**: Match your CPU cores

### 2. Quality Optimization

- Use **temperature: 0.3** for consistent translations
- For better quality: Use the 32B or 72B model
- For speed: Use the 14B model

### 3. Cost Comparison

| Method | Cost for 1000 chapters |
|--------|----------------------|
| GPT-4o | ~$500-700 💸 |
| GPT-4o-mini | ~$70-100 |
| Claude 3.5 | ~$100-150 |
| **Local LLM** | **$0 (FREE!)** ⭐ |

### 4. Translation Speed

With local LLM:
- **Qwen2.5-14B** on GPU: ~10-15 seconds/chapter
- **Qwen2.5-32B** on GPU: ~20-30 seconds/chapter
- **Qwen2.5-32B** on CPU: ~60-120 seconds/chapter

For 1000 chapters: **3-10 hours total** (vs 8-17 hours with GPT-4o)

## Troubleshooting

### "Connection refused" error

Make sure LM Studio server is running:
1. Open LM Studio
2. Go to "Local Server" tab
3. Ensure server is started (green indicator)

### "Model not found" error

The model name doesn't matter for LM Studio - it uses whatever model you selected in the UI.

### Slow translations

1. **Enable GPU acceleration** in LM Studio settings
2. Reduce context length to 4096
3. Use a smaller model (14B instead of 32B)

### Out of memory errors

1. Use a smaller quantization (Q4 → Q3)
2. Use a smaller model (32B → 14B)
3. Reduce context length
4. Close other applications

## Alternative: Ollama

If you prefer Ollama instead of LM Studio:

```bash
# Install Ollama
brew install ollama

# Download model
ollama pull qwen2.5:32b

# Start server (runs automatically)
ollama serve

# Update base URL in code to:
# http://localhost:11434/v1
```

## Monitoring Progress

```bash
# Check translation status
python main.py status

# Monitor in real-time
tail -f logs/translation.log

# Count completed chapters
ls data/translated/chapters/ | wc -l
```

## Quality Check

After translating a few chapters:

```bash
# Export to check quality
python main.py export

# Review the output
cat output/full_book_vietnamese.md
```

If quality is not good, try:
1. Using a larger model (32B or 72B)
2. Adjusting the system prompt
3. Adding more character names to the glossary

---

**Recommended Setup for 1348 Chapters:**

1. ✅ Use **Qwen2.5-32B-Q4_K_M** model
2. ✅ Enable GPU acceleration if available
3. ✅ Run overnight (will take 6-10 hours)
4. ✅ Total cost: **$0** 🎉

Enjoy unlimited free translation!
