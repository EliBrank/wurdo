"use client";
import React from "react";
import { useGameContext } from "@/context";

export default function ScoreMeter() {
  const { wordScore, totalScore, setTotalScore, turns, setTurns } =
    useGameContext();
  if (wordScore === undefined) return null;
  if (totalScore === undefined) return null;

  const percentage = (turns / 10) * 100;

  return (
    <div className="w-full">
      <div className="w-full bg-(--navy-main) rounded h-3 flex items-center">
        <div
          className="bg-white h-1.5 transition-all ml-1 duration-800"
          style={{ width: `${Math.min(percentage)}%` }}
        ></div>
      </div>
      <div className="text-sm mt-1 text-center text-black"></div>
    </div>
  );
}
