"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { PhoneStatusBar } from "../PhoneStatusBar";
import { TimeDisplay } from "./TimeDisplay";
import { EventMap } from "./EventMap";
import { ActivationPopup } from "./ActivationPopup";
import { MOCK_ACTIVATION } from "@/lib/mock-data";
import { postActivationsCheck, getActivationsCurrent } from "@/lib/api";
import type { ActivationCardResponse } from "@/types/api";

export function SimulationController() {
  const [mapExpanded, setMapExpanded] = useState(false);
  const [activation, setActivation] = useState<ActivationCardResponse | null>(null);
  const [popupVisible, setPopupVisible] = useState(false);
  const [mapVisible, setMapVisible] = useState(false);

  // t=0: initial, t=1s: map fades in, t=3s: activation card slides up
  useEffect(() => {
    const t1 = setTimeout(() => setMapVisible(true), 1000);
    return () => clearTimeout(t1);
  }, []);

  useEffect(() => {
    const checkActivation = async () => {
      try {
        const result = await getActivationsCurrent();
        if ("activation_id" in result && result.activation_id && result.opportunity) {
          setActivation(result);
        } else {
          setActivation(MOCK_ACTIVATION);
        }
      } catch {
        setActivation(MOCK_ACTIVATION);
      }
    };
    checkActivation();
  }, []);

  useEffect(() => {
    if (!activation) return;
    const t = setTimeout(() => setPopupVisible(true), 3000);
    return () => clearTimeout(t);
  }, [activation]);

  return (
    <div className="flex flex-col min-h-[calc(100vh-88px)] bg-bg-phone">
      <PhoneStatusBar />
      <div className="flex-1 overflow-y-auto">
        <TimeDisplay />
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: mapVisible ? 1 : 0 }}
          transition={{ duration: 0.5 }}
        >
          <EventMap
            expanded={mapExpanded}
            onExpand={() => setMapExpanded(true)}
            onCollapse={() => setMapExpanded(false)}
          />
        </motion.div>
      </div>
      <ActivationPopup
        activation={activation}
        visible={popupVisible}
        onDismiss={() => setPopupVisible(false)}
        onAccept={() => setPopupVisible(false)}
      />
    </div>
  );
}
