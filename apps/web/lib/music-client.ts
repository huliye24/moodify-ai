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
  audio_asset_key?: string | null;
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

export type MediaUpload = {
  asset_key: string;
  bytes: number;
  sha256: string;
  mime_type: string;
  deduplicated?: boolean;
};

export type UploadProgress = (uploadedBytes: number, totalBytes: number) => void;

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
  uploadAudio: (file: File, onProgress?: UploadProgress): Promise<MediaUpload> => new Promise((resolve, reject) => {
    const request = new XMLHttpRequest();
    request.open("PUT", `${BASE}/media`);
    request.setRequestHeader("Content-Type", file.type || "audio/wav");
    request.setRequestHeader("X-Filename", file.name);
    request.upload.onprogress = (event) => onProgress?.(event.loaded, event.lengthComputable ? event.total : file.size);
    request.onerror = () => reject(new Error("音频上传中断，请检查网络后重试"));
    request.onload = () => {
      let body: (MediaUpload & { error?: { message?: string } }) | null = null;
      try { body = JSON.parse(request.responseText); } catch { /* normalized below */ }
      if (request.status < 200 || request.status >= 300) {
        reject(new Error(body?.error?.message ?? `HTTP ${request.status}`));
        return;
      }
      if (!body?.asset_key) {
        reject(new Error("上传服务返回了无效结果"));
        return;
      }
      resolve(body);
    };
    request.send(file);
  }),
  createCreator: (body: Record<string, unknown>, idempotencyKey = idem()) =>
    req<CreatorProfile>("/creators", { method: "POST", body: JSON.stringify(body), headers: { "Idempotency-Key": idempotencyKey } }),
  creatorByHandle: (handle: string) => req<CreatorProfile>(`/creators/by-handle/${handle}`),
  creatorPage: (creatorId: string) => req<CreatorPage>(`/creators/${creatorId}/page`),
  track: (id: string) => req<TrackDto>(`/tracks/${id}`),
  createTrack: (body: Record<string, unknown>, idempotencyKey = idem()) =>
    req<TrackDto>("/tracks", { method: "POST", body: JSON.stringify(body), headers: { "Idempotency-Key": idempotencyKey } }),
  createVersion: (trackId: string, body: Record<string, unknown>, idempotencyKey = idem()) =>
    req<TrackDto>(`/tracks/${trackId}/versions`, { method: "POST", body: JSON.stringify(body), headers: { "Idempotency-Key": idempotencyKey } }),
  upsertPassport: (trackId: string, body: Record<string, unknown>, idempotencyKey = idem()) =>
    req<Record<string, unknown>>(`/tracks/${trackId}/passport`, { method: "PUT", body: JSON.stringify(body), headers: { "Idempotency-Key": idempotencyKey } }),
  publish: (trackId: string, idempotencyKey = idem()) =>
    req<TrackDto>(`/tracks/${trackId}/publish`, { method: "POST", body: JSON.stringify({}), headers: { "Idempotency-Key": idempotencyKey } }),
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

export type DraftStage = {
  track_id: string;
  stage: "draft" | "version_ready" | "passport_ready" | "published" | "archived";
  next_action: string;
  title: string;
  status: string;
  has_version: boolean;
  has_passport: boolean;
  version: { id: string; version_no: number; audio_asset_key: string | null } | null;
};

export type ResumeState = {
  track: TrackDto;
  stage: string;
  next_action: string;
  media: { asset_key: string; sha256?: string | null; bytes?: number | null; mime_type?: string | null } | null;
  passport: Record<string, unknown> | null;
};

export const lifecycle = {
  myDrafts: (creatorId: string) => req<{ drafts: DraftStage[] }>(`/creators/${creatorId}/drafts`),
  resume: (trackId: string) => req<ResumeState>(`/drafts/${trackId}/resume`),
  abandon: (trackId: string) => req<{ status: string }>(`/drafts/${trackId}/abandon`, { method: "POST", body: JSON.stringify({}) }),
  mediaReferences: () => req<{ references: string[] }>("/media/references"),
};

export const library = {
  myFavorites: (userId: string, cursor?: string) =>
    req<{ tracks: TrackDto[]; next_cursor: string | null }>(`/users/${userId}/favorites${cursor ? `?cursor=${cursor}` : ""}`),
  myRecentPlays: (userId: string) =>
    req<{ tracks: TrackDto[] }>(`/users/${userId}/recent-plays`),
};

export type SearchTrack = {
  id: string; title: string; creator_id: string; primary_language: string | null;
  duration_ms: number | null; published_at: string | null; audio_asset_key: string | null;
};

export type SearchCreator = {
  id: string; handle: string; display_name: string; bio: string | null; avatar_asset_key: string | null;
};

export const search = {
  tracks: (q: string, limit = 10) =>
    req<{ tracks: SearchTrack[] }>(`/search?q=${encodeURIComponent(q)}&type=track&limit=${limit}`),
  creators: (q: string, limit = 10) =>
    req<{ creators: SearchCreator[] }>(`/search?q=${encodeURIComponent(q)}&type=creator&limit=${limit}`),
};

export type ConsoleTrack = {
  id: string; title: string; status: string; visibility: string;
  primary_language: string | null; duration_ms: number | null;
  published_at: string | null; updated_at: string | null; stage: string;
};

export const consoleApi = {
  myTracks: (creatorId: string, status?: string) =>
    req<{ tracks: ConsoleTrack[] }>(`/creators/${creatorId}/tracks${status ? `?status=${status}` : ""}`),
  updateTrack: (trackId: string, body: Record<string, unknown>, ifMatch?: string) =>
    req<TrackDto>(`/tracks/${trackId}`, {
      method: "PATCH", body: JSON.stringify(body),
      headers: ifMatch ? { "If-Match": ifMatch } : {},
    }),
  unpublish: (trackId: string) =>
    req<{ status: string; public_url_live: boolean }>(`/tracks/${trackId}/unpublish`, { method: "POST", body: JSON.stringify({}) }),
};

export type PlaylistDto = {
  id: string; owner_user_id: string; title: string; visibility: string;
  created_at: string | null; updated_at: string | null;
  items: { track_id: string; position: number; added_at: string | null }[];
};

export const playlists = {
  mine: (userId: string) => req<{ playlists: PlaylistDto[] }>(`/users/${userId}/playlists`),
  create: (body: Record<string, unknown>) =>
    req<PlaylistDto>("/playlists", { method: "POST", body: JSON.stringify(body), headers: { "Idempotency-Key": idem() } }),
  get: (id: string) => req<PlaylistDto>(`/playlists/${id}`),
  update: (id: string, body: Record<string, unknown>) =>
    req<PlaylistDto>(`/playlists/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  remove: (id: string) => req<{ deleted: string }>(`/playlists/${id}`, { method: "DELETE" }),
  addItem: (id: string, trackId: string) =>
    req<{ playlist_id: string; track_id: string; position: number }>(`/playlists/${id}/items`, {
      method: "POST", body: JSON.stringify({ track_id: trackId }), headers: { "Idempotency-Key": idem() },
    }),
  removeItem: (id: string, trackId: string) =>
    req<{ removed: boolean }>(`/playlists/${id}/items/${trackId}`, { method: "DELETE" }),
};
