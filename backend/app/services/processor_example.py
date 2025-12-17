"""
Example Usage of Text Processor Architecture

This file demonstrates how to use the new processor architecture
for text-to-JSON conversion.
"""
import asyncio
from processor import (
    # Model abstractions
    LLMModel,
    EmbedModel,
    
    # Processor classes
    RuleBasedTextProcessor,
    LLMBasedTextProcessor,
    
    # Factory and convenience functions
    ProcessorFactory,
    process_text_to_json
)


async def example_rule_based():
    """
    Example 1: Using Rule-Based Processor (Currently Working)
    
    This processor uses regex patterns and is fast, deterministic,
    but limited to predefined patterns.
    """
    print("\n=== Example 1: Rule-Based Processing ===\n")
    
    # Method 1: Direct processor instantiation
    processor = RuleBasedTextProcessor()
    
    test_cases = [
        "this is a cat",
        "I have a red car",
        "dog named Max",
        "create a project with documentation"
    ]
    
    for text in test_cases:
        result = await processor.process(text)
        print(f"Input:  {text}")
        print(f"Output: {result}\n")


async def example_convenience_function():
    """
    Example 2: Using Convenience Function
    
    The easiest way to process text without manually creating processors.
    """
    print("\n=== Example 2: Convenience Function ===\n")
    
    result = await process_text_to_json(
        text="I have a blue bike",
        prefer_llm=False  # Use rule-based for now
    )
    
    print(f"Result: {result}")


async def example_factory():
    """
    Example 3: Using ProcessorFactory
    
    The factory automatically selects the best available processor.
    """
    print("\n=== Example 3: Factory Pattern ===\n")
    
    # Factory will return RuleBasedTextProcessor since LLM not implemented
    processor = ProcessorFactory.create_processor(prefer_llm=False)
    
    print(f"Created processor: {processor.__class__.__name__}")
    
    result = await processor.process("this is a test")
    print(f"Result: {result}")


async def example_llm_based_future():
    """
    Example 4: LLM-Based Processing (Future Implementation)
    
    This shows how the LLM-based processor will be used once implemented.
    Currently raises NotImplementedError.
    """
    print("\n=== Example 4: LLM-Based Processing (TODO) ===\n")
    
    # Step 1: Create model instances
    print("Creating models...")
    model1 = LLMModel(model_name="gpt2", device="cpu", max_length=512)
    model2 = LLMModel(model_name="Qwen/Qwen2-0.5B-Instruct", device="cpu")
    embed_model = EmbedModel(model_name="sentence-transformers/all-MiniLM-L6-v2", device="cpu")
    
    # Step 2: Load models (TODO: implement)
    # await model1.load()
    # await model2.load()
    # await embed_model.load()
    
    # Step 3: Create processor with multiple models
    processor = LLMBasedTextProcessor(
        model1=model1,
        model2=model2,
        embed_model1=embed_model
    )
    
    print(f"Created processor: {processor.__class__.__name__}")
    print("This processor uses:")
    print(f"  - Primary LLM: {model1.model_name}")
    print(f"  - Secondary LLM: {model2.model_name}")
    print(f"  - Embedding Model: {embed_model.model_name}")
    
    # Step 4: Process text (currently not implemented)
    try:
        result = await processor.process(
            text="Extract information from this complex sentence with multiple entities",
            schema_hint='{"entities": [{"type": "string", "value": "string"}]}'
        )
        print(f"Result: {result}")
    except NotImplementedError as e:
        print(f"\n❌ Not yet implemented: {e}")
        print("\n✅ TODO: Implement the multi-model processing pipeline")


async def example_custom_processor():
    """
    Example 5: Creating Custom Processor
    
    Shows how to extend the architecture with your own processor.
    """
    print("\n=== Example 5: Custom Processor ===\n")
    
    from processor import TextProcessor
    from typing import Dict, Any, Optional
    
    class CustomProcessor(TextProcessor):
        """Example custom processor"""
        
        async def process(self, text: str, schema_hint: Optional[str] = None) -> Dict[str, Any]:
            """Custom processing logic"""
            # Example: Always return a fixed structure
            return {
                "custom": {
                    "input": text,
                    "length": len(text),
                    "word_count": len(text.split()),
                    "hint": schema_hint
                }
            }
    
    processor = CustomProcessor()
    result = await processor.process("Hello world")
    print(f"Result: {result}")


async def main():
    """Run all examples"""
    print("=" * 60)
    print("Text Processor Architecture Examples")
    print("=" * 60)
    
    # Run working examples
    await example_rule_based()
    await example_convenience_function()
    await example_factory()
    
    # Show future LLM-based usage
    await example_llm_based_future()
    
    # Show extensibility
    await example_custom_processor()
    
    print("\n" + "=" * 60)
    print("Examples Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
