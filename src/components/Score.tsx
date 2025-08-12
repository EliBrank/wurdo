import React from "react";

interface ScoreProps {
  score: number;
}

export default function Score({ score }: ScoreProps) {
  return (
    <div className="text-xl font-bold text-(--navy-main) flex flex-row items-baseline self-end relative top-1 mr-3">
      <span>{score}</span>
      <span className="text-xs ml-2 text-(--navy-main)">PTS</span>
    </div>
  );
}
