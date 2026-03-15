"use client";

import { useEffect, useState } from "react";

export function PhoneStatusBar() {
  const [time, setTime] = useState("3:00");
  const [period, setPeriod] = useState("AM");

  useEffect(() => {
    // For demo: fixed at 3:00 AM. Optionally use real time:
    // const interval = setInterval(() => {
    //   const now = new Date();
    //   const h = now.getHours();
    //   const m = now.getMinutes();
    //   setTime(`${h % 12 || 12}:${m.toString().padStart(2, "0")}`);
    //   setPeriod(h < 12 ? "AM" : "PM");
    // }, 1000);
    // return () => clearInterval(interval);
    setTime("3:00");
    setPeriod("AM");
  }, []);

  return (
    <div className="relative flex items-center justify-between px-6 pt-3 pb-1">
      <span className="text-[15px] font-semibold tracking-tight text-white">
        {time} {period}
      </span>

      {/* Dynamic Island */}
      <div className="absolute left-1/2 top-3 -translate-x-1/2 w-[126px] h-[37px] bg-black rounded-[20px]" />

      <div className="flex items-center gap-1.5">
        {/* Signal */}
        <svg className="w-[18px] h-[12px]" viewBox="0 0 18 12" fill="white">
          <rect x="0" y="8" width="3" height="4" rx="0.5" />
          <rect x="5" y="5" width="3" height="7" rx="0.5" />
          <rect x="10" y="2" width="3" height="10" rx="0.5" />
          <rect x="15" y="0" width="3" height="12" rx="0.5" />
        </svg>
        {/* WiFi */}
        <svg className="w-[16px] h-[12px]" viewBox="0 0 16 12" fill="white">
          <path d="M8 10a1.5 1.5 0 100-3 1.5 1.5 0 000 3z" />
          <path
            d="M8 6a4 4 0 00-2.83 1.17 1 1 0 11-1.41-1.41 6 6 0 018.48 0 1 1 0 11-1.41 1.41A4 4 0 008 6z"
            fill="white"
          />
          <path
            d="M8 2a8 8 0 00-5.66 2.34 1 1 0 11-1.41-1.41 10 10 0 0114.14 0 1 1 0 11-1.41 1.41A8 8 0 008 2z"
            fill="white"
          />
        </svg>
        {/* Battery */}
        <div className="flex items-center gap-0.5">
          <div className="w-[22px] h-[11px] rounded-[2.5px] border border-white/90 flex items-center justify-end pr-0.5">
            <div
              className="h-[7px] w-[16px] rounded-[1px] bg-white"
              style={{ marginRight: "2px" }}
            />
          </div>
          <span className="text-[12px] font-semibold text-white">87%</span>
        </div>
      </div>
    </div>
  );
}
