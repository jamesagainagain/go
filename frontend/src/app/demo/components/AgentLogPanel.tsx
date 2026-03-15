"use client";

import type { AgentLogEntry } from "../hooks/useAgentStream";

/* Match glow palette: amber, blue, magenta, purple */
const AGENT_COLORS: Record<string, string> = {
  context: "text-[hsl(27deg_93%_60%)]",
  discovery: "text-[#00a6ff]",
  social_proof: "text-[#ff0056]",
  commitment: "text-slate-400",
  momentum: "text-[#6500ff]",
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
      <div className="relative z-[1] flex h-full flex-col overflow-hidden rounded-lg liquid-glass-soft">
        <div className="gradient-underline h-px w-full opacity-50" />
        <div className="px-4 py-2">
          <span className="text-sm font-medium text-stone-600">
            Agent pipeline
          </span>
        </div>
        <div className="flex-1 overflow-y-auto p-4 font-mono text-sm" role="log" aria-live="polite">
          {logs.length === 0 ? (
            <p className="text-stone-500">Waiting for pipeline...</p>
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
                  <span className="text-stone-700">{entry.message}</span>
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
