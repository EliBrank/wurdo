import Image from "next/image";
import BeigeBG from "../assets/images/BeigeBG.png";
import React from "react";

export default function Logo() {
  return (
    <div>
      <Image src={BeigeBG} alt="wurdo" className="h-8 w-19 p-0"></Image>
    </div>
  );
}
