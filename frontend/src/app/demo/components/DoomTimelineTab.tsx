"use client";

const TIMELINE: { time: string; description: string }[] = [
  { time: "5:45pm", description: "Close laptop, pick up phone" },
  { time: "5:47pm", description: "Start scrolling" },
  { time: "6:15pm", description: "Still scrolling" },
  { time: "7:30pm", description: "Still scrolling" },
  { time: "8:00pm", description: "Order Deliveroo" },
  { time: "10:00pm", description: "Go to bed. Nothing happened." },
];

export function DoomTimelineTab() {
  return (
    <div
      className="flex flex-1 flex-col items-center justify-center overflow-y-auto px-6 py-12"
      role="tabpanel"
      id="tabpanel-2"
      aria-labelledby="tab-2"
    >
      <div className="relative flex max-w-xl flex-col gap-6">
        {/* Gradient timeline connector */}
        <div
          className="absolute left-[2.5rem] top-2 bottom-2 w-px"
          style={{
            background:
              "linear-gradient(to bottom, hsl(27deg 93% 60% / 0.3), #00a6ff30, #ff005630, #6500ff30, transparent)",
          }}
        />
        {TIMELINE.map(({ time, description }) => (
          <div key={time} className="relative flex gap-6">
            <span className="gradient-text w-20 shrink-0 text-lg font-medium">
              {time}
            </span>
            <span className="text-xl text-slate-500">{description}</span>
          </div>
        ))}
      </div>
      <p className="mt-12 max-w-xl text-center text-lg text-slate-600">
        As work compresses, there will be more of this time. Not less.
      </p>
    </div>
  );
}
