"use client";

import type { AgentLogEntry } from "../hooks/useAgentStream";

const AGENT_COLORS: Record<string, string> = {
  context: "text-blue-400",
  discovery: "text-green-400",
  social_proof: "text-purple-400",
  commitment: "text-orange-400",
  momentum: "text-red-400",
};

function formatAgentName(agent: string): string {
  const names: Record<string, string> = {
    context: "Context Agent",
    discovery: "Discovery Agent",
    social_proof: "Social Proof Agent",
    commitment: "Commitment Agent",
    momentum: "Momentum Agent",
  };
  return names[agent] ?? agent;
}

interface AgentLogPanelProps {
  logs: AgentLogEntry[];
}

export function AgentLogPanel({ logs }: AgentLogPanelProps) {
  return (
    <div className="glow-box-subtle flex h-full flex-col overflow-hidden rounded-lg">
      <div className="relative z-[1] flex h-full flex-col overflow-hidden rounded-lg bg-[#0d1117]">
        <div className="gradient-underline h-px w-full opacity-30" />
        <div className="px-4 py-2">
          <span className="gradient-text text-sm font-medium">
            Agent pipeline
          </span>
        </div>
        <div className="flex-1 overflow-y-auto p-4 font-mono text-sm" role="log" aria-live="polite">
          {logs.length === 0 ? (
            <p className="text-slate-600">Waiting for pipeline...</p>
          ) : (
            <div className="space-y-1">
              {logs.map((entry, i) => (
                <div
                  key={`${entry.agent}-${i}`}
                  className="animate-[fadeIn_0.2s_ease-out]"
                >
                  <span
                    className={AGENT_COLORS[entry.agent] ?? "text-slate-400"}
                  >
                    [{formatAgentName(entry.agent)}]
                  </span>{" "}
                  <span className="text-slate-300">{entry.message}</span>
                  {entry.status === "complete" && (
                    <span className="ml-1 text-green-500">✓</span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
