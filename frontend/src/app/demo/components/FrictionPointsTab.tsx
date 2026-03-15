"use client";

const FRICTION_POINTS = [
  "Find what to do",
  "Find where it is",
  "Find when it works",
  "Figure out who's going",
  "Commit to it",
  "Get there",
  "Walk in alone",
];

interface FrictionPointsTabProps {
  onSeeGoFixThis: () => void;
}

export function FrictionPointsTab({ onSeeGoFixThis }: FrictionPointsTabProps) {
  return (
    <div
      className="flex flex-1 flex-col items-center justify-center overflow-y-auto px-6 py-12"
      role="tabpanel"
      id="tabpanel-1"
      aria-labelledby="tab-1"
    >
      <div className="flex max-w-2xl flex-col gap-3">
        {FRICTION_POINTS.map((point, i) => (
          <div
            key={point}
            className="glow-box-subtle flex items-center gap-4 rounded-lg px-5 py-3 opacity-0 animate-[fadeIn_0.3s_ease-out_forwards]"
            style={{ animationDelay: `${i * 100}ms` }}
          >
            <span className="gradient-text text-sm font-medium">{i + 1}</span>
            <span className="text-xl text-slate-50">{point}</span>
          </div>
        ))}
      </div>
      <div className="mt-12 w-full max-w-2xl pt-8">
        <div className="gradient-underline mx-auto mb-8 h-px w-full opacity-30" />
        <p className="text-center text-xl text-slate-400">
          Your phone has zero friction points. The screen always wins.
        </p>
        <button
          type="button"
          onClick={onSeeGoFixThis}
          className="glow-box mx-auto mt-6 flex items-center gap-2 rounded-xl px-6 py-3 text-lg font-semibold text-white transition hover:brightness-110"
        >
          See go! fix this
          <span aria-hidden>→</span>
        </button>
      </div>
    </div>
  );
}
