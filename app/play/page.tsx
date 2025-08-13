import React from "react";
import Navbar from "@/src/components/Navbar";
import { GameArea } from "@/src/components/GameArea";
import ScoreArea from "@/src/components/ScoreArea";
import { getStatus } from "@/lib/gsActions";
import Modal from "@/src/components/Modal";

export default async function PlayPage() {
  return (
    <>
      <ScoreArea />
      <GameArea />
      <Modal />
    </>
  );
}
