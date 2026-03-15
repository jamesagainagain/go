"use client";

import { CSSParticleField } from "@/components/CSSParticleField";

interface ParticleFieldProps {
  /** Full-screen background (default) or contained aspect-video box */
  variant?: "fullscreen" | "contained";
}

export function ParticleField({ variant = "fullscreen" }: ParticleFieldProps) {
  const wrapperClass =
    variant === "contained"
      ? "relative aspect-video w-full overflow-hidden rounded-lg"
      : "fixed inset-0 w-full h-full overflow-hidden pointer-events-none z-0";

  return (
    <div className={`${wrapperClass} relative`}>
      <CSSParticleField />
    </div>
  );
}
