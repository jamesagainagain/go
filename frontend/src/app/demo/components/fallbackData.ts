import type { ActivationCardResponse } from "@/types/api";

function getStartsAt(): string {
  const d = new Date();
  d.setMinutes(d.getMinutes() + 75);
  return d.toISOString();
}

function getLeaveBy(): string {
  const d = new Date();
  d.setMinutes(d.getMinutes() + 64); // 11 min before starts_at
  return d.toISOString();
}

export const FALLBACK_ACTIVATION: ActivationCardResponse = {
  activation_id: "fallback-demo-001",
  opportunity: {
    title: "Open Mic Night",
    body: "Chill open mic at a legendary Shoreditch venue. Great for solo visitors.",
    tier: "structured",
    walk_minutes: 11,
    travel_description: "11 min walk along Rivington St",
    social_proof: {
      text: "4 others going solo",
      total_expected: 12,
      solo_count: 4,
      familiar_face: false,
    },
    starts_at: getStartsAt(),
    leave_by: getLeaveBy(),
    cost_pence: 0,
    venue: {
      name: "The Old Blue Last",
      lat: 51.5255,
      lng: -0.0775,
      address: "38 Great Eastern St, London",
    },
    commitment_action: {
      type: "one_tap_rsvp",
      label: "Tap to go",
    },
  },
  stage: "recommend",
  expires_at: getLeaveBy(),
};
