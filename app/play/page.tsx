import React from "react";
import Navbar from "@/src/components/Navbar";
import { GameArea } from "@/src/components/GameArea";
import ScoreArea from "@/src/components/ScoreArea";

export default async function PlayPage() {
  return (
    <>
      <ScoreArea />
      <GameArea />
    </>
  );
}
