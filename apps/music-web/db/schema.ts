import { sql } from "drizzle-orm";
import { index, integer, primaryKey, sqliteTable, text, uniqueIndex } from "drizzle-orm/sqlite-core";

const timestamps = {
  createdAt: text("created_at").notNull().default(sql`CURRENT_TIMESTAMP`),
  updatedAt: text("updated_at").notNull().default(sql`CURRENT_TIMESTAMP`),
};

export const users = sqliteTable("users", {
  id: text("id").primaryKey(),
  authSubject: text("auth_subject").notNull().unique(),
  email: text("email"),
  displayName: text("display_name").notNull(),
  avatarUrl: text("avatar_url"),
  status: text("status", { enum: ["active", "suspended", "deleted"] }).notNull().default("active"),
  ...timestamps,
}, (table) => [uniqueIndex("users_email_unique").on(table.email)]);

export const creatorProfiles = sqliteTable("creator_profiles", {
  id: text("id").primaryKey(),
  userId: text("user_id").notNull().references(() => users.id, { onDelete: "cascade" }),
  handle: text("handle").notNull().unique(),
  displayName: text("display_name").notNull(),
  bio: text("bio").notNull().default(""),
  avatarUrl: text("avatar_url"),
  heroImageUrl: text("hero_image_url"),
  location: text("location"),
  isPublic: integer("is_public", { mode: "boolean" }).notNull().default(true),
  ...timestamps,
}, (table) => [uniqueIndex("creator_profiles_user_unique").on(table.userId)]);

export const tracks = sqliteTable("tracks", {
  id: text("id").primaryKey(),
  creatorId: text("creator_id").notNull().references(() => creatorProfiles.id, { onDelete: "restrict" }),
  title: text("title").notNull(),
  description: text("description").notNull().default(""),
  language: text("language"),
  status: text("status", { enum: ["draft", "published", "unlisted", "withdrawn"] }).notNull().default("draft"),
  sourceType: text("source_type", { enum: ["ai", "human", "hybrid"] }).notNull(),
  licenseStatus: text("license_status", { enum: ["not_available", "inquiry"] }).notNull().default("not_available"),
  currentVersionId: text("current_version_id"),
  publishedAt: text("published_at"),
  ...timestamps,
}, (table) => [index("tracks_creator_status_idx").on(table.creatorId, table.status)]);

export const trackVersions = sqliteTable("track_versions", {
  id: text("id").primaryKey(),
  trackId: text("track_id").notNull().references(() => tracks.id, { onDelete: "cascade" }),
  versionLabel: text("version_label").notNull(),
  audioObjectKey: text("audio_object_key").notNull(),
  audioSha256: text("audio_sha256").notNull(),
  audioBytes: integer("audio_bytes").notNull(),
  mimeType: text("mime_type").notNull(),
  durationMs: integer("duration_ms"),
  coverObjectKey: text("cover_object_key"),
  earProductionCaseId: text("ear_production_case_id"),
  earEvidenceArtifactId: text("ear_evidence_artifact_id"),
  createdAt: text("created_at").notNull().default(sql`CURRENT_TIMESTAMP`),
}, (table) => [uniqueIndex("track_versions_track_label_unique").on(table.trackId, table.versionLabel)]);

export const creationPassports = sqliteTable("creation_passports", {
  id: text("id").primaryKey(),
  trackVersionId: text("track_version_id").notNull().unique().references(() => trackVersions.id, { onDelete: "cascade" }),
  aiTool: text("ai_tool"),
  modelVersion: text("model_version"),
  promptDisclosure: text("prompt_disclosure", { enum: ["private", "partial", "public"] }).notNull().default("private"),
  promptText: text("prompt_text"),
  lyricsAuthor: text("lyrics_author"),
  vocalSource: text("vocal_source"),
  humanEditing: text("human_editing"),
  dawTools: text("daw_tools"),
  collaborators: text("collaborators"),
  rightsStatement: text("rights_statement").notNull(),
  ...timestamps,
});

export const creatorFollows = sqliteTable("creator_follows", {
  followerUserId: text("follower_user_id").notNull().references(() => users.id, { onDelete: "cascade" }),
  creatorId: text("creator_id").notNull().references(() => creatorProfiles.id, { onDelete: "cascade" }),
  createdAt: text("created_at").notNull().default(sql`CURRENT_TIMESTAMP`),
}, (table) => [primaryKey({ columns: [table.followerUserId, table.creatorId] }), index("creator_follows_creator_idx").on(table.creatorId)]);

export const trackFavorites = sqliteTable("track_favorites", {
  userId: text("user_id").notNull().references(() => users.id, { onDelete: "cascade" }),
  trackId: text("track_id").notNull().references(() => tracks.id, { onDelete: "cascade" }),
  createdAt: text("created_at").notNull().default(sql`CURRENT_TIMESTAMP`),
}, (table) => [primaryKey({ columns: [table.userId, table.trackId] }), index("track_favorites_track_idx").on(table.trackId)]);

export const licenseIntents = sqliteTable("license_intents", {
  id: text("id").primaryKey(),
  requesterUserId: text("requester_user_id").references(() => users.id, { onDelete: "set null" }),
  requesterEmail: text("requester_email").notNull(),
  trackId: text("track_id").notNull().references(() => tracks.id, { onDelete: "restrict" }),
  usageType: text("usage_type").notNull(),
  territory: text("territory"),
  term: text("term"),
  budgetRange: text("budget_range"),
  message: text("message").notNull(),
  status: text("status", { enum: ["new", "contacted", "negotiating", "closed_won", "closed_lost"] }).notNull().default("new"),
  ...timestamps,
}, (table) => [index("license_intents_track_status_idx").on(table.trackId, table.status)]);

export const supportIntents = sqliteTable("support_intents", {
  id: text("id").primaryKey(),
  supporterUserId: text("supporter_user_id").references(() => users.id, { onDelete: "set null" }),
  creatorId: text("creator_id").notNull().references(() => creatorProfiles.id, { onDelete: "restrict" }),
  trackId: text("track_id").references(() => tracks.id, { onDelete: "set null" }),
  amountMinor: integer("amount_minor"),
  currency: text("currency"),
  provider: text("provider"),
  providerTxnId: text("provider_txn_id"),
  status: text("status", { enum: ["intent", "pending", "paid", "failed", "refunded"] }).notNull().default("intent"),
  createdAt: text("created_at").notNull().default(sql`CURRENT_TIMESTAMP`),
  updatedAt: text("updated_at").notNull().default(sql`CURRENT_TIMESTAMP`),
}, (table) => [index("support_intents_creator_status_idx").on(table.creatorId, table.status)]);

export const listenEvents = sqliteTable("listen_events", {
  id: text("id").primaryKey(),
  trackId: text("track_id").notNull().references(() => tracks.id, { onDelete: "cascade" }),
  userId: text("user_id").references(() => users.id, { onDelete: "set null" }),
  anonymousSessionId: text("anonymous_session_id"),
  startedAt: text("started_at").notNull(),
  listenedMs: integer("listened_ms").notNull().default(0),
  completionPermille: integer("completion_permille").notNull().default(0),
  sourceSurface: text("source_surface").notNull(),
}, (table) => [index("listen_events_track_started_idx").on(table.trackId, table.startedAt)]);

export const publicationEvents = sqliteTable("publication_events", {
  id: text("id").primaryKey(),
  trackId: text("track_id").notNull().references(() => tracks.id, { onDelete: "cascade" }),
  actorUserId: text("actor_user_id").notNull().references(() => users.id, { onDelete: "restrict" }),
  fromStatus: text("from_status"),
  toStatus: text("to_status").notNull(),
  reason: text("reason"),
  createdAt: text("created_at").notNull().default(sql`CURRENT_TIMESTAMP`),
}, (table) => [index("publication_events_track_created_idx").on(table.trackId, table.createdAt)]);
