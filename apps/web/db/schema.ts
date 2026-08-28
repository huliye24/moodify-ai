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

/* MOOD-GENESIS-002: Genesis Participant Registry — wallet-signature only.
   Additive, non-destructive. Race-safe participant numbering via UNIQUE index
   + INSERT-time allocation (see docs/protocol/GENESIS_REGISTRATION.md).

   MOOD-GENESIS-003: Added `contribution_score` as a simple administrative
   score kept consistent with `reputation_events` (source of truth).

   MOOD-GENESIS-004: Added allocation fields for distribution engine.

   MOOD-GENESIS-006: Added cached `reputation_score` aggregate (sum of
   reputation_events.points_delta). Source of truth remains
   `reputation_events`. Never overwritten by contribution rewards directly —
   the events table is the only allowed mutation surface. */
export const genesisParticipants = sqliteTable("genesis_participants", {
  id: text("id").primaryKey(),
  participantNumber: integer("participant_number").notNull().unique(),
  walletAddress: text("wallet_address").notNull(),
  walletAddressNormalized: text("wallet_address_normalized").notNull().unique(),
  chainId: integer("chain_id").notNull(),
  joinedAt: text("joined_at").notNull().default(sql`CURRENT_TIMESTAMP`),
  status: text("status", { enum: ["registered", "reviewed", "eligible", "allocated", "distributed"] }).notNull().default("registered"),
  /** Allocation amount in MOOD (decimal string). Set by Package 003. */
  allocationMood: text("allocation_mood"),
  /** Allocation amount in atomic units (bigint string). Denormalized for efficiency. */
  allocationAtomic: text("allocation_atomic"),
  /** Reason for allocation (optional audit trail). */
  allocationReason: text("allocation_reason"),
  /** When allocation was set (ISO timestamp). */
  allocatedAt: text("allocated_at"),
  /** Cached admin contribution score (Package 003). Mutated only with an
      accompanying event/reason; default 0 for new participants. */
  contributionScore: integer("contribution_score").notNull().default(0),
  /** Cached aggregate Reputation from `reputation_events` (Package 006).
      Must equal SUM(points_delta) for the participant. */
  reputationScore: integer("reputation_score").notNull().default(0),
  signatureVersion: text("signature_version").notNull(),
  termsVersion: text("terms_version").notNull(),
  createdAt: text("created_at").notNull().default(sql`CURRENT_TIMESTAMP`),
  updatedAt: text("updated_at").notNull().default(sql`CURRENT_TIMESTAMP`),
}, (table) => [
  index("genesis_participants_wallet_idx").on(table.walletAddressNormalized),
  index("genesis_participants_joined_idx").on(table.joinedAt),
  index("genesis_participants_status_idx").on(table.status),
]);

/* MOOD-GENESIS-002: server-issued nonces. The raw nonce is only ever persisted
   as a SHA-256 hash (`nonce_hash`); the random bytes never leave the server
   response. Marking `used_at` atomically prevents replay. */
export const genesisNonces = sqliteTable("genesis_nonces", {
  id: text("id").primaryKey(),
  walletAddressNormalized: text("wallet_address_normalized").notNull(),
  nonceHash: text("nonce_hash").notNull().unique(),
  issuedAt: text("issued_at").notNull(),
  expiresAt: text("expires_at").notNull(),
  usedAt: text("used_at"),
  chainId: integer("chain_id").notNull(),
  termsVersion: text("terms_version").notNull(),
  createdAt: text("created_at").notNull().default(sql`CURRENT_TIMESTAMP`),
}, (table) => [
  index("genesis_nonces_wallet_idx").on(table.walletAddressNormalized),
  index("genesis_nonces_expires_idx").on(table.expiresAt),
]);

/* MOOD-GENESIS-006: Contribution Network.

   This section adds the public/private contribution system on top of the
   existing Genesis identity and admin authorization. No on-chain transfer,
   no token approval, no wallet signing. All values are off-chain.

   Tables:
   - contribution_tasks            — public task catalog
   - contribution_submissions      — per-participant submissions
   - contribution_review_events    — append-only review history
   - reputation_events             — append-only Reputation source of truth
   - reward_events                 — append-only pending MOOD reward ledger

   Genesis allocation is NEVER overwritten by contribution rewards:
   `reward_events` is a separate ledger that downstream distribution
   snapshots can consume (Package 004/005 integration). */

export const contributionTasks = sqliteTable("contribution_tasks", {
  id: text("id").primaryKey(),
  slug: text("slug").notNull().unique(),
  title: text("title").notNull(),
  summary: text("summary").notNull().default(""),
  description: text("description").notNull().default(""),
  /** Controlled category; see lib/contribution-config.ts */
  category: text("category").notNull(),
  /** draft | active | paused | completed | archived */
  status: text("status", { enum: ["draft", "active", "paused", "completed", "archived"] }).notNull().default("draft"),
  /** Free-form requirements text; never executed. */
  requirements: text("requirements").notNull().default(""),
  /** Free-form evidence instructions text. */
  evidenceInstructions: text("evidence_instructions").notNull().default(""),
  /** Default reward points (admin-set; reviewer may override at approval). */
  rewardPointsDefault: integer("reward_points_default").notNull().default(0),
  /** Default pending MOOD reward (decimal string, e.g., "100"). */
  rewardMoodDefault: text("reward_mood_default"),
  /** Atomic units (bigint string) — denormalized for fast queries. */
  rewardMoodAtomicDefault: text("reward_mood_atomic_default"),
  /** Optional deadline (ISO timestamp). */
  deadline: text("deadline"),
  /** Optional cap on number of approvals. */
  maxApprovals: integer("max_approvals"),
  /** Whether duplicate submissions per (task, participant) are allowed. */
  allowDuplicateSubmissions: integer("allow_duplicate_submissions", { mode: "boolean" }).notNull().default(false),
  /** Terms version acknowledged at submission. */
  termsVersion: text("terms_version").notNull().default("contribution-v1"),
  /** Authoring admin display id (subject string, never an email/password). */
  createdBy: text("created_by").notNull(),
  createdAt: text("created_at").notNull().default(sql`CURRENT_TIMESTAMP`),
  updatedAt: text("updated_at").notNull().default(sql`CURRENT_TIMESTAMP`),
  /** Set when the task is activated for the first time. */
  publishedAt: text("published_at"),
}, (table) => [
  index("contribution_tasks_status_idx").on(table.status),
  index("contribution_tasks_category_idx").on(table.category),
  index("contribution_tasks_published_idx").on(table.publishedAt),
]);

export const contributionSubmissions = sqliteTable("contribution_submissions", {
  id: text("id").primaryKey(),
  taskId: text("task_id").notNull().references(() => contributionTasks.id, { onDelete: "restrict" }),
  participantId: text("participant_id").notNull().references(() => genesisParticipants.id, { onDelete: "restrict" }),
  /** submitted | under_review | changes_requested | approved | rejected | withdrawn */
  status: text("status", { enum: ["submitted", "under_review", "changes_requested", "approved", "rejected", "withdrawn"] }).notNull().default("submitted"),
  summary: text("summary").notNull().default(""),
  evidenceText: text("evidence_text").notNull().default(""),
  /** JSON-encoded array of strings. */
  evidenceUrlsJson: text("evidence_urls_json").notNull().default("[]"),
  /** Revision counter; incremented every time a contributor resubmits. */
  revisionNumber: integer("revision_number").notNull().default(1),
  submittedAt: text("submitted_at").notNull().default(sql`CURRENT_TIMESTAMP`),
  updatedAt: text("updated_at").notNull().default(sql`CURRENT_TIMESTAMP`),
  reviewedAt: text("reviewed_at"),
  reviewerId: text("reviewer_id"),
  /** Reviewer's free-form note attached to the latest review action. */
  reviewNote: text("review_note"),
}, (table) => [
  index("contribution_submissions_task_idx").on(table.taskId),
  index("contribution_submissions_participant_idx").on(table.participantId),
  index("contribution_submissions_status_idx").on(table.status),
  index("contribution_submissions_submitted_idx").on(table.submittedAt),
]);

export const contributionReviewEvents = sqliteTable("contribution_review_events", {
  id: text("id").primaryKey(),
  submissionId: text("submission_id").notNull().references(() => contributionSubmissions.id, { onDelete: "restrict" }),
  /** Reviewer admin display id; recorded for audit. */
  actorId: text("actor_id").notNull(),
  /** created | status_change | changes_requested | approved | rejected | withdrawn | reopened */
  eventType: text("event_type").notNull(),
  oldStatus: text("old_status"),
  newStatus: text("new_status"),
  /** Reputation points delta attached to this event (zero for non-approval). */
  pointsDelta: integer("points_delta").notNull().default(0),
  /** Reward (decimal string) attached to this event; zero for non-approval. */
  rewardMood: text("reward_mood").notNull().default("0"),
  /** Reward (atomic units, bigint string) attached to this event; zero for non-approval. */
  rewardAtomic: text("reward_atomic").notNull().default("0"),
  reason: text("reason").notNull().default(""),
  createdAt: text("created_at").notNull().default(sql`CURRENT_TIMESTAMP`),
}, (table) => [
  index("contribution_review_events_submission_idx").on(table.submissionId),
  index("contribution_review_events_actor_idx").on(table.actorId),
  index("contribution_review_events_created_idx").on(table.createdAt),
]);

export const reputationEvents = sqliteTable("reputation_events", {
  id: text("id").primaryKey(),
  participantId: text("participant_id").notNull().references(() => genesisParticipants.id, { onDelete: "restrict" }),
  /** Nullable: reviewer may also record reputation adjustments outside a single submission. */
  submissionId: text("submission_id"),
  /** approval | rollback | manual_adjust */
  eventType: text("event_type").notNull(),
  pointsDelta: integer("points_delta").notNull(),
  reason: text("reason").notNull().default(""),
  /** Admin actor id for audit. */
  actorId: text("actor_id").notNull(),
  createdAt: text("created_at").notNull().default(sql`CURRENT_TIMESTAMP`),
}, (table) => [
  index("reputation_events_participant_idx").on(table.participantId),
  index("reputation_events_submission_idx").on(table.submissionId),
  index("reputation_events_created_idx").on(table.createdAt),
]);

export const rewardEvents = sqliteTable("reward_events", {
  id: text("id").primaryKey(),
  participantId: text("participant_id").notNull().references(() => genesisParticipants.id, { onDelete: "restrict" }),
  submissionId: text("submission_id").references(() => contributionSubmissions.id, { onDelete: "restrict" }),
  taskId: text("task_id").references(() => contributionTasks.id, { onDelete: "restrict" }),
  /** Decimal string (human-readable MOOD). */
  rewardMood: text("reward_mood").notNull(),
  /** Atomic units (bigint string). */
  rewardAtomic: text("reward_atomic").notNull(),
  /** pending | included_in_snapshot | distributed | cancelled */
  status: text("status", { enum: ["pending", "included_in_snapshot", "distributed", "cancelled"] }).notNull().default("pending"),
  reason: text("reason").notNull().default(""),
  approvedBy: text("approved_by").notNull(),
  /** Set when a future distribution snapshot consumes this reward. */
  distributionSnapshotId: text("distribution_snapshot_id"),
  createdAt: text("created_at").notNull().default(sql`CURRENT_TIMESTAMP`),
}, (table) => [
  index("reward_events_participant_idx").on(table.participantId),
  index("reward_events_task_idx").on(table.taskId),
  index("reward_events_status_idx").on(table.status),
  index("reward_events_submission_idx").on(table.submissionId),
]);
