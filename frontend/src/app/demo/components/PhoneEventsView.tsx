"use client";

import Image from "next/image";
import { useState } from "react";
import { RECOMMENDED_EVENTS, LONDON_EVENTS } from "@/lib/mock-data";
import { GoEventMap } from "@/components/GoEventMap";

const CATEGORY_COLORS: Record<string, string> = {
  art: "#a78bfa",
  sport: "#34d399",
  music: "#f472b6",
  food: "#fb923c",
  social: "#60a5fa",
  nature: "#4ade80",
  study: "#94a3b8",
  nightlife: "#c084fc",
  wellness: "#2dd4bf",
  comedy: "#fbbf24",
  tech: "#38bdf8",
};

export function PhoneEventsView() {
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);

  return (
    <div className="flex h-full w-full flex-col bg-[#06060c]">
      {/* Status bar */}
      <div className="flex items-center justify-between px-5 pt-10 text-[10px] text-white/50">
        <span>5:46 PM</span>
        <div className="flex items-center gap-1">
          <span>5G</span>
          <svg className="h-3 w-3" viewBox="0 0 24 24" fill="currentColor">
            <path d="M15.67 4H14V2h-4v2H8.33C7.6 4 7 4.6 7 5.33v15.34C7 21.4 7.6 22 8.33 22h7.34c.73 0 1.33-.6 1.33-1.33V5.33C17 4.6 16.4 4 15.67 4z" />
          </svg>
        </div>
      </div>

      {/* go! header */}
      <div className="flex items-center gap-2.5 border-b border-white/5 px-4 py-2.5">
        <Image
          src="/icon.svg"
          alt="go!"
          width={28}
          height={28}
          className="h-7 w-7 shrink-0 rounded-lg object-contain"
        />
        <span className="text-base font-semibold tracking-tight text-white">
          go!
        </span>
        <span className="ml-auto text-[11px] text-white/40">
          Tuesday evening
        </span>
      </div>

      {/* Content */}
      <div className="flex min-h-0 flex-1 flex-col p-4 pb-6">
        {/* Greeting */}
        <div className="mb-3">
          <h2 className="text-lg font-bold text-white">
            Hey! 5 events for you right now
          </h2>
          <p className="mt-0.5 text-[11px] text-white/50">
            Based on your interests - all within 15 min walk
          </p>
        </div>

        {/* Event cards */}
        <div className="min-h-0 flex-1 space-y-2.5 overflow-y-auto pr-1">
          {RECOMMENDED_EVENTS.map((event) => (
            <button
              key={event.id}
              type="button"
              onClick={() =>
                setSelectedEventId(
                  selectedEventId === event.id ? null : event.id
                )
              }
              className="w-full rounded-xl border border-white/[0.08] bg-[#1c1c2e] p-3 text-left transition-all hover:border-white/15 hover:bg-[#24243a]"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <div className="mb-0.5 flex items-center gap-1.5">
                    <div
                      className="h-2 w-2 shrink-0 rounded-full"
                      style={{
                        backgroundColor: CATEGORY_COLORS[event.category],
                      }}
                    />
                    <span className="text-[9px] font-medium uppercase tracking-wider text-white/40">
                      {event.category}
                    </span>
                  </div>
                  <h3 className="text-[13px] font-semibold leading-tight text-white">
                    {event.title}
                  </h3>
                  <p className="mt-0.5 line-clamp-1 text-[11px] text-white/40">
                    {event.description}
                  </p>
                </div>
                <div className="shrink-0 text-right">
                  <span className="text-[11px] font-medium text-slate-300">
                    {event.time}
                  </span>
                  <p className="mt-0.5 text-[9px] text-white/30">
                    {event.venue}
                  </p>
                </div>
              </div>

              {selectedEventId === event.id && (
                <div className="mt-2.5 flex gap-2 border-t border-white/5 pt-2.5">
                  <button
                    type="button"
                    className="flex-1 rounded-lg border border-white/20 bg-white/10 py-1.5 text-[11px] font-semibold text-white hover:bg-white/15"
                    onClick={(e) => e.stopPropagation()}
                  >
                    Hold my spot
                  </button>
                  <button
                    type="button"
                    className="rounded-lg border border-white/15 px-3 py-1.5 text-[11px] text-white/70 hover:bg-white/5"
                    onClick={(e) => e.stopPropagation()}
                  >
                    Details
                  </button>
                </div>
              )}
            </button>
          ))}
        </div>

        {/* Map */}
        <div className="mt-3 shrink-0">
          <h3 className="mb-2 text-xs font-medium text-white/70">
            Explore nearby
          </h3>
          <div className="h-[180px] overflow-hidden rounded-xl border border-white/10">
            <GoEventMap
              events={LONDON_EVENTS}
              selectedEventId={selectedEventId ?? undefined}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
