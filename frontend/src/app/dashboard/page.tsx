"use client";

import { PhoneFrame } from "@/components/PhoneFrame";
import { SimulationController } from "@/components/dashboard/SimulationController";
import Link from "next/link";

export default function DashboardPage() {
  return (
    <div className="min-h-screen">
      <PhoneFrame>
        <div className="flex flex-col min-h-full">
          <SimulationController />
          <div className="flex gap-4 justify-center py-4 border-t border-white/5">
            <Link
              href="/history"
              className="text-sm text-text-muted hover:text-text-primary"
            >
              History
            </Link>
            <Link
              href="/settings"
              className="text-sm text-text-muted hover:text-text-primary"
            >
              Settings
            </Link>
          </div>
        </div>
      </PhoneFrame>
    </div>
  );
}
