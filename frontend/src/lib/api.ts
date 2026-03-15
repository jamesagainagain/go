/**
 * Fetch wrapper for backend API
 */

import type {
  ActivationCardResponse,
  AuthResponse,
  RegisterRequest,
  LoginRequest,
  UserProfile,
  UserUpdateRequest,
  LocationUpdateRequest,
  ActivationCheckRequest,
  ActivationCheckResult,
  ActivationRespondRequest,
  FeedbackRequest,
  ActivationHistoryResponse,
  EventsNearbyResponse,
  EventAttendeesResponse,
  PushSubscribeRequest,
} from "@/types/api";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

function setToken(token: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem("access_token", token);
}

export function clearToken(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem("access_token");
}

async function fetchApi<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };
  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? err.message ?? `HTTP ${res.status}`);
  }

  if (res.status === 204) return {} as T;
  return res.json();
}

// --- Auth ---
export async function register(data: RegisterRequest): Promise<AuthResponse> {
  const res = await fetchApi<AuthResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });
  if (res.access_token) setToken(res.access_token);
  return res;
}

export async function login(data: LoginRequest): Promise<AuthResponse> {
  const res = await fetchApi<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  });
  if (res.access_token) setToken(res.access_token);
  return res;
}

export function logout(): void {
  clearToken();
}

export function isAuthenticated(): boolean {
  return !!getToken();
}

// --- Users ---
export async function getUsersMe(): Promise<UserProfile> {
  return fetchApi<UserProfile>("/users/me");
}

export async function patchUsersMe(data: UserUpdateRequest): Promise<UserProfile> {
  return fetchApi<UserProfile>("/users/me", {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function postUsersMeLocation(
  data: LocationUpdateRequest
): Promise<void> {
  return fetchApi<void>("/users/me/location", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// --- Activations ---
export async function postActivationsCheck(
  data?: ActivationCheckRequest
): Promise<ActivationCheckResult> {
  return fetchApi<ActivationCheckResult>("/activations/check", {
    method: "POST",
    body: JSON.stringify(data ?? {}),
  });
}

export async function getActivationsCurrent(): Promise<ActivationCheckResult> {
  return fetchApi<ActivationCheckResult>("/activations/current");
}

export async function getActivationById(
  id: string
): Promise<ActivationCardResponse | null> {
  try {
    const result = await fetchApi<ActivationCheckResult>(`/activations/${id}`);
    if ("activation_id" in result && result.activation_id && result.opportunity) {
      return result;
    }
  } catch {
    // Backend may not have GET /activations/:id; try history as fallback
  }
  try {
    const { items } = await getActivationsHistory(50, 0);
    const item = items?.find((i) => i.id === id);
    if (item?.opportunity) {
      return {
        activation_id: id,
        opportunity: item.opportunity,
        stage: "suggest",
        expires_at: "",
      };
    }
  } catch {
    // ignore
  }
  return null;
}

export async function postActivationsRespond(
  id: string,
  data: ActivationRespondRequest
): Promise<void> {
  return fetchApi<void>(`/activations/${id}/respond`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function postActivationsFeedback(
  id: string,
  data: FeedbackRequest
): Promise<void> {
  return fetchApi<void>(`/activations/${id}/feedback`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getActivationsHistory(
  limit = 20,
  offset = 0
): Promise<ActivationHistoryResponse> {
  return fetchApi<ActivationHistoryResponse>(
    `/activations/history?limit=${limit}&offset=${offset}`
  );
}

// --- Events ---
export async function getEventsNearby(
  lat: number,
  lng: number,
  radiusKm = 5,
  limit = 20
): Promise<EventsNearbyResponse> {
  return fetchApi<EventsNearbyResponse>(
    `/events/nearby?lat=${lat}&lng=${lng}&radius_km=${radiusKm}&limit=${limit}`
  );
}

export async function getDemoEventsNearby(
  lat: number,
  lng: number,
  radiusKm = 8,
  limit = 8
): Promise<EventsNearbyResponse> {
  return fetchApi<EventsNearbyResponse>(
    `/events/demo/nearby?lat=${lat}&lng=${lng}&radius_km=${radiusKm}&limit=${limit}`
  );
}

export async function getDemoEventAttendees(
  eventKey: string,
  title: string,
  tags: string[],
  attendeeHint?: number
): Promise<EventAttendeesResponse> {
  const query = new URLSearchParams({
    event_key: eventKey,
    title,
    tags: tags.join(","),
  });
  if (typeof attendeeHint === "number") {
    query.set("attendee_hint", `${attendeeHint}`);
  }
  return fetchApi<EventAttendeesResponse>(`/events/demo/attendees?${query.toString()}`);
}

// --- Push ---
export async function postPushSubscribe(
  data: PushSubscribeRequest
): Promise<void> {
  return fetchApi<void>("/push/subscribe", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
