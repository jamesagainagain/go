"use client";

const TABS = [
  "go!",
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
    <nav
      className="relative flex shrink-0 items-center justify-center gap-8 px-6 py-4"
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
          className={`relative pb-2 text-lg font-medium transition-colors ${
            activeTab === i
              ? "gradient-text-bright"
              : "text-slate-500 hover:text-slate-300"
          }`}
        >
          {label}
          {activeTab === i && (
            <span
              className="gradient-underline absolute bottom-0 left-0 right-0 h-0.5 rounded-full"
              aria-hidden
            />
          )}
        </button>
      ))}
      <div className="gradient-underline absolute bottom-0 left-0 right-0 h-px opacity-20" />
    </nav>
  );
}
