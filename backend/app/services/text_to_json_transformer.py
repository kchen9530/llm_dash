"""
Text to JSON Transformer Service
Decoupled service for transforming natural language to structured JSON using LLM
"""
import json
import re
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class TextToJsonTransformer(ABC):
    """
    Abstract base class for text-to-JSON transformation.
    Implement this interface for different transformation strategies.
    """
    
    @abstractmethod
    async def transform(self, text: str, schema_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Transform text to JSON structure
        
        Args:
            text: Input text to transform
            schema_hint: Optional hint about desired schema structure
            
        Returns:
            Dict containing the structured JSON
        """
        pass


class LLMBasedTransformer(TextToJsonTransformer):
    """
    LLM-based transformer using a running model instance.
    This uses the deployed models in the system.
    """
    
    def __init__(self, model_manager=None):
        from app.services.model_manager import ModelManager
        self.model_manager = model_manager or ModelManager()
    
    async def transform(self, text: str, schema_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Use LLM to transform text to JSON
        """
        # Get a running model
        models = self.model_manager.list_models()
        running_models = [m for m in models if m.status == "RUNNING"]
        
        if not running_models:
            raise ValueError("No running models available. Please deploy a model first.")
        
        # Use the first running model
        model = running_models[0]
        
        # Construct prompt for JSON extraction
        prompt = self._build_prompt(text, schema_hint)
        
        # Call the model (via HTTP to vLLM endpoint)
        import httpx
        
        vllm_url = f"http://localhost:{model.port}/v1/chat/completions"
        payload = {
            "model": model.model_name,
            "messages": [
                {"role": "system", "content": "You are a JSON extraction assistant. Extract structured data from text and return ONLY valid JSON. No explanations."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,  # Low temperature for consistent output
            "max_tokens": 256,
            "stream": False
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(vllm_url, json=payload)
                result = response.json()
                
                # Extract the JSON from the response
                content = result['choices'][0]['message']['content']
                return self._extract_json(content)
        
        except Exception as e:
            raise ValueError(f"LLM transformation failed: {str(e)}")
    
    def _build_prompt(self, text: str, schema_hint: Optional[str] = None) -> str:
        """Build the prompt for LLM"""
        if schema_hint:
            return f"""Extract structured information from the following text and format as JSON with this structure: {schema_hint}

Text: "{text}"

Return only the JSON, nothing else."""
        else:
            return f"""Extract the main entities and their properties from the following text and format as a two-level nested JSON structure.

Example format: {{"category": {{"attribute": "value"}}}}

Text: "{text}"

Return only the JSON, nothing else."""
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response (may include markdown code blocks)"""
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
                json_str = text.strip()
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON from LLM response: {str(e)}\nResponse: {text}")


class SimpleRuleBasedTransformer(TextToJsonTransformer):
    """
    Simple rule-based transformer for basic cases (fallback when no LLM available).
    This is a simple implementation - you can extend with more sophisticated rules.
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
    
    async def transform(self, text: str, schema_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Apply simple pattern matching rules
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


class TransformerFactory:
    """
    Factory for creating the appropriate transformer based on system state.
    This allows easy switching between different transformation strategies.
    """
    
    @staticmethod
    def create_transformer(prefer_llm: bool = True) -> TextToJsonTransformer:
        """
        Create a transformer instance.
        
        Args:
            prefer_llm: Try to use LLM-based transformer if models are available
            
        Returns:
            A TextToJsonTransformer instance
        """
        if prefer_llm:
            try:
                from app.services.model_manager import ModelManager
                manager = ModelManager()
                models = manager.list_models()
                running = [m for m in models if m.status == "RUNNING"]
                
                if running:
                    return LLMBasedTransformer(manager)
            except Exception:
                pass
        
        # Fallback to rule-based
        return SimpleRuleBasedTransformer()


# Convenience function for easy usage
async def transform_text_to_json(
    text: str, 
    schema_hint: Optional[str] = None,
    prefer_llm: bool = True
) -> Dict[str, Any]:
    """
    Transform text to JSON using the best available method.
    
    Args:
        text: Input text to transform
        schema_hint: Optional hint about desired structure
        prefer_llm: Try to use LLM if available
        
    Returns:
        Dict containing the structured JSON
        
    Example:
        >>> result = await transform_text_to_json("this is a cat")
        >>> print(result)
        {"pet": {"category": "cat"}}
    """
    transformer = TransformerFactory.create_transformer(prefer_llm)
    return await transformer.transform(text, schema_hint)


