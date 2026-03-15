"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { OnboardingFlow } from "@/components/OnboardingFlow";
import { register, isAuthenticated } from "@/lib/api";
import { useNotifications } from "@/hooks/useNotifications";
import { getCurrentPosition } from "@/lib/geo";
import type { OnboardingData } from "@/components/OnboardingFlow";

export default function HomePage() {
  const router = useRouter();
  const { requestAndSubscribe } = useNotifications();

  useEffect(() => {
    if (isAuthenticated()) {
      router.replace("/dashboard");
    }
  }, [router]);

  const handleComplete = async (data: OnboardingData) => {
    await register({
      email: data.email,
      display_name: data.displayName,
      password: data.password,
      comfort_level: data.comfortLevel,
      preferences: data.interests,
      timezone: data.timezone,
    });
    router.replace("/dashboard");
  };

  const handleRequestNotifications = async () => {
    return requestAndSubscribe();
  };

  const handleRequestLocation = async () => {
    try {
      const pos = await getCurrentPosition();
      return { lat: pos.lat, lng: pos.lng };
    } catch {
      return null;
    }
  };

  if (typeof window !== "undefined" && isAuthenticated()) {
    return null;
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-lg pt-12">
        <h1 className="mb-8 text-center text-2xl font-bold text-gray-900">
          FirstMove
        </h1>
        <p className="mb-8 text-center text-gray-600">
          From screen to street — we&apos;ll nudge you at the right moment.
        </p>
        <OnboardingFlow
          onComplete={handleComplete}
          onRequestNotifications={handleRequestNotifications}
          onRequestLocation={handleRequestLocation}
        />
      </div>
    </main>
  );
}
