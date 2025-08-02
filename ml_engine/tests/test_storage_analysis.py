#!/usr/bin/env python3
"""
Test script to analyze storage requirements for probability vectors.
"""

import sys
import os
import json
import struct
import numpy as np
from datetime import datetime
from io import StringIO
import contextlib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.advanced_scorer import get_advanced_scorer

def analyze_storage_requirements():
    """Analyze the actual storage requirements for probability vectors."""
    
    # Capture console output
    output_buffer = StringIO()
    
    with contextlib.redirect_stdout(output_buffer):
        print("Probability Vector Storage Analysis\n")
        print("=" * 50)
        
        try:
            # Initialize scorer
            print("1. Initializing scorer...")
            scorer = get_advanced_scorer()
            print("Scorer initialized successfully")
            
            # Get a sample probability vector
            print("\n2. Getting sample probability vector...")
            prompt = "a word that rhymes with cat"
            vector_data = scorer.get_probability_vector(prompt)
            
            # Analyze different storage formats
            print("\n3. Storage Format Analysis")
            print("-" * 40)
            
            # Raw probabilities as float32
            probs_float32 = np.array(vector_data["probability_vector"], dtype=np.float32)
            float32_size = len(probs_float32.tobytes())
            
            # Raw probabilities as float64
            probs_float64 = np.array(vector_data["probability_vector"], dtype=np.float64)
            float64_size = len(probs_float64.tobytes())
            
            # JSON representation
            json_str = json.dumps(vector_data["probability_vector"])
            json_size = len(json_str.encode('utf-8'))
            
            # Compressed JSON (gzip)
            import gzip
            json_compressed = gzip.compress(json_str.encode('utf-8'))
            json_compressed_size = len(json_compressed)
            
            # Binary format (custom)
            binary_data = struct.pack(f'{len(vector_data["probability_vector"])}f', *vector_data["probability_vector"])
            binary_size = len(binary_data)
            
            # Redis storage analysis
            redis_analysis = {
                "vocabulary_size": vector_data["vocabulary_size"],
                "storage_formats": {
                    "float32_binary": {
                        "size_bytes": float32_size,
                        "size_kb": float32_size / 1024,
                        "size_mb": float32_size / (1024 * 1024),
                        "description": "Raw binary float32 array"
                    },
                    "float64_binary": {
                        "size_bytes": float64_size,
                        "size_kb": float64_size / 1024,
                        "size_mb": float64_size / (1024 * 1024),
                        "description": "Raw binary float64 array"
                    },
                    "json_string": {
                        "size_bytes": json_size,
                        "size_kb": json_size / 1024,
                        "size_mb": json_size / (1024 * 1024),
                        "description": "JSON string representation"
                    },
                    "json_compressed": {
                        "size_bytes": json_compressed_size,
                        "size_kb": json_compressed_size / 1024,
                        "size_mb": json_compressed_size / (1024 * 1024),
                        "description": "Gzip compressed JSON"
                    },
                    "binary_custom": {
                        "size_bytes": binary_size,
                        "size_kb": binary_size / 1024,
                        "size_mb": binary_size / (1024 * 1024),
                        "description": "Custom binary format"
                    }
                }
            }
            
            # Print results
            print(f"Vocabulary size: {vector_data['vocabulary_size']:,} tokens")
            print(f"Max probability: {vector_data['max_probability']:.8f}")
            print()
            
            print("Storage Requirements:")
            print("-" * 20)
            
            for format_name, data in redis_analysis["storage_formats"].items():
                print(f"{format_name.replace('_', ' ').title()}:")
                print(f"  Size: {data['size_bytes']:,} bytes ({data['size_kb']:.2f} KB)")
                print(f"  Description: {data['description']}")
                print()
            
            # Real-world scenarios
            print("4. Real-World Storage Scenarios")
            print("-" * 40)
            
            # Common start words (estimate 1000 common words)
            common_words = 1000
            float32_total = common_words * redis_analysis["storage_formats"]["float32_binary"]["size_mb"]
            json_total = common_words * redis_analysis["storage_formats"]["json_string"]["size_mb"]
            compressed_total = common_words * redis_analysis["storage_formats"]["json_compressed"]["size_mb"]
            
            print(f"1000 common start words:")
            print(f"  Float32: {float32_total:.2f} MB")
            print(f"  JSON: {json_total:.2f} MB")
            print(f"  Compressed: {compressed_total:.2f} MB")
            print()
            
            # All possible 3-7 letter words (estimate 50,000 words)
            all_words = 50000
            float32_all = all_words * redis_analysis["storage_formats"]["float32_binary"]["size_mb"]
            json_all = all_words * redis_analysis["storage_formats"]["json_string"]["size_mb"]
            compressed_all = all_words * redis_analysis["storage_formats"]["json_compressed"]["size_mb"]
            
            print(f"50,000 start words (full database):")
            print(f"  Float32: {float32_all:.2f} MB")
            print(f"  JSON: {json_all:.2f} MB")
            print(f"  Compressed: {compressed_all:.2f} MB")
            print()
            
            # Redis cost analysis
            print("5. Redis Storage Cost Analysis")
            print("-" * 40)
            
            # Redis pricing (approximate)
            # Upstash Redis: $0.25 per GB per month
            redis_cost_per_gb_month = 0.25
            
            float32_cost_month = (float32_all / 1024) * redis_cost_per_gb_month
            json_cost_month = (json_all / 1024) * redis_cost_per_gb_month
            compressed_cost_month = (compressed_all / 1024) * redis_cost_per_gb_month
            
            print(f"Monthly Redis costs (50k vectors):")
            print(f"  Float32: ${float32_cost_month:.2f}/month")
            print(f"  JSON: ${json_cost_month:.2f}/month")
            print(f"  Compressed: ${compressed_cost_month:.2f}/month")
            print()
            
            # Recommendations
            print("6. Storage Recommendations")
            print("-" * 40)
            
            print("✅ Float32 binary format is most efficient:")
            print(f"   - {redis_analysis['storage_formats']['float32_binary']['size_kb']:.2f} KB per vector")
            print(f"   - {float32_all:.2f} MB for 50k vectors")
            print(f"   - ${float32_cost_month:.2f}/month for Redis storage")
            print()
            
            print("✅ JSON format is human-readable but larger:")
            print(f"   - {redis_analysis['storage_formats']['json_string']['size_kb']:.2f} KB per vector")
            print(f"   - {json_all:.2f} MB for 50k vectors")
            print(f"   - ${json_cost_month:.2f}/month for Redis storage")
            print()
            
            print("✅ Compressed JSON is a good compromise:")
            print(f"   - {redis_analysis['storage_formats']['json_compressed']['size_kb']:.2f} KB per vector")
            print(f"   - {compressed_all:.2f} MB for 50k vectors")
            print(f"   - ${compressed_cost_month:.2f}/month for Redis storage")
            
            # Save results
            results = {
                "analysis_timestamp": datetime.now().isoformat(),
                "vocabulary_size": vector_data["vocabulary_size"],
                "storage_analysis": redis_analysis,
                "scenarios": {
                    "common_words_1000": {
                        "float32_mb": float32_total,
                        "json_mb": json_total,
                        "compressed_mb": compressed_total
                    },
                    "all_words_50000": {
                        "float32_mb": float32_all,
                        "json_mb": json_all,
                        "compressed_mb": compressed_all
                    }
                },
                "cost_analysis": {
                    "redis_cost_per_gb_month": redis_cost_per_gb_month,
                    "monthly_costs_50k": {
                        "float32": float32_cost_month,
                        "json": json_cost_month,
                        "compressed": compressed_cost_month
                    }
                }
            }
            
            # Save console output
            console_output = output_buffer.getvalue()
            console_file = "shared_results/storage_analysis_console.txt"
            os.makedirs("shared_results", exist_ok=True)
            
            with open(console_file, 'w') as f:
                f.write(console_output)
            
            print(f"\nConsole output saved to: {console_file}")
            
            # Save JSON results
            json_file = "shared_results/storage_analysis_results.json"
            with open(json_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"JSON results saved to: {json_file}")
            
            return True
            
        except Exception as e:
            print(f"Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = analyze_storage_requirements()
    sys.exit(0 if success else 1) 