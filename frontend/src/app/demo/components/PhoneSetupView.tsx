"use client";

import { useState, useCallback } from "react";
import { ModeSelector, type SetupMode } from "@/components/ProfileSetup/ModeSelector";
import { QuestionnaireMode } from "@/components/ProfileSetup/QuestionnaireMode";
import { ChatMode } from "@/components/ProfileSetup/ChatMode";
import { VoiceMode } from "@/components/ProfileSetup/VoiceMode";
import type { UserSetupData } from "@/components/ProfileSetup/QuestionnaireMode";

interface PhoneSetupViewProps {
  onSetupComplete: () => void;
}

export function PhoneSetupView({ onSetupComplete }: PhoneSetupViewProps) {
  const [setupMode, setSetupMode] = useState<SetupMode>("questions");
  const [setupDone, setSetupDone] = useState(false);

  const handleSetupComplete = useCallback((_data?: UserSetupData) => {
    setSetupDone(true);
  }, []);

  return (
    <div className="phone-demo-accent flex h-full w-full flex-col bg-[#06060c]">
      {/* go! header */}
      <div className="flex items-center gap-2.5 border-b border-white/5 px-4 py-3">
        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-[#626262] to-[#94a3b8]">
          <span className="text-[10px] font-bold text-white">go!</span>
        </div>
        <span className="text-base font-semibold tracking-tight text-white">
          go!
        </span>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        <h2 className="mb-1 text-lg font-bold text-white">Tell us about you</h2>
        <p className="mb-4 text-xs text-white/50">
          Pick how you&apos;d like to share — questions, chat, or voice.
        </p>

        <ModeSelector mode={setupMode} onModeChange={setSetupMode} />

        <div className="mt-4">
          {setupMode === "questions" && (
            <QuestionnaireMode onComplete={handleSetupComplete} />
          )}
          {setupMode === "chat" && (
            <ChatMode onComplete={handleSetupComplete} />
          )}
          {setupMode === "voice" && (
            <VoiceMode onComplete={handleSetupComplete} />
          )}
        </div>

        {setupDone && (
          <div className="mt-4 pb-4">
            <button
              type="button"
              onClick={onSetupComplete}
              className="w-full rounded-xl border border-white/20 bg-white/10 px-6 py-3 text-sm font-semibold text-white transition-all hover:bg-white/15 active:scale-[0.98]"
            >
              Continue
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
