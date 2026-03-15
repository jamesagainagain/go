"use client";

import { useState } from "react";
import type { ActivationHistoryItem } from "@/types/api";

interface TimelineProps {
  items: ActivationHistoryItem[];
  onFeedback?: (id: string, attended: boolean, rating?: number, feedbackText?: string) => void;
  loading?: boolean;
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function formatResponse(response?: string): string {
  switch (response) {
    case "accepted":
      return "Accepted";
    case "dismissed":
      return "Dismissed";
    case "expired":
      return "Expired";
    case "snoozed":
      return "Snoozed";
    default:
      return "—";
  }
}

export function Timeline({
  items,
  onFeedback,
  loading = false,
}: TimelineProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="animate-pulse rounded-lg border border-gray-200 bg-gray-50 p-4"
          >
            <div className="h-4 w-3/4 rounded bg-gray-200" />
            <div className="mt-2 h-3 w-1/2 rounded bg-gray-200" />
          </div>
        ))}
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-gray-300 p-8 text-center text-gray-500">
        No past activations yet. When you get nudges and respond, they&apos;ll show up here.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {items.map((item) => (
        <TimelineItem
          key={item.id}
          item={item}
          onFeedback={onFeedback}
        />
      ))}
    </div>
  );
}

interface TimelineItemProps {
  item: ActivationHistoryItem;
  onFeedback?: (id: string, attended: boolean, rating?: number, feedbackText?: string) => void;
}

function TimelineItem({ item, onFeedback }: TimelineItemProps) {
  const opp = item.opportunity;
  const hasFeedback = item.attended != null;
  const needsFeedback = item.response === "accepted" && !hasFeedback;

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="font-medium text-gray-900">{opp?.title}</h3>
          <p className="mt-0.5 text-sm text-gray-500">
            {formatDate(item.shown_at ?? "")} · {formatResponse(item.response)}
          </p>
        </div>
      </div>

      {item.response === "accepted" && (
        <div className="mt-3">
          {hasFeedback ? (
            <p className="text-sm text-gray-600">
              {item.attended ? (
                <>
                  Attended
                  {item.rating != null && ` · ${item.rating}/5`}
                </>
              ) : (
                "Didn't go"
              )}
              {item.feedback_text && (
                <span className="block mt-1 italic">&quot;{item.feedback_text}&quot;</span>
              )}
            </p>
          ) : needsFeedback && onFeedback && item.id ? (
            <FeedbackForm
              activationId={item.id}
              onSubmit={onFeedback}
            />
          ) : null}
        </div>
      )}
    </div>
  );
}

interface FeedbackFormProps {
  activationId: string;
  onSubmit: (id: string, attended: boolean, rating?: number, feedbackText?: string) => void;
}

function FeedbackForm({ activationId, onSubmit }: FeedbackFormProps) {
  const [attended, setAttended] = useState<boolean | null>(null);
  const [rating, setRating] = useState<number | undefined>();
  const [feedbackText, setFeedbackText] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (attended === null) return;
    onSubmit(activationId, attended, rating, feedbackText || undefined);
    setSubmitted(true);
  };

  if (submitted) return null;

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      <p className="text-sm font-medium text-gray-700">How was it?</p>
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => setAttended(true)}
          className={`rounded px-3 py-1 text-sm ${attended === true ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-600"}`}
        >
          Went
        </button>
        <button
          type="button"
          onClick={() => setAttended(false)}
          className={`rounded px-3 py-1 text-sm ${attended === false ? "bg-red-100 text-red-800" : "bg-gray-100 text-gray-600"}`}
        >
          Didn&apos;t go
        </button>
      </div>
      {attended !== null && (
        <>
          <div className="flex gap-1">
            {[1, 2, 3, 4, 5].map((r) => (
              <button
                key={r}
                type="button"
                onClick={() => setRating(r)}
                className={`rounded px-2 py-0.5 text-sm ${rating === r ? "bg-amber-100 text-amber-800" : "text-gray-500"}`}
              >
                {r}★
              </button>
            ))}
          </div>
          <input
            type="text"
            placeholder="Any feedback? (optional)"
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
            className="w-full rounded border border-gray-300 px-2 py-1 text-sm"
          />
          <button
            type="submit"
            className="rounded bg-amber-500 px-3 py-1 text-sm font-medium text-white hover:bg-amber-600"
          >
            Submit
          </button>
        </>
      )}
    </form>
  );
}
