"use client";
import React from "react";
import { useGameContext } from "@/context";

export default function ScoreMeter() {
  const { wordScore, totalScore, setTotalScore } = useGameContext();
  if (totalScore === undefined) return 0;
  if (wordScore === undefined) return 0;
  if (!setTotalScore) return;

  setTotalScore(Math.round(totalScore + wordScore));

  return (
    <div className="w-full">
      <div className="w-full bg-(--navy-main) rounded h-3 flex items-center">
        <div
          className="bg-white h-1.5 transition-all ml-1 duration-300"
          style={{ width: `${Math.min()}%` }}
        />
      </div>
      <div className="text-sm mt-1 text-center text-black"></div>
    </div>
  );
}
