"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { PhoneFrame } from "@/components/PhoneFrame";
import { ActivationCard } from "@/components/ActivationCard";
import { useActivation } from "@/hooks/useActivation";
import { useLocation } from "@/hooks/useLocation";
import { getActivationById } from "@/lib/api";
import { MOCK_ACTIVATION } from "@/lib/mock-data";
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
    if (!id) return;
    getActivationById(id)
      .then((a) => {
        setActivation(a ?? (id === "mock-activation-1" ? MOCK_ACTIVATION : null));
        if (!a && id !== "mock-activation-1") setError("Activation not found or expired");
      })
      .catch(() => {
        setActivation(id === "mock-activation-1" ? MOCK_ACTIVATION : null);
        setError("Failed to load activation");
      })
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

  const content = (
    <div className="min-h-screen bg-bg-phone">
      <header className="border-b border-white/10 bg-bg-card px-4 py-3 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <Link href="/dashboard" className="text-sm text-accent hover:text-amber-400">
            ← Back
          </Link>
          <h1 className="text-lg font-semibold text-text-primary">Opportunity</h1>
          <div className="w-12" />
        </div>
      </header>

      <div className="p-4">
        {loading && (
          <div className="animate-pulse rounded-xl bg-bg-card p-8">
            <div className="h-6 w-3/4 rounded bg-white/10" />
            <div className="mt-4 h-4 w-1/2 rounded bg-white/10" />
          </div>
        )}

        {error && !activation && (
          <div className="rounded-xl bg-bg-card p-8 text-center">
            <p className="text-text-muted">{error}</p>
            <Link
              href="/dashboard"
              className="mt-4 inline-block rounded-xl bg-accent px-4 py-2 text-black font-medium hover:bg-amber-500"
            >
              Back to Dashboard
            </Link>
          </div>
        )}

        {activation && !loading && (
          <ActivationCard
            activation={activation}
            userLat={position?.lat}
            userLng={position?.lng}
            onDismiss={handleDismiss}
            onRespond={handleRespond}
            compact={false}
          />
        )}
      </div>
    </div>
  );

  return <PhoneFrame>{content}</PhoneFrame>;
}
