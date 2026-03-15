"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { ComfortLevel } from "@/types/api";

export interface UserSetupData {
  interests: string[];
  comfort_level: ComfortLevel;
  radius_km: number;
  timing: string[];
  latent_intents: string;
}

const INTEREST_CATEGORIES = [
  "art",
  "sport",
  "food",
  "music",
  "nature",
  "study",
  "nightlife",
  "wellness",
  "comedy",
  "tech",
];

const COMFORT_OPTIONS: { value: ComfortLevel; label: string; desc: string }[] = [
  { value: "solo_ok", label: "Happy solo", desc: "I'm fine going alone" },
  {
    value: "prefer_others",
    label: "Better with others",
    desc: "I'd rather not go alone",
  },
  {
    value: "need_familiar",
    label: "Need a familiar face",
    desc: "I want to know someone there",
  },
];

const TIMING_OPTIONS = [
  { id: "morning", label: "Morning" },
  { id: "afternoon", label: "Afternoon" },
  { id: "evening", label: "Evening" },
  { id: "late_night", label: "Late night" },
];

interface QuestionnaireModeProps {
  onComplete: (data: UserSetupData) => void;
}

export function QuestionnaireMode({ onComplete }: QuestionnaireModeProps) {
  const [step, setStep] = useState(0);
  const [data, setData] = useState<UserSetupData>({
    interests: [],
    comfort_level: "solo_ok",
    radius_km: 2.5,
    timing: [],
    latent_intents: "",
  });

  const toggleInterest = (cat: string) => {
    setData((prev) => ({
      ...prev,
      interests: prev.interests.includes(cat)
        ? prev.interests.filter((c) => c !== cat)
        : [...prev.interests, cat],
    }));
  };

  const toggleTiming = (id: string) => {
    setData((prev) => ({
      ...prev,
      timing: prev.timing.includes(id)
        ? prev.timing.filter((t) => t !== id)
        : [...prev.timing, id],
    }));
  };

  const canProceed = () => {
    if (step === 0) return data.interests.length > 0;
    if (step === 1) return true;
    if (step === 2) return true;
    if (step === 3) return data.timing.length > 0;
    if (step === 4) return true;
    return true;
  };

  const handleNext = () => {
    if (step < 4) {
      setStep((s) => s + 1);
    } else {
      onComplete(data);
    }
  };

  const handleBack = () => {
    if (step > 0) setStep((s) => s - 1);
  };

  return (
    <div className="space-y-6">
      <AnimatePresence mode="wait">
        {step === 0 && (
          <motion.div
            key="interests"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="rounded-2xl bg-bg-card p-6 border border-white/5"
          >
            <h3 className="text-lg font-semibold text-text-primary mb-2">
              What are you into?
            </h3>
            <p className="text-sm text-text-muted mb-4">
              Tap to select. You can pick multiple.
            </p>
            <div className="flex flex-wrap gap-2">
              {INTEREST_CATEGORIES.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => toggleInterest(cat)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                    data.interests.includes(cat)
                      ? "bg-accent text-black"
                      : "bg-bg-card-hover text-text-muted hover:text-text-primary"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        {step === 1 && (
          <motion.div
            key="comfort"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="space-y-3"
          >
            <h3 className="text-lg font-semibold text-text-primary">
              How do you feel about going solo?
            </h3>
            <p className="text-sm text-text-muted mb-4">
              Pick the one that fits you best.
            </p>
            {COMFORT_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() =>
                  setData((prev) => ({ ...prev, comfort_level: opt.value }))
                }
                className={`w-full text-left p-4 rounded-xl border transition-colors ${
                  data.comfort_level === opt.value
                    ? "border-accent bg-accent/10"
                    : "border-white/10 bg-bg-card hover:bg-bg-card-hover"
                }`}
              >
                <span className="font-medium text-text-primary block">
                  {opt.label}
                </span>
                <span className="text-sm text-text-muted">{opt.desc}</span>
              </button>
            ))}
          </motion.div>
        )}

        {step === 2 && (
          <motion.div
            key="radius"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="rounded-2xl bg-bg-card p-6 border border-white/5"
          >
            <h3 className="text-lg font-semibold text-text-primary mb-2">
              How far will you walk?
            </h3>
            <p className="text-sm text-text-muted mb-6">
              {data.radius_km} km - about {Math.round(data.radius_km * 12)} min
              walk
            </p>
            <input
              type="range"
              min="0.5"
              max="5"
              step="0.5"
              value={data.radius_km}
              onChange={(e) =>
                setData((prev) => ({
                  ...prev,
                  radius_km: parseFloat(e.target.value),
                }))
              }
              className="w-full h-2 bg-bg-card-hover rounded-full appearance-none cursor-pointer accent-accent"
            />
            <div className="flex justify-between text-xs text-text-muted mt-2">
              <span>0.5 km</span>
              <span>5 km</span>
            </div>
          </motion.div>
        )}

        {step === 3 && (
          <motion.div
            key="timing"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="rounded-2xl bg-bg-card p-6 border border-white/5"
          >
            <h3 className="text-lg font-semibold text-text-primary mb-2">
              When are you most likely to say yes?
            </h3>
            <p className="text-sm text-text-muted mb-4">
              Select all that apply.
            </p>
            <div className="flex flex-wrap gap-2">
              {TIMING_OPTIONS.map((opt) => (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => toggleTiming(opt.id)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                    data.timing.includes(opt.id)
                      ? "bg-accent text-black"
                      : "bg-bg-card-hover text-text-muted hover:text-text-primary"
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        {step === 4 && (
          <motion.div
            key="intent"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="rounded-2xl bg-bg-card p-6 border border-white/5"
          >
            <h3 className="text-lg font-semibold text-text-primary mb-2">
              What&apos;s on your mind?
            </h3>
            <p className="text-sm text-text-muted mb-4">
              Anything you&apos;ve been meaning to try? (optional)
            </p>
            <textarea
              value={data.latent_intents}
              onChange={(e) =>
                setData((prev) => ({
                  ...prev,
                  latent_intents: e.target.value,
                }))
              }
              placeholder="e.g. I've been wanting to try bouldering, visit that new gallery..."
              className="w-full h-24 px-4 py-3 rounded-xl bg-bg-card-hover border border-white/10 text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent resize-none"
              rows={4}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Progress dots */}
      <div className="flex justify-center gap-2">
        {[0, 1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className={`h-2 rounded-full transition-all ${
              i === step ? "w-6 bg-accent" : "w-2 bg-text-muted/40"
            }`}
          />
        ))}
      </div>

      {/* Navigation */}
      <div className="flex gap-3">
        {step > 0 && (
          <button
            type="button"
            onClick={handleBack}
            className="px-6 py-3 rounded-xl border border-white/20 text-text-primary font-medium hover:bg-white/5"
          >
            Back
          </button>
        )}
        <button
          type="button"
          onClick={handleNext}
          disabled={!canProceed()}
          className="flex-1 px-6 py-3 rounded-xl bg-accent text-black font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-amber-500"
        >
          {step < 4 ? "Next" : "Done"}
        </button>
      </div>
    </div>
  );
}
