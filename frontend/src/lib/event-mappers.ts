/**
 * Maps API EventSummary to MapEvent for map display
 */
import type { EventSummary } from "@/types/api";
import type { MapEvent } from "@/lib/mock-data";

const CATEGORY_FROM_TAG: Record<string, MapEvent["category"]> = {
  art: "art",
  sport: "sport",
  music: "music",
  food: "food",
  social: "social",
  nature: "nature",
  study: "study",
  nightlife: "nightlife",
  wellness: "wellness",
  comedy: "comedy",
  tech: "tech",
  museum: "art",
  gallery: "art",
  restaurant: "food",
  cafe: "food",
  park: "nature",
};

function formatEventTime(startsAt: string | undefined): string {
  if (!startsAt) return "";
  try {
    const d = new Date(startsAt);
    return d.toLocaleTimeString("en-GB", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });
  } catch {
    return "";
  }
}

export function eventSummaryToMapEvent(e: EventSummary, index: number): MapEvent | null {
  const lat = e.venue?.lat;
  const lng = e.venue?.lng;
  if (lat == null || lng == null || lat < -90 || lat > 90 || lng < -180 || lng > 180) {
    return null;
  }
  const tag = e.tags?.[0]?.toLowerCase();
  const mapped = tag ? CATEGORY_FROM_TAG[tag] : undefined;
  const category: MapEvent["category"] = mapped ?? "social";
  return {
    id: e.id ?? `evt-${index}`,
    title: e.title ?? "Event",
    lat,
    lng,
    category,
    time: formatEventTime(e.starts_at),
    venue: e.venue?.name ?? "Venue",
    description: e.description ?? "",
  };
}
