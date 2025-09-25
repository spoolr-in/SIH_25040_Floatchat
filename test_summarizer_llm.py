#!/usr/bin/env python3
"""
Test the DataSummarizer LLM integration
"""

import sys
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from components.data_summarizer import DataSummarizer
from components.interpreter import create_interpreter, QueryEntity
from components.query_engine import QueryEngine

def test_summarizer_llm():
    """Test the data summarizer with LLM integration"""
    
    print("🧪 Testing Data Summarizer with LLM Integration")
    print("=" * 50)
    
    try:
        # Initialize components
        interpreter = create_interpreter()
        query_engine = QueryEngine('processed_data/master_dataset.parquet')
        
        # Test LLM connection
        llm_connected = interpreter.test_connection() if interpreter else False
        print(f"🔌 LLM Connection: {'✅ Connected' if llm_connected else '❌ Not available'}")
        
        # Initialize summarizer with interpreter
        summarizer = DataSummarizer(interpreter)
        
        # Get some test data
        test_data = query_engine.data.head(1000)
        
        # Create test entities
        test_entities = QueryEntity(
            parameter='temperature',
            location='indian ocean',
            date=None,
            date_range=None,
            depth_range=None
        )
        
        # Test summary generation
        print("\n🤖 Generating Summary...")
        summary = summarizer.generate_summary(
            test_data, 
            test_entities, 
            "Show me temperature in the Indian Ocean"
        )
        
        print(f"\n📝 Generated Summary:")
        print("-" * 30)
        print(summary)
        print("-" * 30)
        
        # Check if it's rule-based or LLM-enhanced
        if llm_connected and "Analysis Overview" not in summary:
            print("\n✅ LLM-enhanced summary detected!")
        else:
            print("\n📊 Using rule-based summary (LLM not available)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_summarizer_llm()
