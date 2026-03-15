"use client";

import { ReactNode } from "react";

interface IPadFrameProps {
  children: ReactNode;
  screenOn?: boolean;
  className?: string;
}

export function IPadFrame({ children, screenOn = true, className = "" }: IPadFrameProps) {
  return (
    <div className={`flex items-center justify-center min-h-screen p-4 md:p-8 ${className}`}>
      <div className="relative">
        {/* iPad bezel */}
        <div
          className="relative overflow-hidden rounded-[28px] border-[10px] border-[#1a1a1f] shadow-2xl"
          style={{
            width: "min(820px, calc(100vw - 32px))",
            aspectRatio: "820 / 1130",
            boxShadow:
              "0 0 0 2px #2a2a2f, 0 25px 60px -12px rgba(0,0,0,0.6)",
          }}
        >
          {/* Front camera */}
          <div className="absolute top-3 left-1/2 -translate-x-1/2 w-[8px] h-[8px] rounded-full bg-[#1a1a20] border border-[#2a2a30] z-50" />

          {/* Screen */}
          <div className="relative w-full h-full bg-black overflow-hidden">
            {screenOn ? (
              children
            ) : (
              <div className="w-full h-full bg-[#0a0a0a]" />
            )}
          </div>

          {/* Home indicator bar */}
          <div className="absolute bottom-2 left-1/2 -translate-x-1/2 w-[134px] h-[5px] rounded-full bg-white/20 z-50" />
        </div>
      </div>
    </div>
  );
}
