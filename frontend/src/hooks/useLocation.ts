"use client";

import { useState, useEffect, useCallback } from "react";
import { getCurrentPosition, type GeoPosition, type GeoError } from "@/lib/geo";
import { postUsersMeLocation } from "@/lib/api";

export interface UseLocationResult {
  position: GeoPosition | null;
  loading: boolean;
  error: GeoError | null;
  refresh: () => Promise<void>;
  updateBackend: (pos: GeoPosition) => Promise<void>;
}

export function useLocation(syncToBackend = false): UseLocationResult {
  const [position, setPosition] = useState<GeoPosition | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<GeoError | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const pos = await getCurrentPosition();
      setPosition(pos);
      if (syncToBackend) {
        await postUsersMeLocation({ lat: pos.lat, lng: pos.lng });
      }
    } catch (err) {
      setError(err as GeoError);
      setPosition(null);
    } finally {
      setLoading(false);
    }
  }, [syncToBackend]);

  const updateBackend = useCallback(async (pos: GeoPosition) => {
    await postUsersMeLocation({ lat: pos.lat, lng: pos.lng });
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { position, loading, error, refresh, updateBackend };
}
