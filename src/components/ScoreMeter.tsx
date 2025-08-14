"use client";
import React from "react";
import { useGameContext } from "@/context";

export default function ScoreMeter() {
  const { wordScore, totalScore, setTotalScore, turns, setTurns } =
    useGameContext();
  if (wordScore === undefined) return null;
  if (totalScore === undefined) return null;
  if (!turns) return 10;

  const percentage = (turns / 10) * 100;

  return (
    <div className="flex flex-col items-center space-y-2">
      <div className="text-sm text-gray-600">Turns Remaining</div>
      <div className="w-32 h-4 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="bg-white h-1.5 transition-all mx-1 duration-800"
          style={{ width: `${Math.min(percentage)}%` }}
        ></div>
      </div>
    </div>
  );
}
