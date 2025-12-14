# 📊 Embedding Models Support

## Overview

Embedding models convert text into numerical vectors (lists of floats). Unlike chat models that generate text, embedding models output feature representations useful for:
- Semantic search
- Text similarity
- Classification
- Clustering

---

## 🤖 Recommended Small Embedding Models

### 1. **sentence-transformers/paraphrase-MiniLM-L3-v2** ⭐ Smallest
- **Size**: 61MB
- **Dimensions**: 384
- **Speed**: ⚡⚡⚡ Very Fast
- **Best for**: Quick testing, low memory

### 2. **sentence-transformers/all-MiniLM-L6-v2** ⭐ Recommended
- **Size**: 80MB
- **Dimensions**: 384
- **Speed**: ⚡⚡ Fast
- **Best for**: General use, good balance

### 3. **sentence-transformers/all-MiniLM-L12-v2**
- **Size**: 120MB
- **Dimensions**: 384
- **Speed**: ⚡ Medium
- **Best for**: Better quality, still fast

### 4. **BAAI/bge-small-en-v1.5**
- **Size**: 134MB
- **Dimensions**: 384
- **Speed**: ⚡ Medium
- **Best for**: High quality English embeddings

---

## 🚀 Quick Start

### 1. Install sentence-transformers

```bash
cd /Users/kaichen/Desktop/llm-dash/backend
source venv/bin/activate
pip install sentence-transformers
```

### 2. Use the Embedding API

**Get embedding for single text:**
```bash
curl -X POST http://localhost:7860/api/embeddings/embed \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "sentence-transformers/all-MiniLM-L6-v2",
    "text": "This is a sample sentence"
  }'
```

**Response:**
```json
{
  "embedding": [0.123, -0.456, 0.789, ...],
  "dimension": 384,
  "model": "sentence-transformers/all-MiniLM-L6-v2"
}
```

### 3. Use in Chat Interface

1. ✅ The embedding model will be detected automatically
2. ✅ When you select an embedding model in Chat, it shows "📊 Embedding Mode"
3. ✅ Type your text and press Enter
4. ✅ Get the embedding vector as output!

---

## 🎯 How It Works

### Detection

The system automatically detects embedding models by checking if the model name contains:
- `sentence-transformers`
- `embed` or `embedding`
- `bge-`
- `minilm`
- `gte-`
- `e5-`

### Chat Behavior

**Regular LLM Model:**
- Input: "Hello, how are you?"
- Output: "I'm doing well, thanks for asking! How can I help you?"

**Embedding Model:**
- Input: "Hello, how are you?"
- Output: 
```
Embedding Vector (384 dimensions):

[
  0.0234,
  -0.0567,
  0.0891,
  ...
]

[Showing first 10 of 384 values]
Full vector: 384 floats
```

---

## 📡 API Endpoints

### 1. Get Single Embedding

**POST** `/api/embeddings/embed`

```json
{
  "model_name": "sentence-transformers/all-MiniLM-L6-v2",
  "text": "Your text here"
}
```

### 2. Get Batch Embeddings (More Efficient)

**POST** `/api/embeddings/embed/batch`

```json
{
  "model_name": "sentence-transformers/all-MiniLM-L6-v2",
  "texts": ["First sentence", "Second sentence", "Third sentence"]
}
```

### 3. Get Recommended Models

**GET** `/api/embeddings/models/recommended`

Returns list of recommended models with sizes and dimensions.

### 4. Pre-load Model

**POST** `/api/embeddings/models/{model_name}/load`

Load model into memory before first use (warm-up).

### 5. Unload Model

**DELETE** `/api/embeddings/models/{model_name}`

Free memory by unloading model.

### 6. Get Model Info

**GET** `/api/embeddings/models/{model_name}/info`

Get information about loaded model.

---

## 🧪 Testing

### Test 1: Get Embedding (No Chat UI)

```bash
curl -X POST http://localhost:7860/api/embeddings/embed \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "sentence-transformers/all-MiniLM-L6-v2",
    "text": "The quick brown fox jumps over the lazy dog"
  }' | python3 -m json.tool | head -20
```

### Test 2: Batch Embeddings

```bash
curl -X POST http://localhost:7860/api/embeddings/embed/batch \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "sentence-transformers/all-MiniLM-L6-v2",
    "texts": ["cat", "dog", "tiger", "lion"]
  }' | python3 -m json.tool | head -30
```

### Test 3: In Chat Interface

1. Go to http://localhost:5173/chat
2. Type in the input: `sentence-transformers/all-MiniLM-L6-v2`
3. Model will be detected as embedding model
4. See "📊 Embedding Mode" indicator
5. Enter: "this is a test"
6. Get embedding vector output!

---

## 💡 Use Cases

### 1. Semantic Search

```python
# Get embeddings for documents
docs = ["cat", "dog", "car", "bicycle"]
doc_embeddings = [get_embedding(doc) for doc in docs]

# Get embedding for query
query_embedding = get_embedding("pet")

# Find most similar (using cosine similarity)
similarities = [cosine_sim(query_embedding, doc_emb) for doc_emb in doc_embeddings]
# Results: cat (0.85), dog (0.82), car (0.15), bicycle (0.12)
```

### 2. Text Similarity

```python
text1 = "The cat sat on the mat"
text2 = "A feline rested on the rug"
text3 = "The car is red"

emb1 = get_embedding(text1)
emb2 = get_embedding(text2)
emb3 = get_embedding(text3)

similarity(emb1, emb2)  # High (similar meaning)
similarity(emb1, emb3)  # Low (different meaning)
```

### 3. Clustering

```python
# Get embeddings for many texts
texts = ["..."]
embeddings = [get_embedding(t) for t in texts]

# Cluster using KMeans or HDBSCAN
from sklearn.cluster import KMeans
clusters = KMeans(n_clusters=5).fit_predict(embeddings)
```

---

## 🔧 Integration Example

### Python Client

```python
import requests
import numpy as np

def get_embedding(text, model="sentence-transformers/all-MiniLM-L6-v2"):
    response = requests.post(
        "http://localhost:7860/api/embeddings/embed",
        json={"model_name": model, "text": text}
    )
    return np.array(response.json()["embedding"])

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Usage
emb1 = get_embedding("cat")
emb2 = get_embedding("dog")
emb3 = get_embedding("car")

print(f"cat-dog similarity: {cosine_similarity(emb1, emb2):.3f}")
print(f"cat-car similarity: {cosine_similarity(emb1, emb3):.3f}")
```

### JavaScript Client

```javascript
async function getEmbedding(text, model = "sentence-transformers/all-MiniLM-L6-v2") {
  const response = await fetch("http://localhost:7860/api/embeddings/embed", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model_name: model, text })
  });
  const data = await response.json();
  return data.embedding;
}

// Usage
const emb = await getEmbedding("Hello world");
console.log(`Got ${emb.length} dimensional vector`);
```

---

## 📊 Performance (on 8GB Mac)

| Model | Size | Load Time | Inference | Dimensions |
|-------|------|-----------|-----------|------------|
| paraphrase-MiniLM-L3-v2 | 61MB | ~2s | ~10ms | 384 |
| all-MiniLM-L6-v2 | 80MB | ~3s | ~15ms | 384 |
| all-MiniLM-L12-v2 | 120MB | ~4s | ~25ms | 384 |
| bge-small-en-v1.5 | 134MB | ~5s | ~30ms | 384 |

*Times are approximate for M1/M2 Mac with 8GB RAM*

---

## 🆚 Embedding vs Chat Models

| Feature | Embedding Models | Chat/LLM Models |
|---------|------------------|-----------------|
| **Output** | Vector of floats | Text |
| **Size** | 60-200MB | 500MB-70GB |
| **Speed** | ⚡⚡⚡ Very fast | 🐢 Slow (CPU) |
| **Use Case** | Search, similarity | Conversation |
| **Memory** | Low (~200MB) | High (1-20GB) |
| **Works on 8GB?** | ✅ Yes, easily | ⚠️ Tiny models only |

---

## 🔍 Model Comparison

### Quality (General English)

1. 🥇 BAAI/bge-small-en-v1.5 (best quality)
2. 🥈 sentence-transformers/all-MiniLM-L12-v2
3. 🥉 sentence-transformers/all-MiniLM-L6-v2 (recommended)
4. sentence-transformers/paraphrase-MiniLM-L3-v2 (fastest)

### Speed

1. 🥇 paraphrase-MiniLM-L3-v2 (fastest)
2. 🥈 all-MiniLM-L6-v2
3. 🥉 all-MiniLM-L12-v2
4. bge-small-en-v1.5

### Memory Usage

All models use ~200-400MB RAM when loaded (very efficient!)

---

## 🛠️ Troubleshooting

### "sentence-transformers not installed"

```bash
cd backend
source venv/bin/activate
pip install sentence-transformers
```

### First download is slow

- Models download from HuggingFace (~60-130MB)
- Your proxy will handle it automatically
- Cached in `~/.cache/huggingface/` after first use
- Subsequent loads are instant!

### Out of memory

- Use smaller model (paraphrase-MiniLM-L3-v2)
- Unload unused models
- Close other applications

### Model not detected as embedding model

Add detection in `embedding_model_handler.py`:

```python
def is_embedding_model(model_name: str) -> bool:
    indicators = [
        'your-model-keyword',
        # ... existing indicators
    ]
```

---

## 📝 Quick Reference

### Install
```bash
pip install sentence-transformers
```

### Recommended Model
```
sentence-transformers/all-MiniLM-L6-v2
```

### API Endpoint
```
POST /api/embeddings/embed
```

### Chat UI
- Select embedding model
- See "📊 Embedding Mode"
- Enter text, get vector!

---

**Embedding models are ready! 🎉**

- ✅ Lightweight (60-130MB)
- ✅ Fast inference (~10-30ms)
- ✅ Low memory (~200MB)
- ✅ Perfect for 8GB Mac
- ✅ Works great with your proxy

Try it now: http://localhost:5173/chat

