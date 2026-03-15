"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ModeSelector, type SetupMode } from "@/components/ProfileSetup/ModeSelector";
import { QuestionnaireMode } from "@/components/ProfileSetup/QuestionnaireMode";
import { ChatMode } from "@/components/ProfileSetup/ChatMode";
import { VoiceMode } from "@/components/ProfileSetup/VoiceMode";
import type { UserSetupData } from "@/components/ProfileSetup/QuestionnaireMode";
import { patchUsersMe, isAuthenticated } from "@/lib/api";

export default function SetupPage() {
  const router = useRouter();
  const [mode, setMode] = useState<SetupMode>("questions");
  const [setupComplete, setSetupComplete] = useState(false);

  const handleComplete = async (data: UserSetupData) => {
    try {
      if (isAuthenticated()) {
        await patchUsersMe({
          comfort_level: data.comfort_level,
          willingness_radius_km: data.radius_km,
          preferences: data.interests.map((cat) => ({
            category: cat,
            weight: 1,
            explicit: true,
          })),
        });
      }
    } catch {
      // Backend may not be running; continue to dashboard
    }
    setSetupComplete(true);
    router.push("/dashboard");
  };

  return (
    <div className="min-h-screen px-4 py-8 md:py-12">
      <div className="max-w-lg mx-auto">
        <h1 className="text-2xl font-bold text-text-primary mb-1">
          Tell us about you
        </h1>
        <p className="text-text-muted mb-6">
          Pick how you&apos;d like to share - quick questions, a chat, or
          voice.
        </p>

        <ModeSelector mode={mode} onModeChange={setMode} />

        <div className="mt-6">
          {mode === "questions" && (
            <QuestionnaireMode onComplete={handleComplete} />
          )}
          {mode === "chat" && <ChatMode onComplete={handleComplete} />}
          {mode === "voice" && <VoiceMode onComplete={handleComplete} />}
        </div>

        {setupComplete && (
          <p className="mt-4 text-sm text-accent text-center">
            Redirecting to dashboard...
          </p>
        )}
      </div>
    </div>
  );
}
