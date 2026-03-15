"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { IPadStatusBar } from "./iPadStatusBar";

interface IPadLockScreenProps {
  showNotification: boolean;
  onNotificationClick: () => void;
}

export function IPadLockScreen({
  showNotification,
  onNotificationClick,
}: IPadLockScreenProps) {
  const [currentDate] = useState(() => {
    const d = new Date();
    d.setHours(17, 45, 0, 0);
    return d;
  });

  return (
    <div
      className="w-full h-full flex flex-col relative"
      style={{
        background:
          "linear-gradient(160deg, #0a0a2e 0%, #1a103c 30%, #2d1b69 60%, #1a103c 100%)",
      }}
    >
      <IPadStatusBar time="5:45 PM" />

      {/* Lock icon */}
      <div className="flex justify-center mt-4">
        <svg
          className="w-5 h-5 text-white/40"
          viewBox="0 0 24 24"
          fill="currentColor"
        >
          <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zM9 8V6c0-1.66 1.34-3 3-3s3 1.34 3 3v2H9z" />
        </svg>
      </div>

      {/* Time & Date */}
      <div className="flex flex-col items-center mt-8">
        <div className="text-white text-[96px] md:text-[120px] font-extralight leading-none tracking-tight">
          5:45
        </div>
        <div className="text-white/60 text-xl md:text-2xl font-light mt-2">
          Tuesday, March 15
        </div>
      </div>

      {/* Notification */}
      <div className="flex-1 flex flex-col justify-end px-6 pb-16">
        <AnimatePresence>
          {showNotification && (
            <motion.button
              initial={{ y: 80, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: 80, opacity: 0 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              type="button"
              onClick={onNotificationClick}
              className="w-full rounded-2xl bg-white/15 backdrop-blur-2xl border border-white/10 p-4 text-left hover:bg-white/20 transition-colors active:scale-[0.98]"
            >
              <div className="flex items-start gap-3">
                {/* go! app icon */}
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#f59e0b] to-[#d97706] flex items-center justify-center flex-shrink-0">
                  <span className="text-white text-sm font-bold">go!</span>
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-white/90 text-sm font-semibold">
                      go!
                    </span>
                    <span className="text-white/40 text-xs">now</span>
                  </div>
                  <p className="text-white/90 text-sm font-medium mt-0.5">
                    5 events you&apos;d love in the next hour
                  </p>
                  <p className="text-white/60 text-xs mt-0.5 line-clamp-1">
                    Live jazz, street food market, comedy show and more near you
                  </p>
                </div>
              </div>
            </motion.button>
          )}
        </AnimatePresence>
      </div>

      {/* Home indicator hint */}
      <div className="absolute bottom-3 left-1/2 -translate-x-1/2">
        <div className="w-[134px] h-[5px] rounded-full bg-white/15" />
      </div>
    </div>
  );
}
