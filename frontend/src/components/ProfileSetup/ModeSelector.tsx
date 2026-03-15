"use client";

import type { UserSetupData } from "./QuestionnaireMode";

export type SetupMode = "questions" | "chat" | "voice";

interface ModeSelectorProps {
  mode: SetupMode;
  onModeChange: (mode: SetupMode) => void;
}

const MODES: { id: SetupMode; label: string }[] = [
  { id: "questions", label: "Questions" },
  { id: "chat", label: "Chat" },
  { id: "voice", label: "Voice" },
];

export function ModeSelector({ mode, onModeChange }: ModeSelectorProps) {
  return (
    <div className="flex gap-1 p-1 rounded-xl bg-bg-card border border-white/10">
      {MODES.map((m) => (
        <button
          key={m.id}
          type="button"
          onClick={() => onModeChange(m.id)}
          className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-colors ${
            mode === m.id
              ? "bg-accent text-black"
              : "text-text-muted hover:text-text-primary"
          }`}
        >
          {m.label}
        </button>
      ))}
    </div>
  );
}
