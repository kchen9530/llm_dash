# 📸 Photo Search Feature

## Overview

Semantic photo search using text queries and embedding-based similarity. Find photos by describing what you're looking for in natural language!

**Example:**
- Query: `"a black dog"`
- Result: Finds photos of black dogs ranked by semantic similarity

---

## 🎯 How It Works

### Architecture

```
User Query: "a black dog"
    ↓
1. Embed query using sentence-transformers
    ↓ 
2. Compare with pre-computed photo embeddings
    ↓
3. Calculate cosine similarity scores
    ↓
4. Return top K most similar photos
```

### Pre-computed Photo Embeddings

Each photo has:
- **Description**: Natural language description
- **Embedding**: 384-dimensional vector computed from description
- **Tags**: Keywords for reference

The system computes embeddings for photo descriptions during initialization.

---

## 📊 Sample Photos (10 included)

| ID | Filename | Description | Tags |
|----|----------|-------------|------|
| photo_001 | black_cat_sleeping.jpg | A black cat sleeping peacefully on a soft cushion | cat, black, sleeping, indoor |
| photo_002 | white_dog_running.jpg | A white fluffy dog running happily in a green park | dog, white, running, outdoor, park |
| photo_003 | orange_cat_playing.jpg | An orange tabby cat playing with a toy mouse | cat, orange, playing, toy |
| photo_004 | brown_dog_sitting.jpg | A brown dog sitting obediently | dog, brown, sitting, obedient |
| photo_005 | gray_cat_window.jpg | A gray cat sitting by the window | cat, gray, window, watching |
| photo_006 | black_dog_beach.jpg | A black dog running on the beach | dog, black, beach, ocean, running |
| photo_007 | calico_cat_eating.jpg | A calico cat eating food from a bowl | cat, calico, eating, kitchen |
| photo_008 | golden_dog_fetch.jpg | A golden retriever playing fetch | dog, golden, playing, fetch, ball |
| photo_009 | white_cat_grooming.jpg | A white cat grooming itself | cat, white, grooming, cleaning |
| photo_010 | spotted_dog_grass.jpg | A spotted dalmatian lying on grass | dog, spotted, dalmatian, grass, garden |

---

## 🚀 Quick Start

### 1. Navigate to Photo Search

Click the **"Photos"** tab (📷 icon) in the sidebar, or visit:
```
http://localhost:5173/photos
```

### 2. Initialize Search

Click **"Initialize Search"** button.

This will:
- Load the embedding model (sentence-transformers/all-MiniLM-L6-v2)
- Compute embeddings for all 10 photos
- Takes ~10-15 seconds (first time)
- Model is cached for future use

### 3. Search for Photos

Enter a query like:
- `"a black dog"`
- `"cat playing"`
- `"dog running on beach"`
- `"sleeping cat"`
- `"white fluffy dog"`

Press Enter or click **Search**.

### 4. View Results

See top matching photos with:
- **Similarity score** (percentage)
- **Description**
- **Tags**
- **Visual indicator** (emoji placeholder: 🐱 for cats, 🐕 for dogs)

---

## 🧪 Example Searches

### Example 1: "a black dog"

**Results:**
1. `black_dog_beach.jpg` - **59.5%** ✅ (exact match: black + dog)
2. `brown_dog_sitting.jpg` - **41.8%** (dog, but not black)
3. `black_cat_sleeping.jpg` - **34.5%** (black, but cat not dog)

### Example 2: "cat playing"

**Results:**
1. `orange_cat_playing.jpg` - **70.7%** ✅ (perfect match!)
2. `gray_cat_window.jpg` - **53.3%** (cat, not playing)
3. `calico_cat_eating.jpg` - **53.2%** (cat, different activity)

### Example 3: "dog running on beach"

**Results:**
1. `black_dog_beach.jpg` - **75.2%** ✅ (exact match!)
2. `white_dog_running.jpg` - **62.4%** (running dog, not beach)
3. `golden_dog_fetch.jpg` - **48.1%** (dog, different context)

---

## 📡 API Endpoints

### 1. Initialize Photo Search

**POST** `/api/photos/initialize`

```bash
curl -X POST http://localhost:7860/api/photos/initialize
```

**Response:**
```json
{
  "status": "initialized",
  "model": "sentence-transformers/all-MiniLM-L6-v2",
  "stats": {
    "total_photos": 10,
    "embeddings_initialized": true,
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "embedding_dimension": 384
  }
}
```

### 2. Search Photos

**POST** `/api/photos/search`

```bash
curl -X POST http://localhost:7860/api/photos/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "a black dog",
    "top_k": 5
  }'
```

**Response:**
```json
{
  "query": "a black dog",
  "results": [
    {
      "photo_id": "photo_006",
      "filename": "black_dog_beach.jpg",
      "description": "A black dog running on the beach near the ocean",
      "tags": ["dog", "black", "beach", "ocean", "running"],
      "similarity": 0.5945,
      "similarity_percent": 59.45
    }
  ],
  "total_results": 1
}
```

### 3. Get All Photos

**GET** `/api/photos/photos`

```bash
curl http://localhost:7860/api/photos/photos
```

### 4. Get Photo by ID

**GET** `/api/photos/photos/{photo_id}`

```bash
curl http://localhost:7860/api/photos/photos/photo_001
```

### 5. Get Stats

**GET** `/api/photos/stats`

```bash
curl http://localhost:7860/api/photos/stats
```

---

## 🔧 Technical Details

### Cosine Similarity

The system uses **cosine similarity** to measure how similar two vectors are:

```python
def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b))
```

**Similarity scores:**
- **1.0** (100%) = Identical vectors
- **0.5** (50%) = Moderately similar
- **0.0** (0%) = Orthogonal (no similarity)
- **-1.0** (-100%) = Opposite vectors

### Embedding Model

- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Size**: 80MB
- **Dimensions**: 384
- **Speed**: ~15ms per text
- **Language**: English

### Pre-computed Embeddings

Photo embeddings are computed from descriptions during initialization:

```python
# Example
photo_desc = "A black dog running on the beach near the ocean"
photo_embedding = model.encode(photo_desc)  # [0.123, -0.456, ...]

# Later, during search
query = "a black dog"
query_embedding = model.encode(query)
similarity = cosine_similarity(query_embedding, photo_embedding)
```

---

## 💡 Extending the Feature

### Add More Photos

Edit `backend/app/data/photo_database.json`:

```json
{
  "photos": [
    ...existing photos...,
    {
      "id": "photo_011",
      "filename": "your_photo.jpg",
      "description": "Detailed description of your photo",
      "tags": ["tag1", "tag2", "tag3"]
    }
  ]
}
```

Then re-initialize the search.

### Use Different Embedding Model

Initialize with a different model:

```bash
curl -X POST http://localhost:7860/api/photos/initialize?model_name=BAAI/bge-small-en-v1.5
```

### Add Real Images

Currently uses emoji placeholders (🐱🐕). To add real images:

1. Store images in `backend/static/photos/`
2. Update frontend to display image URLs
3. Modify `PhotoCard` component to show `<img>` tags

### Improve Search

**Better descriptions** = Better search results!

Tips:
- Use detailed descriptions
- Include colors, actions, locations
- Add context and attributes

---

## 🎨 Frontend Customization

### Change Result Display

Edit `frontend/src/pages/PhotoSearch.tsx`:

```tsx
// Customize photo card
const PhotoCard = ({ result }: { result: SearchResult }) => {
  return (
    <div className="your-custom-styles">
      {/* Your custom rendering */}
    </div>
  )
}
```

### Add Filters

Add tag filters, color filters, or category filters:

```tsx
const [selectedTags, setSelectedTags] = useState<string[]>([])

// Filter results by tags
const filteredResults = results.filter(r => 
  selectedTags.every(tag => r.tags.includes(tag))
)
```

### Add Sorting

Sort by similarity, date, filename, etc.:

```tsx
const sortedResults = [...results].sort((a, b) => 
  b.similarity - a.similarity  // Highest similarity first
)
```

---

## 📊 Performance

### Initialization (First Time)
- **Download model**: ~60 seconds (if not cached)
- **Load model**: ~2-3 seconds
- **Compute 10 embeddings**: ~200ms
- **Total**: ~10-15 seconds (first time)

### Initialization (Cached)
- **Load model**: ~2-3 seconds
- **Compute 10 embeddings**: ~200ms
- **Total**: ~2-3 seconds

### Search (Per Query)
- **Embed query**: ~15ms
- **Compute similarities**: ~1ms (for 10 photos)
- **Sort results**: <1ms
- **Total**: ~20ms ⚡

### Scaling
- **100 photos**: ~50ms search time
- **1,000 photos**: ~200ms search time
- **10,000 photos**: ~2s search time

For larger databases, consider:
- Vector databases (Pinecone, Weaviate, Qdrant)
- Approximate nearest neighbor (ANN) algorithms
- Batched processing

---

## 🆚 Comparison

### Text Search vs Semantic Search

**Text Search** (keyword matching):
```
Query: "black dog"
Result: Only finds photos with EXACT words "black" and "dog"
```

**Semantic Search** (meaning-based):
```
Query: "black dog"
Result: Finds photos of:
  - Black dogs (exact match)
  - Dark-colored dogs (similar meaning)
  - Dogs in general (related concept)
Ranked by semantic similarity!
```

### Benefits of Semantic Search
- ✅ Understands **meaning**, not just keywords
- ✅ Finds **similar** concepts
- ✅ **Typo-tolerant**
- ✅ Works with **paraphrases**
- ✅ **Multi-language** capable (with right model)

---

## 🛠️ Troubleshooting

### "Initialize failed"

**Issue**: Model download failed

**Solution:**
- Check internet connection
- Your proxy should handle it automatically
- Wait for download to complete (~60 seconds first time)

### "No results found"

**Issue**: Query too specific or no matching photos

**Solution:**
- Try broader queries
- Check photo database has relevant photos
- Lower similarity threshold (show more results)

### "Slow search"

**Issue**: Too many photos

**Solution:**
- Use vector database for larger datasets
- Implement caching
- Use approximate nearest neighbor (ANN)

### "Poor results"

**Issue**: Photo descriptions don't match queries well

**Solution:**
- Improve photo descriptions
- Add more descriptive keywords
- Use higher-quality embedding model

---

## 📝 Quick Reference

### Installation
```bash
pip install sentence-transformers  ✅ DONE!
```

### Initialize
```bash
POST /api/photos/initialize
```

### Search
```bash
POST /api/photos/search
Body: {"query": "your query", "top_k": 5}
```

### Frontend
```
http://localhost:5173/photos
```

### Photo Database
```
backend/app/data/photo_database.json
```

---

## 🎯 Use Cases

### 1. E-commerce Product Search
- Search products by description
- "red winter jacket"
- "comfortable running shoes"

### 2. Stock Photo Search
- Find images by content
- "sunset over mountains"
- "people working in office"

### 3. Personal Photo Library
- Search your photos by memory
- "birthday party last year"
- "beach vacation"

### 4. Content Moderation
- Find similar images
- Detect duplicates
- Category classification

---

**Your Photo Search is ready! 🎉**

- ✅ 10 sample photos with embeddings
- ✅ Semantic search with cosine similarity
- ✅ Beautiful UI with similarity scores
- ✅ Fast search (~20ms per query)
- ✅ Easy to extend with more photos
- ✅ Works great with your proxy

Visit: http://localhost:5173/photos

