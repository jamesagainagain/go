"use client";

export function TitleTab() {
  return (
    <div
      className="flex flex-1 flex-col items-center justify-center px-6"
      role="tabpanel"
      id="tabpanel-0"
      aria-labelledby="tab-0"
    >
      <div className="glow-box rounded-2xl px-16 py-12">
        <h1 className="wordmark-safe gradient-text-bright text-7xl font-bold tracking-tight md:text-8xl">
          go!
        </h1>
      </div>
      <p className="mt-6 text-xl text-slate-400">Screen to street.</p>
    </div>
  );
}
