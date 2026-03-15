"use client";

import { ReactNode } from "react";

interface PhoneFrameProps {
  children: ReactNode;
  className?: string;
}

export function PhoneFrame({ children, className = "" }: PhoneFrameProps) {
  return (
    <>
      {/* Desktop: phone frame with bezel */}
      <div
        className={`hidden md:flex flex-col items-center justify-center min-h-screen p-8 ${className}`}
      >
        <div className="relative">
          {/* Phone bezel - iPhone 14 Pro proportions */}
          <div
            className="relative w-[375px] max-w-[90vw] overflow-hidden rounded-[47px] border-[12px] border-black shadow-2xl"
            style={{
            boxShadow:
              "0 0 0 3px #1a1a1a, 0 25px 50px -12px rgba(0,0,0,0.5)",
            }}
          >
            {/* Screen content area - safe area for notch and home indicator */}
            <div className="relative w-full bg-bg-phone overflow-hidden">
              {/* Safe area top (notch) */}
              <div className="h-[54px]" />
              {/* Content */}
              <div className="min-h-[calc(812px-54px-34px)] max-h-[calc(80vh-88px)] overflow-y-auto">
                {children}
              </div>
              {/* Home indicator bar */}
              <div className="h-[34px] flex items-center justify-center">
                <div className="w-[134px] h-[5px] rounded-full bg-white/30" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile: no frame, full screen */}
      <div className="md:hidden min-h-screen bg-bg-phone">
        <div className="safe-area-inset min-h-screen overflow-y-auto">
          {children}
        </div>
      </div>
    </>
  );
}
