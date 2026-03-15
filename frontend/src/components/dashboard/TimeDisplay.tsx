"use client";

export function TimeDisplay() {
  const now = new Date();
  const dayName = now.toLocaleDateString("en-GB", { weekday: "long" });
  const dateStr = now.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "long",
  });

  return (
    <div className="px-6 py-4">
      <div className="flex items-baseline gap-2">
        <span className="text-5xl md:text-6xl font-light text-white tracking-tight">
          3:00
        </span>
        <span className="text-2xl font-light text-text-muted">AM</span>
      </div>
      <p className="mt-1 text-sm text-text-muted">
        {dayName}, {dateStr}
      </p>
      <p className="mt-2 text-accent font-medium">
        Work&apos;s done. Time to live.
      </p>
    </div>
  );
}
