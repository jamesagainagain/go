"use client";

import { useState, useCallback } from "react";
import {
  postActivationsCheck,
  getActivationsCurrent,
  postActivationsRespond,
  postActivationsFeedback,
  getActivationsHistory,
} from "@/lib/api";
import type {
  ActivationCardResponse,
  ActivationCheckResult,
  ActivationRespondRequest,
  FeedbackRequest,
  ActivationHistoryItem,
} from "@/types/api";

export interface UseActivationResult {
  activation: ActivationCardResponse | null;
  loading: boolean;
  error: string | null;
  checkActivation: (lat?: number, lng?: number) => Promise<ActivationCheckResult>;
  getCurrent: () => Promise<ActivationCheckResult>;
  respond: (id: string, response: ActivationRespondRequest["response"]) => Promise<void>;
  submitFeedback: (id: string, data: FeedbackRequest) => Promise<void>;
  clearActivation: () => void;
}

export function useActivation(): UseActivationResult {
  const [activation, setActivation] = useState<ActivationCardResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkActivation = useCallback(
    async (lat?: number, lng?: number): Promise<ActivationCheckResult> => {
      setLoading(true);
      setError(null);
      try {
        const result = await postActivationsCheck(
          lat != null && lng != null ? { lat, lng } : undefined
        );
        if ("activation_id" in result && result.activation_id && result.opportunity) {
          setActivation(result);
        } else {
          setActivation(null);
        }
        return result;
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Activation check failed";
        setError(msg);
        setActivation(null);
        return { activation_id: null, opportunity: null, message: msg };
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const getCurrent = useCallback(async (): Promise<ActivationCheckResult> => {
    setLoading(true);
    setError(null);
    try {
      const result = await getActivationsCurrent();
      if ("activation_id" in result && result.activation_id && result.opportunity) {
        setActivation(result);
      } else {
        setActivation(null);
      }
      return result;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to get activation";
      setError(msg);
      setActivation(null);
      return { activation_id: null, opportunity: null };
    } finally {
      setLoading(false);
    }
  }, []);

  const respond = useCallback(
    async (id: string, response: ActivationRespondRequest["response"]) => {
      await postActivationsRespond(id, { response });
      if (activation?.activation_id === id) {
        setActivation(null);
      }
    },
    [activation?.activation_id]
  );

  const submitFeedback = useCallback(
    async (id: string, data: FeedbackRequest) => {
      await postActivationsFeedback(id, data);
    },
    []
  );

  const clearActivation = useCallback(() => setActivation(null), []);

  return {
    activation,
    loading,
    error,
    checkActivation,
    getCurrent,
    respond,
    submitFeedback,
    clearActivation,
  };
}

export interface UseActivationHistoryResult {
  items: ActivationHistoryItem[];
  total: number;
  loading: boolean;
  error: string | null;
  fetchHistory: (limit?: number, offset?: number) => Promise<void>;
}

export function useActivationHistory(): UseActivationHistoryResult {
  const [items, setItems] = useState<ActivationHistoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = useCallback(
    async (limit = 20, offset = 0) => {
      setLoading(true);
      setError(null);
      try {
        const res = await getActivationsHistory(limit, offset);
        setItems(res.items ?? []);
        setTotal(res.total ?? 0);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load history");
        setItems([]);
        setTotal(0);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return { items, total, loading, error, fetchHistory };
}
