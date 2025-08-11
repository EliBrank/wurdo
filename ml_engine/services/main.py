# main.py

from fastapi import FastAPI
from pydantic import BaseModel
# 1. Import the CORS middleware
from fastapi.middleware.cors import CORSMiddleware
from ml_engine.services.game_service import GameService

app = FastAPI()
game = GameService()


# 2. Configure the CORS middleware
origins = [
    "http://localhost:3000",  # Your Next.js app's URL
    # You can add other origins here if needed, e.g., your production domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

class WordInput(BaseModel):
    word: str

@app.get("/init")
def read_root():
   return game.initialized


@app.get("/start")
def startGame():
    return game.start_game().__dict__

@app.get("/end")
def startGame():

    return game.end_game().__dict__

@app.post("/play")
def play_word(word_input: WordInput):
    move = game.process_player_move()
    return {
        "received_word": word_input.word,
        "message": f"Your word '{word_input.word}' has been processed.",
        "game" :f"{move}"
    }


