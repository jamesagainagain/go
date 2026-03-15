"use client";

import { useCallback, useState } from "react";
import type { ActivationCardResponse, ActivationCheckResult } from "@/types/api";
import { FALLBACK_ACTIVATION } from "../components/fallbackData";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";
const DEMO_LAT = 51.5274;
const DEMO_LNG = -0.0777;
const TIMEOUT_MS = 5000;

export function useActivationCheck() {
  const [activation, setActivation] = useState<ActivationCardResponse | null>(
    null
  );
  const [loading, setLoading] = useState(false);

  const runCheck = useCallback(async () => {
    setLoading(true);
    setActivation(null);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);

    try {
      const token =
        typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      const headers: HeadersInit = {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      };

      const res = await fetch(`${API_BASE}/activations/check`, {
        method: "POST",
        headers,
        body: JSON.stringify({ lat: DEMO_LAT, lng: DEMO_LNG }),
        signal: controller.signal,
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const result: ActivationCheckResult = await res.json();
      if (
        "activation_id" in result &&
        result.activation_id &&
        result.opportunity
      ) {
        setActivation(result);
      } else {
        setActivation(FALLBACK_ACTIVATION);
      }
    } catch {
      setActivation(FALLBACK_ACTIVATION);
    } finally {
      clearTimeout(timeoutId);
      setLoading(false);
    }
  }, []);

  return { activation, loading, runCheck };
}
