import Image from "next/image";
import LogoLight from "../assets/images/LogoLight.png";
import React from "react";

export default function Logo() {
  return (
    <div>
      <Image src={LogoLight} alt="wurdo" className="h-10 w-24"></Image>
    </div>
  );
}
