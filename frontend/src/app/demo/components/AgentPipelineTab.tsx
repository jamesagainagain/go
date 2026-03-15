"use client";

const AGENTS = [
  {
    name: "Context",
    description: "Time, location, calendar - is this a dead moment?",
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
      id="tabpanel-3"
      aria-labelledby="tab-3"
    >
      <div className="flex flex-wrap items-stretch justify-center gap-3">
        {AGENTS.map((agent, i) => (
          <div key={agent.name} className="flex items-center gap-3">
            <div className="liquid-glass-card rounded-lg px-5 py-4">
              <p className="font-semibold text-stone-800">{agent.name}</p>
              <p className="mt-1 text-sm text-stone-600">{agent.description}</p>
            </div>
            {i < AGENTS.length - 1 && (
              <span className="text-stone-500" aria-hidden>
                →
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
