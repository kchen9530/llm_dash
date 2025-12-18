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
    
    Pipeline:
    1. Model1: Generate category JSON from user input
    2. Model2: Generate detailed JSON based on category
    3. EmbedModel: Add embedding information to final JSON
    """
    
    def __init__(
        self,
        model1_id: str,
        model2_id: str,
        embed_model_id: str
    ):
        """
        Initialize with deployed model IDs
        
        Args:
            model1_id: ID of deployed LLM for category generation
            model2_id: ID of deployed LLM for detail generation
            embed_model_id: ID of deployed embedding model
        """
        self.model1_id = model1_id
        self.model2_id = model2_id
        self.embed_model_id = embed_model_id
    
    async def process(self, text: str, schema_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Process text using 3-step LLM pipeline
        
        Step 1: Generate category JSON using model1
        Step 2: Generate detailed JSON using model2
        Step 3: Add embedding info using embed model
        """
        import httpx
        
        # Step 1: Generate category JSON with model1
        category_json = await self._generate_category(text, self.model1_id)
        
        # Step 2: Generate detailed JSON with model2
        detailed_json = await self._generate_details(text, category_json, self.model2_id, schema_hint)
        
        # Step 3: Add embedding information
        final_json = await self._add_embedding_info(text, detailed_json, self.embed_model_id)
        
        return final_json
    
    async def _generate_category(self, text: str, model_id: str) -> Dict[str, Any]:
        """
        Step 1: Generate high-level category using model1
        """
        import httpx
        
        # Get model info
        from app.services.lightweight_model_manager import LightweightModelManager
        manager = LightweightModelManager()
        model_info = manager.get_model(model_id)
        
        if not model_info or model_info.status != "RUNNING":
            raise ValueError(f"Model {model_id} is not running")
        
        # Build prompt for category extraction
        prompt = f"""Extract the main category or type from this text and return ONLY a JSON object.

Text: "{text}"

Return a JSON object with this structure: {{"category": "main_category", "type": "specific_type"}}

JSON:"""
        
        # Generate using lightweight manager
        response = await manager.generate(
            model_id=model_id,
            prompt=prompt,
            max_tokens=100,
            temperature=0.3
        )
        
        # Extract JSON from response
        return self._extract_json(response)
    
    async def _generate_details(
        self, 
        text: str, 
        category_json: Dict[str, Any], 
        model_id: str,
        schema_hint: Optional[str]
    ) -> Dict[str, Any]:
        """
        Step 2: Generate detailed JSON using model2
        """
        from app.services.lightweight_model_manager import LightweightModelManager
        manager = LightweightModelManager()
        model_info = manager.get_model(model_id)
        
        if not model_info or model_info.status != "RUNNING":
            raise ValueError(f"Model {model_id} is not running")
        
        # Build prompt with category context
        category_str = json.dumps(category_json)
        schema_instruction = f"\nDesired structure: {schema_hint}" if schema_hint else ""
        
        prompt = f"""Given the category information, extract detailed structured information from the text.

Text: "{text}"
Category: {category_str}{schema_instruction}

Return a detailed JSON object with all relevant attributes and properties.

JSON:"""
        
        # Generate details
        response = await manager.generate(
            model_id=model_id,
            prompt=prompt,
            max_tokens=200,
            temperature=0.3
        )
        
        # Extract and merge with category
        detailed = self._extract_json(response)
        
        # Merge category info into detailed JSON
        return {
            **category_json,
            "details": detailed
        }
    
    async def _add_embedding_info(
        self, 
        text: str, 
        json_data: Dict[str, Any],
        embed_model_id: str
    ) -> Dict[str, Any]:
        """
        Step 3: Add embedding information using embed model
        """
        from app.services.lightweight_model_manager import LightweightModelManager
        manager = LightweightModelManager()
        
        # Get embedding model instance
        instances = manager.list_embedding_models()
        embed_instance = None
        for inst in instances:
            if inst.id == embed_model_id:
                embed_instance = manager._instances.get(embed_model_id)
                break
        
        if not embed_instance or not embed_instance.embedding_handler:
            raise ValueError(f"Embedding model {embed_model_id} is not loaded")
        
        # Generate embedding
        embedding = await embed_instance.embedding_handler.encode(text)
        
        # Add embedding info to JSON
        result = {
            **json_data,
            "embedding_info": {
                "model": embed_instance.model_name,
                "dimension": len(embedding),
                "vector_preview": embedding[:10],  # First 10 values
                "vector_norm": sum(x*x for x in embedding) ** 0.5
            }
        }
        
        return result
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response"""
        import re
        
        # Try to find JSON in code blocks first
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                # Fallback: return simple structure
                return {"text": text.strip(), "raw": True}
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback
            return {"text": text.strip(), "parse_error": True}


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
        model1_id: Optional[str] = None,
        model2_id: Optional[str] = None,
        embed_model_id: Optional[str] = None
    ) -> TextProcessor:
        """
        Create appropriate text processor
        
        Args:
            prefer_llm: Try to use LLM-based processor if available
            model1_id: ID of deployed LLM for category generation
            model2_id: ID of deployed LLM for detail generation
            embed_model_id: ID of deployed embedding model
            
        Returns:
            TextProcessor instance
        """
        if prefer_llm and model1_id and model2_id and embed_model_id:
            # Verify models are running
            from app.services.lightweight_model_manager import LightweightModelManager
            manager = LightweightModelManager()
            
            # Check if all models exist and are running
            model1 = manager.get_model(model1_id)
            model2 = manager.get_model(model2_id)
            embed = manager.get_model(embed_model_id)
            
            if (model1 and model1.status == "RUNNING" and
                model2 and model2.status == "RUNNING" and
                embed and embed.status == "RUNNING"):
                return LLMBasedTextProcessor(model1_id, model2_id, embed_model_id)
        
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
