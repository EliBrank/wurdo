"use client";
import React from "react";
import { useGameContext } from "@/context";

export default function ScoreMeter() {
  const { turns } = useGameContext();
  if (turns === undefined) return null;

  const percentage = (turns / 10) * 100;

  return (
    <div className="w-full">
      <div className="w-full bg-(--navy-main) rounded h-3 flex items-center">
        <div
          className="bg-white h-1.5 transition-all mx-1 duration-800"
          style={{ width: `${Math.min(percentage, 100)}%` }}
        ></div>
      </div>
      <div className="text-sm mt-1 text-center text-black"></div>
    </div>
  );
}
