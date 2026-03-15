"use client";

import { useEffect } from "react";

export function useKeyboardNav(
  activeTab: number,
  onTabChange: (tab: number) => void,
  totalTabs: number
) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }
      if (e.key >= "1" && e.key <= "6") {
        const tab = parseInt(e.key, 10) - 1;
        if (tab < totalTabs) {
          e.preventDefault();
          onTabChange(tab);
        }
      }
      if (e.key === "ArrowLeft") {
        e.preventDefault();
        onTabChange(Math.max(0, activeTab - 1));
      }
      if (e.key === "ArrowRight") {
        e.preventDefault();
        onTabChange(Math.min(totalTabs - 1, activeTab + 1));
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [activeTab, onTabChange, totalTabs]);
}
