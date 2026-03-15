"use client";

const TABS = [
  "The Problem",
  "Without go!",
  "With go!",
  "How It Works",
  "Why It Matters",
];

interface DemoTabsProps {
  activeTab: number;
  onTabChange: (tab: number) => void;
}

export function DemoTabs({ activeTab, onTabChange }: DemoTabsProps) {
  return (
    <header className="glow-box-subtle w-fit shrink-0 rounded-2xl px-6 py-4">
      <nav
        className="flex items-center justify-center gap-8"
        role="tablist"
      >
        {TABS.map((label, i) => (
          <button
            key={label}
            type="button"
            role="tab"
            aria-selected={activeTab === i}
            aria-controls={`tabpanel-${i}`}
            id={`tab-${i}`}
            onClick={() => onTabChange(i)}
            className={`px-3 py-2 text-sm font-medium transition-colors ${
              activeTab === i
                ? "tab-shimmer-active" 
                : "text-stone-600 hover:text-stone-800"
            }`}
          >
            {label}
          </button>
        ))}
      </nav>
    </header>
  );
}
