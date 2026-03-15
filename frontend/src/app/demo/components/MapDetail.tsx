"use client";

import { useEffect, useRef, useState } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import type { Opportunity } from "@/types/api";

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN;
const USER_LAT = 51.5274;
const USER_LNG = -0.0777;

function formatLeaveBy(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleTimeString(undefined, {
    hour: "numeric",
    minute: "2-digit",
  });
}

interface MapDetailProps {
  opportunity: Opportunity;
  className?: string;
}

export function MapDetail({ opportunity, className = "" }: MapDetailProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const markersRef = useRef<mapboxgl.Marker[]>([]);
  const [error, setError] = useState<string | null>(null);

  const venue = opportunity.venue;
  const destLat = venue?.lat ?? 51.5255;
  const destLng = venue?.lng ?? -0.0775;

  useEffect(() => {
    if (!MAPBOX_TOKEN) {
      setError("Mapbox token not configured");
      return;
    }
    if (!containerRef.current) return;

    mapboxgl.accessToken = MAPBOX_TOKEN;

    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: "mapbox://styles/mapbox/light-v11",
      center: [USER_LNG, USER_LAT],
      zoom: 14,
      attributionControl: false,
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

    // Clear markers
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    // User location (blue dot)
    const userMarker = new mapboxgl.Marker({ color: "#3b82f6" })
      .setLngLat([USER_LNG, USER_LAT])
      .addTo(map);
    markersRef.current.push(userMarker);

    // Venue pin
    const venueMarker = new mapboxgl.Marker({ color: "#64748b" })
      .setLngLat([destLng, destLat])
      .addTo(map);
    markersRef.current.push(venueMarker);

    // Fetch walking route from Mapbox Directions API
    const url = `https://api.mapbox.com/directions/v5/mapbox/walking/${USER_LNG},${USER_LAT};${destLng},${destLat}?geometries=geojson&access_token=${MAPBOX_TOKEN}`;

    fetch(url)
      .then((res) => res.json())
      .then((data) => {
        const route = data.routes?.[0];
        if (!route?.geometry?.coordinates?.length) return;

        const coordinates = route.geometry.coordinates as [number, number][];

        const setupRoute = () => {
          if (map.getSource("route")) {
            (map.getSource("route") as mapboxgl.GeoJSONSource).setData({
              type: "Feature",
              properties: {},
              geometry: {
                type: "LineString",
                coordinates,
              },
            });
          } else {
            map.addSource("route", {
              type: "geojson",
              data: {
                type: "Feature",
                properties: {},
                geometry: {
                  type: "LineString",
                  coordinates,
                },
              },
            });
            map.addLayer({
              id: "route",
              type: "line",
              source: "route",
              layout: {
                "line-join": "round",
                "line-cap": "round",
              },
              paint: {
                "line-color": "#64748b",
                "line-width": 4,
              },
            });
          }

          const bounds = coordinates.reduce(
            (acc, [lng, lat]) => acc.extend([lng, lat]),
            new mapboxgl.LngLatBounds(coordinates[0], coordinates[0])
          );
          map.fitBounds(bounds, { padding: 40 });
        };

        if (map.loaded()) {
          setupRoute();
        } else {
          map.once("load", setupRoute);
        }
      })
      .catch(() => {
        setError("Could not load route");
      });
  }, [destLat, destLng]);

  if (error) {
    return (
      <div
        className={`flex flex-col items-center justify-center bg-slate-100 p-6 text-slate-600 ${className}`}
      >
        <p>{error}</p>
        <p className="mt-2 text-sm font-medium text-slate-700">
          Leave by {formatLeaveBy(opportunity.leave_by)}
        </p>
      </div>
    );
  }

  return (
    <div className={`relative h-full w-full ${className}`}>
      <div ref={containerRef} className="h-full w-full" />
      <div className="absolute left-2 top-2 rounded-lg bg-black/60 px-2 py-1 text-sm font-medium text-white">
        {opportunity.social_proof?.text}
      </div>
      <div className="absolute bottom-2 left-2 rounded-lg bg-black/60 px-2 py-1 text-sm font-medium text-white">
        Leave by {formatLeaveBy(opportunity.leave_by)}
      </div>
    </div>
  );
}
