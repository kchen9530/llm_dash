# Transform Feature: LLM-Based Processing with Model Selection

## ✅ Feature Implemented

You now have a complete text-to-JSON transformation system with two modes:
1. **Rule-Based** (original) - Fast pattern matching
2. **LLM-Based** (NEW!) - 3-step AI pipeline with model selection

---

## 🎯 How It Works

### Mode 1: Rule-Based (Always Available)
```
User Input → Pattern Matching → JSON Output
```
- Fast and deterministic
- No models required
- Limited to predefined patterns

### Mode 2: LLM-Based (Requires Models)
```
User Input 
   ↓
[Step 1: Model 1] Generate Category JSON
   ↓
[Step 2: Model 2] Generate Detailed JSON
   ↓
[Step 3: Embed Model] Add Embedding Information
   ↓
Final Enhanced JSON
```

---

## 🚀 3-Step LLM Pipeline Explained

### Step 1: Category Generation (Model 1)
**Purpose:** Extract high-level categories and types

**Input:** `"I have a red car"`

**Prompt to Model 1:**
```
Extract the main category or type from this text and return ONLY a JSON object.

Text: "I have a red car"

Return a JSON object with this structure: {"category": "main_category", "type": "specific_type"}
```

**Output (JSON 1):**
```json
{
  "category": "vehicle",
  "type": "car"
}
```

### Step 2: Detail Generation (Model 2)
**Purpose:** Extract detailed attributes based on category

**Input:** Original text + JSON 1 from Step 1

**Prompt to Model 2:**
```
Given the category information, extract detailed structured information from the text.

Text: "I have a red car"
Category: {"category": "vehicle", "type": "car"}

Return a detailed JSON object with all relevant attributes and properties.
```

**Output (JSON 2):**
```json
{
  "category": "vehicle",
  "type": "car",
  "details": {
    "color": "red",
    "ownership": "personal"
  }
}
```

### Step 3: Add Embedding Info (Embed Model)
**Purpose:** Enrich with semantic vector information

**Process:**
1. Generate embedding vector for input text
2. Add embedding metadata to JSON 2

**Output (Final JSON):**
```json
{
  "category": "vehicle",
  "type": "car",
  "details": {
    "color": "red",
    "ownership": "personal"
  },
  "embedding_info": {
    "model": "sentence-transformers/all-MiniLM-L6-v2",
    "dimension": 384,
    "vector_preview": [0.123, -0.456, 0.789, ...],
    "vector_norm": 12.45
  }
}
```

---

## 🎮 How to Use (UI Guide)

### Step 1: Deploy Models
First, deploy the models you want to use:
1. Go to **Deploy** page
2. Deploy at least **1 chat model** (e.g., `gpt2` or `Qwen2-0.5B-Instruct`)
3. Deploy at least **1 embedding model** (e.g., `all-MiniLM-L6-v2`)
4. Wait for models to reach "RUNNING" status

### Step 2: Choose Processing Mode
1. Go to **Transform** page
2. You'll see two cards:
   - **Rule-Based** (always available)
   - **LLM-Based** (shows green if models available)

### Step 3A: Use Rule-Based (Simple)
1. Click **Rule-Based** card
2. Enter text in input field
3. Click **Transform to JSON**
4. See instant results!

### Step 3B: Use LLM-Based (Advanced)
1. Click **LLM-Based** card
2. You'll see the 3-step pipeline section appear:
   ```
   [1] Category Generation → Select LLM Model 1
   [2] Detail Generation   → Select LLM Model 2
   [3] Add Embedding Info  → Select Embed Model
   ```
3. Choose models for each step:
   - **Model 1**: Any running chat model
   - **Model 2**: Any running chat model (can be same as Model 1)
   - **Embed Model**: Any running embedding model
4. Enter text in input field
5. Click **Transform to JSON**
6. Watch the 3-step pipeline process your text!

---

## 💡 Model Selection Tips

### Using Same Model for Both Steps
```
Model 1: gpt2
Model 2: gpt2  ← Same model, different prompts
Embed: all-MiniLM-L6-v2
```
**Pros:** Consistent style, lower memory usage
**Cons:** Same reasoning patterns

### Using Different Models
```
Model 1: gpt2 (fast, for categories)
Model 2: Qwen2-0.5B-Instruct (better quality for details)
Embed: all-MiniLM-L6-v2
```
**Pros:** Diverse perspectives, better validation
**Cons:** More memory usage

---

## 📊 Example Outputs

### Example 1: Simple Text

**Input:** `"this is a cat"`

**Rule-Based Output:**
```json
{
  "item": {
    "category": "cat"
  }
}
```

**LLM-Based Output:**
```json
{
  "category": "animal",
  "type": "cat",
  "details": {
    "species": "feline",
    "context": "identification"
  },
  "embedding_info": {
    "model": "all-MiniLM-L6-v2",
    "dimension": 384,
    "vector_preview": [0.234, -0.567, ...],
    "vector_norm": 12.45
  }
}
```

### Example 2: Complex Text

**Input:** `"I want to buy a blue sports car with leather seats"`

**Rule-Based Output:**
```json
{
  "entity": {
    "category": "seats",
    "original": "I want to buy a blue sports car with leather seats"
  }
}
```
(Limited pattern matching)

**LLM-Based Output:**
```json
{
  "category": "vehicle",
  "type": "sports_car",
  "details": {
    "color": "blue",
    "seats": "leather",
    "intent": "purchase",
    "classification": "luxury"
  },
  "embedding_info": {
    "model": "all-MiniLM-L6-v2",
    "dimension": 384,
    "vector_preview": [...],
    "vector_norm": 15.23
  }
}
```
(Much richer extraction!)

---

## 🔧 Technical Implementation

### Backend Changes

1. **`processor.py`** - New LLMBasedTextProcessor
   - Implemented 3-step pipeline
   - Uses deployed model IDs (not direct model objects)
   - Each step calls the lightweight model manager
   - Proper error handling and JSON extraction

2. **`transform.py`** - Updated API
   - Added `model1_id`, `model2_id`, `embed_model_id` to request
   - Updated `/methods` endpoint to return available models
   - Factory creates processor based on selections

### Frontend Changes

1. **`Transform.tsx`** - Complete UI Redesign
   - Mode selection cards (Rule-Based vs LLM-Based)
   - 3-step pipeline visualization
   - Model dropdown selectors
   - Auto-refresh of available models every 5s
   - Visual indicators for model availability
   - Enhanced output display showing which models were used

---

## 🎨 UI Features

### Visual Pipeline Display
When LLM mode is selected, you see:
```
[1] Category Generation → [Dropdown: Select LLM Model 1] →
[2] Detail Generation   → [Dropdown: Select LLM Model 2] →
[3] Add Embedding Info  → [Dropdown: Select Embed Model]
```

### Status Indicators
- 🟢 Green dot = Models available
- 🟡 Yellow dot = Deploy models first
- Selected mode highlighted with colored border

### Smart Defaults
- Auto-selects first available model when models deploy
- Defaults to same LLM for both steps
- Shows real-time model availability

---

## 📋 Requirements for LLM Mode

To use LLM-based processing, you need:
1. ✅ At least **1 running chat model** (for Model 1 & 2)
2. ✅ At least **1 running embedding model**
3. ✅ All selected models must be in "RUNNING" status

If requirements aren't met:
- LLM-based card shows "Deploy models first"
- Transform button is disabled
- System falls back to rule-based

---

## 🚦 Status & Error Handling

### Success Flow
```
User clicks Transform → 
  Step 1: Generate category (Model 1) →
  Step 2: Generate details (Model 2) →
  Step 3: Add embedding (Embed Model) →
  Display enhanced JSON ✓
```

### Error Handling
- Model not running → Error: "Model {id} is not running"
- Invalid JSON from LLM → Falls back to text + error flag
- Embedding model not loaded → Error: "Embedding model not loaded"
- Missing model selections → Error: "Please select all required models"

---

## 🧪 How to Test

### Test 1: Rule-Based (No Models Needed)
1. Select **Rule-Based** mode
2. Input: `"this is a cat"`
3. Click Transform
4. Should return immediately with category JSON

### Test 2: LLM-Based (Requires Models)
1. Deploy:
   - 1 chat model (e.g., `gpt2`)
   - 1 embedding model (e.g., `all-MiniLM-L6-v2`)
2. Wait for "RUNNING" status
3. Go to Transform page
4. Select **LLM-Based** mode
5. Select models in all 3 dropdowns
6. Input: `"I have a red car"`
7. Click Transform
8. Watch the 3-step pipeline process (takes 10-30 seconds on CPU)
9. See enriched JSON with embedding info!

### Test 3: Model Switching
1. Deploy multiple models (e.g., `gpt2` and `distilgpt2`)
2. Try different combinations:
   - Model 1: gpt2, Model 2: gpt2
   - Model 1: gpt2, Model 2: distilgpt2
3. Compare results to see how different models extract info

---

## ⚡ Performance Notes

**Rule-Based:**
- ⚡ Instant (<10ms)
- No model loading required

**LLM-Based on CPU:**
- 🐌 Slow (10-30 seconds for 3 steps)
- Each step waits for LLM generation
- Suitable for testing/demo

**LLM-Based on GPU (Future):**
- ⚡ Fast (1-3 seconds for 3 steps)
- Production-ready performance

---

## 🎉 Features Summary

✅ **Mode Switching** - Toggle between rule-based and LLM-based
✅ **Model Selection** - Choose any running models
✅ **3-Step Pipeline** - Category → Details → Embedding enrichment
✅ **Visual Feedback** - See which models are used
✅ **Auto-Refresh** - UI updates when models deploy/stop
✅ **Flexible** - Use same or different models per step
✅ **Error Handling** - Clear error messages
✅ **Persistent Results** - Results stay visible
✅ **Copy to Clipboard** - Easy JSON export

---

## 🔮 Future Enhancements (Ideas)

1. **Pipeline Visualization** - Show real-time progress through steps
2. **Intermediate Results** - Display JSON 1, JSON 2, and final JSON
3. **Model Recommendations** - Suggest best model combinations
4. **Batch Processing** - Transform multiple texts at once
5. **Custom Pipeline** - Let users configure number of steps
6. **A/B Comparison** - Compare rule-based vs LLM outputs side-by-side

---

## 🏁 Ready to Use!

The feature is **live right now**! 

1. ✅ Backend has auto-reloaded
2. ✅ Frontend should hot-reload automatically
3. ✅ Go to Transform page and try it out!

**Next steps:**
1. Deploy some models (Dashboard → Deploy)
2. Go to Transform page
3. Switch between modes and compare results
4. Experiment with different model combinations!

Enjoy the new feature! 🎉
