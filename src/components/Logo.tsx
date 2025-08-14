import Image from "next/image";
import WurdoLogo from "../assets/images/logo.png";
import React from "react";

export default function Logo() {
  return (
    <div>
      <Image src={WurdoLogo} alt="wurdo" className="h-8 w-19 p-0"></Image>
    </div>
  );
}
