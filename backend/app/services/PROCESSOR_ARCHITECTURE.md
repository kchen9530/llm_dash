# Text Processing Architecture

## Overview

This module provides a flexible, extensible architecture for processing natural language text into structured JSON using different strategies.

## Architecture

### 1. Model Abstraction Layer

#### `BaseModel` (Abstract)
Base class for all model types with common interface:
- `load()` - Load model into memory
- `unload()` - Free model from memory
- `device` - "cpu" or "gpu"

#### `LLMModel` (Concrete)
Represents Language Models (GPT, Qwen, LLaMA, etc.):
```python
model = LLMModel(model_name="gpt2", device="cpu", max_length=512)
await model.load()
text = await model.generate(prompt="Hello", max_tokens=100)
```

**Status:** 🚧 Interface defined, implementation TODO

#### `EmbedModel` (Concrete)
Represents Embedding Models (sentence-transformers, BGE, etc.):
```python
model = EmbedModel(model_name="all-MiniLM-L6-v2", device="cpu")
await model.load()
vector = await model.encode("some text")  # Returns list[float]
```

**Status:** 🚧 Interface defined, implementation TODO

---

### 2. Text Processor Layer

#### `TextProcessor` (Abstract)
Base interface for all text processing strategies:
```python
async def process(text: str, schema_hint: Optional[str]) -> Dict[str, Any]
```

#### `RuleBasedTextProcessor` (Concrete)
Simple, fast processor using regex patterns:

**Features:**
- ✅ No models required
- ✅ Deterministic output
- ✅ Fast execution
- ❌ Limited patterns
- ❌ No context understanding

**Example:**
```python
processor = RuleBasedTextProcessor()
result = await processor.process("this is a cat")
# Returns: {"item": {"category": "cat"}}
```

**Status:** ✅ Fully implemented

#### `LLMBasedTextProcessor` (Concrete)
Advanced processor using multiple AI models:

**Architecture:**
```
Input Text
    ↓
[Semantic Analysis via embed_model1]
    ↓
[Primary Extraction via model1]
    ↓
[Validation & Refinement via model2]
    ↓
Structured JSON Output
```

**Constructor:**
```python
processor = LLMBasedTextProcessor(
    model1=LLMModel("gpt2", device="cpu"),
    model2=LLMModel("qwen", device="gpu"),
    embed_model1=EmbedModel("all-MiniLM-L6-v2", device="cpu")
)
```

**Status:** 🚧 Architecture defined, implementation TODO

**TODO Implementation Steps:**
1. `_semantic_analysis()` - Use embed_model1 to understand intent
2. `_primary_extraction()` - Use model1 to extract structured data
3. `_validate_and_refine()` - Use model2 to validate/improve
4. Combine all insights into robust JSON output

---

## Usage

### Basic Usage (Rule-Based)
```python
from app.services.processor import process_text_to_json

result = await process_text_to_json(
    text="I have a red car",
    prefer_llm=False
)
# Returns: {"item": {"color": "red", "type": "car"}}
```

### Advanced Usage (Future - Multi-Model)
```python
from app.services.processor import (
    LLMModel,
    EmbedModel,
    LLMBasedTextProcessor,
    process_text_to_json
)

# Create models
model1 = LLMModel("gpt2", device="cpu")
model2 = LLMModel("qwen", device="gpu")
embed = EmbedModel("all-MiniLM-L6-v2", device="cpu")

# Create processor
processor = LLMBasedTextProcessor(model1, model2, embed)

# Process text
result = await process_text_to_json(
    text="Complex query requiring understanding",
    processor=processor
)
```

### Using Factory
```python
from app.services.processor import ProcessorFactory

# Automatically chooses best available processor
processor = ProcessorFactory.create_processor(prefer_llm=True)
result = await processor.process("some text")
```

---

## Implementation Roadmap

### Phase 1: ✅ Architecture Setup
- [x] Define base classes
- [x] Implement RuleBasedTextProcessor
- [x] Create factory pattern
- [x] Integrate with API router

### Phase 2: 🚧 Model Integration (TODO)
- [ ] Implement LLMModel.load() using CPUModelRunner
- [ ] Implement LLMModel.generate()
- [ ] Implement EmbedModel.load() using EmbeddingModelHandler
- [ ] Implement EmbedModel.encode()
- [ ] Add GPU support detection and routing

### Phase 3: 🚧 LLM Processor (TODO)
- [ ] Implement semantic analysis step
- [ ] Implement primary extraction with prompt engineering
- [ ] Implement validation and refinement logic
- [ ] Add error handling and fallbacks
- [ ] Add confidence scoring

### Phase 4: 🚧 Advanced Features (Future)
- [ ] Chain-of-thought reasoning
- [ ] Multi-step refinement pipeline
- [ ] Parallel model execution
- [ ] Caching and optimization
- [ ] Custom schema validation

---

## Design Benefits

1. **Separation of Concerns**
   - Models are separate from processing logic
   - Easy to swap implementations

2. **Extensibility**
   - Add new model types (e.g., MultimodalModel)
   - Add new processors (e.g., HybridProcessor)

3. **Testability**
   - Mock models for unit testing
   - Test processors independently

4. **Future-Proof**
   - Ready for multi-model architectures
   - Supports both CPU and GPU deployment

---

## Migration Notes

**Old Code:**
```python
from app.services.text_to_json_transformer import transform_text_to_json
result = await transform_text_to_json(text, schema_hint, prefer_llm)
```

**New Code:**
```python
from app.services.processor import process_text_to_json
result = await process_text_to_json(text, schema_hint, prefer_llm)
```

The API is backward compatible! The old `text_to_json_transformer.py` can be kept for reference or gradually phased out.

---

## Contributing

When implementing TODO sections:

1. **Follow the established patterns** - Use async/await, proper error handling
2. **Add comprehensive docstrings** - Explain parameters and return values
3. **Write tests** - Unit tests for each processor and model type
4. **Update this documentation** - Keep architecture docs in sync
5. **Consider performance** - Multi-model processing should be optimized

---

## Questions?

See existing code:
- `processor.py` - Main architecture
- `transform.py` - API integration example
- `text_to_json_transformer.py` - Legacy implementation for reference
