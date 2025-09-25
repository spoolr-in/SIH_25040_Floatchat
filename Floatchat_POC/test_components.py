#!/usr/bin/env python3
"""
Test Script for FloatChat Components
Tests all components to ensure they work correctly.
"""

import sys
import os
from pathlib import Path
import logging

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from components.interpreter import create_interpreter
from components.query_engine import QueryEngine
from components.visualizer import DataVisualizer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_data_availability():
    """Test if the master dataset is available"""
    logger.info("Testing data availability...")
    
    data_path = Path("processed_data/master_dataset.parquet")
    if not data_path.exists():
        logger.error("Master dataset not found. Please run: python src/data_consolidation.py")
        return False
    
    logger.info("✅ Master dataset found")
    return True

def test_query_engine():
    """Test the query engine"""
    logger.info("Testing Query Engine...")
    
    try:
        engine = QueryEngine("processed_data/master_dataset.parquet")
        summary = engine.get_dataset_summary()
        
        logger.info(f"✅ Query Engine loaded {summary['total_records']} records")
        logger.info(f"   Float count: {summary['float_count']}")
        logger.info(f"   Parameters: {list(summary['parameter_counts'].keys())}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Query Engine test failed: {str(e)}")
        return False

def test_interpreter():
    """Test the AI interpreter"""
    logger.info("Testing AI Interpreter...")
    
    try:
        interpreter = create_interpreter()
        
        # Test query extraction
        test_query = "show me temperature in the Arabian Sea"
        entities = interpreter.extract_entities(test_query)
        
        logger.info(f"✅ Interpreter extracted entities:")
        logger.info(f"   Parameter: {entities.parameter}")
        logger.info(f"   Location: {entities.location}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Interpreter test failed: {str(e)}")
        return False

def test_visualizer():
    """Test the visualizer"""
    logger.info("Testing Visualizer...")
    
    try:
        visualizer = DataVisualizer()
        
        # Create a simple test with the query engine
        engine = QueryEngine("processed_data/master_dataset.parquet")
        
        # Get a small sample of data
        sample_data = engine.data.head(100)
        
        # Test map creation
        fig = visualizer.create_map_visualization(sample_data, parameter='temperature')
        
        if fig:
            logger.info("✅ Visualizer created map successfully")
            return True
        else:
            logger.error("❌ Visualizer failed to create map")
            return False
            
    except Exception as e:
        logger.error(f"❌ Visualizer test failed: {str(e)}")
        return False

def test_integration():
    """Test the full integration flow"""
    logger.info("Testing Full Integration...")
    
    try:
        # Initialize components
        interpreter = create_interpreter()
        engine = QueryEngine("processed_data/master_dataset.parquet")
        visualizer = DataVisualizer()
        
        # Test query
        test_query = "show temperature data"
        
        # Extract entities
        entities = interpreter.extract_entities(test_query)
        logger.info(f"Entities: parameter={entities.parameter}, location={entities.location}")
        
        # Execute query
        results = engine.execute_query(entities)
        logger.info(f"Query returned {len(results)} records")
        
        # Create visualization
        fig = visualizer.create_map_visualization(results, parameter=entities.parameter)
        
        if fig and len(results) > 0:
            logger.info("✅ Full integration test passed!")
            return True
        else:
            logger.error("❌ Integration test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Integration test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    logger.info("🧪 FloatChat Component Tests")
    logger.info("=" * 50)
    
    tests = [
        ("Data Availability", test_data_availability),
        ("Query Engine", test_query_engine),
        ("AI Interpreter", test_interpreter),
        ("Visualizer", test_visualizer),
        ("Full Integration", test_integration),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Running {test_name} test...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ {test_name} test crashed: {str(e)}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        logger.info("🎉 All tests passed! FloatChat is ready to run.")
        logger.info("Start the application with: streamlit run src/app.py")
    else:
        logger.info("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
