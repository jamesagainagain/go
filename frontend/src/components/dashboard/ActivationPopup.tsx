"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import type { ActivationCardResponse } from "@/types/api";
import { SocialProof } from "../SocialProof";

interface ActivationPopupProps {
  activation: ActivationCardResponse | null;
  onDismiss?: () => void;
  onAccept?: () => void;
  visible: boolean;
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

export function ActivationPopup({
  activation,
  onDismiss,
  onAccept,
  visible,
}: ActivationPopupProps) {
  const [accepted, setAccepted] = useState(false);

  if (!activation) return null;

  const opp = activation.opportunity;
  const primaryLabel = opp.commitment_action?.label ?? "Hold my spot";

  const handleAccept = () => {
    setAccepted(true);
    onAccept?.();
  };

  if (accepted) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="fixed inset-x-0 bottom-0 p-4 pb-8 bg-bg-phone"
      >
        <div className="rounded-2xl bg-accent/20 border border-accent/40 p-6 text-center">
          <div className="w-12 h-12 rounded-full bg-accent/30 flex items-center justify-center mx-auto mb-3">
            <svg
              className="w-6 h-6 text-accent"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <h3 className="font-semibold text-text-primary">You&apos;re going!</h3>
          <p className="text-sm text-text-muted mt-1">{opp.title}</p>
        </div>
      </motion.div>
    );
  }

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ y: "100%" }}
          animate={{ y: 0 }}
          exit={{ y: "100%" }}
          transition={{ type: "spring", damping: 25, stiffness: 300 }}
          className="fixed inset-x-0 bottom-0 rounded-t-2xl bg-bg-card border-t border-white/10 shadow-2xl overflow-hidden"
        >
          <div className="p-4 pb-8 max-h-[70vh] overflow-y-auto">
            <button
              type="button"
              onClick={onDismiss}
              className="absolute right-4 top-4 text-text-muted hover:text-text-primary"
              aria-label="Dismiss"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <h2 className="text-lg font-semibold text-text-primary pr-8">
              {opp.title}
            </h2>
            <div className="mt-1 flex flex-wrap gap-x-3 text-sm text-text-muted">
              <span>{formatTime(opp.starts_at)}</span>
              <span>{opp.venue?.name}</span>
              <span className="text-accent">{formatCost(opp.cost_pence)}</span>
            </div>
            <p className="mt-2 text-sm text-text-primary leading-relaxed">
              {opp.body}
            </p>
            <p className="mt-1 text-sm text-text-muted flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              {opp.travel_description}
            </p>
            {opp.social_proof && (
              <div className="mt-2">
                <SocialProof data={opp.social_proof} />
              </div>
            )}
            <p className="mt-2 text-sm font-medium text-accent">
              Leave by {formatTime(opp.leave_by)}
            </p>
            <div className="mt-4 flex flex-col gap-2">
              <button
                type="button"
                onClick={handleAccept}
                className="w-full py-3 rounded-xl bg-accent text-black font-semibold hover:bg-amber-500 transition-colors"
              >
                {primaryLabel}
              </button>
              <Link
                href={`/activation/${activation.activation_id}`}
                className="block text-center text-sm text-text-muted hover:text-text-primary"
              >
                Details
              </Link>
              <button
                type="button"
                onClick={onDismiss}
                className="text-sm text-text-muted hover:text-text-primary"
              >
                Not tonight
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
