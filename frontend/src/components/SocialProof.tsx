"use client";

import type { SocialProof as SocialProofType } from "@/types/api";

interface SocialProofProps {
  data?: SocialProofType | null;
  className?: string;
}

export function SocialProof({ data, className = "" }: SocialProofProps) {
  if (!data?.text) return null;

  return (
    <div
      className={`inline-flex items-center gap-1.5 rounded-full bg-accent/20 px-3 py-1 text-sm text-accent ${className}`}
      role="status"
    >
      <span aria-hidden>👥</span>
      <span>{data.text}</span>
      {data.familiar_face && (
        <span className="text-accent" title="Someone you know is going">
          ✓
        </span>
      )}
    </div>
  );
}
