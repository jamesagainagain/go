"use client";

import { useEffect } from "react";
import Link from "next/link";
import { PhoneFrame } from "@/components/PhoneFrame";
import { Timeline } from "@/components/Timeline";
import { useActivation, useActivationHistory } from "@/hooks/useActivation";

export default function HistoryPage() {
  const { submitFeedback } = useActivation();
  const { items, loading, error, fetchHistory } = useActivationHistory();

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

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

  const content = (
    <div className="min-h-screen bg-bg-phone">
      <header className="border-b border-white/10 bg-bg-card px-4 py-3 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <Link href="/dashboard" className="text-sm text-accent hover:text-amber-400">
            ← Back
          </Link>
          <h1 className="text-lg font-semibold text-text-primary">History</h1>
          <div className="w-12" />
        </div>
      </header>

      <div className="p-4">
        {error && (
          <div className="mb-4 rounded-xl bg-red-500/10 border border-red-500/20 p-3 text-sm text-red-400">
            {error}
          </div>
        )}
        <Timeline
          items={items}
          onFeedback={handleFeedback}
          loading={loading}
        />
      </div>
    </div>
  );

  return <PhoneFrame>{content}</PhoneFrame>;
}
