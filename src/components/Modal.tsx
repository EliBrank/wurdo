"use client";

import React, { useEffect, useRef } from "react";
import { useGameContext } from "@/context";

export default function Modal() {
  const {
    gameOver,
    setGameOver,
    totalScore,
    setTurns,
    setTotalScore,
    setWordHistory,
  } = useGameContext();

  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    if (gameOver && dialogRef.current) {
      dialogRef.current.showModal();
    } else if (!gameOver && dialogRef.current) {
      dialogRef.current.close();
    }
  }, [gameOver]);

  const handleReload = () => {
    window.location.reload();
  };

  const handleClose = () => {
    setGameOver(false);
  };

  return (
    <dialog
      ref={dialogRef}
      className="p-8 rounded-lg shadow-xl backdrop-blur-xl bg-(--purple-main) text-white mx-auto self-center"
    >
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Game Over</h1>

        <p className="text-lg mb-2">You've completed all 10 turns!</p>

        <p className="text-xl font-semibold mb-6 text-(--navy-main)">
          Final Score: {totalScore}
        </p>

        <div className="flex gap-4 justify-center">
          <button
            onClick={handleReload}
            className="bg-(--green-main) hover:bg-(--green-dark) text-white px-6 py-2 rounded-lg"
          >
            New Game
          </button>

          <button
            onClick={handleClose}
            className="bg-(--navy-main) hover:bg-gray-900 text-white px-6 py-2 rounded-lg"
          >
            Close
          </button>
        </div>
      </div>
    </dialog>
  );
}
