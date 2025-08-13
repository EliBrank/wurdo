from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from services.game_service import get_game_service, GameService
from contextlib import asynccontextmanager

# This global variable will hold our single, initialized game service instance.
game_service: GameService = None

# --- Lifespan and Startup Logic ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the application.
    """
    global game_service
    print("Application startup initiated.")
    
    # Initialize the game service here.
    game_service = await get_game_service()
    
    print("Application is ready to serve requests.")
    
    yield  # The application is now running.
    
    # --- SHUTDOWN LOGIC ---
    print("Application shutdown initiated.")
    # No game logic here, just resource cleanup if needed.
    print("Application shutdown completed.")
    

# Create the FastAPI instance and attach the lifespan event
app = FastAPI(lifespan=lifespan)

# --- CORS Middleware ---

origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for API Data ---

class StartGameInput(BaseModel):
    start_word: str

class PlayerMoveInput(BaseModel):
    candidate_word: str

# --- API Endpoints ---

@app.get("/status")
async def get_game_status_endpoint():
    if not game_service:
        raise HTTPException(status_code=503, detail="Game service is not initialized.")
    return await game_service.get_game_status()

@app.post("/start")
async def start_new_game_endpoint(data: StartGameInput):
    try:
        # We now use the correct variable: game_service
        await game_service.reset_game()
        return await game_service.start_game(data.start_word)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/play")
async def play_player_move_endpoint(data: PlayerMoveInput):
    try:
        # We now use the correct variable: game_service
        return await game_service.process_player_move(data.candidate_word)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/end")
async def end_current_game_endpoint():
    try:
        # We now use the correct variable: game_service
        await game_service.end_game()
        return await game_service.reset_game()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/reset")
async def reset_game_endpoint():
    """
    Optional endpoint to manually reset the game state.
    """
    if not game_service:
        raise HTTPException(status_code=503, detail="Game service is not initialized.")
    try:
        return await game_service.reset_game()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))