#!/usr/bin/env python3
import sys
import os
import asyncio
import time
import random
import json
import datetime
from typing import Optional
from pathlib import Path

sys.path.append("/app")

def print_title_card():
    """Print the retro-gaming style title card"""
    title_art = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    ██╗    ██╗██╗   ██╗██████╗ ██████╗  ██████╗                          ║
║    ██║    ██║██║   ██║██╔══██╗██╔══██╗██╔═══██╗                          ║
║    ██║ █╗ ██║██║   ██║██████╔╝██║  ██║██║   ██║                          ║
║    ██║███╗██║██║   ██║██╔══██╗██║  ██║██║   ██║                          ║
║    ╚███╔███╔╝╚██████╔╝██║  ██║██████╔╝╚██████╔╝                          ║
║     ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝                           ║
║                                                                              ║
║                    ✧ Transform • Anagram • Rhyme • One-Letter-Off ✧        ║
║                                                                              ║
║                         Slant rhymes = bonus points!                        ║
║                           Low stakes, high fun!                            ║
║                                                                              ║
║                              atlas_school 2005                              ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(title_art)

def print_loading_animation():
    """Print a retro loading animation"""
    loading_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    for i in range(20):
        char = loading_chars[i % len(loading_chars)]
        print(f"\r{char} Loading ML Engine... {i*5}%", end="", flush=True)
        time.sleep(0.1)
    print("\r✅ ML Engine Ready!    100%")

def print_score_display(start_word: str, candidate_word: str, score_result):
    """Print the score results in a retro style"""
    print("\n" + "═" * 60)
    print("📊 SCORE RESULTS")
    print("═" * 60)
    
    # Check if the result is successful
    if not score_result.get("success", False):
        print(f"❌ Error: {score_result.get('message', 'Unknown error')}")
        print("═" * 60)
        return False
    
    # Get data from the result
    data = score_result.get("data", {})
    
    # Create a visual score bar
    best_score = data.get("best_score", 0)
    creativity_score = data.get("creativity_score", 0)
    overall_percent = int(creativity_score * 100)
    bar_length = 40
    filled_length = int(bar_length * creativity_score)
    bar = "█" * filled_length + "░" * (bar_length - filled_length)
    
    print(f"🎯 {start_word.upper()} → {candidate_word.upper()}")
    print(f"🏆 Best Score: {best_score:.2f}")
    print(f"🎨 Creativity: {creativity_score:.4f} ({overall_percent}%)")
    print(f"   [{bar}]")
    print()
    
    # Show category breakdown
    all_scores = data.get("all_category_scores", {})
    if all_scores:
        print("📊 Category Breakdown:")
        for category, score in all_scores.items():
            percent = int((score / 1500.0) * 100)  # Normalize to percentage
            bar_length = 25
            filled_length = int(bar_length * (score / 1500.0))
            bar = "█" * filled_length + "░" * (bar_length - filled_length)
            print(f"   {category.upper():4} {score:6.1f} ({percent:3}%) [{bar}]")
    
    print("═" * 60)
    return True

def print_instructions():
    """Print game instructions in retro style"""
    instructions = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                              HOW TO PLAY                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🎯 Enter a START WORD (e.g., 'xylophone')                                 ║
║  🎯 Enter up to 5 CANDIDATE WORDS (e.g., 'telephone')                      ║
║  📊 See the creativity score breakdown for each                            ║
║  🔄 DYNAMIC GAMEPLAY: Your last valid word becomes the new start word!     ║
║  🚫 DUPLICATE PREVENTION: You cannot use the same word twice!              ║
║  🚪 Type 'quit' to exit, 'new' for a new word                             ║
║                                                                              ║
║  Categories:                                                                ║
║  🔤 Ana - Anagram transformations                                           ║
║  🔀 Olo - One-letter-off transformations                                   ║
║  🎵 Rhy - Rhyme transformations                                             ║
║  📊 Frq - Frequency-based scoring                                          ║
║  ⭐ Prf - Perfect rhyme bonus                                               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(instructions)

def get_input_with_prompt(prompt: str) -> Optional[str]:
    """Get user input with retro styling"""
    try:
        user_input = input(f"\n{prompt} ").strip().lower()
        if user_input == 'quit':
            return None
        return user_input
    except KeyboardInterrupt:
        return None

class ScoringGame:
    """Enhanced scoring game with 5-word sessions and dynamic gameplay."""
    
    def __init__(self):
        """Initialize the game."""
        self.scoring_service = None
        self.current_word = None
        self.candidates_entered = 0
        self.max_candidates = 5
        
        # Track used words to prevent duplicates
        self.used_words = set()
        self.initial_start_word = None
        
        # Data storage
        self.game_data_file = Path("scoring_game_results.json")
        self.session_data = {
            "sessions": [],
            "total_sessions": 0,
            "total_candidates": 0,
            "last_updated": datetime.datetime.now().isoformat()
        }
        self.current_session = {
            "session_id": None,
            "start_word": None,
            "candidates": [],
            "session_score": 0,
            "timestamp": None
        }
        
        # Load existing data
        self.load_game_data()
    
    def load_game_data(self):
        """Load existing game data."""
        if self.game_data_file.exists():
            try:
                with open(self.game_data_file, 'r') as f:
                    self.session_data = json.load(f)
                print(f"📊 Loaded {self.session_data['total_sessions']} previous sessions")
            except Exception as e:
                print(f"⚠️ Could not load existing data: {e}")
    
    def save_game_data(self):
        """Save game data to file."""
        try:
            self.session_data["last_updated"] = datetime.datetime.now().isoformat()
            with open(self.game_data_file, 'w') as f:
                json.dump(self.session_data, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving data: {e}")
    
    def start_new_session(self, reset_used_words=True):
        """Start a new game session."""
        session_id = f"session_{self.session_data['total_sessions'] + 1}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = {
            "session_id": session_id,
            "start_word": None,
            "candidates": [],
            "session_score": 0,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Only reset used words if we're starting completely fresh
        if reset_used_words:
            self.used_words = set()
            self.initial_start_word = None
        
        print(f"🎯 Starting session: {session_id}")
    
    def get_start_word(self, previous_valid_word=None):
        """Get a start word for the game."""
        if previous_valid_word:
            # Use the previous valid word as the new start word
            self.current_word = previous_valid_word
            # Add to used words and update session
            self.used_words.add(self.current_word)
            self.current_session["start_word"] = self.current_word
            print(f"\n🎯 New start word (from previous valid word): '{self.current_word}'")
            return
        
        # You can customize this list or make it random
        start_words = [
            "cat", "hat", "dog", "run", "play", "computer", 
            "algorithm", "beautiful", "mountain", "ocean"
        ]
        
        print("📝 Choose a start word:")
        for i, word in enumerate(start_words, 1):
            print(f"  {i}. {word}")
        print("  Or type your own word:")
        
        choice = input("Enter choice (1-10) or word: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(start_words):
            self.current_word = start_words[int(choice) - 1]
        else:
            self.current_word = choice if choice else "cat"  # Default to "cat" if empty
        
        # Track the initial start word and add it to used words
        self.initial_start_word = self.current_word
        self.used_words.add(self.current_word)
        
        self.current_session["start_word"] = self.current_word
        print(f"\n🎯 Start word: '{self.current_word}'")
        print("=" * 50)
    
    def display_transformation_hints(self):
        """Display hints for possible transformations."""
        print("💡 Possible transformation types:")
        print("  • Perfect rhymes (e.g., cat → hat)")
        print("  • Rich rhymes/homophones (e.g., cat → kat)")
        print("  • Slant rhymes (e.g., cat → bat)")
        print("  • Anagrams (e.g., cat → act)")
        print("  • One-letter-off (added/removed/changed)")
        print()
    
    async def score_candidate(self, candidate_word: str):
        """Score a candidate word and display results."""
        print(f"\n🔍 Scoring '{candidate_word}'...")
        
        # Check if word has already been used
        if candidate_word in self.used_words:
            print(f"❌ WORD ALREADY USED!")
            print(f"   '{candidate_word}' has already been played or was the initial start word.")
            print(f"   Try a different word!")
            print("-" * 50)
            return None
        
        # Get comprehensive scoring
        result = await self.scoring_service.score_candidate_comprehensive(self.current_word, candidate_word)
        
        candidate_data = {
            "word": candidate_word,
            "timestamp": datetime.datetime.now().isoformat(),
            "result": result
        }
        
        if result["success"]:
            data = result["data"]
            
            # Store candidate data
            candidate_data["score"] = data["best_score"]
            candidate_data["category"] = data["best_category"]
            candidate_data["creativity"] = data["creativity_score"]
            candidate_data["probability"] = data["full_probability"]
            
            # Update session score
            self.current_session["session_score"] += data["best_score"]
            
            # Add to used words
            self.used_words.add(candidate_word)
            
            # Update current_word to the valid word for the next play
            self.current_word = candidate_word
            self.current_session["start_word"] = self.current_word
            
            print(f"✅ VALID TRANSFORMATION!")
            print(f"   Word: '{candidate_word}'")
            print(f"   Category: {data['best_category'].upper()}")
            print(f"   Total Score: {data['best_score']:.1f}")
            print(f"   Creativity: {data['creativity_score']:.4f}")
            print(f"   Probability: {data['full_probability']:.8f}")
            print(f"   Base Score: {data['base_score']:.1f}")
            print(f"   Category Bonus: {data['category_bonus']:.1f}")
            
            # Show all category scores
            print(f"   All Categories:")
            for category, score in data['all_category_scores'].items():
                print(f"     {category.upper()}: {score:.1f}")
            
            # Show token analysis
            token_analysis = data['token_analysis']
            print(f"   Token Analysis:")
            print(f"     Tokens: {token_analysis['token_count']}")
            if 'prompt' in token_analysis:
                print(f"     Prompt: '{token_analysis['prompt']}'")
            if 'using_probability_tree' in token_analysis:
                print(f"     Method: {'Probability Tree' if token_analysis['using_probability_tree'] else 'ML Model'}")
            if 'tree_category' in token_analysis:
                print(f"     Tree Category: {token_analysis['tree_category']}")
            
            # Store candidate data
            self.current_session["candidates"].append(candidate_data)
            
            print("-" * 50)
            
            # Return the valid word for potential use as new start word
            return candidate_word
            
        else:
            print(f"❌ INVALID TRANSFORMATION")
            print(f"   Error: {result['message']}")
            candidate_data["error"] = result["message"]
            
            # Store candidate data even for invalid attempts
            self.current_session["candidates"].append(candidate_data)
            
            print("-" * 50)
            
            return None
    
    def end_session(self):
        """End the current session and save data."""
        if self.current_session["session_id"]:
            # Add session to data
            self.session_data["sessions"].append(self.current_session)
            self.session_data["total_sessions"] += 1
            self.session_data["total_candidates"] += len(self.current_session["candidates"])
            
            # Save data
            self.save_game_data()
            
            # Display session summary
            print(f"\n📊 SESSION SUMMARY:")
            print(f"   Session ID: {self.current_session['session_id']}")
            print(f"   Start Word: '{self.current_session['start_word']}'")
            print(f"   Candidates: {len(self.current_session['candidates'])}")
            print(f"   Total Score: {self.current_session['session_score']:.1f}")
            print(f"   Average Score: {self.current_session['session_score'] / len(self.current_session['candidates']):.1f}" if self.current_session['candidates'] else "   Average Score: 0.0")
    
    async def play_round(self, previous_valid_word=None):
        """Play one round of the game."""
        # Only reset used words if we're starting fresh (no previous valid word)
        reset_used_words = previous_valid_word is None
        self.start_new_session(reset_used_words=reset_used_words)
        self.get_start_word(previous_valid_word)
        self.display_transformation_hints()
        
        self.candidates_entered = 0
        last_valid_word = None
        
        while self.candidates_entered < self.max_candidates:
            remaining = self.max_candidates - self.candidates_entered
            print(f"\n📝 Enter candidate word ({remaining} remaining):")
            print("   (or type 'quit' to exit, 'new' for new word)")
            
            # Show used words if any
            if self.used_words:
                used_list = ", ".join(sorted(self.used_words))
                print(f"   Used words: {used_list}")
            
            candidate = input("> ").strip().lower()
            
            if candidate == "quit":
                self.end_session()
                return False
            elif candidate == "new":
                self.end_session()
                return "NEW_SESSION"  # Continue to next round with new word
            elif candidate == "":
                continue
            else:
                valid_word = await self.score_candidate(candidate)
                if valid_word:
                    last_valid_word = valid_word  # Track the last valid word
                self.candidates_entered += 1
        
        print(f"\n🎉 Round complete! You entered {self.candidates_entered} candidates.")
        self.end_session()
        
        # Return the last valid word for use as next start word
        return last_valid_word
    
    def display_statistics(self):
        """Display game statistics."""
        if self.session_data["total_sessions"] > 0:
            print(f"\n📈 GAME STATISTICS:")
            print(f"   Total Sessions: {self.session_data['total_sessions']}")
            print(f"   Total Candidates: {self.session_data['total_candidates']}")
            print(f"   Last Updated: {self.session_data['last_updated']}")
            
            # Calculate average scores
            total_score = sum(session["session_score"] for session in self.session_data["sessions"])
            avg_session_score = total_score / self.session_data["total_sessions"]
            print(f"   Average Session Score: {avg_session_score:.1f}")
    
    async def play(self):
        """Main game loop."""
        print("🎯 WELCOME TO THE SCORING GAME!")
        print("=" * 50)
        print("Rules:")
        print("• You'll be given a start word")
        print("• Enter up to 5 candidate transformation words")
        print("• See real-time scoring for each candidate")
        print("• Type 'quit' to exit, 'new' for a new word")
        print("• All scoring data will be saved automatically")
        print("• 🆕 DYNAMIC GAMEPLAY: Your last valid word becomes the new start word!")
        print("• 🚫 DUPLICATE PREVENTION: You cannot use the same word twice!")
        print()
        
        self.display_statistics()
        
        previous_valid_word = None
        
        while True:
            print("\n" + "=" * 50)
            last_valid_word = await self.play_round(previous_valid_word)
            
            if last_valid_word is False:  # User quit
                break
            
            if last_valid_word == "NEW_SESSION":
                # User requested new session, start fresh
                previous_valid_word = None
                print("\n🔄 Starting fresh with a new word.")
            elif last_valid_word:
                # Use the last valid word as the start word for the next round
                previous_valid_word = last_valid_word
                print(f"\n🔄 Using '{last_valid_word}' as the new start word for the next round!")
            else:
                # No valid words in this round, start fresh
                previous_valid_word = None
                print("\n🔄 No valid words entered. Starting fresh with a new word.")
            
            print("\n🎮 Starting new round...")
        
        print("\n👋 Thanks for playing the Scoring Game!")
        print(f"📁 Your data is saved in: {self.game_data_file}")

async def run_scoring_game():
    """Main game loop with retro styling"""
    try:
        # Clear screen and show title
        os.system('clear' if os.name == 'posix' else 'cls')
        print_title_card()
        
        # Show loading animation
        print_loading_animation()
        
        # Import and initialize scoring service
        from services.enhanced_scoring_service import get_enhanced_scoring_service
        scoring_service = get_enhanced_scoring_service()
        
        # Initialize game
        game = ScoringGame()
        game.scoring_service = scoring_service
        
        # Show instructions
        print_instructions()
        
        # Start the game
        await game.play()
        
        # Farewell message
        print("\n" + "═" * 60)
        print("🎉 Thanks for testing the ML Engine!")
        print("   WÜRDO - Where words become magic!")
        print("═" * 60)
        
    except Exception as e:
        print(f"❌ Failed to start game: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_scoring_game()) 