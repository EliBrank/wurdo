#!/usr/bin/env python3
import sys
import os
import asyncio
import time
import random
from typing import Optional

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
        return
    
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

def print_instructions():
    """Print game instructions in retro style"""
    instructions = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                              HOW TO PLAY                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🎯 Enter a START WORD (e.g., 'xylophone')                                 ║
║  🎯 Enter a CANDIDATE WORD (e.g., 'telephone')                             ║
║  📊 See the creativity score breakdown                                      ║
║  🚪 Type 'quit' to exit                                                     ║
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
        
        # Show instructions
        print_instructions()
        
        # Game loop
        while True:
            try:
                # Get start word
                start_word = get_input_with_prompt("🎯 START WORD")
                if start_word is None:
                    break
                
                if not start_word:
                    print("❌ Please enter a valid word")
                    continue
                
                # Get candidate word
                candidate_word = get_input_with_prompt("🎯 CANDIDATE WORD")
                if candidate_word is None:
                    break
                
                if not candidate_word:
                    print("❌ Please enter a valid word")
                    continue
                
                # Show calculating animation
                print("\n🔄 Calculating creativity score...")
                for i in range(3):
                    print(f"\r{'⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'[i*2:(i*2)+2]} Processing...", end="", flush=True)
                    time.sleep(0.3)
                
                # Get comprehensive score
                score_result = await scoring_service.score_candidate_comprehensive(start_word, candidate_word)
                
                # Display results
                print_score_display(start_word, candidate_word, score_result)
                
                # Ask if they want to continue
                print("\n🎮 Press Enter to continue or type 'quit' to exit...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Thanks for playing WÜRDO!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("🔄 Please try again...")
        
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