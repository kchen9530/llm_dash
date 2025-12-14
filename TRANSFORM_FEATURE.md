# 🔮 Transform Feature - Text to JSON

## Overview

The Transform feature converts natural language text into structured JSON using LLM or rule-based methods.

**Example:**
- Input: `"this is a cat"`
- Output: `{"pet": {"category": "cat"}}`

---

## 🎯 Architecture

### Decoupled Design

The transformation logic is **completely decoupled** from the routing layer, making it easy to extend:

```
Frontend (Transform.tsx)
    ↓
Backend Router (routers/transform.py)
    ↓
Transformer Service (services/text_to_json_transformer.py)
    ↓ (Factory Pattern)
    ├── LLMBasedTransformer (uses deployed models)
    └── SimpleRuleBasedTransformer (fallback)
```

### Key Components

1. **`TextToJsonTransformer` (Abstract Base Class)**
   - Interface for all transformation strategies
   - Easy to implement new transformers

2. **`LLMBasedTransformer`**
   - Uses deployed LLM models
   - Constructs prompts for JSON extraction
   - Handles LLM responses and JSON parsing

3. **`SimpleRuleBasedTransformer`**
   - Fallback when no LLM available
   - Pattern matching rules
   - Good for simple cases

4. **`TransformerFactory`**
   - Automatically selects best available method
   - Tries LLM first, falls back to rules

---

## 🚀 Usage

### Frontend

Navigate to the **Transform** tab in the dashboard.

1. Enter text (e.g., "this is a cat")
2. Optionally add a schema hint
3. Click "Transform to JSON"
4. View the structured result

### API Endpoints

**Transform Text to JSON:**
```bash
curl -X POST http://localhost:7860/api/transform/text-to-json \
  -H "Content-Type: application/json" \
  -d '{
    "text": "this is a cat",
    "prefer_llm": true
  }'
```

**Response:**
```json
{
  "success": true,
  "result": {
    "pet": {
      "category": "cat"
    }
  },
  "method": "rule-based",
  "model_used": null
}
```

**Check Available Methods:**
```bash
curl http://localhost:7860/api/transform/methods
```

**Response:**
```json
{
  "llm_available": false,
  "llm_models": [],
  "rule_based_available": true,
  "recommendation": "rule-based"
}
```

---

## 🔧 Extending the Feature

### Adding New Transformation Strategies

Create a new transformer by implementing the abstract base class:

```python
# backend/app/services/text_to_json_transformer.py

class MyCustomTransformer(TextToJsonTransformer):
    """Your custom transformation logic"""
    
    async def transform(self, text: str, schema_hint: Optional[str] = None) -> Dict[str, Any]:
        # Your implementation here
        result = my_custom_logic(text)
        return result
```

### Adding New Rules (Rule-Based)

Extend the `PATTERNS` list in `SimpleRuleBasedTransformer`:

```python
class SimpleRuleBasedTransformer(TextToJsonTransformer):
    PATTERNS = [
        # Existing patterns...
        
        # Add your pattern
        (
            r'new pattern regex here',
            lambda m: {"your": {"json": "structure"}}
        ),
    ]
```

### Using External APIs

Create a new transformer that calls external services:

```python
class APIBasedTransformer(TextToJsonTransformer):
    """Use external API for transformation"""
    
    async def transform(self, text: str, schema_hint: Optional[str] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.example.com/transform",
                json={"text": text, "schema": schema_hint}
            )
            return response.json()
```

Then update the factory to use it:

```python
class TransformerFactory:
    @staticmethod
    def create_transformer(prefer_llm: bool = True) -> TextToJsonTransformer:
        # Try your custom transformer first
        if should_use_custom:
            return APIBasedTransformer()
        
        # Fallback to existing logic
        if prefer_llm:
            # ... existing code
```

---

## 🧪 Examples

### Example 1: Simple Entity Extraction

**Input:** `"this is a cat"`

**Output:**
```json
{
  "pet": {
    "category": "cat"
  }
}
```

### Example 2: Multiple Attributes

**Input:** `"I have a red car"`

**Output:**
```json
{
  "item": {
    "color": "red",
    "type": "car"
  }
}
```

### Example 3: Named Entity

**Input:** `"dog named Max"`

**Output:**
```json
{
  "dog": {
    "name": "Max"
  }
}
```

### Example 4: With Schema Hint

**Input:** `"blue bicycle"`

**Schema Hint:** `{"vehicle": {"color": "string", "type": "string"}}`

**Output:**
```json
{
  "vehicle": {
    "color": "blue",
    "type": "bicycle"
  }
}
```

---

## 🎨 Frontend Customization

### Modifying the UI

The Transform page (`frontend/src/pages/Transform.tsx`) is fully customizable:

```tsx
// Add new input fields
<Input
  label="Custom Field"
  value={customValue}
  onChange={(e) => setCustomValue(e.target.value)}
/>

// Add new buttons
<Button onClick={handleCustomAction}>
  Custom Action
</Button>

// Customize result display
<div className="custom-result-display">
  {/* Your custom rendering */}
</div>
```

### Adding Pre-Processing

Add preprocessing before sending to API:

```tsx
const handleTransform = async () => {
  // Pre-process input
  const processedText = preprocessText(inputText)
  
  // Send to API
  const response = await fetch('...', {
    body: JSON.stringify({
      text: processedText,
      // ... other params
    })
  })
}
```

---

## 🔬 Testing

### Test Rule-Based Transformation (Works Now)

```bash
# No LLM needed
curl -X POST http://localhost:7860/api/transform/text-to-json \
  -H "Content-Type: application/json" \
  -d '{"text": "this is a cat", "prefer_llm": false}'
```

### Test LLM-Based Transformation (Needs Model)

1. Deploy a model (e.g., `gpt2` or `Qwen/Qwen2-0.5B-Instruct`)
2. Wait for it to reach "RUNNING" status
3. Try transformation:

```bash
curl -X POST http://localhost:7860/api/transform/text-to-json \
  -H "Content-Type: application/json" \
  -d '{"text": "this is a cat", "prefer_llm": true}'
```

### Test from Frontend

1. Visit http://localhost:5173/transform
2. Enter: "this is a cat"
3. Click "Transform to JSON"
4. See result on the right side

---

## 📊 Current Status

### ✅ What Works Now

- ✅ Transform tab in UI
- ✅ API endpoints functional
- ✅ Rule-based transformation (no LLM needed)
- ✅ Schema hint support
- ✅ Method detection (LLM vs rule-based)
- ✅ Error handling
- ✅ Copy to clipboard
- ✅ Example suggestions

### ⚠️ What Needs LLM

- ⚠️ LLM-based transformation (requires deployed model)
- ⚠️ Complex entity extraction
- ⚠️ Context-aware transformations

### 🔮 Future Enhancements

1. **More Pattern Rules**
   - Add patterns for dates, numbers, locations
   - Support for multi-entity extraction
   - Complex relationship parsing

2. **Template System**
   - Predefined templates (e.g., "person", "product", "event")
   - User-defined templates
   - Template library

3. **Batch Processing**
   - Transform multiple texts at once
   - Export results as CSV/JSON
   - Progress tracking

4. **Validation**
   - JSON schema validation
   - Required field checking
   - Type enforcement

5. **History**
   - Save transformation history
   - Reuse previous transformations
   - Export history

---

## 🎯 Integration with Your Workflow

### Example: Product Catalog

```python
# Custom transformer for product descriptions
class ProductTransformer(TextToJsonTransformer):
    async def transform(self, text: str, schema_hint: Optional[str] = None):
        # Extract: name, price, category, features
        return {
            "product": {
                "name": extracted_name,
                "price": extracted_price,
                "category": extracted_category,
                "features": extracted_features
            }
        }
```

### Example: Customer Support

```python
# Extract support ticket information
class TicketTransformer(TextToJsonTransformer):
    async def transform(self, text: str, schema_hint: Optional[str] = None):
        return {
            "ticket": {
                "issue_type": detected_issue,
                "priority": calculated_priority,
                "category": determined_category,
                "sentiment": analyzed_sentiment
            }
        }
```

---

## 📚 API Documentation

Full API documentation available at:
- **Swagger UI**: http://localhost:7860/docs
- **ReDoc**: http://localhost:7860/redoc

Look for the "文本转换" (Transform) section.

---

## 🛠️ Troubleshooting

### "No running models available"

**Issue:** LLM-based transformation fails

**Solution:**
1. Go to Deploy tab
2. Deploy a model (e.g., `Qwen/Qwen2-0.5B-Instruct`)
3. Wait for "RUNNING" status
4. Try again

### "Transformation failed"

**Issue:** Result doesn't match expected format

**Solution:**
- Check your schema hint format
- Try with rule-based first (`prefer_llm: false`)
- Check API logs for details

### Rule-based gives unexpected results

**Issue:** Pattern not matching

**Solution:**
- Add custom patterns to `SimpleRuleBasedTransformer`
- Use LLM-based transformation for complex cases
- Provide schema hint for guidance

---

## 📝 Quick Reference

### Backend Files
- `backend/app/services/text_to_json_transformer.py` - Core transformation logic
- `backend/app/routers/transform.py` - API endpoints

### Frontend Files
- `frontend/src/pages/Transform.tsx` - Transform page UI
- `frontend/src/App.tsx` - Route registration
- `frontend/src/components/Layout.tsx` - Navigation

### API Endpoints
- `POST /api/transform/text-to-json` - Transform text
- `GET /api/transform/methods` - Check available methods

---

**Your Transform feature is ready! 🎉**

- ✅ Fully functional UI
- ✅ Decoupled architecture
- ✅ Easy to extend
- ✅ Works with or without LLM

Visit http://localhost:5173/transform to try it out!

