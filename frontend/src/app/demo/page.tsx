"use client";

import { useCallback, useState } from "react";
import { useKeyboardNav } from "./hooks/useKeyboardNav";
import { DemoTabs } from "./components/DemoTabs";
import { TitleTab } from "./components/TitleTab";
import { FrictionPointsTab } from "./components/FrictionPointsTab";
import { DoomTimelineTab } from "./components/DoomTimelineTab";
import { LiveDemoTab } from "./components/LiveDemoTab";
import { AgentPipelineTab } from "./components/AgentPipelineTab";
import { CloseTab } from "./components/CloseTab";

const TOTAL_TABS = 6;

export default function DemoPage() {
  const [activeTab, setActiveTab] = useState(0);

  useKeyboardNav(activeTab, setActiveTab, TOTAL_TABS);

  const handleTabChange = useCallback((tab: number) => {
    setActiveTab(tab);
  }, []);

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <DemoTabs activeTab={activeTab} onTabChange={handleTabChange} />
      <div className="relative flex flex-1 min-h-0">
        {activeTab === 0 && <TitleTab />}
        {activeTab === 1 && (
          <FrictionPointsTab onSeeGoFixThis={() => handleTabChange(3)} />
        )}
        {activeTab === 2 && <DoomTimelineTab />}
        {activeTab === 3 && <LiveDemoTab />}
        {activeTab === 4 && <AgentPipelineTab />}
        {activeTab === 5 && <CloseTab />}
      </div>
      <div
        className="gradient-text absolute bottom-4 right-4 text-sm"
        aria-live="polite"
      >
        {activeTab + 1}/{TOTAL_TABS}
      </div>
    </div>
  );
}
