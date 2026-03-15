"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { ActivationCard } from "@/components/ActivationCard";
import { useActivation } from "@/hooks/useActivation";
import { useLocation } from "@/hooks/useLocation";
import { getActivationById, isAuthenticated } from "@/lib/api";
import type { ActivationCardResponse } from "@/types/api";

export default function ActivationDetailPage() {
  const router = useRouter();
  const params = useParams();
  const id = params.id as string;
  const [activation, setActivation] = useState<ActivationCardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { position } = useLocation(false);
  const { respond } = useActivation();

  useEffect(() => {
    if (typeof window !== "undefined" && !isAuthenticated()) {
      router.replace("/");
      return;
    }
  }, [router]);

  useEffect(() => {
    if (!id) return;
    getActivationById(id)
      .then((a) => {
        setActivation(a);
        if (!a) setError("Activation not found or expired");
      })
      .catch(() => setError("Failed to load activation"))
      .finally(() => setLoading(false));
  }, [id]);

  const handleDismiss = () => {
    if (activation) respond(activation.activation_id, "dismissed");
    router.push("/dashboard");
  };

  const handleRespond = (response: "accepted" | "dismissed" | "expired" | "snoozed") => {
    if (activation) respond(activation.activation_id, response);
    router.push("/dashboard");
  };

  if (typeof window !== "undefined" && !isAuthenticated()) {
    return null;
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50 p-4">
        <div className="mx-auto max-w-lg">
          <div className="animate-pulse rounded-lg bg-white p-8">
            <div className="h-6 w-3/4 rounded bg-gray-200" />
            <div className="mt-4 h-4 w-1/2 rounded bg-gray-200" />
          </div>
        </div>
      </main>
    );
  }

  if (error || !activation) {
    return (
      <main className="min-h-screen bg-gray-50 p-4">
        <div className="mx-auto max-w-lg">
          <div className="rounded-lg bg-white p-8 text-center">
            <p className="text-gray-600">{error ?? "Activation not found"}</p>
            <Link
              href="/dashboard"
              className="mt-4 inline-block rounded-lg bg-amber-500 px-4 py-2 text-white hover:bg-amber-600"
            >
              Back to Dashboard
            </Link>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white px-4 py-3">
        <div className="mx-auto flex max-w-lg items-center justify-between">
          <Link href="/dashboard" className="text-sm text-gray-600 hover:text-gray-900">
            ← Back
          </Link>
          <h1 className="text-lg font-semibold text-gray-900">Opportunity</h1>
          <div className="w-12" />
        </div>
      </header>

      <div className="mx-auto max-w-lg p-4">
        <ActivationCard
          activation={activation}
          userLat={position?.lat}
          userLng={position?.lng}
          onDismiss={handleDismiss}
          onRespond={handleRespond}
          compact={false}
        />
      </div>
    </main>
  );
}
