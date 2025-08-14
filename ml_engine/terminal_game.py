#!/usr/bin/env python3
"""
Terminal Game Interface for Wurdo Game

This script provides an interactive terminal interface to test the GameService
functionality with real gameplay. It allows you to:
- Choose a start word
- Play 7 rounds interactively
- See all game responses and state
- End the game and see final results
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services.game_service import get_game_service, GameServiceError

class TerminalGame:
    """Terminal interface for Wurdo game"""
    
    def __init__(self):
        self.game_service = None
        self.current_round = 0
        self.max_rounds = 7
        
    async def initialize(self):
        """Initialize the game service"""
        try:
            self.game_service = await get_game_service()
            print("✅ Game service initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize game service: {e}")
            return False
    def print_title_art(self):
        """Print the beautiful retro title screen."""
        title_art = """
        ╔══════════════════════════════════════════════════════════════════════════════╗
        ║    ✧            ✧       ✧             ✧            ✧              ✧          ║
        ║        ██╗✧ ✧ ██╗ ██╗ ██╗ ██████╗ ██████╗   ██╗ ✧    ✧ ██╗    ✧           ✧  ║
        ║ ✧   ✧  ██║    ██║ ╚═╝ ╚═╝ ██╔══██╗ ██╔══██╗ █╔╝  ████╗ ╚█║        ✧     ✧    ║
        ║        ██║ █╗ ██║██╗   ██╗██████╔╝ ██║  ██║ █║ ██╔══██╗ █║             ✧   ✧ ║
        ║        ██║███╗██║██╗   ██║██╔══██╗ ██║  ██║ █║ ██║  ██║ █║       ✧      ✧    ║
        ║        ╚███╔███╔╝╚██████╔╝██║  ██║ ██████╔╝ ██╗╚████╔═╝██║ ✧  ✧              ║
        ║  ✧   ✧ ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ╚═╝ ╚═══╝  ╚═╝         ✧ ✧        ║
        ║   ✧             ✧                        ✧                  ✧        ✧   ✧   ║
        ║          ✧     ✧   ✧ Anagram - Rhyme - One-Letter-Off ✧          ✧      ✧    ║
        ║           ✧                     ✧                 ✧                ✧         ║
        ║       ✧          ✧                          ✧                  ✧             ║
        ║                  First word supplied - where will you go?   ✧            ✧   ║
        ║                                               ✧        ✧          ✧     ✧    ║
        ║           ✧                    ✧                              ✧      ✧       ║
        ║                              atlas_school 2025      ✧           ✧            ║
        ║                                                             ✧          ✧     ║
        ╚══════════════════════════════════════════════════════════════════════════════╝"""
        print(title_art)
    
    def print_game_status(self):
        """Print current game status"""
        if not self.game_service.game_state:
            print("📊 Game Status: No active game")
            return
            
        state = self.game_service.game_state
        print(f"\n📊 Game Status:")
        print(f"   Current Word: {state.get('current_word', 'None')}")
        print(f"   Round: {state.get('rounds_played', 0)}/{self.max_rounds}")
        print(f"   Player Score: {state.get('player_score', 0)}")
        print(f"   Umi Score: {state.get('umi_score', 0)}")
        if 'player_chain' in state and state['player_chain']:
            print(f"   Player Chain: {' → '.join(state['player_chain'])}")
        if 'umi_chain' in state and state['umi_chain']:
            print(f"   Umi Chain: {' → '.join(state['umi_chain'])}")
        if 'word_chain' in state and state['word_chain']:
            print(f"   Word Chain: {' → '.join(state['word_chain'])}")
    
    def print_round_header(self):
        """Print round header"""
        print(f"\n{'='*50}")
        print(f"🎯 ROUND {self.current_round + 1} of {self.max_rounds}")
        print(f"{'='*50}")
        
        # Show the current word the player should transform from
        if self.game_service.game_state:
            current_word = self.game_service.game_state.get('current_word', 'Unknown')
            print(f"🎯 Transform the word: '{current_word.upper()}'")
            print(f"💡 Enter a valid transformation (anagram, rhyme, one-letter-off, etc.)")
    
    async def start_game(self):
        """Start a new game"""
        print("\n🎯 Starting New Game")
        print("=" * 30)
        
        # Get start word from user
        while True:
            start_word = input("Enter a start word (or 'quit' to exit): ").strip().lower()
            if start_word == 'quit':
                return False
            if not start_word:
                print("❌ Please enter a valid word")
                continue
            break
        
        try:
            print(f"\n🚀 Starting game with word: '{start_word}'")
            result = await self.game_service.start_game(start_word)
            
            print(f"✅ Game started: {result['status']}")
            if 'message' in result:
                print(f"📝 {result['message']}")
            
            # Display available suggestions
            if 'player_suggestions' in result and result['player_suggestions']:
                print(f"\n💡 Available Play Types and Suggestions:")
                suggestions = result['player_suggestions']
                for play_type, suggestion in suggestions.items():
                    if suggestion:
                        word = suggestion.get('word', 'N/A')
                        rank = suggestion.get('frequency_rank', 'N/A')
                        print(f"   {play_type.upper()}: {word} (rank: {rank})")
            else:
                print("⚠️  No suggestions available")
            
            self.current_round = 0
            self.print_game_status()
            return True
            
        except GameServiceError as e:
            print(f"❌ Failed to start game: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    async def play_round(self):
        """Play one round of the game"""
        if self.current_round >= self.max_rounds:
            print("🎉 Game completed! No more rounds to play.")
            return False
        
        self.print_round_header()
        
        # Get player's word
        while True:
            player_word = input(f"Enter your word (or 'quit' to exit): ").strip().lower()
            if player_word == 'quit':
                return False
            if not player_word:
                print("❌ Please enter a valid word")
                continue
            break
        
        try:
            print(f"\n🎮 Processing your move: '{player_word}'")
            result = await self.game_service.process_player_move(player_word)
            
            print(f"✅ Move processed: {result['status']}")
            
            # Handle different move statuses
            if result['status'] == 'duplicate_word':
                print(f"❌ {result['error']}")
                print("💡 Try a different word that hasn't been played yet")
                return True  # Don't increment round for invalid moves
            elif result['status'] == 'invalid_word':
                print(f"❌ {result['error']}")
                print("💡 Make sure your word is a valid transformation of the current word")
                return True  # Don't increment round for invalid moves
            elif result['status'] == 'move_processed':
                print("✅ Move processed successfully!")
            else:
                print(f"ℹ️  Status: {result['status']}")
            
            # Display detailed results - handle the actual response structure
            if 'player_result' in result and result['player_result']:
                player_result = result['player_result']
                if player_result.get('success') and player_result.get('data'):
                    data = player_result['data']
                    print(f"\n🎯 Your Result:")
                    print(f"   Word: {data.get('candidate_word', 'N/A')}")
                    print(f"   Score: {data.get('total_score', 0):.2f}")
                    print(f"   Categories: {', '.join(data.get('valid_categories', []))}")
                    print(f"   Category Count: {data.get('category_count', 0)}")
                    if 'category_scores' in data:
                        print(f"   Category Scores:")
                        for cat, score in data['category_scores'].items():
                            print(f"     {cat.upper()}: {score:.2f}")
                else:
                    print(f"\n🎯 Your Result: {player_result.get('message', 'N/A')}")
            
            if 'umi_result' in result and result['umi_result']:
                umi_result = result['umi_result']
                if umi_result.get('success') and umi_result.get('data'):
                    data = umi_result['data']
                    print(f"\n🤖 Umi's Response:")
                    print(f"   Word: {data.get('candidate_word', 'N/A')}")
                    print(f"   Score: {data.get('total_score', 0):.2f}")
                    print(f"   Categories: {', '.join(data.get('valid_categories', []))}")
                    print(f"   Category Count: {data.get('category_count', 0)}")
                    if 'category_scores' in data:
                        print(f"   Category Scores:")
                        for cat, score in data['category_scores'].items():
                            print(f"     {cat.upper()}: {score:.2f}")
                else:
                    print(f"\n🤖 Umi's Response: {umi_result.get('message', 'N/A')}")
            
            if 'game_state' in result:
                print(f"\n📈 Game State Updated:")
                state = result['game_state']
                print(f"   Current Word: {state.get('current_word', 'N/A')}")
                print(f"   Round: {state.get('rounds_played', 0)}")
                print(f"   Player Score: {state.get('player_score', 0)}")
                print(f"   Umi Score: {state.get('umi_score', 0)}")
                if 'player_chain' in state:
                    print(f"   Player Chain: {' → '.join(state['player_chain'])}")
                if 'umi_chain' in state:
                    print(f"   Umi Chain: {' → '.join(state['umi_chain'])}")
            
            # Display updated suggestions
            if 'player_suggestions' in result and result['player_suggestions']:
                print(f"\n💡 Updated Suggestions for Next Move:")
                suggestions = result['player_suggestions']
                for play_type, suggestion in suggestions.items():
                    if suggestion:
                        word = suggestion.get('word', 'N/A')
                        rank = suggestion.get('frequency_rank', 'N/A')
                        print(f"   {play_type.upper()}: {word} (rank: {rank})")
            else:
                print("⚠️  No updated suggestions available")
            
            self.current_round += 1
            return True
            
        except GameServiceError as e:
            print(f"❌ Move failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    async def end_game(self):
        """End the current game"""
        print(f"\n🏁 Ending Game (Round {self.current_round}/{self.max_rounds})")
        print("=" * 40)
        
        try:
            result = await self.game_service.end_game()
            
            print(f"✅ Game ended: {result['status']}")
            
            # Display final results
            if 'player_summary' in result:
                player_summary = result['player_summary']
                print(f"\n🎯 Final Player Summary:")
                print(f"   Total Score: {player_summary.get('total_score', 0)}")
                print(f"   Words Played: {len(player_summary.get('words', []))}")
                print(f"   Average Score: {player_summary.get('avg_score', 0):.2f}")
            
            if 'umi_summary' in result:
                umi_summary = result['umi_summary']
                print(f"\n🤖 Final Umi Summary:")
                print(f"   Total Score: {umi_summary.get('total_score', 0)}")
                print(f"   Words Played: {len(umi_summary.get('words', []))}")
                print(f"   Average Score: {umi_summary.get('avg_score', 0):.2f}")
            
            if 'final_stats' in result:
                final_stats = result['final_stats']
                print(f"\n📊 Final Game Statistics:")
                print(f"   Total Rounds: {final_stats.get('total_rounds', 0)}")
                print(f"   Final Word: {final_stats.get('final_state', {}).get('current_word', 'N/A')}")
                print(f"   Player Chain Length: {final_stats.get('player_chain_length', 0)}")
                print(f"   Umi Chain Length: {final_stats.get('umi_chain_length', 0)}")
                print(f"   Game Duration: {final_stats.get('game_duration', 'N/A'):.1f}s")
            
            if 'redis_update' in result:
                redis_update = result['redis_update']
                print(f"\n🗄️  Redis Update Results:")
                print(f"   New Words Added: {redis_update.get('successful_adds', 0)}")
                print(f"   Total Words Processed: {redis_update.get('total_words', 0)}")
            
            return True
            
        except GameServiceError as e:
            print(f"❌ Failed to end game: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    async def run_game(self):
        """Run the complete game loop"""
        # Initialize game service first (this will show technical logs)
        print("🎮 Initializing Wurdo Game...")
        if not await self.initialize():
            return
        
        # Print the beautiful title art after initialization is complete
        self.print_title_art()
        
        # Now show welcome message after the title art
        print("\n🎮 Welcome to Wurdo Terminal Game!")
        print("=" * 40)
        print("This interface will test the actual GameService functionality")
        print("You'll play 7 rounds against Umi, the AI opponent")
        print("Type 'quit' at any time to exit")
        print("=" * 40)
        
        # Start game
        if not await self.start_game():
            return
        
        # Play rounds
        while self.current_round < self.max_rounds:
            if not await self.play_round():
                break
        
        # End game
        if self.current_round >= self.max_rounds:
            await self.end_game()
        
        print("\n🎉 Game session completed!")
        print("Thanks for testing Wurdo!")

async def main():
    """Main entry point"""
    game = TerminalGame()
    await game.run_game()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Game interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
