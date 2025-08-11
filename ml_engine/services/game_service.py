#!/usr/bin/env python3
"""
Game Service API for Wurdo ML Engine Integration

This module provides a clean interface between the frontend and ML engine,
implementing the game flow architecture defined in GAME_FLOW_ARCHITECTURE.md
Leverages existing, proven components from services and utils folders.
"""

import asyncio
import json
import logging
import os
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# ML Engine imports - using existing, proven components
from ml_engine.services.enhanced_scoring_service import get_enhanced_scoring_service
from ml_engine.services.efficient_word_service import get_efficient_word_service
from ml_engine.services.optimized_storage_service import get_optimized_storage_service, StorageConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GameServiceError(Exception):
    """Custom exception for game service errors"""
    pass

class GameService:
    """
    Main game service class implementing the Wurdo game flow architecture.

    Handles game initialization, player moves, Umi responses, and game state management
    through integration with existing ML engine services and Redis storage.
    """

    def __init__(self, game_data_path: str = None):
        """
        Initialize GameService with game data path

        Args:
            game_data_path: Path to game data directory (defaults to ml_engine/game_data)
        """
        self.game_data_path = Path(game_data_path) if game_data_path else Path("game_data")
        self.scoring_service = None
        self.word_service = None
        self.storage_service = None
        self.frequencies_data = {}
        self.game_state = None
        self.initialized = False
        self.logger = logging.getLogger(__name__)

    async def initialize(self) -> Dict[str, Any]:
        """
        PHASE 1: Initialize ML components and prepare game state

        Returns:
            Dict containing initialization status
        """
        try:
            self.logger.info(f"Initializing GameService at {datetime.now()}")

            # Initialize storage service with hybrid configuration (Redis + JSON fallback)
            # Storage service will handle its own Redis connection for proper pipelining support
            # Uses REDIS_URL from environment (Upstash cloud Redis for production)
            storage_config = StorageConfig(
                storage_type="hybrid",
                json_file_path=str(self.game_data_path / "probability_trees.json")
                # redis_url will be picked up from REDIS_URL environment variable
            )
            self.storage_service = get_optimized_storage_service(storage_config)

            # Get existing, proven services - pass storage service to scoring service
            self.scoring_service = get_enhanced_scoring_service(storage_service=self.storage_service)
            self.word_service = get_efficient_word_service()

            # Load frequencies.json for word validation and frequency lookup
            await self._load_frequencies_data()

            self.initialized = True
            self.logger.info("GameService initialization completed successfully")

            return {"status": "initialized", "message": "Game service ready"}

        except Exception as e:
            error_msg = f"GameService initialization failed: {str(e)}"
            self.logger.error(f"{error_msg} at {traceback.extract_stack()[-1]}")
            raise GameServiceError(error_msg)

    async def _load_frequencies_data(self):
        """Load frequency data from frequencies.json for word validation and frequency lookup"""
        try:
            frequencies_path = self.game_data_path / "frequencies.json"
            if frequencies_path.exists():
                with open(frequencies_path, 'r') as f:
                    self.frequencies_data = json.load(f)
                self.logger.info(f"Loaded {len(self.frequencies_data)} word frequencies")
            else:
                self.logger.warning(f"frequencies.json not found at {frequencies_path}, word validation will be limited")
                self.frequencies_data = {}
        except Exception as e:
            self.logger.error(f"Failed to load frequencies.json: {e}")
            self.frequencies_data = {}



    async def _populate_redis_with_new_words(self, probability_trees_path: str = None) -> Dict[str, int]:
        """
        Populate storage with new words from probability_trees.json (incremental update only)
        Uses unified storage service for efficient compressed data transfer

        Args:
            probability_trees_path: Path to probability_trees.json (defaults to game_data location)

        Returns:
            Dict with counts of new words added and total processed
        """
        try:
            # Use provided path or default to game_data location
            if probability_trees_path is None:
                probability_trees_path = self.game_data_path / "probability_trees.json"

            if not Path(probability_trees_path).exists():
                self.logger.warning(f"Probability trees file not found: {probability_trees_path}")
                return {"new_words_added": 0, "total_processed": 0}

            # Use the unified storage service for efficient population
            # This ensures consistency with our harmonized storage approach
            result = await self.storage_service.populate_from_file(str(probability_trees_path))

            # Map the result to maintain backward compatibility
            return {
                "new_words_added": result.get("new_trees_added", 0),
                "total_processed": result.get("total_processed", 0)
            }

        except Exception as e:
            self.logger.error(f"Failed to populate storage: {e}")
            return {"new_words_added": 0, "total_processed": 0, "error": str(e)}



    def _is_valid_word(self, word: str) -> bool:
        """
        Check if word exists in frequencies.json (PHASE 2 requirement)

        Args:
            word: Word to validate

        Returns:
            True if word exists in dictionary
        """
        return word.lower() in self.frequencies_data

    def _get_word_frequency(self, word: str) -> float:
        """
        Get word frequency from frequencies.json

        Args:
            word: Word to get frequency for

        Returns:
            Frequency value or 0.0 if not found
        """
        return self.frequencies_data.get(word.lower(), 0.0)

    async def start_game(self, start_word: str) -> Dict[str, Any]:
        """
        Start a new game with the specified start word

        Args:
            start_word: The word to begin the game with

        Returns:
            Dict containing player_suggestions and game state
        """
        try:
            if not self.initialized:
                raise GameServiceError("GameService not initialized")

            self.logger.info(f"Starting game with start_word: {start_word}")

            # Validate start word against frequencies.json (PHASE 1 requirement)
            if not self._is_valid_word(start_word):
                raise GameServiceError(f"Start word '{start_word}' is not in the dictionary")

            # Validate start word using word service transformations
            transformations = self.word_service.get_comprehensive_transformations(start_word)
            if not transformations.all_transformations:
                raise GameServiceError(f"Start word '{start_word}' has no valid transformations")

            # Get probability tree using unified hybrid storage (Redis first, JSON fallback)
            probability_tree = self.storage_service.get_probability_tree(start_word)

            # Create suggestion objects using existing word service with real frequencies
            # Exclude the start word from suggestions since it's already played
            player_suggestions = await self._create_suggestions_with_frequencies(transformations, excluded_words=[start_word])
            umi_suggestions = player_suggestions.copy()

            # Initialize game state
            self.game_state = {
                "start_word": start_word,
                "current_word": start_word,
                "player_chain": [start_word],
                "umi_chain": [start_word],
                "player_suggestions": player_suggestions,
                "umi_suggestions": umi_suggestions,
                "rounds_played": 0,
                "player_score": 0,
                "umi_score": 0,
                "game_started": datetime.now().isoformat()
            }

            self.logger.info(f"Game started successfully with {len(player_suggestions)} suggestion categories")

            return {
                "status": "game_started",
                "player_suggestions": player_suggestions,
                "game_state": self.game_state
            }

        except Exception as e:
            error_msg = f"Failed to start game: {str(e)}"
            self.logger.error(f"{error_msg} at {traceback.extract_stack()[-1]}")
            raise GameServiceError(error_msg)

    async def process_player_move(self, candidate_word: str) -> Dict[str, Any]:
        """
        Process a player move and generate Umi response

        Args:
            candidate_word: The word played by the player

        Returns:
            Dict containing play results and updated suggestions
        """
        try:
            if not self.initialized or not self.game_state:
                raise GameServiceError("Game not initialized or started")

            self.logger.info(f"Processing player move: {candidate_word}")

            # PHASE 2: Candidate validation against frequencies.json
            if not self._is_valid_word(candidate_word):
                return {
                    "error": f"Oops! It looks like '{candidate_word}' is not in the dictionary",
                    "status": "invalid_word"
                }

            # Check if word has already been played
            if candidate_word in self.game_state.get("player_chain", []) or candidate_word in self.game_state.get("umi_chain", []):
                return {
                    "error": f"Oops! '{candidate_word}' has already been played in this game",
                    "status": "duplicate_word"
                }

            # Validate candidate word using existing word service
            transformations = self.word_service.get_comprehensive_transformations(self.game_state["current_word"])
            if candidate_word not in transformations.all_transformations:
                return {
                    "error": f"Oops! It looks like '{candidate_word}' is not a valid transformation of '{self.game_state['current_word']}'",
                    "status": "invalid_word"
                }

            # Score player's move using existing scoring service
            player_result = await self.scoring_service.score_candidate_comprehensive(
                self.game_state["current_word"],
                candidate_word
            )

            # Extract only the highest scoring category for player
            player_result = self._extract_highest_scoring_category(player_result)

            # Extract play type and select Umi response
            play_type = self._extract_play_type(self.game_state["current_word"], candidate_word)
            umi_word = self._select_umi_response(play_type)

            # Score Umi's response using existing scoring service
            # Umi should be scored against her last word in her chain, not the player's word
            umi_last_word = self.game_state["umi_chain"][-1] if self.game_state["umi_chain"] else self.game_state["start_word"]
            umi_result = await self.scoring_service.score_candidate_comprehensive(
                umi_last_word,  # Umi responds to her own last word in her chain
                umi_word
            )

            # Extract only the highest scoring category for Umi
            umi_result = self._extract_highest_scoring_category(umi_result)

            # Update game state
            await self._update_game_state(candidate_word, umi_word, player_result, umi_result)

            # Update suggestions using existing word service with real frequencies
            await self._update_suggestions_with_frequencies(candidate_word, umi_word)

            self.logger.info(f"Player move processed successfully. Player score: {player_result.get('data', {}).get('total_score', 0):.2f}")

            return {
                "status": "move_processed",
                "player_result": player_result,
                "umi_result": umi_result,
                "player_suggestions": self.game_state["player_suggestions"],
                "game_state": self.game_state
            }

        except Exception as e:
            error_msg = f"Failed to process player move: {str(e)}"
            self.logger.error(f"{error_msg} at {traceback.extract_stack()[-1]}")
            raise GameServiceError(error_msg)

    async def end_game(self) -> Dict[str, Any]:
        """
        End the current game and generate summaries

        Returns:
            Dict containing game summaries and final statistics
        """
        try:
            if not self.game_state:
                raise GameServiceError("No active game to end")

            self.logger.info("Ending game and generating summaries")

            # Generate chain summaries using existing word service with real frequencies
            player_summary = await self._generate_chain_summary_with_frequencies(self.game_state["player_chain"], "player")
            umi_summary = await self._generate_chain_summary_with_frequencies(self.game_state["umi_chain"], "umi")

            # Calculate final statistics
            final_stats = {
                "total_rounds": self.game_state["rounds_played"],
                "player_chain_length": len(self.game_state["player_chain"]),
                "umi_chain_length": len(self.game_state["umi_chain"]),
                "game_duration": (datetime.now() - datetime.fromisoformat(self.game_state["game_started"])).total_seconds(),
                "final_state": self.game_state
            }

            # Sync Redis with JSON file to ensure all probability trees are cached
            # This captures any updates that may have been added to the JSON file
            redis_sync_result = await self._populate_redis_with_new_words()
            self.logger.info(f"Redis sync completed: {redis_sync_result}")

            self.logger.info(f"Game ended successfully. Total rounds: {final_stats['total_rounds']}")

            return {
                "status": "game_ended",
                "player_summary": player_summary,
                "umi_summary": umi_summary,
                "final_stats": final_stats,
                "redis_update": redis_sync_result
            }

        except Exception as e:
            error_msg = f"Failed to end game: {str(e)}"
            self.logger.error(f"{error_msg} at {traceback.extract_stack()[-1]}")
            raise GameServiceError(error_msg)

    def _extract_play_type(self, start_word: str, candidate_word: str) -> str:
        """
        Extract the play type from word transformation

        Args:
            start_word: The starting word
            candidate_word: The transformed word

        Returns:
            String representing the play type
        """
        # Use existing word service logic for play type detection
        transformations = self.word_service.get_comprehensive_transformations(start_word)

        # Check each category systematically (matching terminal implementation patterns)
        if candidate_word in transformations.perfect_rhymes:
            return "prf"
        elif candidate_word in transformations.rich_rhymes:
            return "rch"
        elif candidate_word in transformations.slant_rhymes:
            return "sln"
        elif candidate_word in transformations.anagrams:
            return "ana"
        elif candidate_word in transformations.added_letters:
            return "ola"
        elif candidate_word in transformations.removed_letters:
            return "olr"
        elif candidate_word in transformations.changed_letters:
            return "olx"
        else:
            return "unknown"

    def _select_umi_response(self, play_type: str) -> str:
        """
        Select Umi's response based on her own chain, not the player's play type

        Args:
            play_type: The type of play made by the player (used for logging only)

        Returns:
            String representing Umi's selected word
        """
        # Umi should respond to her own chain, not to the player's word
        # Get Umi's last word from her chain
        umi_last_word = self.game_state["umi_chain"][-1] if self.game_state["umi_chain"] else self.game_state["start_word"]

        # Get Umi's suggestions based on her own word
        umi_suggestions = self.game_state.get("umi_suggestions", {})

        # Try to find the best available suggestion from Umi's suggestions
        # Priority: same play type first, then any available suggestion
        if play_type in umi_suggestions and umi_suggestions[play_type] and umi_suggestions[play_type].get("word"):
            selected_word = umi_suggestions[play_type]["word"]
            self.logger.debug(f"Umi selected {play_type} word: {selected_word} from her own chain")
            return selected_word
        else:
            # Try to find any available suggestion from other play types
            for other_play_type, other_suggestions in umi_suggestions.items():
                if other_suggestions and other_suggestions.get("word") and other_play_type != play_type:
                    selected_word = other_suggestions["word"]
                    self.logger.debug(f"Umi using {other_play_type} suggestion '{selected_word}' from her own chain")
                    return selected_word

            # If no suggestions available at all, use the current word (pass turn)
            self.logger.warning(f"No Umi suggestions available for her chain")
            return umi_last_word

    async def _update_game_state(self, player_word: str, umi_word: str,
                                player_result: Dict, umi_result: Dict):
        """
        Update the game state after a move

        Args:
            player_word: The word played by the player
            umi_word: The word played by Umi
            player_result: The scoring result for the player's move
            umi_result: The scoring result for Umi's move
        """
        # Update chains
        self.game_state["player_chain"].append(player_word)
        self.game_state["umi_chain"].append(umi_word)

        # Update current word for next round
        # Player will continue from their own word (player_word), creating divergent chains
        # Umi will continue from her own word (umi_word) in her own chain
        # The current_word represents the player's current word for their next move
        self.game_state["current_word"] = player_word

        # Update round count
        self.game_state["rounds_played"] += 1

        # Update scores from scoring results
        if player_result.get('success') and player_result.get('data'):
            player_score = player_result['data'].get('total_score', 0)
            self.game_state["player_score"] = self.game_state.get("player_score", 0) + player_score
            self.logger.info(f"Updated player score: {player_score} (total: {self.game_state['player_score']})")

        if umi_result.get('success') and umi_result.get('data'):
            umi_score = umi_result['data'].get('total_score', 0)
            self.game_state["umi_score"] = self.game_state.get("umi_score", 0) + umi_score
            self.logger.info(f"Updated Umi score: {umi_score} (total: {self.game_state['umi_score']})")

        # Store results for history
        if "move_history" not in self.game_state:
            self.game_state["move_history"] = []

        self.game_state["move_history"].append({
            "round": self.game_state["rounds_played"],
            "player_word": player_word,
            "umi_word": umi_word,
            "player_result": player_result,
            "umi_result": umi_result
        })

    async def _update_suggestions_with_frequencies(self, player_word: str, umi_word: str):
        """
        Update suggestions for both player and Umi with real frequency data

        Args:
            player_word: The word played by the player
            umi_word: The word played by Umi
        """
        try:
            # Get all words already played in both chains
            player_chain = self.game_state.get("player_chain", [])
            umi_chain = self.game_state.get("umi_chain", [])
            all_played_words = player_chain + umi_chain

            # Update player suggestions using existing word service with real frequencies
            # Exclude words already played by either player
            player_transformations = self.word_service.get_comprehensive_transformations(player_word)
            self.game_state["player_suggestions"] = await self._create_suggestions_with_frequencies(
                player_transformations, excluded_words=all_played_words
            )

            # Update Umi suggestions using existing word service with real frequencies
            # Umi's suggestions should be based on her last word in her chain, not the word she just played
            # This ensures Umi has valid moves for her next turn based on her own chain
            umi_last_word = self.game_state["umi_chain"][-1] if self.game_state["umi_chain"] else self.game_state["start_word"]
            umi_transformations = self.word_service.get_comprehensive_transformations(umi_last_word)
            self.game_state["umi_suggestions"] = await self._create_suggestions_with_frequencies(
                umi_transformations, excluded_words=all_played_words
            )

        except Exception as e:
            self.logger.warning(f"Failed to update suggestions: {str(e)}")
            # Keep existing suggestions if update fails

    async def _create_suggestions_with_frequencies(self, transformations, excluded_words: List[str] = None) -> Dict[str, Dict]:
        """
        Create suggestion objects from transformation data with real frequencies and ML scores

        Args:
            transformations: TransformationData object from word service
            excluded_words: List of words to exclude from suggestions (already played)

        Returns:
            Dict containing single best suggestion for each play type with real data
        """
        if excluded_words is None:
            excluded_words = []

        suggestions = {}

        # Map transformation categories to play types (matching terminal implementation)
        category_mapping = {
            "prf": transformations.perfect_rhymes,
            "rch": transformations.rich_rhymes,
            "sln": transformations.slant_rhymes,
            "ana": transformations.anagrams,
            "ola": transformations.added_letters,
            "olr": transformations.removed_letters,
            "olx": transformations.changed_letters
        }

        for play_type, word_list in category_mapping.items():
            if word_list:
                # Filter out already played words
                available_words = [word for word in word_list if word not in excluded_words]

                if available_words:
                    # Find the word with highest frequency among available words
                    best_word = None
                    best_frequency = -1

                    for word in available_words:
                        frequency = self._get_word_frequency(word)
                        if frequency > best_frequency:
                            best_frequency = frequency
                            best_word = word

                    if best_word:
                        # Create single suggestion object with real data
                        suggestions[play_type] = {
                            "word": best_word,
                            "frequency": best_frequency,
                            "frequency_rank": self._calculate_frequency_rank(best_frequency)
                        }

        return suggestions

    def _calculate_frequency_rank(self, frequency: float) -> str:
        """
        Calculate frequency rank based on real frequency data

        Args:
            frequency: Frequency value from frequencies.json

        Returns:
            String representing frequency rank
        """
        if frequency >= 1e-03:  # 0.001
            return "very_common"
        elif frequency >= 1e-05:  # 0.00001
            return "common"
        elif frequency >= 1e-07:  # 0.0000001
            return "uncommon"
        elif frequency >= 1e-09:  # 0.000000001
            return "rare"
        else:
            return "very_rare"

    async def _generate_chain_summary_with_frequencies(self, word_chain: List[str], chain_type: str = "player") -> Dict[str, Any]:
        """
        Generate summary for a word chain with real frequency data and scores

        Args:
            word_chain: List of words in the chain
            chain_type: Either "player" or "umi" to get the correct scores

        Returns:
            Dict containing chain summary with real frequency data and scores
        """
        if not word_chain:
            return {
                "chain_length": 0,
                "words": [],
                "start_word": None,
                "end_word": None,
                "avg_frequency": 0.0,
                "frequency_distribution": {},
                "total_score": 0,
                "avg_score": 0.0
            }

        # Calculate real frequency statistics
        frequencies = [self._get_word_frequency(word) for word in word_chain]
        avg_frequency = sum(frequencies) / len(frequencies) if frequencies else 0.0

        # Calculate frequency distribution
        frequency_distribution = {}
        for word in word_chain:
            rank = self._calculate_frequency_rank(self._get_word_frequency(word))
            frequency_distribution[rank] = frequency_distribution.get(rank, 0) + 1

        # Get scores from game state
        total_score = 0
        if self.game_state and "move_history" in self.game_state:
            for move in self.game_state["move_history"]:
                if chain_type == "player" and move.get("player_word") in word_chain:
                    if move.get("player_result", {}).get("success") and move.get("player_result", {}).get("data"):
                        total_score += move["player_result"]["data"].get("total_score", 0)
                elif chain_type == "umi" and move.get("umi_word") in word_chain:
                    if move.get("umi_result", {}).get("success") and move.get("umi_result", {}).get("data"):
                        total_score += move["umi_result"]["data"].get("total_score", 0)

        avg_score = total_score / len(word_chain) if word_chain else 0.0

        return {
            "chain_length": len(word_chain),
            "words": word_chain,
            "start_word": word_chain[0],
            "end_word": word_chain[-1],
            "avg_frequency": avg_frequency,
            "frequency_distribution": frequency_distribution,
            "total_frequency_score": sum(frequencies),
            "total_score": total_score,
            "avg_score": avg_score
        }

    async def get_game_status(self) -> Dict[str, Any]:
        """
        Get current game status

        Returns:
            Dict containing current game state
        """
        if not self.game_state:
            return {"status": "no_active_game"}

        return {
            "status": "active_game",
            "game_state": self.game_state
        }

    async def reset_game(self) -> Dict[str, Any]:
        """
        Reset the current game

        Returns:
            Dict containing reset status
        """
        self.game_state = {}
        self.logger.info("Game reset successfully")

        return {"status": "game_reset", "message": "Game has been reset"}

    async def populate_redis_manually(self, probability_trees_path: str = None) -> Dict[str, Any]:
        """
        Manually populate Redis with new words from probability_trees.json

        Args:
            probability_trees_path: Path to probability_trees.json (defaults to game_data location)

        Returns:
            Dict containing population results
        """
        try:
            if not self.initialized:
                raise GameServiceError("GameService not initialized")

            self.logger.info("Manually populating Redis with new words")
            result = await self._populate_redis_with_new_words(probability_trees_path)

            return {
                "status": "redis_population_completed",
                "result": result
            }

        except Exception as e:
            error_msg = f"Failed to populate Redis manually: {str(e)}"
            self.logger.error(f"{error_msg} at {traceback.extract_stack()[-1]}")
            raise GameServiceError(error_msg)

    def _extract_highest_scoring_category(self, scoring_result: Dict) -> Dict:
        """
        Extract only the highest scoring category from a scoring result

        Args:
            scoring_result: The raw scoring result from the scoring service

        Returns:
            Dict with only the highest scoring category
        """
        if not scoring_result.get('success') or not scoring_result.get('data'):
            return scoring_result

        data = scoring_result['data']
        category_scores = data.get('category_scores', {})

        if not category_scores:
            return scoring_result

        # Find the category with the highest score
        highest_category = None
        highest_score = -1

        for category, score in category_scores.items():
            if isinstance(score, (int, float)) and score > highest_score:
                highest_score = score
                highest_category = category

        if highest_category:
            # Create a new result with only the highest scoring category
            filtered_data = data.copy()
            filtered_data['category_scores'] = {highest_category: highest_score}
            filtered_data['valid_categories'] = [highest_category]
            filtered_data['category_count'] = 1
            filtered_data['total_score'] = highest_score

            return {
                'success': True,
                'message': f"Scored in highest category: {highest_category}",
                'data': filtered_data
            }

        return scoring_result

async def get_game_service(game_data_path: str = None) -> GameService:
    """
    Factory function to get a configured game service instance

    Args:
        game_data_path: Path to game data directory (defaults to ml_engine/game_data)

    Returns:
        Configured GameService instance
    """
    service = GameService(game_data_path)
    await service.initialize()
    return service
