"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ActivationCard } from "@/components/ActivationCard";
import { useActivation } from "@/hooks/useActivation";
import { useLocation } from "@/hooks/useLocation";
import { isAuthenticated } from "@/lib/api";

function formatExpiresAt(iso: string): string {
  const d = new Date(iso);
  const now = new Date();
  const secs = Math.max(0, Math.round((d.getTime() - now.getTime()) / 1000));
  if (secs < 60) return `${secs}s`;
  const mins = Math.floor(secs / 60);
  const s = secs % 60;
  return s ? `${mins}m ${s}s` : `${mins}m`;
}

export default function DashboardPage() {
  const router = useRouter();
  const { position, loading: locationLoading, refresh: refreshLocation } = useLocation(true);
  const {
    activation,
    loading: activationLoading,
    error: activationError,
    checkActivation,
    getCurrent,
    respond,
    clearActivation,
  } = useActivation();

  useEffect(() => {
    if (typeof window !== "undefined" && !isAuthenticated()) {
      router.replace("/");
      return;
    }
  }, [router]);

  useEffect(() => {
    if (!isAuthenticated()) return;
    getCurrent();
  }, []);

  useEffect(() => {
    if (!isAuthenticated() || !position) return;
    checkActivation(position.lat, position.lng);
  }, [position?.lat, position?.lng]);

  const handleDismiss = () => {
    if (activation) {
      respond(activation.activation_id, "dismissed");
    }
    clearActivation();
  };

  const handleRespond = (response: "accepted" | "dismissed" | "expired" | "snoozed") => {
    if (activation) {
      respond(activation.activation_id, response);
    }
    clearActivation();
  };

  if (typeof window !== "undefined" && !isAuthenticated()) {
    return null;
  }

  const loading = locationLoading || activationLoading;

  return (
    <main className="min-h-screen bg-gray-50">
      <header className="sticky top-0 z-20 border-b border-gray-200 bg-white px-4 py-3">
        <div className="mx-auto flex max-w-lg items-center justify-between">
          <h1 className="text-lg font-semibold text-gray-900">FirstMove</h1>
          <nav className="flex gap-4">
            <Link href="/history" className="text-sm text-gray-600 hover:text-gray-900">
              History
            </Link>
            <Link href="/settings" className="text-sm text-gray-600 hover:text-gray-900">
              Settings
            </Link>
          </nav>
        </div>
      </header>

      <div className="mx-auto max-w-lg p-4">
        {loading && !activation && (
          <div className="rounded-lg border border-gray-200 bg-white p-8 text-center">
            <p className="text-gray-500">Checking for opportunities...</p>
          </div>
        )}

        {activationError && !activation && (
          <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">
            {activationError}
          </div>
        )}

        {activation && (
          <div className="space-y-4">
            <div className="flex items-center justify-between text-sm text-gray-500">
              <span>Expires in {formatExpiresAt(activation.expires_at)}</span>
              <button
                type="button"
                onClick={() => refreshLocation()}
                className="text-amber-600 hover:underline"
              >
                Refresh location
              </button>
            </div>
            <ActivationCard
              activation={activation}
              userLat={position?.lat}
              userLng={position?.lng}
              onDismiss={handleDismiss}
              onRespond={handleRespond}
            />
          </div>
        )}

        {!loading && !activation && !activationError && (
          <div className="rounded-lg border border-dashed border-gray-300 bg-white p-12 text-center">
            <p className="text-gray-600">
              No opportunity right now. We&apos;ll nudge you when something good comes up.
            </p>
            <button
              type="button"
              onClick={() => position && checkActivation(position.lat, position.lng)}
              className="mt-4 rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-white hover:bg-amber-600"
            >
              Check again
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
