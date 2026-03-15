/**
 * API types derived from docs/api-spec.yaml
 */

export type ComfortLevel = "solo_ok" | "prefer_others" | "need_familiar";

export type ActivationStage = "suggest" | "recommend" | "precommit" | "activate";

export type OpportunityTier =
  | "structured"
  | "recurring_pattern"
  | "micro_coordination"
  | "solo_nudge";

export type ActivationResponse = "accepted" | "dismissed" | "expired" | "snoozed";

export type CommitmentActionType =
  | "one_tap_rsvp"
  | "deep_link"
  | "internal_going"
  | "none";

// --- Auth ---
export interface RegisterRequest {
  email: string;
  display_name?: string;
  password?: string;
  comfort_level?: ComfortLevel;
  preferences?: PreferenceInput[];
  timezone?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token?: string;
  token_type?: string;
  user?: UserProfile;
}

// --- User ---
export interface UserProfile {
  id?: string;
  email?: string;
  display_name?: string;
  comfort_level?: ComfortLevel;
  willingness_radius_km?: number;
  activation_stage?: ActivationStage;
  timezone?: string;
  location_lat?: number;
  location_lng?: number;
  location_updated_at?: string;
  preferences?: Preference[];
  created_at?: string;
}

export interface UserUpdateRequest {
  display_name?: string;
  comfort_level?: ComfortLevel;
  willingness_radius_km?: number;
  timezone?: string;
  preferences?: PreferenceInput[];
}

export interface LocationUpdateRequest {
  lat: number;
  lng: number;
}

export interface Preference {
  category: string;
  weight?: number;
  explicit?: boolean;
}

export interface PreferenceInput {
  category: string;
  weight?: number;
  explicit?: boolean;
}

// --- Activations ---
export interface ActivationCheckRequest {
  lat?: number;
  lng?: number;
}

export interface ActivationCardResponse {
  activation_id: string;
  opportunity: Opportunity;
  stage: ActivationStage;
  expires_at: string;
}

export interface NoOpportunityResponse {
  activation_id: null;
  opportunity: null;
  message?: string;
}

export type ActivationCheckResult = ActivationCardResponse | NoOpportunityResponse;

export interface Opportunity {
  title: string;
  body: string;
  tier: OpportunityTier;
  walk_minutes: number;
  travel_description: string;
  starts_at: string;
  leave_by: string;
  cost_pence: number;
  venue: VenueSummary;
  social_proof?: SocialProof;
  commitment_action?: CommitmentAction;
  route_polyline?: string;
}

export interface VenueSummary {
  name?: string;
  lat?: number;
  lng?: number;
  address?: string;
}

export interface SocialProof {
  text?: string;
  total_expected?: number;
  solo_count?: number;
  familiar_face?: boolean;
}

export interface CommitmentAction {
  type?: CommitmentActionType;
  label?: string;
  url?: string;
}

export interface ActivationRespondRequest {
  response: ActivationResponse;
}

export interface FeedbackRequest {
  attended: boolean;
  rating?: number;
  feedback_text?: string;
}

export interface ActivationHistoryResponse {
  items?: ActivationHistoryItem[];
  total?: number;
}

export interface ActivationHistoryItem {
  id?: string;
  opportunity?: Opportunity;
  shown_at?: string;
  response?: ActivationResponse;
  attended?: boolean;
  rating?: number;
  feedback_text?: string;
}

// --- Events ---
export interface EventsNearbyResponse {
  events?: EventSummary[];
}

export interface EventSummary {
  id?: string;
  title?: string;
  description?: string;
  starts_at?: string;
  ends_at?: string;
  cost_pence?: number;
  tags?: string[];
  venue?: VenueSummary;
  tier?: OpportunityTier;
}

// --- Push ---
export interface PushSubscribeRequest {
  endpoint: string;
  expirationTime?: number | null;
  keys: {
    p256dh: string;
    auth: string;
  };
}
