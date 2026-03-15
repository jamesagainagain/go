import Link from "next/link";

export default function Page() {
  return (
    <div className="ambient-bg min-h-screen flex flex-col items-center justify-center px-6">
      <main className="relative z-10 flex flex-col items-center text-center max-w-2xl">
        <h1 className="text-5xl md:text-6xl font-bold text-white tracking-tight">
          FirstMove
        </h1>
        <p className="mt-6 text-lg md:text-xl text-text-muted leading-relaxed">
          The gap between &quot;I could&quot; and &quot;I am&quot; has seven
          friction points. We collapse them to one.
        </p>
        <Link
          href="/setup"
          className="mt-10 inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-black bg-accent rounded-xl transition-all duration-300 hover:shadow-[0_0_30px_var(--accent-glow)] hover:scale-[1.02]"
        >
          Get Started
        </Link>
      </main>
    </div>
  );
}
