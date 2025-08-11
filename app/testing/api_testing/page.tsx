"use client";

import { useState } from "react";

export default function Page() {
  const [word, setWord] = useState<string | undefined>("");
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setWord(e.target.value);
  };

  async function submitWord(word: any) {
    const response = await fetch("http://localhost:8000/play", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ word: word }),
    });

    if (!response.ok) {
      // Handle error
      throw new Error("API request failed");
    }

    const data = await response.json();
    console.log(data); // { "received_word": "yourword", "message": "Your word 'yourword' has been processed." }
    return data;
  }
  async function Initlize() {
    const response = await fetch("http://localhost:8000/init", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      // Handle error
      throw new Error("API request failed");
    }

    const data = await response.json();
    if (data.status === "initalized") {
      console.log("game initlaized");
    }
    return data;
  }
  async function startGame() {
    const response = await fetch("http://localhost:8000/start", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      // Handle error
      throw new Error("API request failed");
    }

    const data = await response.json();
    return data;
  }
  async function endGame() {
    const response = await fetch("http://localhost:8000/end", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      // Handle error
      throw new Error("API request failed");
    }

    const data = await response.json();
    return data;
  }
  return (
    <>
      <div>
        <label className="block text-sm font-medium text-gray-700">
          Word to test
        </label>
        <input
          name="Test"
          type="text"
          className="border p-2 rounded-md w-full mt-1"
          placeholder="Enter word to test"
          value={word}
          onChange={handleInputChange}
        />
        <button onClick={() => submitWord(word)}>Play Word</button>
      </div>
      <div className="flex flex-col align-bottom">
        <button onClick={() => Initlize()}>Initlize</button>
        <button onClick={() => startGame()}>startGame</button>
        <button onClick={() => endGame()}>end game</button>
      </div>
    </>
  );
}
