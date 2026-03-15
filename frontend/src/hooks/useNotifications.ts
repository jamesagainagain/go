"use client";

import { useState, useCallback, useEffect } from "react";
import {
  isPushSupported,
  getPermissionState,
  requestPermission,
  subscribeToPush,
  registerServiceWorker,
  type PushPermissionState,
} from "@/lib/push";

export interface UseNotificationsResult {
  supported: boolean;
  permission: PushPermissionState;
  subscribed: boolean;
  loading: boolean;
  error: string | null;
  requestAndSubscribe: () => Promise<boolean>;
  checkPermission: () => PushPermissionState;
}

export function useNotifications(): UseNotificationsResult {
  const [supported] = useState(isPushSupported);
  const [permission, setPermission] = useState<PushPermissionState>("prompt");
  const [subscribed, setSubscribed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkPermission = useCallback((): PushPermissionState => {
    const state = getPermissionState();
    setPermission(state);
    return state;
  }, []);

  useEffect(() => {
    if (supported) {
      setPermission(getPermissionState());
    }
  }, [supported]);

  const requestAndSubscribe = useCallback(async (): Promise<boolean> => {
    if (!supported) {
      setError("Push notifications not supported");
      return false;
    }
    setLoading(true);
    setError(null);
    try {
      const ok = await subscribeToPush();
      setSubscribed(ok);
      setPermission(getPermissionState());
      return ok;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to subscribe";
      setError(msg);
      return false;
    } finally {
      setLoading(false);
    }
  }, [supported]);

  return {
    supported,
    permission,
    subscribed,
    loading,
    error,
    requestAndSubscribe,
    checkPermission,
  };
}
