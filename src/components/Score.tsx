"use client";
import React, { use } from "react";
import { useGameContext } from "@/context";

export default function Score() {
  const { currentScore } = useGameContext();

  return (
    <div className="text-xl font-bold text-(--navy-main) flex flex-row items-baseline self-end relative top-1 mr-3">
      <span>{currentScore}</span>
      <span className="text-xs ml-2 text-(--navy-main)">PTS</span>
    </div>
  );
}
