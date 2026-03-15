"use client";

import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";
import { useState, useRef, useEffect } from "react";
import type { UserSetupData } from "./QuestionnaireMode";
import type { ComfortLevel } from "@/types/api";

interface ChatModeProps {
  onComplete: (data: UserSetupData) => void;
}

export function ChatMode({ onComplete }: ChatModeProps) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { messages, sendMessage, status } = useChat({
    transport: new DefaultChatTransport({ api: "/api/chat" }),
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Check if agent said "ready to see what's out there" - then we can complete
  const lastAssistantMessage = messages
    .filter((m) => m.role === "assistant")
    .pop();
  const lastText = lastAssistantMessage?.parts
    ?.filter((p): p is { type: "text"; text: string } => p.type === "text")
    .map((p) => p.text)
    .join("") ?? "";
  const isReady =
    lastText.toLowerCase().includes("ready to see") ||
    lastText.toLowerCase().includes("ready to find") ||
    lastText.toLowerCase().includes("got a good picture");

  const handleComplete = () => {
    // Extract what we can from the conversation - for demo we use defaults
    // In production you'd use a tool/function call to extract structured data
    onComplete({
      interests: ["music", "art"],
      comfort_level: "solo_ok" as ComfortLevel,
      radius_km: 2.5,
      timing: ["evening", "late_night"],
      latent_intents: lastText,
    });
  };

  return (
    <div className="flex flex-col h-[400px]">
      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.length === 0 && (
          <p className="text-sm text-text-muted text-center py-8">
            Say hi! Tell me what you&apos;re into - art, sport, food, music?
            I&apos;ll learn about you through conversation.
          </p>
        )}
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-2.5 ${
                message.role === "user"
                  ? "bg-accent text-black"
                  : "bg-bg-card border border-white/10 text-text-primary"
              }`}
            >
              <div className="text-sm leading-relaxed">
                {message.parts.map((part, index) =>
                  part.type === "text" ? (
                    <span key={index}>{part.text}</span>
                  ) : null
                )}
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="flex gap-2 pt-2 border-t border-white/10">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              if (input.trim()) {
                sendMessage({ text: input });
                setInput("");
              }
            }
          }}
          placeholder="Type a message..."
          disabled={status !== "ready"}
          className="flex-1 px-4 py-3 rounded-xl bg-bg-card border border-white/10 text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent disabled:opacity-50"
        />
        <button
          type="button"
          onClick={() => {
            if (input.trim()) {
              sendMessage({ text: input });
              setInput("");
            }
          }}
          disabled={status !== "ready" || !input.trim()}
          className="px-4 py-3 rounded-xl bg-accent text-black font-medium disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </div>

      {isReady && status === "ready" && (
        <button
          type="button"
          onClick={handleComplete}
          className="mt-4 w-full py-3 rounded-xl bg-accent text-black font-semibold hover:bg-amber-500"
        >
          Continue to Dashboard
        </button>
      )}
    </div>
  );
}
