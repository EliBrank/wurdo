# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire ml_engine directory
COPY . .

# Create a simple test script to verify the setup
RUN echo '#!/usr/bin/env python3\n\
import sys\n\
import os\n\
sys.path.append("/app")\n\
\n\
try:\n\
    from models.production_onnx_scorer import get_onnx_scorer\n\
    from services.enhanced_scoring_service import get_enhanced_scoring_service\n\
    from models.probability_tree import WordProbabilityTree\n\
    print("✅ All core modules imported successfully!")\n\
    \n\
    # Test ONNX model loading\n\
    scorer = get_onnx_scorer()\n\
    print("✅ ONNX model loaded successfully!")\n\
    \n\
    # Test scoring service initialization\n\
    scoring_service = get_enhanced_scoring_service()\n\
    print("✅ Scoring service initialized successfully!")\n\
    \n\
    print("🎉 ML Engine is ready to use!")\n\
    \n\
except Exception as e:\n\
    print(f"❌ Error: {e}")\n\
    sys.exit(1)\n\
' > /app/test_setup.py

# Create an interactive scoring game script
RUN echo '#!/usr/bin/env python3\n\
import sys\n\
import os\n\
import asyncio\n\
sys.path.append("/app")\n\
\n\
async def run_scoring_game():\n\
    try:\n\
        from services.enhanced_scoring_service import get_enhanced_scoring_service\n\
        \n\
        print("🎮 Starting Wurdo Scoring Game...")\n\
        print("=" * 50)\n\
        \n\
        # Initialize the scoring service\n\
        scoring_service = get_enhanced_scoring_service()\n\
        print("✅ Scoring service ready!")\n\
        \n\
        print("\\n📝 Instructions:")\n\
        print("- Enter a start word (e.g., 'xylophone')")\n\
        print("- Enter a candidate word (e.g., 'telephone')")\n\
        print("- See the creativity score and breakdown")\n\
        print("- Type 'quit' to exit")\n\
        print("=" * 50)\n\
        \n\
        while True:\n\
            try:\n\
                start_word = input("\\n🎯 Start word: ").strip().lower()\n\
                if start_word == "quit":\n\
                    print("👋 Thanks for playing!")\n\
                    break\n\
                \n\
                if not start_word:\n\
                    print("❌ Please enter a valid word")\n\
                    continue\n\
                \n\
                candidate_word = input("🎯 Candidate word: ").strip().lower()\n\
                if candidate_word == "quit":\n\
                    print("👋 Thanks for playing!")\n\
                    break\n\
                \n\
                if not candidate_word:\n\
                    print("❌ Please enter a valid word")\n\
                    continue\n\
                \n\
                print("\\n🔄 Calculating score...")\n\
                \n\
                # Get comprehensive score\n\
                score_result = await scoring_service.score_candidate_comprehensive(start_word, candidate_word)\n\
                \n\
                print(f"\\n📊 Score Results:")\n\
                print(f"   Overall Score: {score_result.overall_score:.4f}")\n\
                print(f"   Ana Score: {score_result.ana_score:.4f}")\n\
                print(f"   Olo Score: {score_result.olo_score:.4f}")\n\
                print(f"   Rhy Score: {score_result.rhy_score:.4f}")\n\
                print(f"   Frq Score: {score_result.frq_score:.4f}")\n\
                print(f"   Prf Score: {score_result.prf_score:.4f}")\n\
                \n\
            except KeyboardInterrupt:\n\
                print("\\n👋 Thanks for playing!")\n\
                break\n\
            except Exception as e:\n\
                print(f"❌ Error: {e}")\n\
                \n\
    except Exception as e:\n\
        print(f"❌ Failed to start game: {e}")\n\
        sys.exit(1)\n\
\n\
if __name__ == "__main__":\n\
    asyncio.run(run_scoring_game())\n\
' > /app/scoring_game.py

# Make scripts executable
RUN chmod +x /app/test_setup.py /app/scoring_game.py

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command to test the setup
CMD ["python", "test_setup.py"] 