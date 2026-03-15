"use client";

export function CloseTab() {
  return (
    <div
      className="relative flex flex-1 flex-col items-center justify-center px-6"
      role="tabpanel"
      id="tabpanel-5"
      aria-labelledby="tab-5"
    >
      <div className="ambient-glow-backdrop" />
      <p className="relative z-[1] text-center text-4xl font-semibold text-slate-50 md:text-5xl">
        We&apos;re not competing with loneliness.
      </p>
      <p className="gradient-text-warm relative z-[1] mt-4 text-center text-4xl font-bold md:text-5xl">
        We&apos;re competing with the sofa.
      </p>
      <p className="gradient-text relative z-[1] mt-8 text-xl">
        go! makes leaving it effortless.
      </p>
    </div>
  );
}
