import React from "react";
import Score from "./Score";
import ScoreMeter from "./ScoreMeter";
import Logo from "./Logo";
import Link from "next/link";

export default async function ScoreArea() {
  return (
    <div className="absolute left-4 right-4 flex flex-col items-center z-10">
      <div className="flex flex-row justify-between w-full mb-2 items-end">
        <div className="flex flex-col">
          <Link href="/" className="self-start">
            <div className="text-xl font-bold text-(--navy-main) mb-2">
              &lt;-
            </div>
          </Link>
          <Logo />
        </div>
        <Score />
      </div>

      <ScoreMeter />
    </div>
  );
}
