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
    """Enhanced scoring game with visual interface and Umi's tutorial."""
    
    def __init__(self):
        """Initialize the game."""
        self.scoring_service = get_enhanced_scoring_service()
        self.current_word = None
        self.session_words = []
        self.session_scores = []
        self.total_session_score = 0.0
        self.max_session_turns = 7
        
        # Umi's tutorial data
        self.umi_start_word = None
        self.umi_chain = []
        self.umi_scores = []
        self.umi_total_score = 0.0
        self.umi_suggestions = {}
        
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
        
        # Initialize Umi's tutorial
        self.umi_start_word = self.current_word
        self.umi_chain = []
        self.umi_scores = []
        self.umi_total_score = 0.0
        self.umi_suggestions = {}
        
        # Generate Umi's initial suggestions
        self.generate_umi_suggestions()
        
        self.save_game_data()
        print("New session started!")
        print("🌟 Umi is here to help you learn!")
    
    def get_start_word(self) -> str:
        """Get a start word from user or use default."""
        print("\n🎯 Enter a start word (or press Enter for 'cat'):")
        choice = input("> ").strip().lower()
        return choice if choice else "cat"
    
    def display_score_meter(self, current_score: float, max_score: float = 7000):
        """Display a visual score meter."""
        percentage = min(current_score / max_score, 1.0)
        bar_length = 50
        filled_length = int(bar_length * percentage)
        
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        print(f"\n📊 Score Meter: {current_score:.0f} / {max_score}")
        print(f"   [{bar}] {percentage*100:.1f}%")
    
    def display_contribution_bar(self, contribution: float, max_contribution: float = 1350):
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
            # Suppress debug output during scoring
            import os
            import sys
            from contextlib import redirect_stdout, redirect_stderr
            
            # Save original stdout/stderr
            original_stdout = sys.stdout
            original_stderr = sys.stderr
            
            # Redirect to null during scoring
            with open(os.devnull, 'w') as devnull:
                sys.stdout = devnull
                sys.stderr = devnull
                try:
                    # Get comprehensive score
                    result = await self.scoring_service.score_candidate_comprehensive(
                        self.current_word, candidate_word
                    )
                finally:
                    # Restore original stdout/stderr
                    sys.stdout = original_stdout
                    sys.stderr = original_stderr
            
            if not result["success"]:
                print(f"❌ {result['message']}")
                return None
            
            data = result["data"]
            
            # Calculate contribution percentage
            total_score = data["total_score"]
            contribution_percentage = (total_score / 1350) * 100  # Max score for 7-char anagram with max creativity
            
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
        
        # Show scoring formula breakdown
        if result.total_score > 0:
            # Estimate base score and bonus (since we don't have exact breakdown)
            estimated_base = result.total_score / (1 + 0.5 * result.avg_creativity_score)
            estimated_bonus = result.total_score - estimated_base
            print(f"   Estimated Base Score: {estimated_base:.0f}")
            print(f"   Estimated Creativity Bonus: {estimated_bonus:.0f}")
        
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
        
        # Display Umi's suggestions
        self.display_umi_suggestions()
        
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
        
        # Play Umi's chain for the same category
        if result.categories:
            player_category = result.categories[0]  # Use the first category
            print(f"🎯 Player scored in category: {player_category}")
            success = await self.play_umi_chain(player_category)
            if success:
                print(f"🌟 Umi played '{self.umi_chain[-1]}' for {player_category}")
            else:
                print(f"⚠️ Umi couldn't play for category {player_category}")
        
        # Update current word for next turn
        self.current_word = candidate
        
        # Generate new suggestions for next round
        self.generate_umi_suggestions()
        
        # Save game data
        self.save_game_data()
        
        print(f"\n✅ '{candidate}' scored! Added {result.total_score:.0f} points to your session.")
        
        # Check if session is complete
        if len(self.session_words) >= self.max_session_turns:
            print(f"\n🎉 Session complete! You've played {self.max_session_turns} words.")
            self.display_final_summary()
            self.display_umi_chain_summary()
            self.display_comparison_summary()
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
        print("🎯 Scoring System:")
        print("   • Base Score: Based on category and word length")
        print("   • Creativity Bonus: base_score × 0.5 × creativity_score")
        print("   • Total Score: base_score + bonus")
        print()
        print("📊 Base Scores by Category & Length:")
        print("   • Perfect Rhymes (PRF): 50-250 points (3-7 chars)")
        print("   • Rich Rhymes (RCH): 150-750 points (3-7 chars)")
        print("   • Anagrams (ANA): 100-900 points (3-7 chars)")
        print("   • One-Letter-Off (OLA/OLR/OLX): 100-500 points (3-7 chars)")
        print()
        print("💡 Commands:")
        print("   • 'new': Start a new session")
        print("   • 'quit': Exit the game")
        print()
        print("🌟 Umi's Tutorial:")
        print("   • Umi will suggest words for each category")
        print("   • She'll play her own chain alongside yours")
        print("   • Compare your strategy with Umi's at the end!")
        print()

    def generate_umi_suggestions(self):
        """Generate Umi's suggestions for each valid category."""
        try:
            # Suppress debug output during word service calls
            import os
            import sys
            from contextlib import redirect_stdout, redirect_stderr
            
            # Save original stdout/stderr
            original_stdout = sys.stdout
            original_stderr = sys.stderr
            
            # Redirect to null during word service calls
            with open(os.devnull, 'w') as devnull:
                sys.stdout = devnull
                sys.stderr = devnull
                try:
                    # Get comprehensive transformations for current word
                    from services.efficient_word_service import get_efficient_word_service
                    word_service = get_efficient_word_service()
                    transformations = word_service.get_comprehensive_transformations(self.current_word)
                finally:
                    # Restore original stdout/stderr
                    sys.stdout = original_stdout
                    sys.stderr = original_stderr
            
            self.umi_suggestions = {}
            
            # Find most likely (lowest creativity) word for each category
            if transformations.perfect_rhymes:
                self.umi_suggestions['prf'] = transformations.perfect_rhymes[0]  # Most likely perfect rhyme
            if transformations.rich_rhymes:
                self.umi_suggestions['rch'] = transformations.rich_rhymes[0]  # Most likely rich rhyme
            if transformations.slant_rhymes:
                self.umi_suggestions['sln'] = transformations.slant_rhymes[0]  # Most likely slant rhyme
            if transformations.anagrams:
                self.umi_suggestions['ana'] = transformations.anagrams[0]  # Most likely anagram
            if transformations.added_letters:
                self.umi_suggestions['ola'] = transformations.added_letters[0]  # Most likely one-letter-added
            if transformations.removed_letters:
                self.umi_suggestions['olr'] = transformations.removed_letters[0]  # Most likely one-letter-removed
            if transformations.changed_letters:
                self.umi_suggestions['olx'] = transformations.changed_letters[0]  # Most likely one-letter-changed
                
        except Exception as e:
            print(f"⚠️ Could not generate Umi's suggestions: {e}")
            self.umi_suggestions = {}

    def display_umi_suggestions(self):
        """Display Umi's suggestions for the current word."""
        if not self.umi_suggestions:
            print("🌟 Umi is thinking...")
            return
        
        print(f"\n🌟 Umi's suggestions for '{self.current_word}':")
        print("─" * 50)
        
        category_names = {
            'prf': 'Perfect Rhyme',
            'rch': 'Rich Rhyme',
            'sln': 'Slant Rhyme',
            'ana': 'Anagram',
            'ola': 'One-Letter-Added',
            'olr': 'One-Letter-Removed',
            'olx': 'One-Letter-Changed'
        }
        
        for category, word in self.umi_suggestions.items():
            category_name = category_names.get(category, category.upper())
            print(f"   {category_name}: '{word}'")
        
        print("💡 Try one of these or choose your own!")

    async def play_umi_chain(self, player_category: str):
        """Play Umi's chain for the same category as the player."""
        try:
            print(f"🔍 Umi's suggestions: {self.umi_suggestions}")
            print(f"🔍 Looking for category: {player_category}")
            
            # Get Umi's suggestion for the player's chosen category
            if player_category in self.umi_suggestions:
                umi_word = self.umi_suggestions[player_category]
                print(f"🎯 Umi found word '{umi_word}' for category '{player_category}'")
                
                # Suppress debug output during scoring
                import os
                import sys
                from contextlib import redirect_stdout, redirect_stderr
                
                # Save original stdout/stderr
                original_stdout = sys.stdout
                original_stderr = sys.stderr
                
                # Redirect to null during scoring
                with open(os.devnull, 'w') as devnull:
                    sys.stdout = devnull
                    sys.stderr = devnull
                    try:
                        # Score Umi's word
                        result = await self.scoring_service.score_candidate_comprehensive(
                            self.umi_start_word, umi_word
                        )
                    finally:
                        # Restore original stdout/stderr
                        sys.stdout = original_stdout
                        sys.stderr = original_stderr
                
                if result["success"]:
                    data = result["data"]
                    print(f"✅ Umi's word '{umi_word}' scored {data['total_score']:.0f} points")
                    
                    # Store Umi's play
                    self.umi_chain.append(umi_word)
                    self.umi_scores.append({
                        "word": umi_word,
                        "category": player_category,
                        "total_score": data["total_score"],
                        "categories": data["valid_categories"],
                        "category_scores": data["category_scores"],
                        "avg_creativity_score": data["avg_creativity_score"]
                    })
                    self.umi_total_score += data["total_score"]
                    
                    # Update Umi's start word for next round
                    self.umi_start_word = umi_word
                    
                    return True
                else:
                    print(f"❌ Umi's word '{umi_word}' failed to score: {result.get('message', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print(f"⚠️ Umi had trouble playing: {e}")
        
        return False

    def display_umi_chain_summary(self):
        """Display Umi's complete chain summary."""
        if not self.umi_chain:
            return
        
        print("\n" + "="*80)
        print("🌟 UMI'S CHAIN SUMMARY")
        print("="*80)
        
        # Display Umi's score meter
        self.display_score_meter(self.umi_total_score)
        
        print(f"\n📝 Umi's Words Played:")
        print("-" * 80)
        
        # Header
        print(f"{'Word':<15} {'Category':<20} {'Total':<8} {'Contribution':<15}")
        print("-" * 80)
        
        # Display each word with its contribution
        for i, (word, score_data) in enumerate(zip(self.umi_chain, self.umi_scores)):
            contribution_percentage = (score_data["total_score"] / self.umi_total_score) * 100 if self.umi_total_score > 0 else 0
            contribution_bar = "█" * int(contribution_percentage / 2) + "░" * (50 - int(contribution_percentage / 2))
            
            category_str = score_data['category'].upper()
            print(f"{word:<15} {category_str:<20} {score_data['total_score']:<8.0f} "
                  f"[{contribution_bar}] {contribution_percentage:.1f}%")
        
        print("-" * 80)
        print(f"🌟 Umi's Total Score: {self.umi_total_score:.0f}")
        print(f"📊 Umi's Average Score per Word: {self.umi_total_score / len(self.umi_chain):.0f}" if self.umi_chain else "📊 Umi's Average Score per Word: 0.0")

    def display_comparison_summary(self):
        """Display comparison between player and Umi."""
        print("\n" + "="*80)
        print("🏆 PLAYER vs UMI COMPARISON")
        print("="*80)
        
        print(f"🎮 Your Score: {self.total_session_score:.0f}")
        print(f"🌟 Umi's Score: {self.umi_total_score:.0f}")
        
        if self.total_session_score > self.umi_total_score:
            difference = self.total_session_score - self.umi_total_score
            print(f"🏅 You beat Umi by {difference:.0f} points!")
        elif self.umi_total_score > self.total_session_score:
            difference = self.umi_total_score - self.total_session_score
            print(f"🌟 Umi beat you by {difference:.0f} points!")
        else:
            print("🤝 It's a tie!")
        
        print(f"\n📊 Score Comparison:")
        print(f"   Your Average: {self.total_session_score / len(self.session_words):.0f}" if self.session_words else "   Your Average: 0.0")
        print(f"   Umi's Average: {self.umi_total_score / len(self.umi_chain):.0f}" if self.umi_chain else "   Umi's Average: 0.0")

async def main():
    """Main game loop."""
    # Suppress initialization output
    import os
    import sys
    from contextlib import redirect_stdout, redirect_stderr
    
    # Save original stdout/stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    # Redirect to null during initialization
    with open(os.devnull, 'w') as devnull:
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            game = ScoringGame()
        finally:
            # Restore original stdout/stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr
    
    game.print_instructions()
    
    # Start new session
    game.start_new_session()
    
    while True:
        result = await game.play_round()
        
        if result == "QUIT":
            print("\n👋 Thanks for playing!")
            break
        elif result == "NEW_SESSION":
            game.start_new_session()
        elif result == "SESSION_COMPLETE":
            print("\n🔄 Starting new session...")
            game.start_new_session()

if __name__ == "__main__":
    asyncio.run(main())
