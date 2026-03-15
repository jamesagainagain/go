"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { IPadStatusBar } from "./iPadStatusBar";
import { useEventsNearby } from "@/hooks/useEventsNearby";
import type { MapEvent } from "@/lib/mock-data";
import { GoEventMap } from "./GoEventMap";

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

interface GoAppViewProps {
  mode: "setup" | "events";
  setupContent?: React.ReactNode;
  onSetupComplete?: () => void;
}

export function GoAppView({ mode, setupContent, onSetupComplete }: GoAppViewProps) {
  const [selectedEvent, setSelectedEvent] = useState<MapEvent | null>(null);
  const [mapExpanded, setMapExpanded] = useState(false);
  const { events } = useEventsNearby();
  const recommendedEvents = events.slice(0, 5);

  return (
    <div className="w-full h-full flex flex-col bg-[#06060c]">
      <IPadStatusBar time="5:45 PM" />

      {/* go! header */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-white/5">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#f59e0b] to-[#d97706] flex items-center justify-center">
            <span className="text-white text-xs font-bold">go!</span>
          </div>
          <span className="text-white text-lg font-semibold tracking-tight">go!</span>
        </div>
        {mode === "events" && (
          <span className="text-white/40 text-sm">Tuesday evening</span>
        )}
      </div>

      {/* Content area */}
      <div className="flex-1 overflow-y-auto">
        {mode === "setup" ? (
          <div className="p-5">
            <h2 className="text-xl font-bold text-white mb-1">
              Tell us about you
            </h2>
            <p className="text-white/50 text-sm mb-5">
              Pick how you&apos;d like to share - questions, chat, or voice.
            </p>
            {setupContent}
            {onSetupComplete && (
              <div className="mt-6 pb-4">
                <button
                  type="button"
                  onClick={onSetupComplete}
                  className="w-full rounded-xl bg-gradient-to-r from-[#f59e0b] to-[#d97706] px-6 py-3.5 text-base font-semibold text-black transition-all hover:shadow-lg hover:shadow-amber-500/20 active:scale-[0.98]"
                >
                  Continue
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="p-5 space-y-4">
            {/* Greeting */}
            <div className="mb-2">
              <h2 className="text-2xl font-bold text-white">
                Hey! 5 events for you right now
              </h2>
              <p className="text-white/50 text-sm mt-1">
                Based on your interests - all within 15 min walk
              </p>
            </div>

            {/* Event cards */}
            <div className="space-y-3">
              {recommendedEvents.map((event) => (
                <motion.button
                  key={event.id}
                  type="button"
                  onClick={() => setSelectedEvent(selectedEvent?.id === event.id ? null : event)}
                  className="w-full text-left rounded-xl border border-white/8 bg-[#1c1c2e] p-4 transition-all hover:border-white/15 hover:bg-[#24243a]"
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <div
                          className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                          style={{ backgroundColor: CATEGORY_COLORS[event.category] }}
                        />
                        <span className="text-[11px] uppercase tracking-wider text-white/40 font-medium">
                          {event.category}
                        </span>
                      </div>
                      <h3 className="text-white font-semibold text-[15px] leading-tight">
                        {event.title}
                      </h3>
                      <p className="text-white/40 text-sm mt-1 line-clamp-2">
                        {event.description}
                      </p>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <span className="text-amber-400 text-sm font-medium">
                        {event.time}
                      </span>
                      <p className="text-white/30 text-xs mt-0.5">{event.venue}</p>
                    </div>
                  </div>

                  <AnimatePresence>
                    {selectedEvent?.id === event.id && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden"
                      >
                        <div className="mt-3 pt-3 border-t border-white/5 flex gap-2">
                          <button
                            type="button"
                            className="flex-1 rounded-lg bg-gradient-to-r from-[#f59e0b] to-[#d97706] py-2 text-sm font-semibold text-black"
                            onClick={(e) => e.stopPropagation()}
                          >
                            Hold my spot
                          </button>
                          <button
                            type="button"
                            className="rounded-lg border border-white/15 px-4 py-2 text-sm text-white/70 hover:bg-white/5"
                            onClick={(e) => e.stopPropagation()}
                          >
                            Details
                          </button>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.button>
              ))}
            </div>

            {/* Map section */}
            <div className="mt-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-white/70 text-sm font-medium">
                  Explore nearby
                </h3>
                <button
                  type="button"
                  onClick={() => setMapExpanded(!mapExpanded)}
                  className="text-amber-400 text-xs hover:text-amber-300"
                >
                  {mapExpanded ? "Collapse" : "Expand map"}
                </button>
              </div>
              <motion.div
                animate={{ height: mapExpanded ? 380 : 200 }}
                transition={{ duration: 0.3, ease: "easeInOut" }}
                className="rounded-xl overflow-hidden border border-white/10"
              >
                <GoEventMap events={events} selectedEventId={selectedEvent?.id} />
              </motion.div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
