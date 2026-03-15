"use client";

import { useState, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { IPadFrame } from "@/components/iPadFrame";
import { IPadHomeScreen } from "@/components/iPadHomeScreen";
import { IPadLockScreen } from "@/components/iPadLockScreen";
import { GoAppView } from "@/components/GoAppView";
import { ModeSelector, type SetupMode } from "@/components/ProfileSetup/ModeSelector";
import { QuestionnaireMode } from "@/components/ProfileSetup/QuestionnaireMode";
import { ChatMode } from "@/components/ProfileSetup/ChatMode";
import { VoiceMode } from "@/components/ProfileSetup/VoiceMode";
import type { UserSetupData } from "@/components/ProfileSetup/QuestionnaireMode";

type NarrativeStage =
  | "landing"
  | "ipad-home"
  | "go-setup"
  | "fade-out"
  | "ipad-off"
  | "lock-screen"
  | "notification"
  | "go-events";

export default function Page() {
  const [stage, setStage] = useState<NarrativeStage>("landing");
  const [setupMode, setSetupMode] = useState<SetupMode>("questions");
  const [setupDone, setSetupDone] = useState(false);

  const handleGetStarted = useCallback(() => {
    setStage("ipad-home");
  }, []);

  const handleOpenApp = useCallback(
    (appId: string) => {
      if (appId === "go") {
        setStage("go-setup");
      }
    },
    []
  );

  const handleSetupComplete = useCallback((_data?: UserSetupData) => {
    setSetupDone(true);
  }, []);

  const handleContinue = useCallback(() => {
    setStage("fade-out");
    setTimeout(() => setStage("ipad-off"), 1500);
  }, []);

  const handlePowerOn = useCallback(() => {
    setStage("lock-screen");
    setTimeout(() => setStage("notification"), 1800);
  }, []);

  const handleNotificationClick = useCallback(() => {
    setStage("go-events");
  }, []);

  const setupContent = (
    <>
      <ModeSelector mode={setupMode} onModeChange={setSetupMode} />
      <div className="mt-5">
        {setupMode === "questions" && (
          <QuestionnaireMode onComplete={handleSetupComplete} />
        )}
        {setupMode === "chat" && <ChatMode onComplete={handleSetupComplete} />}
        {setupMode === "voice" && (
          <VoiceMode onComplete={handleSetupComplete} />
        )}
      </div>
    </>
  );

  return (
    <div className="min-h-screen bg-[#06060c] relative overflow-hidden">
      <AnimatePresence mode="wait">
        {/* ==================== LANDING ==================== */}
        {stage === "landing" && (
          <motion.div
            key="landing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.6 }}
            className="min-h-screen flex flex-col items-center justify-center px-6"
          >
            <div
              className="absolute inset-0 pointer-events-none"
              style={{
                background:
                  "radial-gradient(ellipse 80% 50% at 50% 0%, rgba(245,158,11,0.08) 0%, transparent 50%), radial-gradient(ellipse 60% 40% at 80% 80%, rgba(167,139,250,0.05) 0%, transparent 40%)",
              }}
            />
            <main className="relative z-10 flex flex-col items-center text-center max-w-2xl">
              <h1 className="text-5xl md:text-7xl font-bold text-white tracking-tight">
                Go
              </h1>
              <p className="mt-6 text-lg md:text-xl text-white/50 leading-relaxed max-w-md">
                The gap between &quot;I could&quot; and &quot;I am&quot; has
                seven friction points. We collapse them to one.
              </p>
              <button
                type="button"
                onClick={handleGetStarted}
                className="mt-10 inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-black bg-gradient-to-r from-[#f59e0b] to-[#d97706] rounded-xl transition-all duration-300 hover:shadow-[0_0_30px_rgba(245,158,11,0.3)] hover:scale-[1.02] active:scale-[0.98]"
              >
                Get Started
              </button>
            </main>
          </motion.div>
        )}

        {/* ==================== IPAD HOME ==================== */}
        {stage === "ipad-home" && (
          <motion.div
            key="ipad-home"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          >
            <IPadFrame>
              <IPadHomeScreen onOpenApp={handleOpenApp} />
            </IPadFrame>
          </motion.div>
        )}

        {/* ==================== GO APP — SETUP ==================== */}
        {stage === "go-setup" && (
          <motion.div
            key="go-setup"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
          >
            <IPadFrame>
              <GoAppView
                mode="setup"
                setupContent={setupContent}
                onSetupComplete={setupDone ? handleContinue : undefined}
              />
            </IPadFrame>
          </motion.div>
        )}

        {/* ==================== FADE TO BLACK ==================== */}
        {stage === "fade-out" && (
          <motion.div
            key="fade-out"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1.2 }}
            className="min-h-screen bg-black"
          />
        )}

        {/* ==================== IPAD OFF ==================== */}
        {stage === "ipad-off" && (
          <motion.div
            key="ipad-off"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8 }}
          >
            <IPadFrame screenOn={false}>
              <div className="w-full h-full bg-[#0a0a0a]" />
            </IPadFrame>

            {/* Power button overlay */}
            <motion.div
              className="absolute inset-0 flex items-center justify-center z-50"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8, duration: 0.5 }}
            >
              <button
                type="button"
                onClick={handlePowerOn}
                className="flex flex-col items-center gap-4 group"
              >
                <motion.div
                  className="w-20 h-20 rounded-full border-2 border-white/20 flex items-center justify-center bg-white/5 backdrop-blur-sm transition-all group-hover:border-amber-400/50 group-hover:bg-amber-400/10"
                  animate={{ boxShadow: ["0 0 0px rgba(245,158,11,0)", "0 0 20px rgba(245,158,11,0.2)", "0 0 0px rgba(245,158,11,0)"] }}
                  transition={{ repeat: Infinity, duration: 2 }}
                >
                  <svg
                    className="w-8 h-8 text-white/50 group-hover:text-amber-400 transition-colors"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path d="M12 2v4M12 18a6 6 0 100-12 6 6 0 000 12z" strokeLinecap="round" />
                  </svg>
                </motion.div>
                <span className="text-white/30 text-sm tracking-wide">
                  Tap to wake
                </span>
              </button>
            </motion.div>
          </motion.div>
        )}

        {/* ==================== LOCK SCREEN ==================== */}
        {(stage === "lock-screen" || stage === "notification") && (
          <motion.div
            key="lock-screen"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            <IPadFrame>
              <IPadLockScreen
                showNotification={stage === "notification"}
                onNotificationClick={handleNotificationClick}
              />
            </IPadFrame>
          </motion.div>
        )}

        {/* ==================== GO APP — EVENTS ==================== */}
        {stage === "go-events" && (
          <motion.div
            key="go-events"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4 }}
          >
            <IPadFrame>
              <GoAppView mode="events" />
            </IPadFrame>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
