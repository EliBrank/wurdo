#!/usr/bin/env python3
"""
Enhanced Scoring Game with Visual Interface
==========================================

A word transformation game with visual score meters and detailed feedback.
"""

import sys
import asyncio
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Add ml_engine to path
sys.path.append(str(Path(__file__).parent))

from services.enhanced_scoring_service import get_enhanced_scoring_service

@dataclass
class PlayResult:
    """Result of a single play."""
    word: str
    categories: List[str]
    category_scores: Dict[str, float]
    total_score: float
    avg_creativity_score: float
    contribution_percentage: float

class ScoringGame:
    """Enhanced scoring game with visual interface."""
    
    def __init__(self):
        """Initialize the game."""
        self.scoring_service = get_enhanced_scoring_service()
        self.current_word = None
        self.session_words = []
        self.session_scores = []
        self.total_session_score = 0.0
        self.max_session_turns = 7
        
        # Game data file
        self.game_data_file = "game_data/scoring_game_data.json"
        self.load_game_data()
    
    def load_game_data(self):
        """Load game data from file."""
        try:
            if os.path.exists(self.game_data_file):
                with open(self.game_data_file, 'r') as f:
                    data = json.load(f)
                    self.session_words = data.get('session_words', [])
                    self.session_scores = data.get('session_scores', [])
                    self.total_session_score = data.get('total_session_score', 0.0)
                    self.current_word = data.get('current_word', None)
        except Exception as e:
            print(f"⚠️ Could not load game data: {e}")
    
    def save_game_data(self):
        """Save game data to file."""
        try:
            os.makedirs(os.path.dirname(self.game_data_file), exist_ok=True)
            with open(self.game_data_file, 'w') as f:
                json.dump({
                    'session_words': self.session_words,
                    'session_scores': self.session_scores,
                    'total_session_score': self.total_session_score,
                    'current_word': self.current_word,
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save game data: {e}")
    
    def start_new_session(self):
        """Start a new game session."""
        self.session_words = []
        self.session_scores = []
        self.total_session_score = 0.0
        self.current_word = self.get_start_word()
        self.save_game_data()
        print("🎮 New session started!")
    
    def get_start_word(self) -> str:
        """Get a start word from user or use default."""
        print("\n🎯 Enter a start word (or press Enter for 'cat'):")
        choice = input("> ").strip().lower()
        return choice if choice else "cat"
    
    def display_score_meter(self, current_score: float, max_score: float = 5000):
        """Display a visual score meter."""
        percentage = min(current_score / max_score, 1.0)
        bar_length = 50
        filled_length = int(bar_length * percentage)
        
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        print(f"\n📊 Score Meter: {current_score:.0f} / {max_score}")
        print(f"   [{bar}] {percentage*100:.1f}%")
    
    def display_contribution_bar(self, contribution: float, max_contribution: float = 500):
        """Display a bar showing the contribution of the last play."""
        percentage = min(contribution / max_contribution, 1.0)
        bar_length = 30
        filled_length = int(bar_length * percentage)
        
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        print(f"🎯 Last Play Contribution: {contribution:.0f} points")
        print(f"   [{bar}] {percentage*100:.1f}%")
    
    def display_session_progress(self):
        """Display current session progress."""
        turns_remaining = self.max_session_turns - len(self.session_words)
        print(f"\n🔄 Session Progress: {len(self.session_words)}/{self.max_session_turns} turns")
        print(f"   Turns remaining: {turns_remaining}")
        
        if self.session_words:
            print(f"   Words played: {', '.join(self.session_words)}")
    
    async def score_candidate(self, candidate_word: str) -> Optional[PlayResult]:
        """Score a candidate word and return detailed result."""
        if not self.current_word:
            print("❌ No current word set!")
            return None
        
        try:
            # Get comprehensive score
            result = await self.scoring_service.score_candidate_comprehensive(
                self.current_word, candidate_word
            )
            
            if not result["success"]:
                print(f"❌ {result['message']}")
                return None
            
            data = result["data"]
            
            # Calculate contribution percentage
            total_score = data["total_score"]
            contribution_percentage = (total_score / 5000) * 100  # Assuming max score of 5000
            
            return PlayResult(
                word=candidate_word,
                categories=data["valid_categories"],
                category_scores=data["category_scores"],
                total_score=total_score,
                avg_creativity_score=data["avg_creativity_score"],
                contribution_percentage=contribution_percentage
            )
            
        except Exception as e:
            print(f"❌ Error scoring word: {e}")
        return None

    def display_detailed_score(self, result: PlayResult):
        """Display detailed score breakdown."""
        print(f"\n🎯 Score Breakdown for '{result.word}':")
        print(f"   Categories: {', '.join(result.categories).upper()}")
        print(f"   Category Count: {len(result.categories)}")
        
        # Show individual category scores
        for category, score in result.category_scores.items():
            print(f"   {category.upper()}: {score:.0f} points")
        
        print(f"   Total Score: {result.total_score:.0f}")
        print(f"   Avg Creativity: {result.avg_creativity_score:.3f}")
        
        # Display contribution bar
        self.display_contribution_bar(result.total_score)
    
    def display_final_summary(self):
        """Display final session summary with all words and their contributions."""
        if not self.session_words:
            print("❌ No words played in this session!")
            return
        
        print("\n" + "="*80)
        print("🏆 FINAL SESSION SUMMARY")
        print("="*80)
        
        # Display overall score meter
        self.display_score_meter(self.total_session_score)
        
        print(f"\n📝 Words Played (in order):")
        print("-" * 80)
        
        # Header
        print(f"{'Word':<15} {'Categories':<20} {'Total':<8} {'Contribution':<15}")
        print("-" * 80)
        
        # Display each word with its contribution
        for i, (word, score_data) in enumerate(zip(self.session_words, self.session_scores)):
            contribution_percentage = (score_data["total_score"] / self.total_session_score) * 100
            contribution_bar = "█" * int(contribution_percentage / 2) + "░" * (50 - int(contribution_percentage / 2))
            
            categories_str = ", ".join(score_data['categories']).upper()
            print(f"{word:<15} {categories_str:<20} {score_data['total_score']:<8.0f} "
                  f"[{contribution_bar}] {contribution_percentage:.1f}%")
        
        print("-" * 80)
        print(f"🎯 Total Session Score: {self.total_session_score:.0f}")
        print(f"📊 Average Score per Word: {self.total_session_score / len(self.session_words):.0f}")
        
        # Show best and worst words
        if self.session_scores:
            best_word = max(self.session_scores, key=lambda x: x["total_score"])
            worst_word = min(self.session_scores, key=lambda x: x["total_score"])
            
            print(f"\n🏅 Best Word: '{best_word['word']}' ({best_word['total_score']:.0f} points)")
            print(f"📉 Worst Word: '{worst_word['word']}' ({worst_word['total_score']:.0f} points)")
    
    async def play_round(self) -> str:
        """Play a single round."""
        print(f"\n🎯 Current word: '{self.current_word}'")
        self.display_session_progress()
        
        # Show score meter
        self.display_score_meter(self.total_session_score)
        
        print(f"\n💡 Enter a transformation of '{self.current_word}' (or 'new' for new session, 'quit' to exit):")
        candidate = input("> ").strip().lower()
        
        if candidate == "quit":
            return "QUIT"
        elif candidate == "new":
            return "NEW_SESSION"
        elif not candidate:
            print("❌ Please enter a word!")
            return "CONTINUE"
        
        # Score the candidate
        result = await self.score_candidate(candidate)
        if not result:
            return "CONTINUE"
        
        # Display detailed score
        self.display_detailed_score(result)
        
        # Update session
        self.session_words.append(candidate)
        self.session_scores.append({
            "word": candidate,
            "categories": result.categories,
            "category_scores": result.category_scores,
            "total_score": result.total_score,
            "avg_creativity_score": result.avg_creativity_score
        })
        self.total_session_score += result.total_score
        
        # Update current word for next turn
        self.current_word = candidate
        
        # Save game data
        self.save_game_data()
        
        print(f"\n✅ '{candidate}' scored! Added {result.total_score:.0f} points to your session.")
        
        # Check if session is complete
        if len(self.session_words) >= self.max_session_turns:
            print(f"\n🎉 Session complete! You've played {self.max_session_turns} words.")
            self.display_final_summary()
            return "SESSION_COMPLETE"
        
        return "CONTINUE"
    
    def print_instructions(self):
        """Print game instructions."""
        print("🎮 ENHANCED SCORING GAME")
        print("=" * 50)
        print("Transform words and earn points based on creativity!")
        print()
        print("📋 How to play:")
        print("   • Enter a transformation of the current word")
        print("   • Valid transformations: rhymes, anagrams, one-letter changes")
        print("   • Earn points based on creativity and transformation difficulty")
        print("   • Play 7 words to complete a session")
        print()
        print("🎯 Scoring:")
        print("   • Base Score: 500-1000 points (based on creativity)")
        print("   • Category Bonus: Additional points for harder transformations")
        print("   • Anagrams: Highest bonus (250 max)")
        print("   • Perfect Rhymes: Lowest bonus (100 max)")
        print()
        print("💡 Commands:")
        print("   • 'new': Start a new session")
        print("   • 'quit': Exit the game")
        print()

def main():
    """Main game loop."""
    game = ScoringGame()
    game.print_instructions()
    
    # Start new session
    game.start_new_session()
    
    while True:
        result = asyncio.run(game.play_round())
        
        if result == "QUIT":
            print("\n👋 Thanks for playing!")
            break
        elif result == "NEW_SESSION":
            game.start_new_session()
        elif result == "SESSION_COMPLETE":
            print("\n🔄 Starting new session...")
            game.start_new_session()

if __name__ == "__main__":
    main() 