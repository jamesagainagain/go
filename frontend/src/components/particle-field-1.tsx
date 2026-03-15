"use client";

import dynamic from "next/dynamic";

const Scene = dynamic(
  () =>
    import("@/components/mock-uis/ParticleFieldScene").then((m) => m.ParticleFieldScene),
  { ssr: false }
);

export function ParticleField() {
  return (
    <div className="fixed inset-0 w-full h-full overflow-hidden pointer-events-none z-0">
      <Scene />
    </div>
  );
}
