# main.py

from fastapi import FastAPI
from pydantic import BaseModel
# 1. Import the CORS middleware
from fastapi.middleware.cors import CORSMiddleware
from ml_engine.services import

app = FastAPI()

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

@app.get("/")
def read_root():
    return {"message": "Welcome to the game engine API!"}

@app.post("/play")
def play_word(word_input: WordInput):

    return {
        "received_word": word_input.word,
        "message": f"Your word '{word_input.word}' has been processed."
    }


