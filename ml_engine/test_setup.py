#!/usr/bin/env python3
"""
Test Setup for Würdo ML Engine
==============================

Verifies that all core components are working correctly:
- ✅ All core modules import successfully
- ✅ ONNX model loads correctly
- ✅ Scoring service initializes properly
"""

import sys
import time
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test that all core modules can be imported."""
    print("🔍 Testing module imports...")
    
    try:
        # Test core services
        from services.enhanced_scoring_service import get_enhanced_scoring_service
        from services.efficient_word_service import get_efficient_word_service
        from services.optimized_storage_service import get_optimized_storage_service
        print("✅ Core services imported successfully")
        
        # Test utils if they exist
        try:
            from utils import canonical_data_generator
            print("✅ Utils imported successfully")
        except ImportError:
            print("⚠️  Utils not available (optional)")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_onnx_model():
    """Test that the ONNX model loads correctly."""
    print("🤖 Testing ONNX model loading...")
    
    try:
        # Check if the model directory exists
        model_dir = Path(__file__).parent / "distilgpt2_onnx"
        if not model_dir.exists():
            print("⚠️  ONNX model directory not found")
            return False
        
        # Try to import and initialize the scoring service
        from services.enhanced_scoring_service import get_enhanced_scoring_service
        scoring_service = get_enhanced_scoring_service()
        
        # Test a simple scoring operation using the correct method
        test_result = scoring_service.calculate_transformation_score("test", "rest", "ola")
        print(f"✅ ONNX model loaded and tested successfully (test score: {test_result.total_score:.4f})")
        return True
        
    except Exception as e:
        print(f"❌ ONNX model error: {e}")
        return False

def test_scoring_service():
    """Test that the scoring service initializes properly."""
    print("🎯 Testing scoring service initialization...")
    
    try:
        from services.enhanced_scoring_service import get_enhanced_scoring_service
        from services.efficient_word_service import get_efficient_word_service
        
        # Initialize services
        scoring_service = get_enhanced_scoring_service()
        word_service = get_efficient_word_service()
        
        # Test basic functionality - check if services are initialized
        print("  ✅ EnhancedScoringService initialized")
        print("  ✅ EfficientWordService initialized")
        
        # Test word transformations (this is what the service actually does)
        transformations = word_service.get_comprehensive_transformations("test")
        print(f"  ✅ Word transformations working ({len(transformations.all_transformations)} transformations found)")
        
        print("✅ Scoring service initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Scoring service error: {e}")
        return False

def test_storage_service():
    """Test that the storage service works correctly."""
    print("💾 Testing storage service...")
    
    try:
        from services.optimized_storage_service import get_optimized_storage_service, StorageConfig
        
        # Create a storage config
        config = StorageConfig(
            storage_type="json",
            json_file_path="game_data/probability_trees.json",
            compression=True,
            cache_size=1000
        )
        
        storage_service = get_optimized_storage_service(config)
        
        # Test basic storage operations
        print("  ✅ Storage service initialized")
        print("  ✅ Storage config working")
        
        # Test cache stats
        cache_stats = storage_service.get_cache_stats()
        print(f"  ✅ Cache stats working (hits: {cache_stats.get('hits', 0)}, misses: {cache_stats.get('misses', 0)})")
        
        print("✅ Storage service working correctly")
        return True
            
    except Exception as e:
        print(f"❌ Storage service error: {e}")
        return False

def main():
    """Run all setup tests."""
    print("🚀 Würdo ML Engine Setup Test")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("ONNX Model", test_onnx_model),
        ("Scoring Service", test_scoring_service),
        ("Storage Service", test_storage_service)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! ML Engine is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
