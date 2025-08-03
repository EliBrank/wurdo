# ML Engine Schema Implementation Plan

## Overview
This document outlines the implementation plan for updating the ml_engine to support the new Redis JSON schema with probability trees, child node structures, and comprehensive word transformations (anagrams, one-letter-off, rhymes).

## Current Architecture Analysis

### Core Components
- **[`models/cmu_rhyme_client.py`](models/cmu_rhyme_client.py)**: ✅ Already enhanced with new linguistic methods
- **[`models/advanced_scorer.py`](models/advanced_scorer.py)**: 🔄 Needs major updates for probability trees
- **[`services/storage_service.py`](services/storage_service.py)**: 🔄 Needs complete rewrite for new schema
- **[`services/rhyme_service.py`](services/rhyme_service.py)**: 🔄 Needs expansion for all transformation types
- **[`services/game_workflow.py`](services/game_workflow.py)**: 🔄 Needs orchestration updates

## Implementation Phases

### Phase 1: Core Infrastructure 🏗️

#### 1.1 Create Word Transformation Engine
**New File**: [`models/word_transformer.py`](models/word_transformer.py)
- **Purpose**: Generate anagrams and one-letter-off transformations
- **Features**:
  - Anagram generation with filtering (3-7 chars, alphabetic only)
  - One-letter-added (ola): "hats" → "chats", "thats"
  - One-letter-removed (olr): "hats" → "hat"
  - One-letter-exchanged (olx): "hat" → "bat", "cat"
  - Quality filtering (pronounceable, no excessive repeats)

#### 1.2 Create Probability Tree Builder
**New File**: [`models/probability_tree_builder.py`](models/probability_tree_builder.py)
- **Purpose**: Build probability trees from distilGPT-2 outputs
- **Features**:
  - Create child node structures: `[probability, remaining_sequences, prb_structure]`
  - Handle multi-token sequences (1-3 tokens)
  - Generate sparse arrays with child nodes at valid token indices
  - Calculate metadata: `org_max`, `val_prb_sum`, `max_dep`
  - Support all transformation types: `ana`, `olo`, `rhy`

#### 1.3 Update Advanced Scorer
**File**: [`models/advanced_scorer.py`](models/advanced_scorer.py)
- **Current**: Generates probability vectors for rhymes only
- **Updates Needed**:
  - Generate probability trees for all transformation types
  - Support multi-token probability chains
  - Create child node structures
  - Handle sparse array storage
  - Integrate with word frequency data

### Phase 2: Service Integration 🔧

#### 2.1 Update Storage Service
**File**: [`services/storage_service.py`](services/storage_service.py)
- **Current**: Simple Redis/JSON storage for rhyme data
- **Updates Needed**:
  - Implement new schema structure with nested child nodes
  - Support sparse array storage with child nodes
  - Handle `frq`, `ana`, `olo`, `rhy` transformations
  - Redis JSON operations for nested structures
  - Methods for storing/retrieving complete word data

#### 2.2 Update Rhyme Service
**File**: [`services/rhyme_service.py`](services/rhyme_service.py)
- **Current**: Processes rhymes only
- **Updates Needed**:
  - Generate anagrams using word permutations
  - Generate one-letter-off transformations (ola, olr, olx)
  - Categorize all transformation types
  - Integrate with distilGPT-2 for probability scoring
  - Support multi-token word processing

#### 2.3 Update Game Workflow
**File**: [`services/game_workflow.py`](services/game_workflow.py)
- **Current**: Orchestrates rhyme generation
- **Updates Needed**:
  - Orchestrate full word data generation (ana, olo, rhy)
  - Generate complete probability trees
  - Handle word frequency data
  - Coordinate all transformation types
  - Support complete schema population

### Phase 3: New Services 🆕

#### 3.1 Create Frequency Service
**New File**: [`services/frequency_service.py`](services/frequency_service.py)
- **Purpose**: Handle word frequency data for creativity scoring
- **Features**:
  - Integrate with wordfreq library
  - Provide frequency scoring for creativity ranking
  - Support frequency-based filtering

#### 3.2 Create Schema Validator
**New File**: [`utils/schema_validator.py`](utils/schema_validator.py)
- **Purpose**: Validate generated data against schema proposal
- **Features**:
  - Validate child node structures
  - Check probability tree integrity
  - Verify metadata consistency

#### 3.3 Create Probability Utilities
**New File**: [`utils/probability_utils.py`](utils/probability_utils.py)
- **Purpose**: Helper functions for probability calculations
- **Features**:
  - Normalize probability arrays
  - Calculate conditional probabilities
  - Handle sparse array operations

### Phase 4: Testing & Validation 🧪

#### 4.1 Create Comprehensive Test Suite
**New Files**:
- [`tests/test_schema_generation.py`](tests/test_schema_generation.py): Test complete word data generation
- [`tests/test_probability_trees.py`](tests/test_probability_trees.py): Test child node structures
- [`tests/test_transformations.py`](tests/test_transformations.py): Test anagram and one-letter-off generation
- [`tests/test_storage_schema.py`](tests/test_storage_schema.py): Test Redis JSON storage with new schema

#### 4.2 Update Existing Tests
**Files to Update**:
- [`test_tokenization.py`](test_tokenization.py): Add multi-token testing
- [`test_word_chain_scoring.py`](test_word_chain_scoring.py): Update for new schema

## Data Flow Changes

### Current Flow
```
start_word → CMU rhymes → tokenize → store simple data
```

### New Flow
```
start_word → 
├── Generate anagrams (ana)
├── Generate one-letter-off (olo: ola, olr, olx)  
├── Generate rhymes (rhy: prf, rch, sln)
├── Get word frequency (frq)
├── Generate probability trees for each type
├── Build child node structures
└── Store complete schema data
```

## Schema Integration Points

### 1. Child Node Structure
```typescript
ChildNode = [
    number,        // [0] probability for this token
    number[][],    // [1] remaining token sequences
    {              // [2] prb object
        arr: (number | ChildNode)[],
        dat: { org_max, val_prb_sum, max_dep }
    }
]
```

### 2. Complete Word Data Structure
```typescript
FullWordData = {
    frq: number,                    // Word frequency
    ana: WordTransformation,        // Anagram transformations
    olo: OneLetterOff,             // One-letter-off transformations
    rhy: RhymeTransformations      // Rhyme transformations
}
```

### 3. Redis JSON Storage
- **Root Level**: `$.frq`, `$.ana`, `$.olo`, `$.rhy`
- **Child Nodes**: `$.ana.prb.arr.1234` → `[prob, val, prb_structure]`
- **Nested Structure**: `$.ana.prb.arr.1234.2.arr.5678` → child node

## Implementation Priority

### High Priority (Phase 1)
1. **[`models/word_transformer.py`](models/word_transformer.py)** - Core transformation engine
2. **[`models/probability_tree_builder.py`](models/probability_tree_builder.py)** - Probability tree creation
3. **[`models/advanced_scorer.py`](models/advanced_scorer.py)** - Multi-token probability support

### Medium Priority (Phase 2)
1. **[`services/storage_service.py`](services/storage_service.py)** - New schema storage
2. **[`services/rhyme_service.py`](services/rhyme_service.py)** - All transformation types
3. **[`services/game_workflow.py`](services/game_workflow.py)** - Complete orchestration

### Low Priority (Phase 3)
1. **[`services/frequency_service.py`](services/frequency_service.py)** - Frequency integration
2. **[`utils/schema_validator.py`](utils/schema_validator.py)** - Validation utilities
3. **[`utils/probability_utils.py`](utils/probability_utils.py)** - Helper functions

## Success Criteria

### ✅ Phase 1 Complete
- [ ] Word transformer generates quality anagrams and one-letter-off transformations
- [ ] Probability tree builder creates correct child node structures
- [ ] Advanced scorer supports multi-token probability chains

### ✅ Phase 2 Complete
- [ ] Storage service handles complete schema with nested child nodes
- [ ] Rhyme service processes all transformation types
- [ ] Game workflow orchestrates complete word data generation

### ✅ Phase 3 Complete
- [ ] Frequency service provides creativity scoring
- [ ] Schema validator ensures data integrity
- [ ] All tests pass with new schema

### ✅ Integration Complete
- [ ] Complete word data generated for test words
- [ ] Redis JSON storage working with nested structures
- [ ] Performance acceptable for real-time gameplay

## Notes

- **Backward Compatibility**: Consider maintaining old storage format during transition
- **Performance**: Monitor Redis JSON operations with nested structures
- **Testing**: Create comprehensive test data for all transformation types
- **Documentation**: Update all docstrings to reflect new schema structure

## References

- **[Schema Proposal](schema_proposal.md)**: Canonical schema definition
- **[CMU Rhyme Client](models/cmu_rhyme_client.py)**: Enhanced linguistic features
- **[Advanced Scorer](models/advanced_scorer.py)**: Current probability generation
- **[Storage Service](services/storage_service.py)**: Current data storage 