"""
Text Processing Framework
Provides abstraction for text-to-JSON processing with different strategies
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
import re


# ============================================================================
# Model Abstractions
# ============================================================================

class BaseModel(ABC):
    """
    Base class for all model types (LLM, Embedding, etc.)
    """
    
    def __init__(self, model_name: str, device: str = "cpu"):
        """
        Args:
            model_name: Name/identifier of the model
            device: "cpu" or "gpu"
        """
        self.model_name = model_name
        self.device = device
        self.is_loaded = False
    
    @abstractmethod
    async def load(self):
        """Load the model into memory"""
        pass
    
    @abstractmethod
    async def unload(self):
        """Unload the model from memory"""
        pass


class LLMModel(BaseModel):
    """
    Abstraction for Language Models (GPT, Qwen, etc.)
    Handles text generation and completion
    """
    
    def __init__(self, model_name: str, device: str = "cpu", max_length: int = 512):
        super().__init__(model_name, device)
        self.max_length = max_length
    
    async def load(self):
        """Load the LLM model"""
        # TODO: Implement model loading logic
        # This would use the existing CPUModelRunner or GPU inference
        self.is_loaded = True
    
    async def unload(self):
        """Unload the LLM model"""
        # TODO: Implement model unloading logic
        self.is_loaded = False
    
    async def generate(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
        """
        Generate text from prompt
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        # TODO: Implement text generation
        # This would call the actual model inference
        raise NotImplementedError("LLMModel.generate() not yet implemented")


class EmbedModel(BaseModel):
    """
    Abstraction for Embedding Models (sentence-transformers, etc.)
    Converts text to vector representations
    """
    
    def __init__(self, model_name: str, device: str = "cpu"):
        super().__init__(model_name, device)
        self.embedding_dim = None
    
    async def load(self):
        """Load the embedding model"""
        # TODO: Implement embedding model loading
        # This would use the existing EmbeddingModelHandler
        self.is_loaded = True
    
    async def unload(self):
        """Unload the embedding model"""
        # TODO: Implement embedding model unloading
        self.is_loaded = False
    
    async def encode(self, text: str) -> list[float]:
        """
        Convert text to embedding vector
        
        Args:
            text: Input text
            
        Returns:
            List of floats representing the embedding
        """
        # TODO: Implement text encoding
        # This would call the actual embedding model
        raise NotImplementedError("EmbedModel.encode() not yet implemented")
    
    async def encode_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Convert multiple texts to embeddings (more efficient)
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        # TODO: Implement batch encoding
        raise NotImplementedError("EmbedModel.encode_batch() not yet implemented")


# ============================================================================
# Text Processor Abstractions
# ============================================================================

class TextProcessor(ABC):
    """
    Base class for text processing strategies.
    Converts natural language text to structured JSON.
    """
    
    @abstractmethod
    async def process(self, text: str, schema_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Process text and convert to structured JSON
        
        Args:
            text: Input text to process
            schema_hint: Optional hint about desired JSON structure
            
        Returns:
            Dictionary containing structured JSON
        """
        pass


class RuleBasedTextProcessor(TextProcessor):
    """
    Simple rule-based text processor using regex patterns.
    Fast and deterministic, but limited to predefined patterns.
    """
    
    PATTERNS = [
        # Pattern: "this is a [category]"
        (r'this is (?:a|an) (\w+)', lambda m: {"item": {"category": m.group(1)}}),
        
        # Pattern: "I have a [color] [item]"
        (r'I have (?:a|an) (\w+) (\w+)', lambda m: {"item": {"color": m.group(1), "type": m.group(2)}}),
        
        # Pattern: "create a [name] with [property]"
        (r'create (?:a|an) (\w+) with (\w+)', lambda m: {"object": {"name": m.group(1), "property": m.group(2)}}),
        
        # Pattern: "[pet] named [name]"
        (r'(\w+) named (\w+)', lambda m: {m.group(1): {"name": m.group(2)}}),
    ]
    
    async def process(self, text: str, schema_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Apply rule-based pattern matching to extract structured data
        """
        text_lower = text.lower().strip()
        
        # Try each pattern
        for pattern, extractor in self.PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                return extractor(match)
        
        # Fallback: extract key entities
        words = text_lower.split()
        if len(words) > 0:
            # Simple heuristic: last word is likely the category
            category = words[-1].strip('.,!?')
            return {"entity": {"category": category, "original": text}}
        
        return {"entity": {"text": text}}


class LLMBasedTextProcessor(TextProcessor):
    """
    Advanced text processor using multiple LLMs and embedding models.
    
    This processor can leverage multiple models for sophisticated processing:
    - model1: Primary LLM for understanding and extraction
    - model2: Secondary LLM for validation or refinement
    - embed_model1: Embedding model for semantic analysis
    
    TODO: Implement advanced multi-model processing logic:
    1. Use embed_model1 to analyze semantic meaning of input
    2. Use model1 for initial structured extraction
    3. Use model2 to validate/refine the extraction
    4. Combine insights from all models for robust JSON output
    
    Future enhancements:
    - Chain-of-thought reasoning across models
    - Semantic similarity checks using embeddings
    - Multi-step refinement pipeline
    - Confidence scoring and validation
    """
    
    def __init__(
        self,
        model1: LLMModel,
        model2: LLMModel,
        embed_model1: EmbedModel
    ):
        """
        Initialize with multiple models for complex processing
        
        Args:
            model1: Primary LLM for text understanding
            model2: Secondary LLM for validation/refinement
            embed_model1: Embedding model for semantic analysis
        """
        self.model1 = model1
        self.model2 = model2
        self.embed_model1 = embed_model1
    
    async def process(self, text: str, schema_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Process text using multi-model approach
        
        TODO: Implement multi-model processing pipeline:
        
        Step 1: Semantic Analysis
        - Use embed_model1 to get text embedding
        - Analyze semantic features to understand intent
        
        Step 2: Primary Extraction
        - Use model1 to extract structured information
        - Apply schema_hint if provided
        
        Step 3: Validation & Refinement
        - Use model2 to validate extracted data
        - Cross-check with semantic analysis from Step 1
        - Refine or correct any inconsistencies
        
        Step 4: Combine Results
        - Merge insights from all models
        - Return robust, validated JSON structure
        """
        # TODO: Implement the processing pipeline
        # For now, raise NotImplementedError as a placeholder
        raise NotImplementedError(
            "LLMBasedTextProcessor is not yet implemented. "
            "This will be a sophisticated multi-model processing system. "
            "For now, use RuleBasedTextProcessor."
        )
    
    async def _semantic_analysis(self, text: str) -> Dict[str, Any]:
        """
        TODO: Analyze text semantics using embedding model
        
        Returns:
            Dictionary with semantic features
        """
        raise NotImplementedError("Semantic analysis not yet implemented")
    
    async def _primary_extraction(self, text: str, schema_hint: Optional[str]) -> Dict[str, Any]:
        """
        TODO: Extract structured data using primary LLM
        
        Returns:
            Initial structured extraction
        """
        raise NotImplementedError("Primary extraction not yet implemented")
    
    async def _validate_and_refine(
        self,
        text: str,
        extraction: Dict[str, Any],
        semantic_features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        TODO: Validate and refine extraction using secondary LLM
        
        Returns:
            Refined and validated extraction
        """
        raise NotImplementedError("Validation not yet implemented")


# ============================================================================
# Factory for Easy Creation
# ============================================================================

class ProcessorFactory:
    """
    Factory for creating text processors based on available resources
    """
    
    @staticmethod
    def create_processor(
        prefer_llm: bool = False,
        model1: Optional[LLMModel] = None,
        model2: Optional[LLMModel] = None,
        embed_model1: Optional[EmbedModel] = None
    ) -> TextProcessor:
        """
        Create appropriate text processor
        
        Args:
            prefer_llm: Try to use LLM-based processor if available
            model1: Primary LLM (required for LLM-based)
            model2: Secondary LLM (required for LLM-based)
            embed_model1: Embedding model (required for LLM-based)
            
        Returns:
            TextProcessor instance
        """
        if prefer_llm and model1 and model2 and embed_model1:
            # TODO: Once LLMBasedTextProcessor is implemented, uncomment:
            # return LLMBasedTextProcessor(model1, model2, embed_model1)
            pass
        
        # Default to rule-based processor
        return RuleBasedTextProcessor()


# ============================================================================
# Convenience Function
# ============================================================================

async def process_text_to_json(
    text: str,
    schema_hint: Optional[str] = None,
    prefer_llm: bool = False,
    processor: Optional[TextProcessor] = None
) -> Dict[str, Any]:
    """
    Convenience function to process text to JSON
    
    Args:
        text: Input text to process
        schema_hint: Optional structure hint
        prefer_llm: Try to use LLM-based processing
        processor: Optional pre-configured processor (overrides prefer_llm)
        
    Returns:
        Structured JSON dictionary
    """
    if processor is None:
        processor = ProcessorFactory.create_processor(prefer_llm=prefer_llm)
    
    return await processor.process(text, schema_hint)
