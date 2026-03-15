"use client";

import { useState, useRef, useCallback } from "react";
import { motion } from "framer-motion";
import type { UserSetupData } from "./QuestionnaireMode";
import type { ComfortLevel } from "@/types/api";

interface VoiceModeProps {
  onComplete: (data: UserSetupData) => void;
}

interface Turn {
  role: "user" | "assistant";
  content: string;
}

interface VoiceProfileIngest {
  applied?: boolean;
  inferred_preferences?: string[];
  comfort_level?: string | null;
  willingness_radius_km?: number | null;
}

interface VoiceApiResponse {
  transcript: string;
  response_text: string;
  audio_base64: string | null;
  profile_ingest?: VoiceProfileIngest;
}

function toComfortLevel(value: string | null | undefined): ComfortLevel | null {
  if (
    value === "solo_ok" ||
    value === "prefer_others" ||
    value === "need_familiar"
  ) {
    return value;
  }
  return null;
}

export function VoiceMode({ onComplete }: VoiceModeProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [turns, setTurns] = useState<Turn[]>([]);
  const [inferredProfile, setInferredProfile] = useState<{
    interests: string[];
    comfort_level: ComfortLevel;
    radius_km: number;
  } | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const sendAudio = useCallback(async (blob: Blob) => {
    const formData = new FormData();
    formData.append("audio", blob, "audio.webm");
    formData.append(
      "history",
      JSON.stringify(turns.map((t) => ({ role: t.role, content: t.content })))
    );

    const token = localStorage.getItem("access_token");
    const headers: HeadersInit = {};
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    const res = await fetch("/api/voice", {
      method: "POST",
      headers,
      body: formData,
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || "Voice request failed");
    }

    const data = (await res.json()) as VoiceApiResponse;
    const { transcript, response_text, audio_base64, profile_ingest } = data;

    setTurns((prev) => [
      ...prev,
      { role: "user", content: transcript },
      { role: "assistant", content: response_text },
    ]);
    if (profile_ingest?.applied) {
      setInferredProfile((prev) => ({
        interests:
          profile_ingest.inferred_preferences?.length
            ? profile_ingest.inferred_preferences
            : prev?.interests ?? ["music", "art"],
        comfort_level:
          toComfortLevel(profile_ingest.comfort_level) ??
          prev?.comfort_level ??
          "solo_ok",
        radius_km:
          typeof profile_ingest.willingness_radius_km === "number"
            ? profile_ingest.willingness_radius_km
            : prev?.radius_km ?? 2.5,
      }));
    }

    if (audio_base64) {
      const audio = new Audio(`data:audio/mp3;base64,${audio_base64}`);
      audioRef.current = audio;
      setIsPlaying(true);
      audio.onended = () => setIsPlaying(false);
      await audio.play();
    }
  }, [turns]);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data);
      };

      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        if (chunks.length === 0) {
          setIsProcessing(false);
          return;
        }
        const blob = new Blob(chunks, { type: "audio/webm" });
        try {
          await sendAudio(blob);
        } catch (err) {
          console.error("Voice request failed:", err);
          alert("Could not process voice input. Please try again.");
        } finally {
          setIsProcessing(false);
        }
      };

      recorder.start();
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
      setIsProcessing(true);
    } catch (err) {
      console.error("Mic access error:", err);
      setIsProcessing(false);
      alert("Could not access microphone. Please allow mic access.");
    }
  }, [sendAudio]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current = null;
      setIsRecording(false);
    }
  }, [isRecording]);

  const lastAssistantText = turns.filter((t) => t.role === "assistant").pop()?.content ?? "";
  const isReady =
    lastAssistantText.toLowerCase().includes("ready to see") ||
    lastAssistantText.toLowerCase().includes("got a good picture");

  const handleComplete = () => {
    const fallbackInterests = ["music", "art"];
    onComplete({
      interests:
        inferredProfile?.interests.length
          ? inferredProfile.interests
          : fallbackInterests,
      comfort_level: inferredProfile?.comfort_level ?? ("solo_ok" as ComfortLevel),
      radius_km: inferredProfile?.radius_km ?? 2.5,
      timing: ["evening", "late_night"],
      latent_intents: lastAssistantText,
    });
  };

  return (
    <div className="flex flex-col items-center">
      <div className="flex-1 overflow-y-auto w-full max-h-[240px] space-y-3 mb-6">
        {turns.map((turn, i) => (
          <div
            key={i}
            className={`flex ${turn.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-2 text-sm ${
                turn.role === "user"
                  ? "bg-accent text-black"
                  : "bg-bg-card border border-white/10 text-text-primary"
              }`}
            >
              {turn.content}
            </div>
          </div>
        ))}
      </div>

      <div className="flex flex-col items-center">
        <button
          type="button"
          onMouseDown={startRecording}
          onMouseUp={stopRecording}
          onMouseLeave={stopRecording}
          onTouchStart={startRecording}
          onTouchEnd={stopRecording}
          onTouchCancel={stopRecording}
          disabled={isProcessing}
          className="relative w-24 h-24 rounded-full bg-bg-card border-2 border-accent flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:ring-offset-bg-deep disabled:opacity-50"
        >
          {isRecording ? (
            <motion.div
              className="absolute inset-0 rounded-full bg-accent/20"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
            />
          ) : null}
          <svg
            className="w-10 h-10 text-accent relative z-10"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1 2.93c-3.95-.49-7-3.85-7-7.93h2c0 3.31 2.69 6 6 6s6-2.69 6-6h2c0 4.08-3.05 7.44-7 7.93V21h-2v-4.07z" />
          </svg>
        </button>
        <p className="mt-3 text-sm text-text-muted">
          {isRecording
            ? "Release to send"
            : isProcessing
              ? "Processing..."
              : "Hold to talk"}
        </p>

        {isRecording && (
          <div className="flex gap-1 mt-2">
            {[1, 2, 3, 4, 5].map((i) => (
              <motion.div
                key={i}
                className="w-1 h-6 bg-accent rounded-full"
                animate={{ height: [12, 24, 12] }}
                transition={{
                  repeat: Infinity,
                  duration: 0.5,
                  delay: i * 0.1,
                }}
              />
            ))}
          </div>
        )}
      </div>

      {isReady && !isProcessing && (
        <button
          type="button"
          onClick={handleComplete}
          className="mt-6 w-full py-3 rounded-xl bg-accent text-black font-semibold hover:bg-amber-500"
        >
          Continue to Dashboard
        </button>
      )}
    </div>
  );
}
