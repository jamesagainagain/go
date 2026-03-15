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
  { agent: "momentum", message: "selected: Open Mic @ The Old Blue Last - confidence: 0.91" },
];

const STAGGER_MS = 400;

export function useAgentStream() {
  const [logs, setLogs] = useState<AgentLogEntry[]>([]);
  const simulatedTimeoutRef = useRef<ReturnType<typeof setTimeout>[]>([]);

  const clearStream = useCallback(() => {
    simulatedTimeoutRef.current.forEach(clearTimeout);
    simulatedTimeoutRef.current = [];
  }, []);

  const startStream = useCallback(() => {
    setLogs([]);
    clearStream();
    SIMULATED_LOGS.forEach((entry, i) => {
      const timeout = setTimeout(() => {
        setLogs((prev) => [
          ...prev,
          { ...entry, status: "complete" },
        ]);
      }, (i + 1) * STAGGER_MS);
      simulatedTimeoutRef.current.push(timeout);
    });
  }, [clearStream]);

  useEffect(() => {
    return () => clearStream();
  }, [clearStream]);

  return { logs, startStream };
}
