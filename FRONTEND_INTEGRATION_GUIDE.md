# Frontend Integration Guide for Wurdo ML Engine

## Overview
This guide provides everything the frontend team needs to integrate with the Wurdo ML engine's `game_service.py` API. The ML engine handles real-time word scoring, intelligent suggestions, and game state management through an optimized Redis + JSON storage system.

## Current Frontend State
The frontend currently has a basic `GameArea` component with:
- Word input handling (3-7 letters)
- Keyboard interface
- Basic validation
- **TODO**: "connect to word scoring service"

## Required API Integration

### 1. Game Initialization (PHASE 1)
```typescript
// Initialize the game service
const initializeGame = async () => {
  try {
    const response = await fetch('/api/game/initialize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    const data = await response.json();
    
    if (data.status === 'initialized') {
      // Game service is ready
      setGameReady(true);
    }
  } catch (error) {
    console.error('Failed to initialize game:', error);
  }
};
```

### 2. Start Game (PHASE 1)
```typescript
// Start a new game with a start word
const startGame = async (startWord: string) => {
  try {
    const response = await fetch('/api/game/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ start_word: startWord })
    });
    const data = await response.json();
    
    if (data.status === 'game_started') {
      setGameState(data.game_state);
      setPlayerSuggestions(data.player_suggestions);
      setCurrentWord(startWord);
      setGameActive(true);
    }
  } catch (error) {
    console.error('Failed to start game:', error);
  }
};
```

### 3. Process Player Move (PHASE 2 & 3)
```typescript
// Handle word submission
const handleSubmit = async () => {
  if (wordInput.length >= minWordLength && wordInput.length <= maxWordLength) {
    try {
      const response = await fetch('/api/game/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ candidate_word: wordInput })
      });
      const data = await response.json();
      
      if (data.status === 'move_processed') {
        // Update game state
        setGameState(data.game_state);
        setPlayerSuggestions(data.player_suggestions);
        
        // Display results
        setPlayerResult(data.player_result);
        setUmiResult(data.umi_result);
        
        // Clear input for next round
        setWordInput('');
        setError('');
      } else if (data.status === 'invalid_word') {
        setError(data.error);
      } else if (data.status === 'duplicate_word') {
        setError(data.error);
      }
    } catch (error) {
      console.error('Failed to process move:', error);
    }
  }
};
```

### 4. End Game (PHASE 4)
```typescript
// End the current game
const endGame = async () => {
  try {
    const response = await fetch('/api/game/end', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    const data = await response.json();
    
          if (data.status === 'game_ended') {
        setGameSummary({
          playerSummary: data.player_summary,
          umiSummary: data.umi_summary,
          finalStats: data.final_stats,
          redisUpdate: data.redis_update
        });
        setGameActive(false);
      }
  } catch (error) {
    console.error('Failed to end game:', error);
  }
};
```

## Required API Endpoints

The frontend needs these REST endpoints. **Note**: These endpoints don't exist yet - the frontend team will need to create them to connect to the ML engine's `game_service.py`:

```typescript
// API endpoint structure
POST /api/game/initialize     // Initialize ML engine
POST /api/game/start         // Start new game
POST /api/game/move          // Process player move
POST /api/game/end           // End game
GET  /api/game/status        // Get current game state
POST /api/game/reset         // Reset game
```

**Important**: The frontend team will need to create these API routes that call the ML engine's `game_service.py` methods. The ML engine is a Python service that needs to be integrated via these Next.js API routes.

## Data Structures

### Player Suggestions
```typescript
interface PlayerSuggestions {
  prf?: { word: string; frequency: number; frequency_rank: string };
  rch?: { word: string; frequency: number; frequency_rank: string };
  sln?: { word: string; frequency: number; frequency_rank: string };
  ana?: { word: string; frequency: number; frequency_rank: string };
  ola?: { word: string; frequency: number; frequency_rank: string };
  olr?: { word: string; frequency: number; frequency_rank: string };
  olx?: { word: string; frequency: number; frequency_rank: string };
}
```

### Game State
```typescript
interface GameState {
  start_word: string;
  current_word: string;
  player_chain: string[];
  umi_chain: string[];
  player_suggestions: PlayerSuggestions;
  umi_suggestions: PlayerSuggestions;
  rounds_played: number;
  player_score: number;
  umi_score: number;
  game_started: string;
}
```

### Scoring Results
```typescript
interface ScoringResult {
  success: boolean;
  message: string;
  data: {
    total_score: number;
    category_scores: Record<string, number>;
    valid_categories: string[];
    category_count: number;
  };
}
```

## Implementation Steps for Frontend Team

### 1. Create Next.js API Routes
First, create the API routes that will connect to the ML engine. Create these files in `app/api/game/`:

**`app/api/game/initialize/route.ts`:**
```typescript
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    // Call the ML engine's game_service.initialize() method
    // This will require setting up a connection to your Python ML engine
    // You might need to use a process spawn, HTTP server, or similar
    
    // For now, this is a placeholder - you'll need to implement the actual connection
    const response = await fetch('http://localhost:8000/game/initialize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to initialize game service' },
      { status: 500 }
    );
  }
}
```

**`app/api/game/start/route.ts`:**
```typescript
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { start_word } = await request.json();
    
    // Call the ML engine's game_service.start_game(start_word) method
    const response = await fetch('http://localhost:8000/game/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ start_word })
    });
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to start game' },
      { status: 500 }
    );
  }
}
```

**Note**: You'll need to set up a way for Next.js to communicate with your Python ML engine. Options include:
- Running the ML engine as a separate HTTP server
- Using process spawning to call Python scripts
- Setting up a bridge service

### 2. Create API Service Layer
Create `src/services/gameApi.ts`:
```typescript
class GameApiService {
  private baseUrl = '/api/game';
  
  async initialize() {
    const response = await fetch(`${this.baseUrl}/initialize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    return response.json();
  }
  
  async startGame(startWord: string) {
    const response = await fetch(`${this.baseUrl}/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ start_word: startWord })
    });
    return response.json();
  }
  
  async processMove(candidateWord: string) {
    const response = await fetch(`${this.baseUrl}/move`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ candidate_word: candidateWord })
    });
    return response.json();
  }
  
  async endGame() {
    const response = await fetch(`${this.baseUrl}/end`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    return response.json();
  }
  
  async getGameStatus() {
    const response = await fetch(`${this.baseUrl}/status`);
    return response.json();
  }
  
  async resetGame() {
    const response = await fetch(`${this.baseUrl}/reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    return response.json();
  }
}

export const gameApi = new GameApiService();
```

### 2. Update GameArea Component
Replace the current `GameArea.tsx` with:
```typescript
"use client";

import { useState, useEffect } from "react";
import { Keyboard } from "./Keyboard";
import { gameApi } from "../services/gameApi";

export const GameArea = () => {
  const [wordInput, setWordInput] = useState<string>('');
  const [gameReady, setGameReady] = useState(false);
  const [gameActive, setGameActive] = useState(false);
  const [currentWord, setCurrentWord] = useState<string>('');
  const [playerSuggestions, setPlayerSuggestions] = useState({});
  const [gameState, setGameState] = useState(null);
  const [playerResult, setPlayerResult] = useState(null);
  const [umiResult, setUmiResult] = useState(null);
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(false);
  
  const minWordLength = 3, maxWordLength = 7;

  // Initialize game service on component mount
  useEffect(() => {
    initializeGame();
  }, []);

  const initializeGame = async () => {
    try {
      setLoading(true);
      const data = await gameApi.initialize();
      
      if (data.status === 'initialized') {
        setGameReady(true);
        setError('');
      }
    } catch (error) {
      setError('Failed to initialize game service');
      console.error('Initialization error:', error);
    } finally {
      setLoading(false);
    }
  };

  const startGame = async (startWord: string) => {
    try {
      setLoading(true);
      const data = await gameApi.startGame(startWord);
      
      if (data.status === 'game_started') {
        setGameState(data.game_state);
        setPlayerSuggestions(data.player_suggestions);
        setCurrentWord(startWord);
        setGameActive(true);
        setError('');
      }
    } catch (error) {
      setError('Failed to start game');
      console.error('Start game error:', error);
    } finally {
      setLoading(false);
    }
  };

  // EVENT HANDLERS
  const handleKeyPress = (key: string) => {
    if (wordInput.length < maxWordLength) {
      setWordInput(prev => prev + key);
      setError(''); // Clear any previous errors
    }
  };

  const handleBackspace = () => {
    setWordInput(prev => prev.slice(0, -1));
  };

  const handleSubmit = async () => {
    if (wordInput.length >= minWordLength && wordInput.length <= maxWordLength) {
      try {
        setLoading(true);
        const data = await gameApi.processMove(wordInput);
        
        if (data.status === 'move_processed') {
          // Update game state
          setGameState(data.game_state);
          setPlayerSuggestions(data.player_suggestions);
          
          // Display results
          setPlayerResult(data.player_result);
          setUmiResult(data.umi_result);
          
          // Clear input for next round
          setWordInput('');
          setError('');
        } else if (data.status === 'invalid_word') {
          setError(data.error);
        } else if (data.status === 'duplicate_word') {
          setError(data.error);
        }
      } catch (error) {
        setError('Failed to process move');
        console.error('Move processing error:', error);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleEndGame = async () => {
    try {
      setLoading(true);
      const data = await gameApi.endGame();
      
      if (data.status === 'game_ended') {
        // Handle game summary display
        console.log('Game ended:', data);
        setGameActive(false);
      }
    } catch (error) {
      setError('Failed to end game');
      console.error('End game error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center p-4">Loading...</div>;
  }

  if (!gameReady) {
    return <div className="text-center p-4">Initializing game service...</div>;
  }

  if (!gameActive) {
    return (
      <div className="text-center p-4">
        <h2 className="text-xl font-bold mb-4">Start a New Game</h2>
        <button 
          onClick={() => startGame('hello')} // Default start word
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Start Game
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Game Status */}
      <div className="bg-gray-100 p-4 rounded">
        <h3 className="font-bold">Current Word: {currentWord}</h3>
        <p>Round: {gameState?.rounds_played || 0}</p>
        <p>Player Score: {gameState?.player_score || 0}</p>
        <p>Umi Score: {gameState?.umi_score || 0}</p>
      </div>

      {/* Word Input */}
      <div className="text-center">
        <div className="text-2xl font-mono mb-2">{wordInput || '_'.repeat(3)}</div>
        <p className="text-sm text-gray-600">
          {wordInput.length}/{maxWordLength} letters
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Results Display */}
      {playerResult && (
        <div className="bg-green-100 p-4 rounded">
          <h4 className="font-bold">Your Score: {playerResult.data?.total_score || 0}</h4>
          <p>{playerResult.message}</p>
        </div>
      )}

      {umiResult && (
        <div className="bg-blue-100 p-4 rounded">
          <h4 className="font-bold">Umi's Score: {umiResult.data?.total_score || 0}</h4>
          <p>{umiResult.message}</p>
        </div>
      )}

      {/* Suggestions Display */}
      {Object.keys(playerSuggestions).length > 0 && (
        <div className="bg-yellow-100 p-4 rounded">
          <h4 className="font-bold mb-2">Suggestions:</h4>
          <div className="grid grid-cols-2 gap-2 text-sm">
            {Object.entries(playerSuggestions).map(([type, suggestion]) => (
              <div key={type} className="bg-white p-2 rounded">
                <span className="font-bold">{type.toUpperCase()}:</span> {suggestion.word}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Keyboard */}
      <Keyboard
        onKeyPress={handleKeyPress}
        onBackspace={handleBackspace}
      />

      {/* Game Controls */}
      <div className="flex justify-center space-x-4">
        <button 
          onClick={handleSubmit}
          disabled={wordInput.length < minWordLength || wordInput.length > maxWordLength}
          className="bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600 disabled:bg-gray-300"
        >
          Submit Word
        </button>
        <button 
          onClick={handleEndGame}
          className="bg-red-500 text-white px-6 py-2 rounded hover:bg-red-600"
        >
          End Game
        </button>
      </div>
    </div>
  );
};
```

### 3. Add State Management
Create `src/hooks/useGameState.ts`:
```typescript
import { useState, useCallback } from 'react';

export const useGameState = () => {
  const [gameState, setGameState] = useState(null);
  const [playerSuggestions, setPlayerSuggestions] = useState({});
  const [currentWord, setCurrentWord] = useState('');
  const [gameActive, setGameActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const updateGameState = useCallback((newState) => {
    setGameState(newState);
  }, []);

  const updateSuggestions = useCallback((newSuggestions) => {
    setPlayerSuggestions(newSuggestions);
  }, []);

  const setCurrentWordState = useCallback((word) => {
    setCurrentWord(word);
  }, []);

  const setGameActiveState = useCallback((active) => {
    setGameActive(active);
  }, []);

  const setLoadingState = useCallback((loading) => {
    setLoading(loading);
  }, []);

  const setErrorState = useCallback((error) => {
    setError(error);
  }, []);

  const clearError = useCallback(() => {
    setError('');
  }, []);

  return {
    gameState,
    playerSuggestions,
    currentWord,
    gameActive,
    loading,
    error,
    updateGameState,
    updateSuggestions,
    setCurrentWordState,
    setGameActiveState,
    setLoadingState,
    setErrorState,
    clearError
  };
};
```

### 4. Create Result Display Components
Create `src/components/GameResults.tsx`:
```typescript
interface GameResultsProps {
  playerResult: any;
  umiResult: any;
}

export const GameResults = ({ playerResult, umiResult }: GameResultsProps) => {
  if (!playerResult && !umiResult) return null;

  return (
    <div className="space-y-4">
      {playerResult && (
        <div className="bg-green-100 border border-green-400 p-4 rounded">
          <h4 className="font-bold text-green-800">Your Score</h4>
          <div className="text-2xl font-bold text-green-600">
            {playerResult.data?.total_score || 0}
          </div>
          <p className="text-green-700">{playerResult.message}</p>
          {playerResult.data?.valid_categories && (
            <div className="mt-2">
              <span className="text-sm text-green-600">
                Categories: {playerResult.data.valid_categories.join(', ')}
              </span>
            </div>
          )}
        </div>
      )}

      {umiResult && (
        <div className="bg-blue-100 border border-blue-400 p-4 rounded">
          <h4 className="font-bold text-blue-800">Umi's Score</h4>
          <div className="text-2xl font-bold text-blue-600">
            {umiResult.data?.total_score || 0}
          </div>
          <p className="text-blue-700">{umiResult.message}</p>
          {umiResult.data?.valid_categories && (
            <div className="mt-2">
              <span className="text-sm text-blue-600">
                Categories: {umiResult.data.valid_categories.join(', ')}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
```

## Key Benefits of This Integration

- **Real-time ML scoring** using optimized Redis storage
- **Intelligent word suggestions** based on frequency data
- **Comprehensive game flow** following the ML engine architecture
- **Efficient storage** with Redis + JSON fallback
- **Professional error handling** with useful feedback
- **Type-safe API calls** with TypeScript interfaces

## Important Implementation Notes

- **Method Names**: The actual `game_service.py` methods are:
  - `initialize()` - no parameters
  - `start_game(start_word: str)` - takes start_word parameter
  - `process_player_move(candidate_word: str)` - takes candidate_word parameter
  - `end_game()` - no parameters
  - `get_game_status()` - no parameters
  - `reset_game()` - no parameters

- **Parameter Names**: The frontend should send:
  - `start_word` (not `startWord`)
  - `candidate_word` (not `candidateWord`)

- **Return Structure**: All methods return a dict with a `status` field and additional data

## Error Handling

The ML engine provides detailed error messages:
- `invalid_word`: Word not in dictionary or not a valid transformation
- `duplicate_word`: Word already played in this game
- `invalid_transformation`: Word not a valid transformation of the current word

## Performance Considerations

- **Redis-first storage** for fast lookup of common words
- **JSON fallback** for less common combinations
- **Real-time ML scoring** with DistilGPT-2 model
- **Optimized data structures** for minimal API response time

## Testing

Test the integration with:
1. **Valid words** (should score successfully)
2. **Invalid words** (should show appropriate errors)
3. **Game flow** (start → play → end cycle)
4. **Error scenarios** (network issues, invalid responses)

## Next Steps

1. **Implement the API service layer**
2. **Update the GameArea component**
3. **Add proper error handling and loading states**
4. **Test with the ML engine**
5. **Add game summary displays**
6. **Implement suggestion highlighting**

This integration will transform the basic frontend into a fully functional ML-powered word game with real-time scoring and intelligent suggestions!
