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

// Contribution Network tables
export const contributionTasks = sqliteTable("contribution_tasks", {
  id: text("id").primaryKey(),
  slug: text("slug").notNull().unique(),
  title: text("title").notNull(),
  summary: text("summary").notNull(),
  description: text("description").notNull(),
  category: text("category", {
    enum: ["code", "audio-testing", "dataset", "research", "documentation", "translation", "bug-report", "community", "other"]
  }).notNull(),
  status: text("status", { enum: ["draft", "active", "paused", "completed", "archived"] }).notNull().default("draft"),
  evidenceRequirements: text("evidence_requirements", { mode: "json" }).notNull().default(sql`'[]'`),
  defaultReputationPoints: integer("default_reputation_points").notNull().default(100),
  defaultRewardUnits: text("default_reward_units"),
  deadline: text("deadline"),
  maxApprovals: integer("max_approvals"),
  createdAt: text("created_at").notNull().default(sql`CURRENT_TIMESTAMP`),
  updatedAt: text("updated_at").notNull().default(sql`CURRENT_TIMESTAMP`),
}, (table) => [index("contribution_tasks_category_status_idx").on(table.category, table.status)]);

export const contributionSubmissions = sqliteTable("contribution_submissions", {
  id: text("id").primaryKey(),
  taskId: text("task_id").notNull().references(() => contributionTasks.id, { onDelete: "cascade" }),
  residentId: text("resident_id").notNull(),
  summary: text("summary").notNull(),
  evidenceText: text("evidence_text"),
  status: text("status", {
    enum: ["submitted", "under_review", "changes_requested", "approved", "rejected", "withdrawn"]
  }).notNull().default("submitted"),
  revision: integer("revision").notNull().default(1),
  evidenceUrls: text("evidence_urls", { mode: "json" }).default(sql`'[]'`),
  githubPrUrl: text("github_pr_url"),
  githubCommitHash: text("github_commit_hash"),
  demoUrl: text("demo_url"),
  documentUrl: text("document_url"),
  createdAt: text("created_at").notNull().default(sql`CURRENT_TIMESTAMP`),
  updatedAt: text("updated_at").notNull().default(sql`CURRENT_TIMESTAMP`),
}, (table) => [
  index("contribution_submissions_task_status_idx").on(table.taskId, table.status),
  index("contribution_submissions_resident_idx").on(table.residentId)
]);

export const contributionReviewEvents = sqliteTable("contribution_review_events", {
  id: text("id").primaryKey(),
  submissionId: text("submission_id").notNull().references(() => contributionSubmissions.id, { onDelete: "cascade" }),
  reviewerId: text("reviewer_id").notNull(),
  fromStatus: text("from_status").notNull(),
  toStatus: text("to_status").notNull(),
  comment: text("comment"),
  createdAt: text("created_at").notNull().default(sql`CURRENT_TIMESTAMP`),
}, (table) => [
  index("contribution_review_events_submission_created_idx").on(table.submissionId, table.createdAt),
  index("contribution_review_events_reviewer_idx").on(table.reviewerId)
]);

export const reputationEvents = sqliteTable("reputation_events", {
  id: text("id").primaryKey(),
  submissionId: text("submission_id").notNull().references(() => contributionSubmissions.id, { onDelete: "cascade" }),
  residentId: text("resident_id").notNull(),
  points: integer("points").notNull(),
  evidenceType: text("evidence_type").notNull(),
  notes: text("notes"),
  createdAt: text("created_at").notNull().default(sql`CURRENT_TIMESTAMP`),
}, (table) => [
  index("reputation_events_resident_created_idx").on(table.residentId, table.createdAt),
  index("reputation_events_submission_idx").on(table.submissionId)
]);

export const rewardEvents = sqliteTable("reward_events", {
  id: text("id").primaryKey(),
  submissionId: text("submission_id").notNull().references(() => contributionSubmissions.id, { onDelete: "cascade" }),
  residentId: text("resident_id").notNull(),
  amountMinor: integer("amount_minor").notNull(),
  currency: text("currency").notNull().default("MOOD"),
  status: text("status", { enum: ["pending", "processing", "completed", "failed"] }).notNull().default("pending"),
  txHash: text("tx_hash"),
  processedAt: text("processed_at"),
  createdAt: text("created_at").notNull().default(sql`CURRENT_TIMESTAMP`),
  updatedAt: text("updated_at").notNull().default(sql`CURRENT_TIMESTAMP`),
}, (table) => [
  index("reward_events_resident_status_idx").on(table.residentId, table.status),
  index("reward_events_submission_idx").on(table.submissionId)
]);

export const genesisParticipants = sqliteTable("genesis_participants", {
  id: text("id").primaryKey(),
  residentId: text("resident_id").notNull().unique(),
  walletAddress: text("wallet_address").notNull(),
  reputationScore: integer("reputation_score").notNull().default(0),
  isGenesis: integer("is_genesis", { mode: "boolean" }).notNull().default(true),
  joinedAt: text("joined_at").notNull().default(sql`CURRENT_TIMESTAMP`),
  lastActivityAt: text("last_activity_at"),
  metadata: text("metadata", { mode: "json" }).default(sql`'{}'`),
}, (table) => [
  index("genesis_participants_reputation_idx").on(table.reputationScore),
  index("genesis_participants_joined_idx").on(table.joinedAt)
]);

export const genesisNonces = sqliteTable("genesis_nonces", {
  id: text("id").primaryKey(),
  nonce: text("nonce").notNull().unique(),
  walletAddress: text("wallet_address").notNull(),
  issuedAt: text("issued_at").notNull().default(sql`CURRENT_TIMESTAMP`),
  expiresAt: text("expires_at").notNull(),
  usedAt: text("used_at"),
  termsVersion: text("terms_version").notNull(),
  signatureVersion: text("signature_version").notNull(),
  chainId: integer("chain_id").notNull(),
  domain: text("domain").notNull(),
}, (table) => [
  index("genesis_nonces_address_expires_idx").on(table.walletAddress, table.expiresAt),
  index("genesis_nonces_used_idx").on(table.usedAt)
]);

// MOOD Node Registry Tables
export const nodes = sqliteTable("nodes", {
  id: text("id").primaryKey(),
  slug: text("slug").notNull().unique(),
  name: text("name").notNull(),
  description: text("description").default(""),

  // Identity Management
  stableId: text("stable_id").notNull(),
  nodeIdAlias: text("node_id_alias"),
  publicKey: text("public_key"),
  ipHash: text("ip_hash"),

  // Node Roles
  role: text("role", {
    enum: ["compute", "ai", "storage", "verification"]
  }).notNull(),

  // Node Status
  status: text("status", {
    enum: ["draft", "active", "degraded", "offline", "maintenance", "retired"]
  }).notNull().default("draft"),

  // Cloud Provider Information
  cloudProvider: text("cloud_provider"),
  region: text("region"),
  availabilityZone: text("availability_zone"),

  // Machine Configuration
  instanceType: text("instance_type"),
  hostname: text("hostname"),
  operatingSystem: text("operating_system"),
  kernelVersion: text("kernel_version"),

  // Capacity Fields
  cpuCores: integer("cpu_cores"),
  cpuModel: text("cpu_model"),
  memoryGB: integer("memory_gb"),
  storageGB: integer("storage_gb"),
  bandwidthMbps: integer("bandwidth_mbps"),

  // GPU Support
  hasGPU: integer("has_gpu", { mode: "boolean" }).default(false),
  gpuCount: integer("gpu_count").default(0),
  gpuModel: text("gpu_model"),
  gpuMemoryGB: integer("gpu_memory_gb").default(0),

  // Geographic Information
  country: text("country"),
  city: text("city"),
  latitude: text("latitude"),
  longitude: text("longitude"),

  // Operator Information
  operatorType: text("operator_type", {
    enum: ["resident", "organization"]
  }),
  operatorResidentId: text("operator_resident_id"),
  operatorOrganizationId: text("operator_organization_id"),

  // Timestamps
  ...timestamps,
  lastHeartbeatAt: text("last_heartbeat_at"),
  lastSyncAt: text("last_sync_at"),

  // Metadata
  metadata: text("metadata", { mode: "json" }).default(sql`'{}'`),
  tags: text("tags", { mode: "json" }).default(sql`'[]'`),
}, (table) => [
  index("nodes_role_status_idx").on(table.role, table.status),
  index("nodes_operator_resident_idx").on(table.operatorResidentId),
  index("nodes_operator_org_idx").on(table.operatorOrganizationId),
  index("nodes_cloud_provider_idx").on(table.cloudProvider),
  index("nodes_created_idx").on(table.createdAt),
  index("nodes_last_heartbeat_idx").on(table.lastHeartbeatAt),
]);

export const nodeCapacityHistory = sqliteTable("node_capacity_history", {
  id: text("id").primaryKey(),
  nodeId: text("node_id").notNull().references(() => nodes.id, { onDelete: "cascade" }),

  // Timestamp
  recordedAt: text("recorded_at").notNull().default(sql`CURRENT_TIMESTAMP`),

  // Capacity Metrics
  cpuUsagePercent: integer("cpu_usage_percent"),
  memoryUsagePercent: integer("memory_usage_percent"),
  storageUsagePercent: integer("storage_usage_percent"),
  networkInMbps: integer("network_in_mbps"),
  networkOutMbps: integer("network_out_mbps"),

  // Process Count
  processCount: integer("process_count").default(0),

  // Load Average
  loadAvg1: text("load_avg_1"),
  loadAvg5: text("load_avg_5"),
  loadAvg15: text("load_avg_15"),

  // Disk I/O
  diskReadKBs: integer("disk_read_kbs"),
  diskWriteKBs: integer("disk_write_kbs"),

  // System Information
  uptimeSeconds: integer("uptime_seconds"),
  temperature: integer("temperature"),

  // Metadata
  metadata: text("metadata", { mode: "json" }).default(sql`'{}'`),
}, (table) => [
  index("node_capacity_history_node_idx").on(table.nodeId),
  index("node_capacity_history_recorded_idx").on(table.recordedAt),
]);

export const nodeHealth = sqliteTable("node_health", {
  id: text("id").primaryKey(),
  nodeId: text("node_id").notNull().references(() => nodes.id, { onDelete: "cascade" }),

  // Health Status
  status: text("status", {
    enum: ["healthy", "degraded", "unhealthy", "unknown"]
  }).notNull(),

  // Check Timestamp
  checkedAt: text("checked_at").notNull().default(sql`CURRENT_TIMESTAMP`),

  // Latency Measurements
  apiLatencyMs: integer("api_latency_ms"),
  dbLatencyMs: integer("db_latency_ms"),
  externalServiceLatencyMs: integer("external_service_latency_ms"),

  // Service Availability
  servicesAvailable: integer("services_available", { mode: "boolean" }).default(true),
  criticalServicesHealthy: integer("critical_services_healthy", { mode: "boolean" }).default(true),

  // Error Counts
  errorCount24h: integer("error_count_24h").default(0),
  warningCount24h: integer("warning_count_24h").default(0),

  // Resource Thresholds
  cpuThreshold: integer("cpu_threshold").default(90),
  memoryThreshold: integer("memory_threshold").default(90),
  diskThreshold: integer("disk_threshold").default(90),

  // Health Score
  healthScore: integer("health_score").default(100),

  // Details
  details: text("details", { mode: "json" }).default(sql`'{}'`),
  recommendations: text("recommendations", { mode: "json" }).default(sql`'[]'`),

  // Maintenance Windows
  inMaintenanceWindow: integer("in_maintenance_window", { mode: "boolean" }).default(false),
  maintenanceReason: text("maintenance_reason"),
}, (table) => [
  index("node_health_node_idx").on(table.nodeId),
  index("node_health_checked_idx").on(table.checkedAt),
  index("node_health_status_idx").on(table.status),
]);

export const nodeServiceProofs = sqliteTable("node_service_proofs", {
  id: text("id").primaryKey(),
  nodeId: text("node_id").notNull().references(() => nodes.id, { onDelete: "cascade" }),

  // Proof Type
  proofType: text("proof_type", {
    enum: ["health", "capacity", "performance", "security", "compliance", "custom"]
  }).notNull(),

  // Proof Status
  status: text("status", {
    enum: ["pending", "validating", "verified", "failed", "expired"]
  }).notNull().default("pending"),

  // Proof Metadata
  proofId: text("proof_id").notNull().unique(),
  proofVersion: text("proof_version").default("1.0"),

  // Timestamps
  ...timestamps,
  validatedAt: text("validated_at"),
  expiresAt: text("expires_at"),

  // Proof Data
  proofData: text("proof_data", { mode: "json" }).notNull(),
  validationResult: text("validation_result", { mode: "json" }),
  verificationMethod: text("verification_method"),

  // Validator Information
  validatorId: text("validator_id"),
  validatorSignature: text("validator_signature"),

  // Error Information
  errorType: text("error_type"),
  errorMessage: text("error_message"),

  // Metadata
  metadata: text("metadata", { mode: "json" }).default(sql`'{}'`),
}, (table) => [
  index("node_service_proofs_node_idx").on(table.nodeId),
  index("node_service_proofs_type_idx").on(table.proofType),
  index("node_service_proofs_status_idx").on(table.status),
  index("node_service_proofs_expires_idx").on(table.expiresAt),
]);

export const nodeEvents = sqliteTable("node_events", {
  id: text("id").primaryKey(),
  nodeId: text("node_id").notNull().references(() => nodes.id, { onDelete: "cascade" }),

  // Event Type
  eventType: text("event_type", {
    enum: [
      "node_created", "node_updated", "node_deleted",
      "status_changed", "heartbeat_received", "heartbeat_missed",
      "capacity_updated", "health_check", "service_proof_created",
      "service_proof_verified", "service_proof_failed", "maintenance_started",
      "maintenance_ended", "alert_triggered", "alert_resolved"
    ]
  }).notNull(),

  // Event Data
  eventData: text("event_data", { mode: "json" }).default(sql`'{}'`),

  // Timestamp
  timestamp: text("timestamp").notNull().default(sql`CURRENT_TIMESTAMP`),

  // Severity Level
  severity: text("severity", {
    enum: ["info", "warning", "error", "critical"]
  }).default("info"),

  // User/Agent Responsible
  actorType: text("actor_type", {
    enum: ["system", "operator", "admin", "user"]
  }),
  actorId: text("actor_id"),

  // Related Information
  correlationId: text("correlation_id"),
  referenceId: text("reference_id"),

  // Metadata
  metadata: text("metadata", { mode: "json" }).default(sql`'{}'`),
}, (table) => [
  index("node_events_node_idx").on(table.nodeId),
  index("node_events_type_idx").on(table.eventType),
  index("node_events_timestamp_idx").on(table.timestamp),
  index("node_events_severity_idx").on(table.severity),
]);

export const operators = sqliteTable("operators", {
  id: text("id").primaryKey(),

  // Operator Type
  type: text("type", {
    enum: ["resident", "organization"]
  }).notNull(),

  // Resident Operator Fields
  residentId: text("resident_id"),

  // Organization Operator Fields
  organizationId: text("organization_id"),
  organizationName: text("organization_name"),

  // Contact Information
  contactEmail: text("contact_email"),
  contactPhone: text("contact_phone"),

  // Administrative Information
  responsibleParty: text("responsible_party"),
  role: text("role"),

  // Status
  status: text("status", {
    enum: ["active", "inactive", "suspended", "pending"]
  }).notNull().default("active"),

  // Authentication
  apiKeys: text("api_keys", { mode: "json" }).default(sql`'[]'`),
  permissions: text("permissions", { mode: "json" }).default(sql`'[]'`),

  // Timestamps
  ...timestamps,
  lastLoginAt: text("last_login_at"),

  // Compliance
  termsAcceptedAt: text("terms_accepted_at"),
  lastComplianceReviewAt: text("last_compliance_review_at"),

  // Metadata
  metadata: text("metadata", { mode: "json" }).default(sql`'{}'`),
}, (table) => [
  index("operators_type_idx").on(table.type),
  index("operators_resident_idx").on(table.residentId),
  index("operators_org_idx").on(table.organizationId),
  index("operators_status_idx").on(table.status),
]);

export const nodeObservatoryMetrics = sqliteTable("node_observatory_metrics", {
  id: text("id").primaryKey(),
  nodeId: text("node_id").notNull().references(() => nodes.id, { onDelete: "cascade" }),

  // Metric Type
  metricType: text("metric_type", {
    enum: ["uptime", "performance", "reliability", "availability", "latency", "throughput"]
  }).notNull(),

  // Metric Value
  value: text("value").notNull(),
  unit: text("unit"),

  // Time Period
  periodStart: text("period_start").notNull(),
  periodEnd: text("period_end").notNull(),

  // Aggregation
  aggregation: text("aggregation", {
    enum: ["avg", "min", "max", "sum", "count", "p50", "p95", "p99"]
  }).default("avg"),

  // Timestamp
  recordedAt: text("recorded_at").notNull().default(sql`CURRENT_TIMESTAMP`),

  // Metadata
  metadata: text("metadata", { mode: "json" }).default(sql`'{}'`),
}, (table) => [
  index("node_observatory_metrics_node_idx").on(table.nodeId),
  index("node_observatory_metrics_type_idx").on(table.metricType),
  index("node_observatory_metrics_period_idx").on(table.periodStart, table.periodEnd),
  index("node_observatory_metrics_recorded_idx").on(table.recordedAt),
]);
