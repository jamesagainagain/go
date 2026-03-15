"use client";

const TIMELINE: { time: string; description: string }[] = [
  { time: "5:45pm", description: "Close laptop, pick up phone" },
  { time: "6:45pm", description: "Start scrolling" },
  { time: "7:45pm", description: "Still scrolling" },
  { time: "8:45pm", description: "Still scrolling" },
  { time: "9:45pm", description: "Order Deliveroo" },
  { time: "10:45pm", description: "Go to bed. Nothing happened." },
];

export function DoomTimelineTab() {
  return (
    <div
      className="flex flex-1 flex-col items-center justify-center overflow-y-auto px-6 py-12"
      role="tabpanel"
      id="tabpanel-1"
      aria-labelledby="tab-1"
    >
      <div className="relative flex max-w-xl flex-col">
        <div
          className="absolute left-[1.25rem] top-3 bottom-3 w-px opacity-40"
          style={{
            background:
              "linear-gradient(to bottom, hsl(27deg 93% 60%), #00a6ff, #ff0056, #6500ff, transparent)",
          }}
        />
        {TIMELINE.map(({ time, description }, i) => (
          <div key={`${time}-${i}`} className="relative flex items-center gap-4 py-3">
            <div className="flex w-10 shrink-0 items-center justify-center">
              <div className="h-2 w-2 shrink-0 rounded-full bg-stone-400" />
            </div>
            <span className="w-16 shrink-0 text-sm font-medium text-stone-500">
              {time}
            </span>
            <span className="text-lg text-stone-600">{description}</span>
          </div>
        ))}
      </div>
      <p className="mt-12 max-w-xl text-center text-stone-600">
        As work compresses, there will be more of this time. Not less.
      </p>
    </div>
  );
}
