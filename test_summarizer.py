#!/usr/bin/env python3
"""
Test script for the data summarizer component
"""

import sys
sys.path.append('src')

import pandas as pd
from components.query_engine import QueryEngine
from components.interpreter import QueryEntity
from components.data_summarizer import DataSummarizer
from components.visualizer import DataVisualizer

def test_summarizer():
    """Test the data summarizer component"""
    
    # Initialize components
    engine = QueryEngine('processed_data/master_dataset.parquet')
    summarizer = DataSummarizer()
    visualizer = DataVisualizer()
    
    # Create test data
    test_data = engine.data.dropna(subset=['temperature']).head(100)
    
    # Create test entities
    entities = QueryEntity(
        parameter='temperature',
        location='Indian Ocean',
        date=None,
        date_range=None,
        depth_range=None
    )
    
    # Get stats
    stats = visualizer.get_summary_stats(test_data, 'temperature')
    print(f"Stats: {stats}")
    print(f"Stats type: {type(stats)}")
    
    # Test summary generation
    try:
        summary = summarizer.generate_summary(
            test_data, 
            entities, 
            "Show me temperature data in the Indian Ocean",
            stats
        )
        print(f"✅ Summary generated successfully:")
        print(summary)
    except Exception as e:
        print(f"❌ Summary generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_summarizer()
