#!/usr/bin/env python3
"""
Examine stored probability tree data to verify probabilities were captured correctly.
"""

import json
import gzip
import pickle
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.probability_tree import WordProbabilityTree

def examine_stored_data():
    """Examine the stored probability tree data."""
    
    # Load the JSON data
    with open('probability_trees.json', 'r') as f:
        data = json.load(f)
    
    print("📊 Examining stored probability tree data...")
    print(f"📁 File contains {len(data)} entries")
    
    # Get the xylophone data
    xylophone_data = data['xylophone']
    print(f"📦 Xylophone data size: {xylophone_data['metadata']['size_bytes']} bytes")
    print(f"📅 Stored at: {xylophone_data['metadata']['stored_at']}")
    
    # Decompress and deserialize
    serialized = xylophone_data['serialized']
    decompressed = gzip.decompress(bytes.fromhex(serialized))
    tree = pickle.loads(decompressed)
    
    print(f"\n🔍 Deserialized object type: {type(tree)}")
    
    # Handle both dict and WordProbabilityTree objects
    if isinstance(tree, dict):
        print("📋 Dictionary structure:")
        for key, value in tree.items():
            if isinstance(value, dict):
                print(f"  {key}: {len(value)} sub-entries")
            else:
                print(f"  {key}: {value}")
        
        # Examine frq entries more closely
        if 'frq' in tree:
            print(f"\n🔍 Frequency Data Analysis:")
            frq_data = tree['frq']
            print(f"  - Type: {type(frq_data)}")
            if isinstance(frq_data, dict):
                print(f"  - Keys: {list(frq_data.keys())[:10]}...")  # Show first 10 keys
                print(f"  - Sample entries:")
                for i, (key, value) in enumerate(list(frq_data.items())[:5]):
                    print(f"    {key}: {value}")
            else:
                print(f"  - Raw data: {frq_data}")
        
        # If it's a dict, let's look at the structure more deeply
        if 'rhy' in tree and 'prf' in tree['rhy']:
            prf_data = tree['rhy']['prf']
            print(f"\n🎯 Perfect Rhyme Data:")
            print(f"  - Type: {type(prf_data)}")
            if hasattr(prf_data, 'prb'):
                print(f"  - Probability entries: {len(prf_data.prb)}")
                print(f"  - Sample entries: {list(prf_data.prb.items())[:5]}")
            else:
                print(f"  - Raw data: {prf_data}")
            
            # Verify val list to prb mapping
            print(f"\n🔍 VAL-TO-PRB MAPPING VERIFICATION:")
            val_list = prf_data['val']
            prb_dict = prf_data['prb']
            
            print(f"  - Val list has {len(val_list)} sequences")
            print(f"  - Prb dict has {len(prb_dict)} entries")
            
            # Check first few sequences
            print(f"\n📋 First 10 sequences from val list:")
            for i, sequence in enumerate(val_list[:10]):
                first_token = sequence[0]
                print(f"  {i+1}. Sequence: {sequence} -> First token: {first_token}")
                if str(first_token) in prb_dict:
                    prob_entry = prb_dict[str(first_token)]
                    if isinstance(prob_entry, dict) and 'probability' in prob_entry:
                        print(f"     ✅ Found in prb with probability: {prob_entry['probability']:.6f}")
                    else:
                        print(f"     ❌ Found in prb but wrong format: {prob_entry}")
                else:
                    print(f"     ❌ NOT FOUND in prb dict!")
            
            # Verify scaling math on a specific sequence
            print(f"\n🧮 SCALING MATH VERIFICATION:")
            # Pick a sequence with multiple tokens to test nested structure
            test_sequence = None
            for seq in val_list:
                if len(seq) > 1:
                    test_sequence = seq
                    break
            
            if test_sequence:
                print(f"  Testing sequence: {test_sequence}")
                first_token = str(test_sequence[0])
                if first_token in prb_dict:
                    prob_entry = prb_dict[first_token]
                    print(f"  First token {first_token} probability: {prob_entry['probability']:.6f}")
                    
                    # Check nested structure
                    if 'child_prb' in prob_entry:
                        child_prb = prob_entry['child_prb']
                        print(f"  Child prb structure: {child_prb['prb']}")
                        
                        # Verify the remaining sequence matches child structure
                        remaining_seq = test_sequence[1:]
                        print(f"  Remaining sequence: {remaining_seq}")
                        
                        # Check if the child structure matches the remaining sequence
                        if len(remaining_seq) == 1:
                            next_token = str(remaining_seq[0])
                            if next_token in child_prb['prb']:
                                child_prob = child_prb['prb'][next_token]
                                print(f"  ✅ Child probability for {next_token}: {child_prob}")
                            else:
                                print(f"  ❌ Child token {next_token} not found in child_prb")
                        else:
                            print(f"  ⚠️  Multi-token remaining sequence, need deeper verification")
                    else:
                        print(f"  ❌ No child_prb found for multi-token sequence")
                else:
                    print(f"  ❌ First token {first_token} not found in prb")
            else:
                print(f"  ⚠️  No multi-token sequences found for testing")
            
            # Check probability sum validation
            print(f"\n📊 PROBABILITY SUM VALIDATION:")
            total_prob = 0
            for token_str, prob_entry in prb_dict.items():
                if isinstance(prob_entry, dict) and 'probability' in prob_entry:
                    total_prob += prob_entry['probability']
                elif isinstance(prob_entry, (int, float)):
                    total_prob += prob_entry
            
            print(f"  Total probability sum: {total_prob:.6f}")
            if abs(total_prob - 1.0) < 0.001:
                print(f"  ✅ Probability sum is valid (≈ 1.0)")
            else:
                print(f"  ❌ Probability sum is {total_prob:.6f}, should be 1.0")
    
    else:
        # Original WordProbabilityTree object
        print("\n🌳 Tree Structure Analysis:")
        print(f"  - Ana: {len(tree.ana.prb)} entries")
        print(f"  - OLO: {sum(len(node.prb) for node in tree.olo.values())} total entries")
        print(f"  - Rhymes: {sum(len(node.prb) for node in tree.rhy.values())} total entries")
        
        # Examine rhyme probabilities
        print("\n🎯 Perfect Rhyme Probabilities:")
        prf_node = tree.rhy['prf']
        print(f"  - Total entries: {len(prf_node.prb)}")
        print(f"  - Metadata: org_max={prf_node.dat.org_max:.6f}, val_prb_sum={prf_node.dat.val_prb_sum:.6f}")
        
        # Show sample probabilities
        print("\n📋 Sample Probability Entries:")
        for i, (token, prob) in enumerate(list(prf_node.prb.items())[:10]):
            if isinstance(prob, float):
                print(f"  Token {token}: {prob:.6f} (terminal)")
            else:
                print(f"  Token {token}: {prob.probability:.6f} (child node with {len(prob.remaining_sequences)} sequences)")
        
        # Check if probabilities sum to 1.0
        total_prob = sum(
            prob if isinstance(prob, float) else prob.probability
            for prob in prf_node.prb.values()
        )
        print(f"\n✅ Probability validation: sum = {total_prob:.6f}")
    
    print("\n✅ Data examination complete!")

if __name__ == "__main__":
    examine_stored_data() 