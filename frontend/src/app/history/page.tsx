"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Timeline } from "@/components/Timeline";
import { useActivation, useActivationHistory } from "@/hooks/useActivation";
import { isAuthenticated } from "@/lib/api";

export default function HistoryPage() {
  const router = useRouter();
  const { submitFeedback } = useActivation();
  const { items, loading, error, fetchHistory } = useActivationHistory();

  useEffect(() => {
    if (typeof window !== "undefined" && !isAuthenticated()) {
      router.replace("/");
      return;
    }
  }, [router]);

  useEffect(() => {
    if (isAuthenticated()) {
      fetchHistory();
    }
  }, []);

  const handleFeedback = (
    id: string,
    attended: boolean,
    rating?: number,
    feedbackText?: string
  ) => {
    submitFeedback(id, {
      attended,
      rating,
      feedback_text: feedbackText,
    });
    fetchHistory();
  };

  if (typeof window !== "undefined" && !isAuthenticated()) {
    return null;
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white px-4 py-3">
        <div className="mx-auto flex max-w-lg items-center justify-between">
          <Link href="/dashboard" className="text-sm text-gray-600 hover:text-gray-900">
            ← Back
          </Link>
          <h1 className="text-lg font-semibold text-gray-900">History</h1>
          <div className="w-12" />
        </div>
      </header>

      <div className="mx-auto max-w-lg p-4">
        {error && (
          <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>
        )}
        <Timeline
          items={items}
          onFeedback={handleFeedback}
          loading={loading}
        />
      </div>
    </main>
  );
}
