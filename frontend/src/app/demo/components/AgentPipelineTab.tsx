"use client";

const AGENTS = [
  {
    name: "Context",
    description: "Time, location, calendar — is this a dead moment?",
  },
  {
    name: "Discovery",
    description: "What's happening nearby right now?",
  },
  {
    name: "Social Proof",
    description: "Who else is going?",
  },
  {
    name: "Commitment",
    description: "One tap. Done.",
  },
  {
    name: "Momentum",
    description: "Learns what gets YOU out the door.",
  },
];

export function AgentPipelineTab() {
  return (
    <div
      className="flex flex-1 flex-col items-center justify-center overflow-y-auto px-6 py-12"
      role="tabpanel"
      id="tabpanel-4"
      aria-labelledby="tab-4"
    >
      <div className="flex flex-wrap items-stretch justify-center gap-4">
        {AGENTS.map((agent, i) => (
          <div key={agent.name} className="flex items-center gap-3">
            <div className="glow-box-subtle rounded-lg px-6 py-4">
              <p className="gradient-text-bright font-bold">{agent.name}</p>
              <p className="relative z-[1] mt-1 text-sm text-slate-400">
                {agent.description}
              </p>
            </div>
            {i < AGENTS.length - 1 && (
              <span className="gradient-text-warm text-2xl font-light" aria-hidden>
                →
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
