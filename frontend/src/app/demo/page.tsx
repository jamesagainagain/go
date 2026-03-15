"use client";

import { useCallback, useState } from "react";
import { useKeyboardNav } from "./hooks/useKeyboardNav";
import { DemoTabs } from "./components/DemoTabs";
import { FrictionPointsTab } from "./components/FrictionPointsTab";
import { DoomTimelineTab } from "./components/DoomTimelineTab";
import { LiveDemoTab } from "./components/LiveDemoTab";
import { AgentPipelineTab } from "./components/AgentPipelineTab";
import { CloseTab } from "./components/CloseTab";

const TOTAL_TABS = 5;

export default function DemoPage() {
  const [activeTab, setActiveTab] = useState(0);

  useKeyboardNav(activeTab, setActiveTab, TOTAL_TABS);

  const handleTabChange = useCallback((tab: number) => {
    setActiveTab(tab);
  }, []);

  return (
    <div className="flex h-full flex-col overflow-visible">
      <div className="relative z-20 flex shrink-0 justify-center pt-6">
        <DemoTabs activeTab={activeTab} onTabChange={handleTabChange} />
      </div>
      <div className="relative z-0 flex flex-1 min-h-0 overflow-visible">
        {activeTab === 0 && (
          <FrictionPointsTab onSeeGoFixThis={() => handleTabChange(2)} />
        )}
        {activeTab === 1 && <DoomTimelineTab />}
        {activeTab === 2 && <LiveDemoTab />}
        {activeTab === 3 && <AgentPipelineTab />}
        {activeTab === 4 && <CloseTab />}
      </div>
      <div
        className="absolute bottom-4 right-4 text-xs text-stone-500"
        aria-live="polite"
      >
        {activeTab + 1}/{TOTAL_TABS}
      </div>
    </div>
  );
}
