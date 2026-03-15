"use client";

interface IPadStatusBarProps {
  time?: string;
  dark?: boolean;
}

export function IPadStatusBar({ time = "5:45", dark = true }: IPadStatusBarProps) {
  const textColor = dark ? "text-white" : "text-black";

  return (
    <div className={`flex items-center justify-between px-6 py-2 ${textColor}`}>
      <span className="text-[13px] font-semibold">{time}</span>

      <div className="flex items-center gap-1.5">
        {/* WiFi */}
        <svg className="w-[15px] h-[11px]" viewBox="0 0 16 12" fill="currentColor">
          <path d="M8 10a1.5 1.5 0 100-3 1.5 1.5 0 000 3z" />
          <path d="M8 6a4 4 0 00-2.83 1.17 1 1 0 11-1.41-1.41 6 6 0 018.48 0 1 1 0 11-1.41 1.41A4 4 0 008 6z" />
          <path d="M8 2a8 8 0 00-5.66 2.34 1 1 0 11-1.41-1.41 10 10 0 0114.14 0 1 1 0 11-1.41 1.41A8 8 0 008 2z" />
        </svg>
        {/* Battery */}
        <div className="flex items-center gap-0.5">
          <div className="w-[22px] h-[10px] rounded-[2.5px] border border-current/60 flex items-center p-[1.5px]">
            <div className="h-full w-[75%] rounded-[1px] bg-current" />
          </div>
        </div>
      </div>
    </div>
  );
}
