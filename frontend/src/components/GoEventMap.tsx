"use client";

import { useEffect, useRef } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import type { MapEvent } from "@/lib/mock-data";

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

interface GoEventMapProps {
  events: MapEvent[];
  selectedEventId?: string;
}

export function GoEventMap({ events, selectedEventId }: GoEventMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const markersRef = useRef<mapboxgl.Marker[]>([]);

  useEffect(() => {
    if (!MAPBOX_TOKEN || !containerRef.current) return;

    mapboxgl.accessToken = MAPBOX_TOKEN;

    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: "mapbox://styles/mapbox/dark-v11",
      center: [-0.1, 51.513],
      zoom: 12.5,
      attributionControl: false,
    });

    mapRef.current = map;

    map.on("load", () => {
      events.forEach((event) => {
        const el = document.createElement("div");
        const isSelected = event.id === selectedEventId;
        const size = isSelected ? 16 : 10;
        el.style.width = `${size}px`;
        el.style.height = `${size}px`;
        el.style.borderRadius = "50%";
        el.style.backgroundColor = CATEGORY_COLORS[event.category] ?? "#f59e0b";
        el.style.border = isSelected ? "2px solid white" : "2px solid rgba(255,255,255,0.3)";
        el.style.boxShadow = `0 0 ${isSelected ? 12 : 6}px ${CATEGORY_COLORS[event.category] ?? "#f59e0b"}80`;
        el.style.cursor = "pointer";
        el.style.transition = "all 0.2s";

        const popup = new mapboxgl.Popup({
          offset: 15,
          closeButton: false,
          maxWidth: "220px",
        }).setHTML(
          `<div style="font-family:Inter,sans-serif;padding:4px">
            <strong style="font-size:13px">${event.title}</strong>
            <div style="font-size:11px;color:#999;margin-top:2px">${event.venue} · ${event.time}</div>
          </div>`
        );

        const marker = new mapboxgl.Marker({ element: el })
          .setLngLat([event.lng, event.lat])
          .setPopup(popup)
          .addTo(map);

        markersRef.current.push(marker);
      });
    });

    return () => {
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];
      map.remove();
      mapRef.current = null;
    };
  }, [events, selectedEventId]);

  if (!MAPBOX_TOKEN) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-[#1c1c2e] text-white/40 text-sm">
        Map unavailable - add NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN
      </div>
    );
  }

  return <div ref={containerRef} className="w-full h-full" />;
}
