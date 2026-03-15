"use client";

import { useEffect, useState } from "react";

interface PhoneLockScreenProps {
  onNotificationClick: () => void;
}

export function PhoneLockScreen({ onNotificationClick }: PhoneLockScreenProps) {
  const [showNotification, setShowNotification] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setShowNotification(true), 900);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div
      className="flex h-full w-full flex-col"
      style={{
        background:
          "linear-gradient(160deg, #0a0a2e 0%, #1a103c 30%, #2d1b69 60%, #1a103c 100%)",
      }}
    >
      {/* Status bar */}
      <div className="flex items-center justify-between px-6 pt-10 text-[10px] text-white/50">
        <span>5:45 PM</span>
        <div className="flex items-center gap-1">
          <span>5G</span>
          <svg className="h-3 w-3" viewBox="0 0 24 24" fill="currentColor">
            <path d="M15.67 4H14V2h-4v2H8.33C7.6 4 7 4.6 7 5.33v15.34C7 21.4 7.6 22 8.33 22h7.34c.73 0 1.33-.6 1.33-1.33V5.33C17 4.6 16.4 4 15.67 4z" />
          </svg>
        </div>
      </div>

      {/* Lock icon */}
      <div className="mt-3 flex justify-center">
        <svg
          className="h-4 w-4 text-white/40"
          viewBox="0 0 24 24"
          fill="currentColor"
        >
          <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zM9 8V6c0-1.66 1.34-3 3-3s3 1.34 3 3v2H9z" />
        </svg>
      </div>

      {/* Time & Date */}
      <div className="mt-6 flex flex-col items-center">
        <div className="text-6xl font-extralight leading-none tracking-tight text-white">
          5:45
        </div>
        <div className="mt-1.5 text-sm font-light text-white/60">
          Tuesday, March 15
        </div>
      </div>

      {/* Notification area */}
      <div className="flex flex-1 flex-col justify-end px-4 pb-12">
        {showNotification && (
          <button
            type="button"
            onClick={onNotificationClick}
            className="w-full animate-[slideUp_0.4s_ease-out] rounded-2xl border border-white/10 bg-white/15 p-3.5 text-left backdrop-blur-2xl transition-colors hover:bg-white/20 active:scale-[0.98]"
          >
            <div className="flex items-start gap-3">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-[#626262] to-[#94a3b8]">
                <span className="text-xs font-bold text-white">go!</span>
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold text-white/90">
                    go!
                  </span>
                  <span className="text-[10px] text-white/40">now</span>
                </div>
                <p className="mt-0.5 text-xs font-medium text-white/90">
                  5 events you&apos;d love in the next hour
                </p>
                <p className="mt-0.5 text-[10px] leading-tight text-white/60">
                  Live jazz, street food market, comedy show and more near you
                </p>
              </div>
            </div>
          </button>
        )}
      </div>

      {/* Home indicator */}
      <div className="flex justify-center pb-2">
        <div className="h-[4px] w-[100px] rounded-full bg-white/15" />
      </div>
    </div>
  );
}
