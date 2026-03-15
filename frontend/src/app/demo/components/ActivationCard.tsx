"use client";

import type { Opportunity } from "@/types/api";

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString(undefined, {
    hour: "numeric",
    minute: "2-digit",
  });
}

interface DemoActivationCardProps {
  opportunity: Opportunity;
  onTapToGo: () => void;
}

export function DemoActivationCard({ opportunity, onTapToGo }: DemoActivationCardProps) {
  const opp = opportunity;
  const primaryLabel = opp.commitment_action?.label ?? "Tap to go";

  return (
    <article
      className="absolute inset-x-4 bottom-4 animate-[slideUp_0.3s_ease-out] rounded-xl border border-slate-200 bg-white p-4 shadow-lg"
      role="article"
    >
      <h2 className="text-lg font-semibold text-slate-900">{opp.title}</h2>
      <p className="mt-1 text-sm text-slate-600">
        {opp.walk_minutes} min walk · {opp.travel_description}
      </p>
      {opp.social_proof?.text && (
        <p className="mt-2 text-sm text-slate-500">{opp.social_proof.text}</p>
      )}
      <p className="mt-1 text-sm font-medium text-slate-700">
        {formatTime(opp.starts_at)} · {opp.venue?.name}
      </p>
      <button
        type="button"
        onClick={onTapToGo}
        className="mt-4 w-full rounded-xl bg-slate-800 px-4 py-3 font-semibold text-white transition hover:bg-slate-700"
      >
        {primaryLabel}
      </button>
    </article>
  );
}
