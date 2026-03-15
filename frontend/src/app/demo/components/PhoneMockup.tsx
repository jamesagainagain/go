"use client";

import { ReactNode } from "react";

interface PhoneMockupProps {
  children: ReactNode;
}

export function PhoneMockup({ children }: PhoneMockupProps) {
  return (
    <div className="glow-box relative h-[780px] w-[380px] shrink-0 rounded-[2.5rem] border-[14px] border-gray-800">
      {/* Volume buttons */}
      <div className="absolute -left-[17px] top-[72px] h-[32px] w-[3px] rounded-l-lg bg-gray-800" />
      <div className="absolute -left-[17px] top-[124px] h-[46px] w-[3px] rounded-l-lg bg-gray-800" />
      <div className="absolute -left-[17px] top-[178px] h-[46px] w-[3px] rounded-l-lg bg-gray-800" />
      {/* Power button */}
      <div className="absolute -right-[17px] top-[142px] h-[64px] w-[3px] rounded-r-lg bg-gray-800" />
      {/* Dynamic Island */}
      <div className="absolute left-1/2 top-0 z-10 h-[28px] w-[120px] -translate-x-1/2 rounded-b-[1rem] bg-gray-800" />
      {/* Screen */}
      <div className="relative z-[1] h-full w-full overflow-hidden rounded-[2rem] bg-white">
        {children}
      </div>
    </div>
  );
}
