# Wurdo Game Flow Architecture

## Overview
This document outlines the complete action flow for the Wurdo word-chaining game, detailing how the ML engine integrates with the frontend through a game_service.py API layer.

## Game Flow Phases

### PHASE 1: Application Startup
**Objective**: Initialize ML components and prepare game state

**Actions**:
1. **Component Validation**: Check all scoring components are present
2. **Model Warmup**: Spin up DistilGPT-2 model for real-time scoring
3. **Start Word Resolution**:
   - Primary: Look up start_word in Redis storage
   - Fallback: Check JSON file storage
   - Generate: Build new probability tree if not found, store in JSON
4. **Suggestion Objects Creation**:
   - Player suggestions: Highest frequency valid words for each play type from start_word
   - Umi suggestions: Copy of player suggestions (will diverge during gameplay)
5. **Return**: player_suggestions object to frontend

### PHASE 2: First Player Move
**Objective**: Process initial player input and establish game state

**Actions**:
1. **Candidate Validation**: Check candidate_word exists in frequencies.json
   - If invalid: Return "Oops! It looks like {candidate_word} is not in the dictionary"
   - If valid: Proceed to scoring
2. **Player Scoring**: Score candidate_word using ML engine
3. **Umi Response**: Extract play type, select Umi's play from Umi's suggestions
4. **Umi Scoring**: Score Umi's selected play
5. **State Updates**:
   - Update player_suggestions with highest frequency valid words from candidate_word
   - Update umi_suggestions with highest frequency valid words from Umi's play
6. **Return**: PlayResult for player, PlayResult for Umi, updated player_suggestions

### PHASE 3: Subsequent Player Moves
**Objective**: Continue gameplay with divergent player/Umi chains

**Actions**:
1. **Candidate Validation & Scoring**: Check and score new candidate_word
2. **Player Suggestions Update**: Update player_suggestions from candidate_word
3. **Umi Response**: Use player's play type to select Umi's play from umi_suggestions
4. **Umi Scoring**: Score Umi's selected play
5. **Umi Suggestions Update**: Update umi_suggestions from Umi's play
6. **Return**: PlayResult for player, PlayResult for Umi, updated player_suggestions

### PHASE 4: Game Conclusion
**Objective**: Generate final game summaries

**Actions**:
1. **Game End Signal**: Receive frontend signal indicating game conclusion
2. **Chain Summary Creation**: Generate summary objects for player_chain and umi_chain
3. **Return**: Chain summary objects to frontend

## Technical Requirements

### Data Structure Updates
- **frequencies.json**: Primary data source for word validation and frequency lookup
- **Validation Patterns**: Use frequencies.json keys for word existence checks
- **Frequency Integration**: Leverage existing frequency data for intelligent suggestions

### Performance Considerations
- **Real-time ML Scoring**: DistilGPT-2 must respond quickly to each candidate word
- **Redis Integration**: Use Isaac's batched updates for common word combinations
- **JSON Fallback**: Store probability trees for less common combinations
- **Caching Strategy**: Optimize for fast lookup during gameplay

### Error Handling & Debugging
- **Comprehensive Logging**: Include file and line numbers for frontend debugging
- **Performance Monitoring**: Track response times and failure points
- **Graceful Degradation**: Fallback mechanisms for component failures

## Integration Strategy

### Hybrid Storage Approach
- **Redis**: Fast lookup for common word combinations (Isaac's batched updates)
- **JSON Storage**: Probability trees for less common combinations
- **ML Engine**: Real-time scoring for new/unseen combinations

### API Design Principles
- **Concise & Professional**: Clean, maintainable code without emojis
- **Error Messages**: Useful feedback for frontend debugging
- **Debug Logs**: Critical point logging with file/line references
- **Performance**: Optimized for real-time gameplay requirements

## File Structure
```
ml_engine/
├── game_service.py          # Main API layer for frontend integration
├── GAME_FLOW_ARCHITECTURE.md # This document
├── services/                # ML engine services
├── models/                  # ML models and scoring
├── utils/                   # Utilities including Redis integration
└── game_data/              # Data files including frequencies.json
```

## Next Steps
1. Validate architecture feasibility with current ML engine capabilities
2. Design game_service.py API interface
3. Implement single-file frequency data approach using frequencies.json
4. Test real-time scoring performance
5. Integrate with frontend components
