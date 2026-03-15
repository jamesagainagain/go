import Link from "next/link";

export default function Page() {
  return (
    <div className="demo-bg fixed inset-0 flex flex-col items-center justify-center">
      <div className="ambient-glow-backdrop" />

      <div className="relative z-[1] flex flex-col items-center text-center">
        <div className="glow-box rounded-2xl px-16 py-12">
          <h1 className="wordmark-safe gradient-text-bright text-7xl font-bold tracking-tight md:text-8xl">
            go!
          </h1>
        </div>

        <p className="mt-6 text-xl text-slate-400">Screen to street.</p>

        <div className="mt-12 flex items-center gap-6">
          <div className="glow-box-subtle rounded-xl opacity-50 cursor-not-allowed">
            <span className="relative z-[1] block rounded-xl bg-[#1e1e24] px-8 py-4 text-lg font-semibold text-slate-400">
              Install go!
            </span>
          </div>

          <Link href="/demo">
            <div className="glow-box rounded-xl">
              <span className="relative z-[1] block rounded-xl bg-[#1e1e24] px-8 py-4 text-lg font-semibold text-white transition-colors hover:text-white/90">
                go! DEMO
              </span>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}
