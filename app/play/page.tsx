import React from "react";
import Navbar from "@/src/components/Navbar";
import { GameArea } from "@/src/components/GameArea";
import ScoreArea from "@/src/components/ScoreArea";
import { getStatus } from "@/lib/gsActions";
// import Link from "next/link";

export default async function PlayPage() {
  let status = await getStatus();
  console.log(status);

  return (
    <>
      <ScoreArea />
      <GameArea />
    </>
  );
}
