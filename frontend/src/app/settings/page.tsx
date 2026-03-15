"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { PhoneFrame } from "@/components/PhoneFrame";
import { getUsersMe, patchUsersMe, logout } from "@/lib/api";
import { useNotifications } from "@/hooks/useNotifications";
import { MOCK_USER_PROFILE } from "@/lib/mock-data";
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
  "nature",
  "nightlife",
  "wellness",
  "comedy",
  "tech",
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
    getUsersMe()
      .then((p) => {
        setProfile(p);
        setDisplayName(p.display_name ?? "");
        setComfortLevel((p.comfort_level as ComfortLevel) ?? "prefer_others");
        setPreferences(new Set((p.preferences ?? []).map((pr) => pr.category)));
      })
      .catch(() => {
        setProfile(MOCK_USER_PROFILE as UserProfile);
        setDisplayName(MOCK_USER_PROFILE.display_name ?? "");
        setComfortLevel(MOCK_USER_PROFILE.comfort_level);
        setPreferences(
          new Set(MOCK_USER_PROFILE.preferences?.map((p) => p.category) ?? [])
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
    } catch {
      // Backend may not be running
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.replace("/");
  };

  const content = (
    <div className="min-h-screen bg-bg-phone">
      <header className="border-b border-white/10 bg-bg-card px-4 py-3 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <Link href="/dashboard" className="text-sm text-accent hover:text-amber-400">
            ← Back
          </Link>
          <h1 className="text-lg font-semibold text-text-primary">Settings</h1>
          <div className="w-12" />
        </div>
      </header>

      <div className="p-4 space-y-6">
        {loading ? (
          <div className="animate-pulse rounded-xl bg-bg-card p-8">
            <div className="h-6 w-1/2 rounded bg-white/10" />
          </div>
        ) : (
          <>
            <section className="rounded-xl border border-white/10 bg-bg-card p-4">
              <h2 className="mb-3 font-medium text-text-primary">Profile</h2>
              <input
                type="text"
                placeholder="Display name"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                className="w-full rounded-xl border border-white/10 bg-bg-card-hover px-3 py-2 text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent"
              />
            </section>

            <section className="rounded-xl border border-white/10 bg-bg-card p-4">
              <h2 className="mb-3 font-medium text-text-primary">Comfort level</h2>
              <div className="space-y-2">
                {COMFORT_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => setComfortLevel(opt.value)}
                    className={`block w-full rounded-xl border px-4 py-2 text-left text-sm transition-colors ${
                      comfortLevel === opt.value
                        ? "border-accent bg-accent/10 text-accent"
                        : "border-white/10 bg-bg-card-hover text-text-primary hover:bg-white/5"
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </section>

            <section className="rounded-xl border border-white/10 bg-bg-card p-4">
              <h2 className="mb-3 font-medium text-text-primary">Interests</h2>
              <div className="flex flex-wrap gap-2">
                {INTEREST_CATEGORIES.map((cat) => (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => togglePreference(cat)}
                    className={`rounded-full px-3 py-1 text-sm transition-colors ${
                      preferences.has(cat)
                        ? "bg-accent text-black"
                        : "bg-bg-card-hover text-text-muted hover:text-text-primary"
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </section>

            <section className="rounded-xl border border-white/10 bg-bg-card p-4">
              <h2 className="mb-3 font-medium text-text-primary">Notifications</h2>
              <p className="mb-2 text-sm text-text-muted">
                Status:{" "}
                {permission === "granted"
                  ? "Enabled"
                  : permission === "denied"
                    ? "Blocked"
                    : "Not set"}
              </p>
              {permission !== "granted" && (
                <button
                  type="button"
                  onClick={requestAndSubscribe}
                  disabled={notifLoading}
                  className="rounded-xl bg-accent px-4 py-2 text-sm font-medium text-black hover:bg-amber-500 disabled:opacity-50"
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
                className="flex-1 rounded-xl bg-accent px-4 py-2 font-medium text-black hover:bg-amber-500 disabled:opacity-50"
              >
                {saving ? "Saving..." : "Save changes"}
              </button>
              <button
                type="button"
                onClick={handleLogout}
                className="rounded-xl border border-white/20 px-4 py-2 font-medium text-text-primary hover:bg-white/5"
              >
                Log out
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );

  return <PhoneFrame>{content}</PhoneFrame>;
}
