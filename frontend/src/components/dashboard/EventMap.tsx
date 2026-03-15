"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { LONDON_EVENTS } from "@/lib/mock-data";

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN;

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

interface EventMapProps {
  expanded?: boolean;
  onExpand?: () => void;
  onCollapse?: () => void;
}

export function EventMap({
  expanded = false,
  onExpand,
  onCollapse,
}: EventMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const markersRef = useRef<mapboxgl.Marker[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<typeof LONDON_EVENTS[0] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!MAPBOX_TOKEN) {
      setError("Mapbox token not configured");
      return;
    }
    if (!containerRef.current) return;

    mapboxgl.accessToken = MAPBOX_TOKEN;

    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: "mapbox://styles/mapbox/dark-v11",
      center: [-0.09, 51.505],
      zoom: 12,
    });

    mapRef.current = map;

    return () => {
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !MAPBOX_TOKEN) return;

    const loadMarkers = () => {
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];

      LONDON_EVENTS.forEach((event) => {
        const color = CATEGORY_COLORS[event.category] ?? "#f59e0b";
        const el = document.createElement("div");
        el.className = "event-dot";
        el.style.width = "12px";
        el.style.height = "12px";
        el.style.borderRadius = "50%";
        el.style.backgroundColor = color;
        el.style.border = "2px solid white";
        el.style.cursor = "pointer";
        el.style.boxShadow = "0 0 8px rgba(0,0,0,0.3)";

        const marker = new mapboxgl.Marker(el)
          .setLngLat([event.lng, event.lat])
          .setPopup(
            new mapboxgl.Popup({ offset: 15 }).setHTML(
              `<div class="text-sm font-medium">${event.title}</div><div class="text-xs text-gray-500">${event.time}</div>`
            )
          )
          .addTo(map);

        el.addEventListener("click", () => setSelectedEvent(event));
        markersRef.current.push(marker);
      });
    };

    if (map.loaded()) {
      loadMarkers();
    } else {
      map.once("load", loadMarkers);
    }
  }, [expanded]);

  if (error) {
    return (
      <div
        className="rounded-xl bg-bg-card border border-white/10 flex items-center justify-center p-8 text-text-muted"
        style={{ minHeight: expanded ? 400 : 160 }}
      >
        {error}
      </div>
    );
  }

  return (
    <div className="px-4 pb-4">
      <motion.div
        layout
        className="relative rounded-xl overflow-hidden border border-white/10"
        style={{
          height: expanded ? 400 : 160,
        }}
      >
        <div ref={containerRef} className="absolute inset-0 w-full h-full" />
        {!expanded && (
          <button
            type="button"
            onClick={onExpand}
            className="absolute inset-0 flex items-center justify-center bg-black/20 hover:bg-black/30 transition-colors"
            aria-label="Expand map"
          >
            <span className="text-sm text-white/80 font-medium">
              Tap to expand map
            </span>
          </button>
        )}
        {expanded && onCollapse && (
          <button
            type="button"
            onClick={onCollapse}
            className="absolute top-2 right-2 z-10 w-8 h-8 rounded-full bg-black/60 flex items-center justify-center text-white hover:bg-black/80"
            aria-label="Close map"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </motion.div>

      <AnimatePresence>
        {selectedEvent && expanded && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="mt-2 p-3 rounded-xl bg-bg-card border border-white/10"
          >
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-medium text-text-primary">{selectedEvent.title}</h4>
                <p className="text-sm text-text-muted">{selectedEvent.time}</p>
              </div>
              <button
                type="button"
                onClick={() => setSelectedEvent(null)}
                className="text-text-muted hover:text-text-primary"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
