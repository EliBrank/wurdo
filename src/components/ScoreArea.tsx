import React from "react";
import Score from "./Score";
import ScoreMeter from "./ScoreMeter";
import Logo from "./Logo";
import Link from "next/link";

interface ScoreAreaProps {
  currentScore: number;
  maxScore: number;
}

export default function ScoreArea({ currentScore, maxScore }: ScoreAreaProps) {
  return (
    <div className="absolute left-4 right-4 flex flex-col items-center z-10">
      <div className="flex flex-row justify-between w-[90%] mb-2 items-end">
        <div className="flex flex-col">
          <Link href="/" className="self-start">
            <div className="text-xl font-bold text-(--navy-main) mb-2">
              &lt;-
            </div>
          </Link>
          <Logo />
        </div>
        <Score score={currentScore} />
      </div>

      <ScoreMeter currentScore={currentScore} maxScore={maxScore} />
    </div>
  );
}
