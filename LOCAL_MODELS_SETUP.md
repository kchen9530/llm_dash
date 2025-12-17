# 📦 Local Models Directory Setup

## ✅ What Changed

You asked for models to be stored **locally under project root** instead of system cache. Done!

### Key Changes:

1. **Local Model Storage**: `llm-dash/models/`
   - `models/chat/` - Chat/LLM models
   - `models/embeddings/` - Embedding models
   - All downloads go here automatically

2. **HuggingFace Cache Redirect**:
   - `HF_HOME` → `llm-dash/models/`
   - `TRANSFORMERS_CACHE` → `llm-dash/models/`
   - No more polluting `~/.cache/huggingface/`

3. **Recommended Models API**:
   - New endpoint: `/api/recommendations/models`
   - Returns curated lists for 8GB RAM
   - Separated chat vs embedding models

4. **Deploy Page Enhancements**:
   - Two tabs: "Chat Models" and "Embedding Models"
   - Shows size, RAM, speed, quality ratings
   - All models optimized for 8GB RAM

5. **Smart Model Detection**:
   - Auto-detects embedding models
   - Filters them out of Chat dropdown
   - Shows only chat models for chat
   - Shows only embedding models for photo search

6. **Photo Search Integration**:
   - Uses deployed embedding models
   - No need to download separately
   - Reuses already-loaded models

---

## 🚀 How It Works Now

### 1. Deploy Chat Model (for Chat tab)

```
Go to: http://localhost:5173/deploy
Tab: Chat Models
Select: gpt2 (recommended)
Click: Deploy Model

Result:
- Downloads to: llm-dash/models/models--gpt2/
- Loads into memory
- Available in Chat tab
```

### 2. Deploy Embedding Model (for Photo Search tab)

```
Go to: http://localhost:5173/deploy
Tab: Embedding Models
Select: sentence-transformers/all-MiniLM-L6-v2
Click: Deploy Model

Result:
- Downloads to: llm-dash/models/models--sentence-transformers--all-MiniLM-L6-v2/
- Loads into memory
- NOT shown in Chat tab (it only outputs vectors)
- Used automatically in Photo Search tab
```

### 3. Use Deployed Models

**Chat Tab:**
- Dropdown shows: gpt2, distilgpt2, gpt2-medium
- Does NOT show: sentence-transformers/... (embedding models)

**Photo Search Tab:**
- Click "Initialize Search"
- Uses first deployed embedding model automatically
- No need to download again!

---

## 📁 Directory Structure

```
llm-dash/
├── models/                          # 🆕 Local models directory
│   ├── chat/                        # Chat models (not used yet)
│   ├── embeddings/                  # Embedding models (not used yet)
│   ├── models--gpt2/                # Downloaded gpt2
│   │   └── snapshots/...
│   ├── models--sentence-transformers--all-MiniLM-L6-v2/
│   │   └── snapshots/...
│   ├── hub/                         # HuggingFace cache
│   ├── .gitignore                   # Ignores downloaded models
│   └── README.md                    # Model directory docs
│
├── backend/
│   └── app/
│       ├── core/
│       │   └── model_config.py      # 🆕 Model recommendations
│       ├── routers/
│       │   └── recommendations.py   # 🆕 Recommendations API
│       └── services/
│           ├── lightweight_model_manager.py  # 🔧 Updated: model detection
│           └── photo_search_service.py       # 🔧 Updated: use deployed models
│
└── frontend/
    └── src/
        └── pages/
            ├── Deploy.tsx           # 🔧 Updated: show recommendations
            ├── Chat.tsx             # 🔧 Updated: filter embeddings
            └── PhotoSearch.tsx      # 🔧 Updated: use deployed models
```

---

## 🤖 Recommended Models for 8GB RAM

### Chat Models (use in Chat tab)

| Model | Size | RAM | Speed | Quality | Best For |
|-------|------|-----|-------|---------|----------|
| `distilgpt2` | 82M (350MB) | ~600MB | ⚡⚡⚡ | ⭐ | Quick testing |
| `gpt2` | 124M (500MB) | ~800MB | ⚡⚡ | ⭐⭐ | **General use (BEST)** |
| `gpt2-medium` | 355M (1.5GB) | ~2.5GB | ⚡ | ⭐⭐⭐ | Better responses |

### Embedding Models (use in Photo Search tab)

| Model | Size | RAM | Dimensions | Best For |
|-------|------|-----|------------|----------|
| `sentence-transformers/paraphrase-MiniLM-L3-v2` | 61MB | ~200MB | 384 | Quick testing |
| `sentence-transformers/all-MiniLM-L6-v2` | 80MB | ~250MB | 384 | **Recommended** |
| `sentence-transformers/all-MiniLM-L12-v2` | 120MB | ~300MB | 384 | Better quality |
| `BAAI/bge-small-en-v1.5` | 134MB | ~350MB | 384 | Best quality |

---

## 🎯 Usage Guide

### Deploy Both Types

1. **Deploy Chat Model** (for chatting):
   ```
   Deploy → Chat Models → gpt2 → Deploy
   Wait for: RUNNING status
   Use in: Chat tab
   ```

2. **Deploy Embedding Model** (for photo search):
   ```
   Deploy → Embedding Models → all-MiniLM-L6-v2 → Deploy
   Wait for: RUNNING status
   Use in: Photo Search tab
   ```

### Smart Filtering

- **Chat Tab Dropdown**: Shows only `gpt2`, `gpt2-medium`, `distilgpt2`
  - Automatically hides embedding models (they can't chat!)

- **Photo Search**: Uses deployed embedding models automatically
  - No need to specify model name
  - Reuses already-loaded models

### Model Lifecycle

```
Deploy → Model downloads to models/ → Loads into RAM → RUNNING
  ↓
Chat with it (if chat model)
  OR
Use for photo search (if embedding model)
  ↓
Stop → Unloads from RAM (file stays in models/)
  ↓
Delete → Removes from list (file still in models/)
```

---

## 💾 Disk Space

### Budget for 8GB RAM:

- **1 chat model**: ~1GB (gpt2)
- **1-2 embedding models**: ~200MB (all-MiniLM-L6-v2 × 2)
- **Total**: ~1.5GB disk space

### Check What's Downloaded:

```bash
cd /Users/kaichen/Desktop/llm-dash
ls -lh models/models--*/
```

### Clean Up:

```bash
# Remove specific model
rm -rf models/models--gpt2

# Clear all models (keeps directory structure)
rm -rf models/models--*
rm -rf models/hub
```

---

## 🔄 Moving to Another Server

### Option 1: Copy Models (Faster Setup)

```bash
# On Mac - pack everything
cd /Users/kaichen/Desktop/llm-dash
tar czf models.tar.gz models/

# Transfer to server
scp models.tar.gz user@server:/path/to/llm-dash/

# On server - unpack
cd /path/to/llm-dash
tar xzf models.tar.gz

# Models ready to use immediately!
```

### Option 2: Fresh Download (Cleaner)

```bash
# Don't copy models/ directory
# On new server, models will download on first deploy
# Takes 3-5 minutes per model
```

---

## 🚦 Testing Guide

### Test 1: Deploy and Chat with Chat Model

```bash
# 1. Restart backend
lsof -ti:7860 | xargs kill
cd backend && source venv/bin/activate && python run.py

# 2. Deploy gpt2
http://localhost:5173/deploy
→ Chat Models tab
→ Click gpt2
→ Deploy

# 3. Wait for RUNNING
http://localhost:5173/

# 4. Chat
http://localhost:5173/chat
→ Select gpt2
→ Type "Hello!"
→ Get response ✅
```

### Test 2: Deploy and Use Embedding Model

```bash
# 1. Deploy embedding model
http://localhost:5173/deploy
→ Embedding Models tab
→ Click all-MiniLM-L6-v2
→ Deploy

# 2. Wait for RUNNING
http://localhost:5173/

# 3. Initialize photo search
http://localhost:5173/photos
→ Click "Initialize Search"
→ Wait 10 seconds

# 4. Search
→ Type "a black dog"
→ See results ✅
```

### Test 3: Verify Model Separation

```bash
# After deploying both gpt2 and all-MiniLM-L6-v2:

# Chat tab should show:
- gpt2 ✅
- all-MiniLM-L6-v2 ❌ (hidden)

# Photo search should use:
- all-MiniLM-L6-v2 ✅ (auto-selected)
```

---

## 🎓 Key Concepts

### Model Types

1. **Chat Models (LLM)**:
   - Input: Text prompt
   - Output: Text response
   - Examples: gpt2, distilgpt2
   - Use: Chat tab

2. **Embedding Models**:
   - Input: Text
   - Output: Vector (list of floats)
   - Examples: all-MiniLM-L6-v2
   - Use: Photo Search tab

### Auto-Detection

The system automatically detects model type by name:

```python
# Embedding model if name contains:
- "sentence-transformers"
- "bge-"
- "gte-"
- "e5-"
- "embed"
- "minilm"
- "mpnet"
```

### Local Storage Benefits

✅ **Portable** - Move project with models  
✅ **Clean** - No system cache pollution  
✅ **Visible** - See what's downloaded  
✅ **Controllable** - Easy to manage  
✅ **Safe** - Delete = clean  

---

## 📚 Related Docs

- **`models/README.md`** - Model directory details
- **`TINY_MODELS_GUIDE.md`** - Tiny models for 8GB RAM
- **`EMBEDDING_MODELS.md`** - Embedding models guide
- **`PHOTO_SEARCH.md`** - Photo search feature
- **`QUICKSTART.txt`** - Quick start guide

---

## ✅ Summary

**What you asked for:**
> "I feel like you can have local model dir under project root, then download any model there if missing, also include some small embedding model there as well, so that I can deploy these small size embed model using web as well, anyway, do not select embed model deployed as available in chat tab, since embed only give list of float value, but I will use deployed embed model in photo search tab"

**What's implemented:**

✅ Local model directory: `llm-dash/models/`  
✅ All downloads go there automatically  
✅ Deploy both chat and embedding models via web UI  
✅ Embedding models hidden from Chat tab dropdown  
✅ Embedding models shown in Embedding Models tab  
✅ Photo Search uses deployed embedding models  
✅ Smart model type detection  
✅ Curated recommendations for 8GB RAM  

**Ready to test!** 🚀

1. Restart backend
2. Deploy `gpt2` (Chat Models tab)
3. Deploy `all-MiniLM-L6-v2` (Embedding Models tab)
4. Chat with gpt2 (only gpt2 shows in dropdown)
5. Use photo search (uses all-MiniLM-L6-v2 automatically)

Everything stores in `llm-dash/models/` locally! 📦


