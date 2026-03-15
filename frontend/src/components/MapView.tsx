"use client";

import { useEffect, useRef, useState } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import type { VenueSummary } from "@/types/api";

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN;

interface MapViewProps {
  userLat?: number;
  userLng?: number;
  venue?: VenueSummary | null;
  routePolyline?: string | null;
  walkMinutes?: number;
  className?: string;
}

export function MapView({
  userLat,
  userLng,
  venue,
  routePolyline,
  walkMinutes,
  className = "",
}: MapViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const markersRef = useRef<mapboxgl.Marker[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!MAPBOX_TOKEN) {
      setError("Mapbox token not configured");
      return;
    }
    if (!containerRef.current) return;

    mapboxgl.accessToken = MAPBOX_TOKEN;

    const centerLng = venue?.lng ?? userLng ?? -0.1276;
    const centerLat = venue?.lat ?? userLat ?? 51.5074;

    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: "mapbox://styles/mapbox/dark-v11",
      center: [centerLng, centerLat],
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
    // eslint-disable-next-line react-hooks/exhaustive-deps -- map init runs once on mount
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !MAPBOX_TOKEN) return;

    // Clear existing markers
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    // User location (blue dot)
    if (userLat != null && userLng != null) {
      const m = new mapboxgl.Marker({ color: "#3b82f6" })
        .setLngLat([userLng, userLat])
        .addTo(map);
      markersRef.current.push(m);
    }

    // Venue pin
    if (venue?.lat != null && venue?.lng != null) {
      const m = new mapboxgl.Marker({ color: "#f59e0b" })
        .setLngLat([venue.lng, venue.lat])
        .setPopup(
          new mapboxgl.Popup().setHTML(
            `<strong>${venue.name ?? "Venue"}</strong>${venue.address ? `<br/>${venue.address}` : ""}`
          )
        )
        .addTo(map);
      markersRef.current.push(m);
    }

    // Fit bounds to show both user and venue
    if (
      userLat != null &&
      userLng != null &&
      venue?.lat != null &&
      venue?.lng != null
    ) {
      const bounds = new mapboxgl.LngLatBounds(
        [userLng, userLat],
        [venue.lng, venue.lat]
      );
      map.fitBounds(bounds, { padding: 60 });
    } else if (venue?.lat != null && venue?.lng != null) {
      map.flyTo({ center: [venue.lng, venue.lat], zoom: 15 });
    }

    // Route polyline
    if (routePolyline) {
      const setupRoute = () => {
        try {
          const coordinates = decodePolyline(routePolyline!);
          if (coordinates.length < 2) return;

          const bounds = coordinates.reduce(
            (acc, [lng, lat]) => acc.extend([lng, lat]),
            new mapboxgl.LngLatBounds(coordinates[0], coordinates[0])
          );
          map.fitBounds(bounds, { padding: 50 });

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
                "line-color": "#ea580c",
                "line-width": 4,
              },
            });
          }
        } catch {
          // Ignore polyline decode errors
        }
      };

      if (map.loaded()) {
        setupRoute();
      } else {
        map.once("load", setupRoute);
      }
    }
  }, [userLat, userLng, venue, routePolyline]);

  if (error) {
    return (
      <div
        className={`flex items-center justify-center rounded-xl bg-bg-card border border-white/10 p-8 text-text-muted ${className}`}
      >
        {error}
        {walkMinutes != null && (
          <span className="ml-2">~{walkMinutes} min walk</span>
        )}
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      <div ref={containerRef} className="h-48 w-full rounded-xl overflow-hidden" />
      {walkMinutes != null && (
        <div className="absolute bottom-2 left-2 rounded-lg bg-black/60 px-2 py-1 text-sm font-medium text-white">
          ~{walkMinutes} min walk
        </div>
      )}
    </div>
  );
}

function decodePolyline(encoded: string): [number, number][] {
  const points: [number, number][] = [];
  let index = 0;
  let lat = 0;
  let lng = 0;

  while (index < encoded.length) {
    let b: number;
    let shift = 0;
    let result = 0;
    do {
      b = encoded.charCodeAt(index++) - 63;
      result |= (b & 0x1f) << shift;
      shift += 5;
    } while (b >= 0x20);
    const dlat = (result & 1) ? ~(result >> 1) : result >> 1;
    lat += dlat;

    shift = 0;
    result = 0;
    do {
      b = encoded.charCodeAt(index++) - 63;
      result |= (b & 0x1f) << shift;
      shift += 5;
    } while (b >= 0x20);
    const dlng = (result & 1) ? ~(result >> 1) : result >> 1;
    lng += dlng;

    points.push([lng / 1e5, lat / 1e5]);
  }

  return points;
}
