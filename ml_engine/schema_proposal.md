# Rhyme Probability Tree Schema Proposal

## Overview
This document defines the exact data structure for storing rhyme probabilities using distilGPT-2 soft-max probabilities in a Redis JSON database.

## Core Data Structure

### Root Level Schema
```typescript
[start_word] = {
    'frq': int,                       // from wordfreq.word_frequency([start_word], 'en')
    'ana': {                          // containing anagram probability object
        'val': List[List[int]],       // list of valid words as token index sequences
        'prb': {                      // containing probability array and scaling data
            'arr': [...],             // sparse array with non-zero values at indices for first tokens of valid words
            'dat': {
                'org_max': float,     // original max value of array before setting invalid_index values to 0
                'val_prb_sum': float, // sum of probabilities at valid first token indices
                'max_dep': int        // maximum depth of token sequences
            }
        }
    },
    'olo': {                          // containing probability objects for one-letter-off transformations
        'ola': {                          // containing one-letter-added probability object
            'val': List[List[int]],       // list of valid words as token index sequences
            'prb': {                      // containing probability array and scaling data
                'arr': [...],             // sparse array with non-zero values at indices for first tokens of valid words
                'dat': {
                    'org_max': float,     // original max value of array before setting invalid_index values to 0
                    'val_prb_sum': float, // sum of probabilities at valid first token indices
                    'max_dep': int        // maximum depth of token sequences
                    }
                }
            },
        'olr': {                           // containing one-letter-removed probability object
            'val': List[List[int]],       // list of valid words as token index sequences
            'prb': {                      // containing probability array and scaling data
                'arr': [...],             // sparse array with non-zero values at indices for first tokens of valid words
                'dat': {
                    'org_max': float,     // original max value of array before setting invalid_index values to 0
                    'val_prb_sum': float, // sum of probabilities at valid first token indices
                    'max_dep': int        // maximum depth of token sequences
                }
            }
        },
        'olx': {                          // containing one-letter-exchanged probability object
            'val': List[List[int]],       // list of valid words as token index sequences
            'prb': {                      // containing probability array and scaling data
                'arr': [...],             // sparse array with non-zero values at indices for first tokens of valid words
                'dat': {
                    'org_max': float,     // original max value of array before setting invalid_index values to 0
                    'val_prb_sum': float, // sum of probabilities at valid first token indices
                    'max_dep': int        // maximum depth of token sequences
                }
            }
        }
    },
    'rhy': {                          // containing probability objects for rhyme transformations
        'prf': {                          // containing perfect_rhyme probability object
            'val': List[List[int]],       // list of valid words as token index sequences
            'prb': {                      // containing probability array and scaling data
                'arr': [...],             // sparse array with non-zero values at indices for first tokens of valid words
                'dat': {
                    'org_max': float,     // original max value of array before setting invalid_index values to 0
                    'val_prb_sum': float, // sum of probabilities at valid first token indices
                    'max_dep': int        // maximum depth of token sequences
                }
            }
        },
        'rch': {                          // containing rich-rhyme probability object
            'val': List[List[int]],       // list of valid words as token index sequences
            'prb': {                      // containing probability array and scaling data
                'arr': [...],             // sparse array with non-zero values at indices for first tokens of valid words
                'dat': {
                    'org_max': float,     // original max value of array before setting invalid_index values to 0
                    'val_prb_sum': float, // sum of probabilities at valid first token indices
                    'max_dep': int        // maximum depth of token sequences
                }
            }
        },
        'sln': {                          // containing slant-rhyme probability object
            'val': List[List[int]],       // list of valid words as token index sequences
            'prb': {                      // containing probability array and scaling data
                'arr': [...],             // sparse array with non-zero values at indices for first tokens of valid words
                'dat': {
                    'org_max': float,     // original max value of array before setting invalid_index values to 0
                    'val_prb_sum': float, // sum of probabilities at valid first token indices
                    'max_dep': int        // maximum depth of token sequences
                }
            }
        }
    }
}

```

### Child Node Schema (Recursive)
```typescript
ProbabilityNode = [
    float,                                 // [0] probability for this token
    List[List[int]],                       // [1] remaining token sequences from this point
    {                                      // [2] prb object
        arr: [...],                       // sparse probability array for next tokens
        dat: {
            org_max: float,               // original max for this context
            val_prb_sum: float,           // sum of valid probabilities at this level
            max_dep: int                  // remaining depth from this node
        }
    }
]
```

## Example Data Structure

### Single Token Word Example: "hat"
```typescript
word:hat = {
    frq: 42,                    // frequency from wordfreq
    ana: {
        val: [
            [9012],      // "hat" -> "ath" (anagram)
            [4567]       // "hat" -> "tha" (anagram)
        ],
        prb: {
            arr: [
                0.0, 0.0, ..., 0.0,  // sparse array (vocab_size length)
                0.60,                 // index 9012: probability for "ath" normalized over all valid token probabilities
                0.0, 0.0, ..., 0.0,
                0.40                  // index 4567: probability for "tha" normalized over all valid token probabilities
            ],
            dat: {
                org_max: 0.000015,        // original max from distilGPT-2
                val_prb_sum: 0.000027,     // sum of valid probabilities (un_normalized)
                max_dep: 1            // maximum depth (single token words)
            }
        }
    },
    olo: {
        ola: {                       // one-letter-added
            val: [
                [1234],      // "hat" -> "chat"
                [5678]       // "hat" -> "that"
            ],
            prb: {
                arr: [
                    0.0, 0.0, ..., 0.0,
                    0.50,                 // index 1234: normalized probability for "chat"
                    0.0, 0.0, ..., 0.0,
                    0.50                  // index 5678: normalized probability for "that"
                ],
                dat: {
                    org_max: 0.000012,
                    val_prb_sum: 0.000019,
                    max_dep: 1
                }
            }
        },
        olr: {                       // one-letter-removed
            val: [
                [9012]       // "hat" -> "at"
            ],
            prb: {
                arr: [
                    0.0, 0.0, ..., 0.0,
                    1.0                  // index 9012: normalized probability for "at"
                ],
                dat: {
                    org_max: 0.00008,
                    val_prb_sum: 0.00008,
                    max_dep: 1
                }
            }
        },
        olx: {                       // one-letter-exchanged
            val: [
                [3456],      // "hat" -> "bat"
                [7890]       // "hat" -> "cat"
            ],
            prb: {
                arr: [
                    0.0, 0.0, ..., 0.0,
                    0.60,                 // index 3456: normalized probability for "bat"
                    0.0, 0.0, ..., 0.0,
                    0.40                  // index 7890: normalized probability for "cat"
                ],
                dat: {
                    org_max: 0.00010,
                    val_prb_sum: 0.00016,
                    max_dep: 1
                }
            }
        }
    },
    rhy: {
        prf: {                       // perfect-rhyme
            val: [
                [9012],      // "cat" tokenized
                [4567],      // "bat" tokenized  
                [7890],      // "rat" tokenized
                [1234]       // "sat" tokenized
            ],
            prb: {
                arr: [
                    0.0, 0.0, ..., 0.0,  // sparse array (vocab_size length)
                    0.25,                 // index 9012: normalized probability for "cat"
                    0.0, 0.0, ..., 0.0,
                    0.30,                 // index 4567: normalized probability for "bat"
                    0.0, 0.0, ..., 0.0,
                    0.25,                 // index 7890: normalized probability for "rat"
                    0.0, 0.0, ..., 0.0,
                    0.20                  // index 1234: normalized probability for "sat"
                ],
                dat: {
                    org_max: 0.000015,        // original max from distilGPT-2
                    val_prb_sum: 0.000049,     // sum of unnormalized valid probabilities (renormalized)
                    max_dep: 1            // maximum depth (single token words)
                }
            }
        },
        rch: {                       // rich-rhyme aka homophone
            val: [
                [5678]       // homophone tokenized
            ],
            prb: {
                arr: [
                    0.0, 0.0, ..., 0.0,
                    1.0                  // index 5678: normalized probability for homophone
                ],
                dat: {
                    org_max: 0.000008,
                    val_prb_sum: 0.000008,
                    max_dep: 1
                }
            }
        },
        sln: {                       // slant-rhyme
            val: [
                [3456]       // "bad" tokenized
            ],
            prb: {
                arr: [
                    0.0, 0.0, ..., 0.0,
                    1.0                  // index 3456: normalized probability for "bad"
                ],
                dat: {
                    org_max: 0.000005,
                    val_prb_sum: 0.000005,
                    max_dep: 1
                }
            }
        }
    }
}
```

### Multi-Token Word Example: "computer"
```typescript
word:computer = {
    frq: 156,                   // frequency from wordfreq
    ana: {
        val: [
            [1234, 5678, 9012]    // "computer" -> (3-token anagram)
        ],
        prb: {
            arr: [
                0.0, 0.0, ..., 0.0,
                [                  // index 1234: Child node for first token
                    0.60,          // [0] normalized probability for first token
                    [[5678, 9012]], // [1] remaining sequences after first token
                    {              // [2] probability structure for next tokens
                        arr: [
                            0.0, 0.0, ..., 0.0,
                            [                  // index 5678: Child node for second tokem
                                0.70,          // [0] normalized probability for second token given given first token
                                [[9012]],      // [1] remaining sequences after second token
                                {              // [2] probability structure for final token
                                    arr: [
                                        0.0, 0.0, ..., 0.0,
                                        1.0                      // index 9012: normalized probability for final token given "comp uter"
                                    ],
                                    dat: {
                                        org_max: 0.000020,
                                        val_prb_sum: 0.000020,
                                        max_dep: 1
                                    }
                                }
                            ]
                        ],
                        dat: {
                            org_max: 0.000015,
                            val_prb_sum: 0.000015,
                            max_dep: 2
                        }
                    }
                ]
            ],
            dat: {
                org_max: 0.000020,
                val_prb_sum: 0.000020,
                max_dep: 3
            }
        }
    },
    olo: {
        ola: {
            val: [
                [9012, 3456]    // "computer" -> "computers" (2-token)
            ],
            prb: {
                arr: [
                    0.0, 0.0, ..., 0.0,
                    [                  // index 9012: Child node for first token
                        0.50,          // [0] normalized probability for first token
                        [[3456]],      // [1] remaining sequences after first token
                        {              // [2] probability structure for second token
                            arr: [
                                0.0, 0.0, ..., 0.0,
                                1.0                      // index 3456: normalized probability for second token given first
                            ],
                            dat: {
                                org_max: 0.000015,
                                val_prb_sum: 0.000015,
                                max_dep: 1
                            }
                        }
                    ]
                ],
                dat: {
                    org_max: 0.000015,
                    val_prb_sum: 0.000015,
                    max_dep: 2
                }
            }
        },
        olr: {
            val: [
                [6789, 1234]    // "computer" -> "compute" (2-token)
            ],
            prb: {
                arr: [
                    0.0, 0.0, ..., 0.0,
                    [                  // index 6789: Child node for first token
                        1.0,          // [0] normalized probability for first token
                        [[1234]],      // [1] remaining sequences after first token
                        {              // [2] probability structure for second token
                            arr: [
                                0.0, 0.0, ..., 0.0,
                                1.0                      // index 1234: normalized probability for second token given first
                            ],
                            dat: {
                                org_max: 0.000012,
                                val_prb_sum: 0.000012,
                                max_dep: 1
                            }
                        }
                    ]
                ],
                dat: {
                    org_max: 0.000012,
                    val_prb_sum: 0.000012,
                    max_dep: 2
                }
            }
        },
        olx: {
            val: [
                [2345, 6789]    // "computer" -> "compuser" (2-token)
            ],
            prb: {
                arr: [
                    0.0, 0.0, ..., 0.0,
                    [                  // index 2345: Child node for first token
                        1.0,          // [0] normalized probability for first token
                        [[6789]],      // [1] remaining sequences after first token
                        {              // [2] probability structure for second token
                            arr: [
                                0.0, 0.0, ..., 0.0,
                                1.0                      // index 6789: normalized probability for second token given first
                            ],
                            dat: {
                                org_max: 0.000008,
                                val_prb_sum: 0.000008,
                                max_dep: 1
                            }
                        }
                    ]
                ],
                dat: {
                    org_max: 0.000008,
                    val_prb_sum: 0.000008,
                    max_dep: 2
                }
            }
        }
    },
    rhy: {
        prf: {                       // perfect-rhyme
            val: [
                [1234, 5678],    // "recorder" -> [rec, order] (2-token)
                [9012, 3456],    // "processor" -> [pro, cessor] (2-token)
                [6789, 1234]     // "developer" -> [de, veloper] (2-token)
            ],
            prb: {
                arr: [
                    0.0, 0.0, ..., 0.0,
                    [                     // index 1234: Child node for "rec"
                        0.40,             // [0] normalized probability for "rec"
                        [[5678]],         // [1] remaining sequences after "rec"
                        {                 // [2] probability structure for next tokens
                            arr: [
                                0.0, 0.0, ..., 0.0,
                                1.0                      // index 5678: normalized probability for "order" given "rec"
                            ],
                            dat: {
                                org_max: 0.000012,
                                val_prb_sum: 0.000012,
                                max_dep: 1
                            }
                        }
                    ],
                    0.0, 0.0, ..., 0.0,
                    [                     // index 9012: Child node for "pro"
                        0.35,             // [0] normalized probability for "pro"
                        [[3456]],         // [1] remaining sequences after "pro"
                        {                 // [2] probability structure for next tokens
                            arr: [
                                0.0, 0.0, ..., 0.0,
                                1.0                      // index 3456: normalized probability for "cessor" given "pro"
                            ],
                            dat: {
                                org_max: 0.000010,
                                val_prb_sum: 0.000010,
                                max_dep: 1
                            }
                        }
                    ],
                    0.0, 0.0, ..., 0.0,
                    [                     // index 6789: Child node for "de"
                        0.25,             // [0] normalized probability for "de"
                        [[1234]],         // [1] remaining sequences after "de"
                        {                 // [2] probability structure for next tokens
                            arr: [
                                0.0, 0.0, ..., 0.0,
                                1.0                      // index 1234: normalized probability for "veloper" given "de"
                            ],
                            dat: {
                                org_max: 0.000008,
                                val_prb_sum: 0.000008,
                                max_dep: 1
                            }
                        }
                    ]
                ],
                dat: {
                    org_max: 0.000020,        // original max from distilGPT-2
                    val_prb_sum: 0.000030,     // sum of unnormalized valid probabilities
                    max_dep: 2            // maximum depth (two token words)
                }
            }
        },
        rch: {                       // rich-rhyme aka homophone
            val: [
                [2345]    // "computer" -> "compuser" (single token)
            ],
            prb: {
                arr: [
                    0.0, 0.0, ..., 0.0,
                    1.0                  // index 2345: normalized probability for homophone
                ],
                dat: {
                    org_max: 0.000008,
                    val_prb_sum: 0.000008,
                    max_dep: 1
                }
            }
        },
        sln: {                       // slant-rhyme
            val: [
                [3456]    // "computer" -> "compter" (single token)
            ],
            prb: {
                arr: [
                    0.0, 0.0, ..., 0.0,
                    1.0                  // index 3456: normalized probability for "compter"
                ],
                dat: {
                    org_max: 0.000005,
                    val_prb_sum: 0.000005,
                    max_dep: 1
                }
            }
        }
    }
}
```

## Redis JSON Path Structure

### Root Level Paths
```
word:hat = {
    frq: "$.frq"                           # Frequency data
    ana: {
        val: "$.ana.val"                    # Anagram token sequences
        prb: {
            arr: "$.ana.prb.arr"           # Anagram probability array
            dat: "$.ana.prb.dat"           # Anagram metadata
        }
    }
    olo: {
        ola: {                              # one-letter-added
            val: "$.olo.ola.val"
            prb: {
                arr: "$.olo.ola.prb.arr"
                dat: "$.olo.ola.prb.dat"
            }
        }
        olr: {                              # one-letter-removed
            val: "$.olo.olr.val"
            prb: {
                arr: "$.olo.olr.prb.arr"
                dat: "$.olo.olr.prb.dat"
            }
        }
        olx: {                              # one-letter-exchanged
            val: "$.olo.olx.val"
            prb: {
                arr: "$.olo.olx.prb.arr"
                dat: "$.olo.olx.prb.dat"
            }
        }
    }
    rhy: {
        prf: {                              # perfect-rhyme
            val: "$.rhy.prf.val"
            prb: {
                arr: "$.rhy.prf.prb.arr"
                dat: "$.rhy.prf.prb.dat"
            }
        }
        rch: {                              # rich-rhyme
            val: "$.rhy.rch.val"
            prb: {
                arr: "$.rhy.rch.prb.arr"
                dat: "$.rhy.rch.prb.dat"
            }
        }
        sln: {                              # slant-rhyme
            val: "$.rhy.sln.val"
            prb: {
                arr: "$.rhy.sln.prb.arr"
                dat: "$.rhy.sln.prb.dat"
            }
        }
    }
}
```

### Child Node Paths
```
# For multi-token words, child nodes are stored at:
word:computer = {
    rhy: {
        prf: {
            prb: {
                arr: {
                    1234: "$.rhy.prf.prb.arr.1234"           # [prob, val, prb_structure]
                    9012: "$.rhy.prf.prb.arr.9012"           # [prob, val, prb_structure]
                    6789: "$.rhy.prf.prb.arr.6789"           # [prob, val, prb_structure]
                }
            }
        }
    }
}

# For three-token words, nested child nodes are stored at:
word:computer = {
    ana: {
        prb: {
            arr: {
                1234: "$.ana.prb.arr.1234"                   # [prob, val, prb_structure]
                # Child node at 1234 contains nested structure:
                "$.ana.prb.arr.1234.2.arr.5678": [           # [2] = prb_structure, .arr = nested array
                    0.70,                                     # [0] = probability for second token
                    [[9012]],                                 # [1] = remaining sequences
                    {                                         # [2] = nested prb_structure
                        "arr": {
                            9012: 1.0                        # Final token probability
                        },
                        "dat": {                              # Metadata for final level
                            "org_max": 0.000020,
                            "val_prb_sum": 0.000020,
                            "max_dep": 1
                        }
                    }
                ],
                "$.ana.prb.arr.1234.2.dat": {                # Metadata for second level
                    "org_max": 0.000015,
                    "val_prb_sum": 0.000015,
                    "max_dep": 2
                }
            }
        }
    }
}
```

## TypeScript Interface Definitions

```typescript
export interface ChildNode {
    [0]: number;                           // probability for this token
    [1]: number[][];                       // remaining token sequences from this point
    [2]: {                                 // prb object
        arr: (number | ChildNode)[];       // sparse probability array for next tokens
        dat: {
            org_max: number;               // original max for this context
            val_prb_sum: number;           // sum of valid probabilities at this level
            max_dep: number;               // remaining depth from this node
        }
    }
}

export interface WordTransformation {
    val: number[][];  // Valid words as token index sequences
    prb: {
        arr: (number | ChildNode)[];  // Sparse array with child nodes
        dat: {
            org_max: number;      // Original max probability
            val_prb_sum: number;  // Sum of valid probabilities
            max_dep: number;      // Maximum depth
        }
    }
}

export interface OneLetterOff {
    ola: WordTransformation;  // one-letter-added
    olr: WordTransformation;  // one-letter-removed
    olx: WordTransformation;  // one-letter-exchanged
}

export interface RhymeTransformations {
    prf: WordTransformation;  // perfect-rhyme
    rch: WordTransformation;  // rich-rhyme aka homophone
    sln: WordTransformation;  // slant-rhyme
}

export interface FullWordData {
    frq: number;              // Frequency from wordfreq
    ana: WordTransformation;  // Anagram transformations
    olo: OneLetterOff;        // One-letter-off transformations
    rhy: RhymeTransformations; // Rhyme transformations
}

export interface PartialUpdateData {
    frq?: number;
    ana?: WordTransformation;
    olo?: OneLetterOff;
    rhy?: RhymeTransformations;
}
```

## Key Design Principles

### 1. Child Node Structure
- **Array format**: `[probability, remaining_sequences, prb_structure]`
- **Index access**: `child_node[0]` = probability, `child_node[1]` = sequences, `child_node[2]` = prb
- **Recursive**: Same structure at every level
- **Placement**: `prb.arr[token_index] = [child_node]`

### 2. Sparse Array Storage
- Only store non-zero probabilities at valid token indices
- `arr[token_idx]` contains either:
  - `number`: Probability for single-token words
  - `ChildNode`: Probability + child node for multi-token words

### 3. Recursive Structure
- Every level uses identical `ChildNode` structure
- Enables shared traversal logic across all depths
- Consistent metadata at every level

### 4. Mathematical Properties
- Normalized probabilities at each level sum to 1.0 (after renormalization)
- Unnormalized probabilities preserved in `val_prb_sum` for creativity scoring
- Conditional probability chain: P(word) = P(token_0) × P(token_1|token_0) × ...
- Original max values (`org_max`) preserved for creativity scoring

### 5. Memory Efficiency
- Token indices instead of strings
- Sparse arrays only store valid probabilities
- Shared context for sequences with common prefixes

## Multi-Token Probability Lookup

### Lookup Pattern
```typescript
function get_multi_token_probability(word_data, token_sequence) {
    let current_node = word_data.rhy.prf.prb;
    let total_prob = 1.0;
    
    for (let i = 0; i < token_sequence.length; i++) {
        const token = token_sequence[i];
        
        if (i === 0) {
            // First token - check if it's a child node or direct probability
            const first_token_data = current_node.arr[token];
            if (Array.isArray(first_token_data)) {
                // Multi-token word - child node
                total_prob *= first_token_data[0];  // [0] = probability
                current_node = first_token_data[2];  // [2] = nested prb structure
            } else {
                // Single-token word - direct probability
                total_prob *= first_token_data;
            }
        } else {
            // Subsequent tokens - navigate child nodes
            const child_node = current_node.arr[token];
            if (Array.isArray(child_node)) {
                // Another level of nesting
                total_prob *= child_node[0];        // [0] = probability
                current_node = child_node[2];        // [2] = nested prb structure
            } else {
                // Final token - direct probability
                total_prob *= child_node;
            }
        }
    }
    
    return total_prob;
}
```

### Example Lookup
```typescript
// For "recorder" -> [1234, 5678] (2-token word)
const first_token_data = word_data.rhy.prf.prb.arr[1234];  // Get child node array
const first_prob = first_token_data[0];                     // [0] First token probability
const remaining_sequences = first_token_data[1];            // [1] Remaining sequences
const child_prb = first_token_data[2];                     // [2] Child probability structure
const second_prob = child_prb.arr[5678];                   // Second token probability (direct number)

// For "computer" -> [1234, 5678, 9012] (3-token word)
const first_token_data = word_data.ana.prb.arr[1234];      // Get child node array
const first_prob = first_token_data[0];                     // [0] First token probability
const child_prb = first_token_data[2];                     // [2] Child probability structure
const second_token_data = child_prb.arr[5678];             // Get nested child node array
const second_prob = second_token_data[0];                   // [0] Second token probability
const final_prb = second_token_data[2];                     // [2] Final probability structure
const final_prob = final_prb.arr[9012];                    // Final token probability (direct number)
```

## Questions for Clarification

1. **Array Structure**: Is the sparse array structure correct? Should it be:
   ```typescript
   arr: (number | ChildNode)[]
   ```
   Or should it be:
   ```typescript
   arr: Record<number, number | ChildNode>
   ```

2. **Child Node Storage**: Are child nodes stored as nested objects within the array, or as separate Redis paths?

3. **Metadata Storage**: Should `org_max`, `val_prb_sum`, `max_dep` be stored at every level or only at the root?

4. **Token Indexing**: Should we use the actual distilGPT-2 token indices or create a mapping to smaller indices for efficiency?