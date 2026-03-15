"use client";

import { useCallback, useEffect, useRef, useState } from "react";

export interface AgentLogEntry {
  agent: string;
  message: string;
  status: "complete" | "running";
}

const SIMULATED_LOGS: Omit<AgentLogEntry, "status">[] = [
  { agent: "context", message: "reading user state..." },
  { agent: "context", message: "intervention_score: 0.84" },
  { agent: "discovery", message: "searching 3 tiers..." },
  { agent: "discovery", message: "4 candidates found" },
  { agent: "social_proof", message: "enriching candidates..." },
  { agent: "social_proof", message: "2 candidates have solo attendees" },
  { agent: "commitment", message: "preparing one-tap RSVP" },
  { agent: "momentum", message: "ranking by user history..." },
  { agent: "momentum", message: "selected: Open Mic @ The Old Blue Last — confidence: 0.91" },
];

const STAGGER_MS = 400;
const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";
const SSE_URL = `${API_BASE.replace(/\/$/, "")}/activations/stream`;

export function useAgentStream() {
  const [logs, setLogs] = useState<AgentLogEntry[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);
  const simulatedTimeoutRef = useRef<ReturnType<typeof setTimeout>[]>([]);

  const clearStream = useCallback(() => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
    simulatedTimeoutRef.current.forEach(clearTimeout);
    simulatedTimeoutRef.current = [];
  }, []);

  const startSimulatedStream = useCallback(
    (onFinalMessage?: (eventTitle: string) => void) => {
      setLogs([]);
      SIMULATED_LOGS.forEach((entry, i) => {
        const timeout = setTimeout(() => {
          setLogs((prev) => [
            ...prev,
            {
              ...entry,
              status: i === SIMULATED_LOGS.length - 1 ? "complete" : "complete",
            },
          ]);
          if (i === SIMULATED_LOGS.length - 1 && onFinalMessage) {
            const match = entry.message.match(/selected: (.+?) —/);
            if (match) onFinalMessage(match[1]);
          }
        }, (i + 1) * STAGGER_MS);
        simulatedTimeoutRef.current.push(timeout);
      });
    },
    []
  );

  const startStream = useCallback(
    (onFinalMessage?: (eventTitle: string) => void) => {
      setIsStreaming(true);
      setLogs([]);
      clearStream();

      try {
        const url = `${SSE_URL}?user_id=demo-user-001`;
        const es = new EventSource(url);
        eventSourceRef.current = es;

        es.onmessage = (e) => {
          try {
            const data = JSON.parse(e.data) as AgentLogEntry;
            setLogs((prev) => [...prev, { ...data, status: "complete" }]);
          } catch {
            // ignore parse errors
          }
        };

        es.onerror = () => {
          es.close();
          eventSourceRef.current = null;
          startSimulatedStream(onFinalMessage);
        };

        es.addEventListener("open", () => {
          // SSE connected - real stream will populate logs
        });
      } catch {
        startSimulatedStream(onFinalMessage);
      }
    },
    [clearStream, isStreaming, startSimulatedStream]
  );

  useEffect(() => {
    return () => clearStream();
  }, [clearStream]);

  return { logs, startStream, startSimulatedStream, isStreaming };
}
