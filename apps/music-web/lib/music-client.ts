"use client";

const BASE = "/api/v1/music";

export type BootstrapUser = {
  id: string | null;
  display_name: string;
  status: string;
  auth_state?: string;
  demo_creator_handle?: string;
  capabilities?: { account_actions: boolean; creator_writes: boolean };
};

export type CreatorProfile = {
  id: string;
  user_id: string;
  handle: string;
  display_name: string;
  bio: string | null;
  avatar_asset_key: string | null;
  banner_asset_key: string | null;
  status: string;
};

export type TrackDto = {
  id: string;
  creator_id: string;
  creator_handle?: string | null;
  title: string;
  slug: string | null;
  status: string;
  visibility: string;
  primary_language: string | null;
  duration_ms: number | null;
  cover_asset_key: string | null;
  current_version_id: string | null;
  published_at: string | null;
  version: { id: string; version_no: number; audio_asset_key: string | null } | null;
};

export type CreatorPage = {
  profile: CreatorProfile;
  tracks: TrackDto[];
  albums: { id: string; title: string; cover_asset_key: string | null }[];
  follower_count: number;
  viewer_following: boolean | null;
};

export type LicenseIntentDto = {
  id: string;
  track_id: string;
  license_type: string;
  usage_description: string;
  requester_name: string | null;
  budget_amount_minor: number | null;
  budget_currency: string | null;
  status: string;
  created_at: string | null;
};

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({})) as { error?: { message?: string } };
    throw new Error(body.error?.message ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

const idem = () => crypto.randomUUID();

export const api = {
  signInWithInvite: (inviteCode: string) =>
    req<{ authenticated: boolean }>("/session", { method: "POST", body: JSON.stringify({ invite_code: inviteCode }) }),
  signOut: () => req<{ authenticated: boolean }>("/session", { method: "DELETE" }),
  bootstrap: () => req<BootstrapUser>("/bootstrap"),
  catalogue: () => req<{ tracks: TrackDto[] }>("/catalogue"),
  createCreator: (body: Record<string, unknown>) =>
    req<CreatorProfile>("/creators", { method: "POST", body: JSON.stringify(body), headers: { "Idempotency-Key": idem() } }),
  creatorByHandle: (handle: string) => req<CreatorProfile>(`/creators/by-handle/${handle}`),
  creatorPage: (creatorId: string) => req<CreatorPage>(`/creators/${creatorId}/page`),
  track: (id: string) => req<TrackDto>(`/tracks/${id}`),
  createTrack: (body: Record<string, unknown>) =>
    req<TrackDto>("/tracks", { method: "POST", body: JSON.stringify(body), headers: { "Idempotency-Key": idem() } }),
  createVersion: (trackId: string, body: Record<string, unknown>) =>
    req<TrackDto>(`/tracks/${trackId}/versions`, { method: "POST", body: JSON.stringify(body), headers: { "Idempotency-Key": idem() } }),
  upsertPassport: (trackId: string, body: Record<string, unknown>) =>
    req<Record<string, unknown>>(`/tracks/${trackId}/passport`, { method: "PUT", body: JSON.stringify(body), headers: { "Idempotency-Key": idem() } }),
  publish: (trackId: string) =>
    req<TrackDto>(`/tracks/${trackId}/publish`, { method: "POST", body: JSON.stringify({}), headers: { "Idempotency-Key": idem() } }),
  follow: (userId: string, creatorId: string) =>
    req<{ following: boolean }>(`/users/${userId}/follows/${creatorId}`, { method: "PUT", body: "{}", headers: { "Idempotency-Key": idem() } }),
  unfollow: (userId: string, creatorId: string) =>
    req<{ following: boolean }>(`/users/${userId}/follows/${creatorId}`, { method: "DELETE" }),
  favorite: (userId: string, trackId: string) =>
    req<{ favorited: boolean }>(`/users/${userId}/favorites/${trackId}`, { method: "PUT", body: "{}", headers: { "Idempotency-Key": idem() } }),
  unfavorite: (userId: string, trackId: string) =>
    req<{ favorited: boolean }>(`/users/${userId}/favorites/${trackId}`, { method: "DELETE" }),
  playEvent: (body: Record<string, unknown>) =>
    req<{ id: string }>("/play-events", { method: "POST", body: JSON.stringify(body) }),
  licenseIntent: (body: Record<string, unknown>) =>
    req<{ id: string }>("/license-intents", { method: "POST", body: JSON.stringify(body), headers: { "Idempotency-Key": idem() } }),
  creatorInbox: (creatorId: string) => req<{ intents: LicenseIntentDto[] }>(`/creators/${creatorId}/license-intents`),
  supportIntent: (body: Record<string, unknown>) =>
    req<{ id: string }>("/support-intents", { method: "POST", body: JSON.stringify(body), headers: { "Idempotency-Key": idem() } }),
};
