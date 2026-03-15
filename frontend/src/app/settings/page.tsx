"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getUsersMe, patchUsersMe, logout, isAuthenticated } from "@/lib/api";
import { useNotifications } from "@/hooks/useNotifications";
import type { UserProfile, ComfortLevel, PreferenceInput } from "@/types/api";

const COMFORT_OPTIONS: { value: ComfortLevel; label: string }[] = [
  { value: "solo_ok", label: "Happy going solo" },
  { value: "prefer_others", label: "Prefer others around" },
  { value: "need_familiar", label: "Need familiar faces" },
];

const INTEREST_CATEGORIES = [
  "art",
  "sport",
  "food",
  "music",
  "study",
  "creative",
  "outdoor",
  "social",
  "wellness",
];

export default function SettingsPage() {
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [displayName, setDisplayName] = useState("");
  const [comfortLevel, setComfortLevel] = useState<ComfortLevel>("prefer_others");
  const [preferences, setPreferences] = useState<Set<string>>(new Set());

  const { permission, requestAndSubscribe, loading: notifLoading } = useNotifications();

  useEffect(() => {
    if (typeof window !== "undefined" && !isAuthenticated()) {
      router.replace("/");
      return;
    }
  }, [router]);

  useEffect(() => {
    if (!isAuthenticated()) return;
    getUsersMe()
      .then((p) => {
        setProfile(p);
        setDisplayName(p.display_name ?? "");
        setComfortLevel((p.comfort_level as ComfortLevel) ?? "prefer_others");
        setPreferences(
          new Set((p.preferences ?? []).map((pr) => pr.category))
        );
      })
      .finally(() => setLoading(false));
  }, []);

  const togglePreference = (cat: string) => {
    setPreferences((prev) => {
      const next = new Set(prev);
      if (next.has(cat)) next.delete(cat);
      else next.add(cat);
      return next;
    });
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const prefs: PreferenceInput[] = Array.from(preferences).map((cat) => ({
        category: cat,
        weight: 0.8,
        explicit: true,
      }));
      await patchUsersMe({
        display_name: displayName,
        comfort_level: comfortLevel,
        preferences: prefs,
      });
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.replace("/");
  };

  if (typeof window !== "undefined" && !isAuthenticated()) {
    return null;
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50 p-4">
        <div className="mx-auto max-w-lg">
          <div className="animate-pulse rounded-lg bg-white p-8">
            <div className="h-6 w-1/2 rounded bg-gray-200" />
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
          <h1 className="text-lg font-semibold text-gray-900">Settings</h1>
          <div className="w-12" />
        </div>
      </header>

      <div className="mx-auto max-w-lg space-y-6 p-4">
        <section className="rounded-lg border border-gray-200 bg-white p-4">
          <h2 className="mb-3 font-medium text-gray-900">Profile</h2>
          <input
            type="text"
            placeholder="Display name"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2"
          />
        </section>

        <section className="rounded-lg border border-gray-200 bg-white p-4">
          <h2 className="mb-3 font-medium text-gray-900">Comfort level</h2>
          <div className="space-y-2">
            {COMFORT_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setComfortLevel(opt.value)}
                className={`block w-full rounded-lg border px-4 py-2 text-left text-sm ${
                  comfortLevel === opt.value
                    ? "border-amber-500 bg-amber-50"
                    : "border-gray-200"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </section>

        <section className="rounded-lg border border-gray-200 bg-white p-4">
          <h2 className="mb-3 font-medium text-gray-900">Interests</h2>
          <div className="flex flex-wrap gap-2">
            {INTEREST_CATEGORIES.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => togglePreference(cat)}
                className={`rounded-full px-3 py-1 text-sm ${
                  preferences.has(cat)
                    ? "bg-amber-500 text-white"
                    : "bg-gray-100 text-gray-600"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </section>

        <section className="rounded-lg border border-gray-200 bg-white p-4">
          <h2 className="mb-3 font-medium text-gray-900">Notifications</h2>
          <p className="mb-2 text-sm text-gray-600">
            Status: {permission === "granted" ? "Enabled" : permission === "denied" ? "Blocked" : "Not set"}
          </p>
          {permission !== "granted" && (
            <button
              type="button"
              onClick={requestAndSubscribe}
              disabled={notifLoading}
              className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-white hover:bg-amber-600 disabled:opacity-50"
            >
              {notifLoading ? "..." : "Enable push notifications"}
            </button>
          )}
        </section>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleSave}
            disabled={saving}
            className="flex-1 rounded-lg bg-amber-500 px-4 py-2 font-medium text-white hover:bg-amber-600 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save changes"}
          </button>
          <button
            type="button"
            onClick={handleLogout}
            className="rounded-lg border border-gray-300 px-4 py-2 font-medium text-gray-700 hover:bg-gray-50"
          >
            Log out
          </button>
        </div>
      </div>
    </main>
  );
}
