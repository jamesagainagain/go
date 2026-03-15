"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useAgentStream } from "../hooks/useAgentStream";
import { PhoneMockup } from "./PhoneMockup";
import { PhoneSetupView } from "./PhoneSetupView";
import { PhoneLockScreen } from "./PhoneLockScreen";
import { PhoneEventsView } from "./PhoneEventsView";
import { AgentLogPanel } from "./AgentLogPanel";

type PhoneStage = "setup" | "fade-out" | "off" | "lock-screen" | "events";

export function LiveDemoTab() {
  const { logs, startStream } = useAgentStream();
  const [stage, setStage] = useState<PhoneStage>("setup");
  const fadeTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      if (fadeTimerRef.current) clearTimeout(fadeTimerRef.current);
    };
  }, []);

  const handleSetupComplete = useCallback(() => {
    setStage("fade-out");
    fadeTimerRef.current = setTimeout(() => {
      setStage("off");
    }, 1500);
  }, []);

  const handleWake = useCallback(() => {
    setStage("lock-screen");
  }, []);

  const handleNotificationClick = useCallback(() => {
    setStage("events");
    startStream();
  }, [startStream]);

  return (
    <div
      className="flex flex-1 overflow-hidden"
      role="tabpanel"
      id="tabpanel-3"
      aria-labelledby="tab-3"
    >
      {/* Left: Phone mockup */}
      <div className="flex flex-1 items-center justify-center overflow-visible p-6">
        <PhoneMockup>
          {/* Setup */}
          {stage === "setup" && (
            <PhoneSetupView onSetupComplete={handleSetupComplete} />
          )}

          {/* Fade to black */}
          {stage === "fade-out" && (
            <div className="h-full w-full bg-[#06060c] transition-opacity duration-[1500ms]">
              <div className="flex h-full items-center justify-center">
                <div className="animate-pulse text-sm text-white/30">
                  Setting up your profile...
                </div>
              </div>
              <div className="absolute inset-0 animate-[fadeIn_1.5s_ease-in_forwards] bg-black" />
            </div>
          )}

          {/* Phone off */}
          {stage === "off" && (
            <div className="flex h-full w-full flex-col items-center justify-center bg-black">
              <button
                type="button"
                onClick={handleWake}
                className="group flex flex-col items-center gap-3"
              >
                <div className="flex h-16 w-16 items-center justify-center rounded-full border-2 border-white/20 bg-white/5 transition-all group-hover:border-amber-400/50 group-hover:bg-amber-400/10">
                  <svg
                    className="h-7 w-7 text-white/50 transition-colors group-hover:text-amber-400"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path
                      d="M12 2v4M12 18a6 6 0 100-12 6 6 0 000 12z"
                      strokeLinecap="round"
                    />
                  </svg>
                </div>
                <span className="text-xs tracking-wide text-white/30">
                  Tap to wake
                </span>
              </button>
            </div>
          )}

          {/* Lock screen with notification */}
          {stage === "lock-screen" && (
            <PhoneLockScreen onNotificationClick={handleNotificationClick} />
          )}

          {/* Events view */}
          {stage === "events" && <PhoneEventsView />}
        </PhoneMockup>
      </div>

      {/* Right: Agent log terminal */}
      <div className="flex w-[480px] shrink-0 flex-col p-6">
        <AgentLogPanel logs={logs} />
      </div>
    </div>
  );
}
