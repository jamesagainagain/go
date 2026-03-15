import type { ActivationCardResponse } from "@/types/api";

export interface MapEvent {
  id: string;
  title: string;
  lat: number;
  lng: number;
  category:
    | "art"
    | "sport"
    | "music"
    | "food"
    | "social"
    | "nature"
    | "study"
    | "nightlife"
    | "wellness"
    | "comedy"
    | "tech";
  time: string;
  venue: string;
  description: string;
}

export const RECOMMENDED_EVENTS: MapEvent[] = [
  {
    id: "r1",
    title: "Live Jazz at Ronnie Scott's",
    lat: 51.5133,
    lng: -0.1318,
    category: "music",
    time: "6:00 PM",
    venue: "Ronnie Scott's Jazz Club",
    description:
      "Intimate jazz session in Soho's legendary venue. Solo-friendly bar seating. 8 min walk.",
  },
  {
    id: "r2",
    title: "Borough Market Street Food",
    lat: 51.5055,
    lng: -0.0910,
    category: "food",
    time: "5:30 PM",
    venue: "Borough Market",
    description:
      "World-class street food vendors closing up - last chance for fresh Korean BBQ and craft beer. 12 min walk.",
  },
  {
    id: "r3",
    title: "Comedy Night at the Backyard",
    lat: 51.5246,
    lng: -0.0832,
    category: "comedy",
    time: "6:15 PM",
    venue: "Backyard Comedy Club",
    description:
      "Open mic + headliner. Relaxed crowd, great for solo visitors. Free entry. 15 min walk.",
  },
  {
    id: "r4",
    title: "Sunset Yoga on the South Bank",
    lat: 51.5065,
    lng: -0.1162,
    category: "wellness",
    time: "6:00 PM",
    venue: "South Bank Centre",
    description:
      "Drop-in session on the terrace. Mats provided. Perfect for unwinding after work. 10 min walk.",
  },
  {
    id: "r5",
    title: "Tate Modern Late Opening",
    lat: 51.5076,
    lng: -0.0994,
    category: "art",
    time: "5:45 PM",
    venue: "Tate Modern",
    description:
      "Extended hours tonight. Current exhibition: 'New Realities'. Free entry to main galleries. 11 min walk.",
  },
];

export const LONDON_EVENTS: MapEvent[] = [
  ...RECOMMENDED_EVENTS,
  {
    id: "6",
    title: "Craft Beer Tasting",
    lat: 51.519,
    lng: -0.077,
    category: "food",
    time: "6:00 PM",
    venue: "The Bermondsey Beer Mile",
    description: "Sample local microbrews along the beer mile.",
  },
  {
    id: "7",
    title: "Improv Workshop",
    lat: 51.5178,
    lng: -0.106,
    category: "comedy",
    time: "6:30 PM",
    venue: "The Free Association",
    description: "Beginners welcome improv workshop.",
  },
  {
    id: "8",
    title: "Regent's Park Run",
    lat: 51.527,
    lng: -0.155,
    category: "sport",
    time: "5:50 PM",
    venue: "Regent's Park",
    description: "Community 5K run through the park.",
  },
  {
    id: "9",
    title: "Thames Path Walk",
    lat: 51.502,
    lng: -0.118,
    category: "nature",
    time: "5:45 PM",
    venue: "Westminster Bridge",
    description: "Guided sunset walk along the Thames.",
  },
  {
    id: "10",
    title: "Tech Meetup: AI & Creativity",
    lat: 51.521,
    lng: -0.072,
    category: "tech",
    time: "6:00 PM",
    venue: "Plexal, Queen Elizabeth Park",
    description: "Lightning talks on generative AI in creative industries.",
  },
  {
    id: "11",
    title: "Vinyl DJ Set",
    lat: 51.512,
    lng: -0.102,
    category: "nightlife",
    time: "6:30 PM",
    venue: "Spiritland King's Cross",
    description: "Analogue sound system, vinyl-only DJ sets.",
  },
  {
    id: "12",
    title: "Book Club Social",
    lat: 51.518,
    lng: -0.097,
    category: "social",
    time: "6:00 PM",
    venue: "London Review Bookshop",
    description: "Monthly social reading meetup. All welcome.",
  },
];

export const MOCK_ACTIVATION: ActivationCardResponse = {
  activation_id: "mock-activation-1",
  opportunity: {
    title: "Live Jazz at Ronnie Scott's",
    body: "Intimate jazz session in Soho's legendary venue. Solo-friendly bar seating. The Tuesday night resident band is playing - warm, relaxed crowd.",
    tier: "structured",
    walk_minutes: 8,
    travel_description: "8 min walk through Soho",
    starts_at: "2026-03-15T18:00:00Z",
    leave_by: "2026-03-15T17:50:00Z",
    cost_pence: 0,
    venue: {
      name: "Ronnie Scott's Jazz Club",
      lat: 51.5133,
      lng: -0.1318,
      address: "47 Frith St, Soho, London",
    },
    social_proof: {
      text: "6 others going solo",
      total_expected: 24,
      solo_count: 6,
      familiar_face: false,
    },
    commitment_action: {
      type: "one_tap_rsvp",
      label: "Hold my spot",
    },
  },
  stage: "recommend",
  expires_at: "2026-03-15T17:55:00Z",
};

export const MOCK_USER_PROFILE = {
  display_name: "Demo User",
  comfort_level: "solo_ok" as const,
  willingness_radius_km: 2.5,
  preferences: [
    { category: "music", weight: 1, explicit: true },
    { category: "art", weight: 0.9, explicit: true },
    { category: "food", weight: 0.85, explicit: true },
  ],
};
