"use client";

import { useState, useEffect, useCallback } from "react";
import { getEventsNearby } from "@/lib/api";
import { eventSummaryToMapEvent } from "@/lib/event-mappers";
import type { MapEvent } from "@/lib/mock-data";
import { LONDON_EVENTS } from "@/lib/mock-data";

const LONDON_LAT = 51.5074;
const LONDON_LNG = -0.1278;

export interface UseEventsNearbyResult {
  events: MapEvent[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function useEventsNearby(
  lat: number = LONDON_LAT,
  lng: number = LONDON_LNG,
  radiusKm = 5,
  limit = 20
): UseEventsNearbyResult {
  const [events, setEvents] = useState<MapEvent[]>(LONDON_EVENTS);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getEventsNearby(lat, lng, radiusKm, limit);
      const mapped = (res.events ?? [])
        .map((e, i) => eventSummaryToMapEvent(e, i))
        .filter((e): e is MapEvent => e !== null);
      setEvents(mapped.length > 0 ? mapped : LONDON_EVENTS);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load events");
      setEvents(LONDON_EVENTS);
    } finally {
      setLoading(false);
    }
  }, [lat, lng, radiusKm, limit]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { events, loading, error, refresh };
}
