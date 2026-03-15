"use client";

import { IPadStatusBar } from "./iPadStatusBar";

interface AppIcon {
  id: string;
  name: string;
  gradient: string;
  icon: string;
  onClick?: () => void;
}

interface IPadHomeScreenProps {
  onOpenApp: (appId: string) => void;
}

const APPS: AppIcon[] = [
  {
    id: "instagram",
    name: "Instagram",
    gradient: "from-[#f09433] via-[#e6683c] to-[#dc2743]",
    icon: "M12 2.2c2.7 0 3 0 4.1.1 1 .1 1.5.2 1.9.3.5.2.8.4 1.1.7.3.3.5.7.7 1.1.1.4.3.9.3 1.9.1 1.1.1 1.4.1 4.1s0 3-.1 4.1c-.1 1-.2 1.5-.3 1.9-.2.5-.4.8-.7 1.1-.3.3-.7.5-1.1.7-.4.1-.9.3-1.9.3-1.1.1-1.4.1-4.1.1s-3 0-4.1-.1c-1-.1-1.5-.2-1.9-.3-.5-.2-.8-.4-1.1-.7-.3-.3-.5-.7-.7-1.1-.1-.4-.3-.9-.3-1.9C2.2 15 2.2 14.7 2.2 12s0-3 .1-4.1c.1-1 .2-1.5.3-1.9.2-.5.4-.8.7-1.1.3-.3.7-.5 1.1-.7.4-.1.9-.3 1.9-.3C7 2.2 7.3 2.2 12 2.2zM12 0C9.3 0 8.9 0 7.8.1 6.7.1 5.9.3 5.2.6c-.7.3-1.3.6-1.9 1.2C2.7 2.4 2.4 3 2.1 3.7c-.3.7-.5 1.5-.5 2.6C1.5 7.4 1.5 7.8 1.5 12s0 4.6.1 5.7c.1 1.1.2 1.9.5 2.6.3.7.6 1.3 1.2 1.9.6.6 1.2.9 1.9 1.2.7.3 1.5.5 2.6.5 1.1.1 1.5.1 5.7.1s4.6 0 5.7-.1c1.1-.1 1.9-.2 2.6-.5.7-.3 1.3-.6 1.9-1.2.6-.6.9-1.2 1.2-1.9.3-.7.5-1.5.5-2.6.1-1.1.1-1.5.1-5.7s0-4.6-.1-5.7c-.1-1.1-.2-1.9-.5-2.6-.3-.7-.6-1.3-1.2-1.9-.6-.6-1.2-.9-1.9-1.2-.7-.3-1.5-.5-2.6-.5C16.6 0 16.2 0 12 0zm0 5.8a6.2 6.2 0 100 12.4 6.2 6.2 0 000-12.4zm0 10.2a4 4 0 110-8 4 4 0 010 8zm6.4-10.5a1.4 1.4 0 11-2.8 0 1.4 1.4 0 012.8 0z",
  },
  {
    id: "tiktok",
    name: "TikTok",
    gradient: "from-[#000000] to-[#1a1a2e]",
    icon: "M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .56.04.81.11v-3.5a6.37 6.37 0 00-.81-.05A6.34 6.34 0 003.15 15.2a6.34 6.34 0 0010.42 4.84 6.33 6.33 0 001.91-4.52V9.4a8.16 8.16 0 004.76 1.53v-3.4a4.85 4.85 0 01-.65-.84z",
  },
  {
    id: "x",
    name: "X",
    gradient: "from-[#000000] to-[#14171a]",
    icon: "M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z",
  },
  {
    id: "facebook",
    name: "Facebook",
    gradient: "from-[#1877f2] to-[#0c5dc7]",
    icon: "M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z",
  },
  {
    id: "reddit",
    name: "Reddit",
    gradient: "from-[#ff4500] to-[#cc3700]",
    icon: "M12 0A12 12 0 000 12a12 12 0 0012 12 12 12 0 0012-12A12 12 0 0012 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 01-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 01.042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 014.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 01.14-.197.35.35 0 01.238-.042l2.906.617a1.214 1.214 0 011.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 00-.231.094.33.33 0 000 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 00.029-.463.33.33 0 00-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 00-.232-.094z",
  },
  {
    id: "go",
    name: "Go",
    gradient: "from-[#f59e0b] to-[#d97706]",
    icon: "",
  },
];

export function IPadHomeScreen({ onOpenApp }: IPadHomeScreenProps) {
  return (
    <div
      className="w-full h-full flex flex-col"
      style={{
        background: "linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)",
      }}
    >
      <IPadStatusBar time="5:45" />

      {/* App grid */}
      <div className="flex-1 flex items-center justify-center px-12 py-8">
        <div className="grid grid-cols-4 md:grid-cols-6 gap-6 md:gap-8 max-w-[600px]">
          {APPS.map((app) => (
            <button
              key={app.id}
              type="button"
              onClick={() => onOpenApp(app.id)}
              className="flex flex-col items-center gap-1.5 group"
            >
              <div
                className={`w-[60px] h-[60px] md:w-[72px] md:h-[72px] rounded-[16px] md:rounded-[18px] bg-gradient-to-br ${app.gradient} flex items-center justify-center shadow-lg transition-transform group-hover:scale-105 group-active:scale-95`}
              >
                {app.id === "go" ? (
                  <span className="text-white text-xl md:text-2xl font-bold tracking-tight">Go</span>
                ) : (
                  <svg
                    className="w-7 h-7 md:w-8 md:h-8 text-white"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                  >
                    <path d={app.icon} />
                  </svg>
                )}
              </div>
              <span className="text-white/80 text-[10px] md:text-[11px] font-medium">
                {app.name}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Dock */}
      <div className="mx-6 mb-6 rounded-2xl bg-white/10 backdrop-blur-xl px-6 py-3 flex justify-center gap-6">
        {["safari", "mail", "photos", "music"].map((app) => (
          <div
            key={app}
            className="w-[50px] h-[50px] md:w-[56px] md:h-[56px] rounded-[14px] bg-white/20 flex items-center justify-center"
          >
            <span className="text-white/50 text-[10px] capitalize">{app}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
