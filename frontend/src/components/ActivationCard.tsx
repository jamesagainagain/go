"use client";

import { useState } from "react";
import Link from "next/link";
import type { ActivationCardResponse } from "@/types/api";
import { SocialProof } from "./SocialProof";
import { MapView } from "./MapView";

interface ActivationCardProps {
  activation: ActivationCardResponse;
  userLat?: number;
  userLng?: number;
  onDismiss?: () => void;
  onRespond?: (response: "accepted" | "dismissed" | "expired" | "snoozed") => void;
  compact?: boolean;
}

function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleTimeString(undefined, {
    hour: "numeric",
    minute: "2-digit",
  });
}

function formatCost(pence: number): string {
  if (pence === 0) return "Free";
  return `£${(pence / 100).toFixed(2)}`;
}

function formatLeaveBy(iso: string): string {
  const d = new Date(iso);
  const now = new Date();
  const mins = Math.round((d.getTime() - now.getTime()) / 60000);
  if (mins <= 0) return "Leave now";
  if (mins < 60) return `Leave in ${mins} min`;
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  return m ? `Leave in ${h}h ${m}m` : `Leave in ${h}h`;
}

export function ActivationCard({
  activation,
  userLat,
  userLng,
  onDismiss,
  onRespond,
  compact = false,
}: ActivationCardProps) {
  const [dismissing, setDismissing] = useState(false);
  const { activation_id, opportunity } = activation;
  const opp = opportunity;

  const handleDismiss = () => {
    if (dismissing) return;
    setDismissing(true);
    onRespond?.("dismissed");
    onDismiss?.();
  };

  const handlePrimary = () => {
    if (opp.commitment_action?.type === "deep_link" && opp.commitment_action?.url) {
      window.open(opp.commitment_action.url, "_blank");
    }
    onRespond?.("accepted");
    onDismiss?.();
  };

  const primaryLabel = opp.commitment_action?.label ?? "I'm going";

  return (
    <article
      className="relative overflow-hidden rounded-xl border border-white/10 bg-bg-card"
      role="article"
    >
      <button
        type="button"
        onClick={handleDismiss}
        className="absolute right-2 top-2 z-10 rounded-full p-1.5 text-text-muted transition hover:bg-white/10 hover:text-text-primary"
        aria-label="Dismiss"
      >
        <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <div className="p-4">
        <h2 className="pr-8 text-lg font-semibold text-text-primary">{opp.title}</h2>
        <div className="mt-1 flex flex-wrap gap-x-3 gap-y-0 text-sm text-text-muted">
          <span>{formatTime(opp.starts_at)}</span>
          <span>{opp.venue?.name}</span>
          <span className="text-accent">{formatLeaveBy(opp.leave_by)}</span>
        </div>
        <p className="mt-2 line-clamp-3 text-sm text-text-primary">{opp.body}</p>
        <p className="mt-1 text-sm text-text-muted">{opp.travel_description}</p>
        {opp.social_proof && (
          <div className="mt-2">
            <SocialProof data={opp.social_proof} />
          </div>
        )}
        <p className="mt-2 text-sm font-medium text-text-primary">
          {formatCost(opp.cost_pence)}
        </p>
        {!compact && (
          <div className="mt-3">
            <MapView
              userLat={userLat}
              userLng={userLng}
              venue={opp.venue}
              routePolyline={opp.route_polyline}
              walkMinutes={opp.walk_minutes}
            />
          </div>
        )}
        <div className="mt-4 flex gap-2">
          <button
            type="button"
            onClick={handlePrimary}
            className="flex-1 rounded-xl bg-accent px-4 py-2.5 font-medium text-black transition hover:bg-amber-500"
          >
            {primaryLabel}
          </button>
          <Link
            href={`/activation/${activation_id}`}
            className="rounded-xl border border-white/20 px-4 py-2.5 font-medium text-text-primary transition hover:bg-white/5"
          >
            Details
          </Link>
        </div>
      </div>
    </article>
  );
}
