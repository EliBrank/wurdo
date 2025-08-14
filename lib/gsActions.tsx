// api/gameApi.js

// Get ML engine URL from environment, fallback to localhost for development
const ML_ENGINE_URL = process.env.NEXT_PUBLIC_ML_ENGINE_URL || 'http://localhost:8000';

export async function getStatus() {
  try {
    const response = await fetch(`${ML_ENGINE_URL}/status`);

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const statusData = await response.json();
    return statusData;
  } catch (error) {
    console.error("Failed to fetch game status:", error);
    throw error;
  }
}

export async function startGame(startWord: string) {
  try {
    const response = await fetch(`${ML_ENGINE_URL}/start`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ start_word: startWord }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(
        errorData.detail || `HTTP error! Status: ${response.status}`
      );
    }
    return await response.json();
  } catch (error) {
    console.error("Failed to start game:", error);
    throw error;
  }
}

export async function playGame(candidateWord: string) {
  try {
    const response = await fetch(`${ML_ENGINE_URL}/play`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ candidate_word: candidateWord }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(
        errorData.detail || `HTTP error! Status: ${response.status}`
      );
    }
    return await response.json();
  } catch (error) {
    console.error("Failed to start game:", error);
    throw error;
  }
}

export async function endGame() {
  try {
    const response = await fetch(`${ML_ENGINE_URL}/end`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(
        errorData.detail || `HTTP error! Status: ${response.status}`
      );
    }
    return await response.json();
  } catch (error) {
    console.error("Failed to end game:", error);
    throw error;
  }
}
