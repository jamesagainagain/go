"use client";

import { useState } from "react";
import type { ComfortLevel, PreferenceInput } from "@/types/api";

const INTEREST_CATEGORIES = [
  "art",
  "sport",
  "food",
  "music",
  "study",
  "creative",
  "outdoor",
  "social",
  "wellness",
] as const;

export interface OnboardingData {
  email: string;
  displayName: string;
  password: string;
  interests: PreferenceInput[];
  comfortLevel: ComfortLevel;
  timezone: string;
}

interface OnboardingFlowProps {
  onComplete: (data: OnboardingData) => Promise<void>;
  onRequestNotifications?: () => Promise<boolean>;
  onRequestLocation?: () => Promise<{ lat: number; lng: number } | null>;
}

const COMFORT_OPTIONS: { value: ComfortLevel; label: string }[] = [
  { value: "solo_ok", label: "Happy going solo" },
  { value: "prefer_others", label: "Prefer others around" },
  { value: "need_familiar", label: "Need familiar faces" },
];

export function OnboardingFlow({
  onComplete,
  onRequestNotifications,
  onRequestLocation,
}: OnboardingFlowProps) {
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [selectedInterests, setSelectedInterests] = useState<Set<string>>(new Set());
  const [comfortLevel, setComfortLevel] = useState<ComfortLevel>("prefer_others");
  const [timezone] = useState(
    () => Intl.DateTimeFormat().resolvedOptions().timeZone ?? "Europe/London"
  );

  const toggleInterest = (category: string) => {
    setSelectedInterests((prev) => {
      const next = new Set(prev);
      if (next.has(category)) next.delete(category);
      else next.add(category);
      return next;
    });
  };

  const interests: PreferenceInput[] = Array.from(selectedInterests).map(
    (cat) => ({ category: cat, weight: 0.8, explicit: true })
  );

  const handleNext = async () => {
    setError(null);
    // Steps 0-3: form steps
    if (step < 4) {
      setStep((s) => s + 1);
      return;
    }

    // Step 4: Request notifications
    if (step === 4 && onRequestNotifications) {
      await onRequestNotifications();
      setStep(5);
      return;
    }

    // Step 5: Request location, then submit
    if (step === 5 && onRequestLocation) {
      const pos = await onRequestLocation();
      if (!pos) {
        setError("Location is needed to find opportunities near you.");
        return;
      }
    }

    // Submit (from step 5 or if no location step)
    setLoading(true);
    try {
      await onComplete({
        email,
        displayName,
        password,
        interests,
        comfortLevel,
        timezone,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => setStep((s) => Math.max(0, s - 1));

  const canProceed =
    (step === 0 && email) ||
    (step === 1 && displayName && password.length >= 8) ||
    (step === 2 && selectedInterests.size > 0) ||
    step >= 3;

  return (
    <div className="mx-auto max-w-md space-y-6 p-6">
      <div className="flex gap-1">
        {[0, 1, 2, 3, 4, 5].map((i) => (
          <div
            key={i}
            className={`h-1 flex-1 rounded ${i <= step ? "bg-amber-500" : "bg-gray-200"}`}
          />
        ))}
      </div>

      {step === 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Create your account</h2>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-4 py-2"
            autoFocus
          />
        </div>
      )}

      {step === 1 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Almost there</h2>
          <input
            type="text"
            placeholder="Display name (first name)"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-4 py-2"
          />
          <input
            type="password"
            placeholder="Password (min 8 characters)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-4 py-2"
          />
        </div>
      )}

      {step === 2 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">What interests you?</h2>
          <p className="text-sm text-gray-600">
            Pick a few - we&apos;ll find things you&apos;ll love.
          </p>
          <div className="flex flex-wrap gap-2">
            {INTEREST_CATEGORIES.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => toggleInterest(cat)}
                className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                  selectedInterests.has(cat)
                    ? "bg-amber-500 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">How do you like to go out?</h2>
          <p className="text-sm text-gray-600">
            This helps us tailor suggestions.
          </p>
          <div className="space-y-2">
            {COMFORT_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setComfortLevel(opt.value)}
                className={`block w-full rounded-lg border px-4 py-3 text-left transition ${
                  comfortLevel === opt.value
                    ? "border-amber-500 bg-amber-50"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {step === 4 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Get nudges</h2>
          <p className="text-sm text-gray-600">
            Allow push notifications so we can send you opportunities at the right moment.
          </p>
          <div className="rounded-lg bg-gray-50 p-4 text-sm text-gray-600">
            You can change this anytime in Settings.
          </div>
        </div>
      )}

      {step === 5 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Find nearby opportunities</h2>
          <p className="text-sm text-gray-600">
            We need your location to suggest events and places near you.
          </p>
        </div>
      )}

      {error && (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="flex gap-2">
        {step > 0 && (
          <button
            type="button"
            onClick={handleBack}
            className="rounded-lg border border-gray-300 px-4 py-2 font-medium text-gray-700 hover:bg-gray-50"
          >
            Back
          </button>
        )}
        <button
          type="button"
          onClick={handleNext}
          disabled={!canProceed || loading}
          className="flex-1 rounded-lg bg-amber-500 px-4 py-2 font-medium text-white disabled:opacity-50 hover:bg-amber-600"
        >
          {loading ? "..." : step === 5 ? "Get started" : "Continue"}
        </button>
      </div>
    </div>
  );
}
