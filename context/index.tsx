"use client";

import { createContext, SetStateAction, useContext, useState } from "react";

interface GameContext {
  currentScore?: number;
  setCurrentScore?: React.Dispatch<SetStateAction<number>>;
  wordHistory?: string[];
  setWordHistory?: React.Dispatch<SetStateAction<string[]>>;
  totalScore?: number;
  setTotalScore?: React.Dispatch<SetStateAction<number>>;
  gameOver?: boolean;
  setGameOver?: React.Dispatch<SetStateAction<boolean>>;
  turns?: number;
  setTurns?: React.Dispatch<SetStateAction<number>>;
  wordScore?: number;
  setWordScore?: React.Dispatch<SetStateAction<number>>;
  startWord?: string;
  setStartWord?: React.Dispatch<SetStateAction<string>>;
}

export const GameContext = createContext<GameContext>({});

export function GameContextWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  const [wordScore, setWordScore] = useState(0);
  const [totalScore, setTotalScore] = useState(0);
  const [startWord, setStartWord] = useState("hello");
  const [wordHistory, setWordHistory] = useState([startWord]);
  const [gameOver, setGameOver] = useState(false);
  const [turns, setTurns] = useState(10);

  return (
    <GameContext.Provider
      value={{
        wordHistory,
        setWordHistory,
        wordScore,
        setWordScore,
        totalScore,
        setTotalScore,
        startWord,
        setStartWord,
        gameOver,
        setGameOver,
        turns,
        setTurns,
      }}
    >
      {children}
    </GameContext.Provider>
  );
}

export function useGameContext() {
  return useContext(GameContext);
}
