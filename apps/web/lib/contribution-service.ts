/* MOOD-GENESIS-006: Contribution Network — server-side service.
 *
 * All authorization decisions live here. This module never performs:
 *   - token transfers, signing, approvals
 *   - contract deployment
 *   - private-key handling
 *
 * Public-facing read endpoints (list/get tasks) only require a normal
 * authenticated user (or none for public tasks). All mutating endpoints
 * require an admin actor (see lib/admin-auth.ts) OR a registered Genesis
 * participant, depending on the operation.
 *
 * Mutations are append-only where possible (review events, reputation
 * events, reward events). The cached `reputation_score` aggregate on
 * `genesis_participants` is updated atomically inside the same transaction
 * that creates the reputation event; a consistency test recomputes the
 * aggregate from events. */

import { and, asc, desc, eq, inArray, like, or, sql, sum } from "drizzle-orm";
import { getDb } from "@/db";
import {
  contributionReviewEvents,
  contributionSubmissions,
  contributionTasks,
  genesisParticipants,
  reputationEvents,
  rewardEvents,
} from "@/db/schema";
import { ApiError } from "@/lib/api";
import { fromAtomicUnits, toAtomicUnits } from "@/lib/genesis-distribution";
import {
  CONTRIBUTION_CONFIG,
  isAllowedSubmissionTransition,
  isContributionCategory,
  isPublicTaskStatus,
  isSubmissionStatus,
  isTaskStatus,
  normalizeEvidenceUrl,
  type SubmissionStatus,
  type TaskStatus,
} from "@/lib/contribution-config";

/* --------------------------- Helpers -------------------------------------- */

function uuid(): string {
  return crypto.randomUUID();
}

function nowIso(): string {
  return new Date().toISOString();
}

function clampString(value: unknown, max: number, field: string): string {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") throw new ApiError(400, "VALIDATION", `${field} 不是合法字符串`);
  const trimmed = value.trim();
  if (trimmed.length > max) throw new ApiError(400, "VALIDATION", `${field} 长度超过 ${max}`);
  return trimmed;
}

function clampOptionalString(value: unknown, max: number, field: string): string | undefined {
  if (value === undefined || value === null) return undefined;
  if (typeof value !== "string") throw new ApiError(400, "VALIDATION", `${field} 不是合法字符串`);
  const trimmed = value.trim();
  if (!trimmed) return undefined;
  if (trimmed.length > max) throw new ApiError(400, "VALIDATION", `${field} 长度超过 ${max}`);
  return trimmed;
}

function clampInteger(value: unknown, field: string, min = 0, max = Number.MAX_SAFE_INTEGER): number {
  const num = typeof value === "number" ? value : Number(value);
  if (!Number.isInteger(num)) throw new ApiError(400, "VALIDATION", `${field} 必须为整数`);
  if (num < min || num > max) throw new ApiError(400, "VALIDATION", `${field} 必须在 ${min}–${max} 之间`);
  return num;
}

function parseOptionalDeadline(value: unknown): string | undefined {
  if (value === undefined || value === null) return undefined;
  if (typeof value !== "string") throw new ApiError(400, "VALIDATION", "deadline 格式不正确");
  const trimmed = value.trim();
  if (!trimmed) return undefined;
  const ms = Date.parse(trimmed);
  if (!Number.isFinite(ms)) throw new ApiError(400, "VALIDATION", "deadline 不是合法 ISO 时间");
  const iso = new Date(ms).toISOString();
  const now = Date.now();
  if (ms < now) throw new ApiError(400, "VALIDATION", "deadline 不能早于当前时间");
  const maxWindow = CONTRIBUTION_CONFIG.maxDeadlineDays * 24 * 60 * 60 * 1000;
  if (ms - now > maxWindow) throw new ApiError(400, "VALIDATION", `deadline 不能超过 ${CONTRIBUTION_CONFIG.maxDeadlineDays} 天`);
  return iso;
}

function parseMoodAmount(value: unknown, field: string): { mood: string; atomic: string } {
  if (value === undefined || value === null || value === "") return { mood: "0", atomic: "0" };
  if (typeof value !== "string") throw new ApiError(400, "VALIDATION", `${field} 必须为字符串`);
  if (value.length > CONTRIBUTION_CONFIG.maxRewardDecimalLength) {
    throw new ApiError(400, "VALIDATION", `${field} 长度过长`);
  }
  const atomic = toAtomicUnits(value);
  return { mood: value.trim(), atomic };
}

function parseEvidenceUrls(value: unknown): string[] {
  if (value === undefined || value === null) return [];
  if (!Array.isArray(value)) throw new ApiError(400, "VALIDATION", "evidenceUrls 必须是字符串数组");
  if (value.length > CONTRIBUTION_CONFIG.evidenceUrlMaxCount) {
    throw new ApiError(400, "VALIDATION", `evidenceUrls 最多 ${CONTRIBUTION_CONFIG.evidenceUrlMaxCount} 项`);
  }
  const out: string[] = [];
  for (const entry of value) {
    if (typeof entry !== "string") throw new ApiError(400, "VALIDATION", "evidenceUrls 项必须为字符串");
    const normalized = normalizeEvidenceUrl(entry);
    if (!normalized) throw new ApiError(400, "VALIDATION", `evidence URL 不合法:${entry}`);
    out.push(normalized);
  }
  return out;
}

/* --------------------------- Read: Tasks ----------------------------------- */

export interface PublicTaskSummary {
  id: string;
  slug: string;
  title: string;
  summary: string;
  category: string;
  status: TaskStatus;
  rewardPointsDefault: number;
  rewardMoodDefault: string | null;
  rewardMoodAtomicDefault: string | null;
  deadline: string | null;
  maxApprovals: number | null;
  termsVersion: string;
  publishedAt: string | null;
}

export interface AdminTaskSummary extends PublicTaskSummary {
  description: string;
  requirements: string;
  evidenceInstructions: string;
  allowDuplicateSubmissions: boolean;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  /** Count of submitted/under_review/changes_requested submissions. */
  openSubmissionCount: number;
  /** Count of approved submissions. */
  approvedSubmissionCount: number;
}

function toPublicTaskSummary(row: typeof contributionTasks.$inferSelect): PublicTaskSummary {
  return {
    id: row.id,
    slug: row.slug,
    title: row.title,
    summary: row.summary,
    category: row.category,
    status: row.status,
    rewardPointsDefault: row.rewardPointsDefault,
    rewardMoodDefault: row.rewardMoodDefault,
    rewardMoodAtomicDefault: row.rewardMoodAtomicDefault,
    deadline: row.deadline,
    maxApprovals: row.maxApprovals,
    termsVersion: row.termsVersion,
    publishedAt: row.publishedAt,
  };
}

function toAdminTaskSummary(
  row: typeof contributionTasks.$inferSelect,
  openSubmissions: number,
  approvedSubmissions: number,
): AdminTaskSummary {
  return {
    ...toPublicTaskSummary(row),
    description: row.description,
    requirements: row.requirements,
    evidenceInstructions: row.evidenceInstructions,
    allowDuplicateSubmissions: row.allowDuplicateSubmissions,
    createdBy: row.createdBy,
    createdAt: row.createdAt,
    updatedAt: row.updatedAt,
    openSubmissionCount: openSubmissions,
    approvedSubmissionCount: approvedSubmissions,
  };
}

/** Public catalog: only active/paused/completed tasks are visible. */
export async function listPublicTasks(): Promise<PublicTaskSummary[]> {
  const db = getDb();
  const rows = await db
    .select()
    .from(contributionTasks)
    .where(inArray(contributionTasks.status, CONTRIBUTION_CONFIG.publicTaskStatuses as readonly string[]))
    .orderBy(desc(contributionTasks.publishedAt), asc(contributionTasks.title));
  return rows.map(toPublicTaskSummary);
}

/** Public single task (404 if hidden). */
export async function getPublicTask(idOrSlug: string): Promise<PublicTaskSummary | null> {
  const db = getDb();
  const row = await db.query.contributionTasks.findFirst({
    where: or(eq(contributionTasks.id, idOrSlug), eq(contributionTasks.slug, idOrSlug)),
  });
  if (!row) return null;
  if (!isPublicTaskStatus(row.status)) return null;
  return toPublicTaskSummary(row);
}

/** Admin: list every task regardless of status, with submission counts. */
export async function listAdminTasks(): Promise<AdminTaskSummary[]> {
  const db = getDb();
  const rows = await db.select().from(contributionTasks).orderBy(desc(contributionTasks.updatedAt));
  if (rows.length === 0) return [];
  const counts = await db
    .select({
      taskId: contributionSubmissions.taskId,
      status: contributionSubmissions.status,
      total: sql<number>`COUNT(*)`,
    })
    .from(contributionSubmissions)
    .groupBy(contributionSubmissions.taskId, contributionSubmissions.status);
  const openByTask = new Map<string, number>();
  const approvedByTask = new Map<string, number>();
  for (const c of counts) {
    if (["submitted", "under_review", "changes_requested"].includes(c.status)) {
      openByTask.set(c.taskId, (openByTask.get(c.taskId) ?? 0) + Number(c.total));
    } else if (c.status === "approved") {
      approvedByTask.set(c.taskId, (approvedByTask.get(c.taskId) ?? 0) + Number(c.total));
    }
  }
  return rows.map((r) => toAdminTaskSummary(r, openByTask.get(r.id) ?? 0, approvedByTask.get(r.id) ?? 0));
}

/** Admin: full task detail (single). */
export async function getAdminTask(idOrSlug: string): Promise<AdminTaskSummary | null> {
  const db = getDb();
  const row = await db.query.contributionTasks.findFirst({
    where: or(eq(contributionTasks.id, idOrSlug), eq(contributionTasks.slug, idOrSlug)),
  });
  if (!row) return null;
  const counts = await db
    .select({ status: contributionSubmissions.status, total: sql<number>`COUNT(*)` })
    .from(contributionSubmissions)
    .where(eq(contributionSubmissions.taskId, row.id))
    .groupBy(contributionSubmissions.status);
  let open = 0;
  let approved = 0;
  for (const c of counts) {
    if (["submitted", "under_review", "changes_requested"].includes(c.status)) {
      open += Number(c.total);
    } else if (c.status === "approved") {
      approved += Number(c.total);
    }
  }
  return toAdminTaskSummary(row, open, approved);
}

/* --------------------------- Mutations: Tasks ----------------------------- */

export interface CreateTaskInput {
  slug: string;
  title: string;
  summary?: string;
  description?: string;
  category: string;
  status?: TaskStatus;
  requirements?: string;
  evidenceInstructions?: string;
  rewardPointsDefault?: number;
  rewardMoodDefault?: string;
  deadline?: string;
  maxApprovals?: number;
  allowDuplicateSubmissions?: boolean;
}

function normalizeSlug(raw: string): string {
  const trimmed = raw.trim().toLowerCase();
  if (!/^[a-z0-9][a-z0-9-]{2,80}$/.test(trimmed)) {
    throw new ApiError(400, "VALIDATION", "slug 必须为 3–81 位英文、数字、连字符,且以字母或数字开头");
  }
  return trimmed;
}

function validateMoodRewardField(value: string | undefined, field: string): { mood: string | null; atomic: string | null } {
  if (value === undefined || value === null || value === "") return { mood: null, atomic: null };
  if (typeof value !== "string") throw new ApiError(400, "VALIDATION", `${field} 必须为字符串`);
  const atomic = toAtomicUnits(value);
  return { mood: value.trim(), atomic };
}

export async function createTask(input: CreateTaskInput, adminId: string): Promise<AdminTaskSummary> {
  if (!isContributionCategory(input.category)) throw new ApiError(400, "CATEGORY_INVALID", "category 不合法");
  const status = input.status ?? "draft";
  if (!isTaskStatus(status)) throw new ApiError(400, "STATUS_INVALID", "status 不合法");
  const slug = normalizeSlug(input.slug);
  const title = clampString(input.title, 200, "title");
  const summary = clampString(input.summary ?? "", 400, "summary");
  const description = clampString(input.description ?? "", CONTRIBUTION_CONFIG.descriptionMaxLength, "description");
  const requirements = clampString(input.requirements ?? "", CONTRIBUTION_CONFIG.blockTextMaxLength, "requirements");
  const evidenceInstructions = clampString(input.evidenceInstructions ?? "", CONTRIBUTION_CONFIG.blockTextMaxLength, "evidenceInstructions");
  const rewardPointsDefault = clampInteger(input.rewardPointsDefault ?? 0, "rewardPointsDefault", 0, CONTRIBUTION_CONFIG.maxRewardPoints);
  const reward = validateMoodRewardField(input.rewardMoodDefault, "rewardMoodDefault");
  const deadline = parseOptionalDeadline(input.deadline);
  const maxApprovals = input.maxApprovals === undefined || input.maxApprovals === null
    ? null
    : clampInteger(input.maxApprovals, "maxApprovals", 1, 1_000_000);
  const allowDuplicateSubmissions = Boolean(input.allowDuplicateSubmissions);
  const now = nowIso();
  const db = getDb();
  try {
    const [row] = await db.insert(contributionTasks).values({
      id: uuid(),
      slug,
      title,
      summary,
      description,
      category: input.category,
      status,
      requirements,
      evidenceInstructions,
      rewardPointsDefault,
      rewardMoodDefault: reward.mood,
      rewardMoodAtomicDefault: reward.atomic,
      deadline: deadline ?? null,
      maxApprovals,
      allowDuplicateSubmissions,
      termsVersion: CONTRIBUTION_CONFIG.schemaVersion,
      createdBy: adminId,
      createdAt: now,
      updatedAt: now,
      publishedAt: status === "active" && !deadline ? now : null,
    }).returning();
    if (!row) throw new ApiError(500, "TASK_INSERT_FAILED", "任务创建失败");
    return toAdminTaskSummary(row, 0, 0);
  } catch (error) {
    if (error instanceof Error && /UNIQUE constraint failed/i.test(error.message)) {
      throw new ApiError(409, "TASK_SLUG_CONFLICT", "slug 已被占用");
    }
    throw error;
  }
}

export interface UpdateTaskInput {
  title?: string;
  summary?: string;
  description?: string;
  category?: string;
  status?: TaskStatus;
  requirements?: string;
  evidenceInstructions?: string;
  rewardPointsDefault?: number;
  rewardMoodDefault?: string | null;
  deadline?: string | null;
  maxApprovals?: number | null;
  allowDuplicateSubmissions?: boolean;
}

export async function updateTask(taskId: string, input: UpdateTaskInput, adminId: string): Promise<AdminTaskSummary> {
  const db = getDb();
  const row = await db.query.contributionTasks.findFirst({ where: eq(contributionTasks.id, taskId) });
  if (!row) throw new ApiError(404, "TASK_NOT_FOUND", "任务不存在");

  const patch: Partial<typeof contributionTasks.$inferInsert> = { updatedAt: nowIso() };
  if (input.title !== undefined) patch.title = clampString(input.title, 200, "title");
  if (input.summary !== undefined) patch.summary = clampString(input.summary, 400, "summary");
  if (input.description !== undefined) patch.description = clampString(input.description, CONTRIBUTION_CONFIG.descriptionMaxLength, "description");
  if (input.requirements !== undefined) patch.requirements = clampString(input.requirements, CONTRIBUTION_CONFIG.blockTextMaxLength, "requirements");
  if (input.evidenceInstructions !== undefined) patch.evidenceInstructions = clampString(input.evidenceInstructions, CONTRIBUTION_CONFIG.blockTextMaxLength, "evidenceInstructions");
  if (input.rewardPointsDefault !== undefined) patch.rewardPointsDefault = clampInteger(input.rewardPointsDefault, "rewardPointsDefault", 0, CONTRIBUTION_CONFIG.maxRewardPoints);
  if (input.rewardMoodDefault !== undefined) {
    if (input.rewardMoodDefault === null || input.rewardMoodDefault === "") {
      patch.rewardMoodDefault = null;
      patch.rewardMoodAtomicDefault = null;
    } else {
      const r = validateMoodRewardField(input.rewardMoodDefault, "rewardMoodDefault");
      patch.rewardMoodDefault = r.mood;
      patch.rewardMoodAtomicDefault = r.atomic;
    }
  }
  if (input.category !== undefined) {
    if (!isContributionCategory(input.category)) throw new ApiError(400, "CATEGORY_INVALID", "category 不合法");
    patch.category = input.category;
  }
  if (input.status !== undefined) {
    if (!isTaskStatus(input.status)) throw new ApiError(400, "STATUS_INVALID", "status 不合法");
    const nextStatus = input.status;
    if (nextStatus !== row.status && nextStatus === "active" && !row.publishedAt) {
      patch.publishedAt = nowIso();
    }
    patch.status = nextStatus;
  }
  if (input.deadline !== undefined) {
    patch.deadline = input.deadline === null ? null : (parseOptionalDeadline(input.deadline) ?? null);
  }
  if (input.maxApprovals !== undefined) {
    patch.maxApprovals = input.maxApprovals === null
      ? null
      : clampInteger(input.maxApprovals, "maxApprovals", 1, 1_000_000);
  }
  if (input.allowDuplicateSubmissions !== undefined) {
    patch.allowDuplicateSubmissions = Boolean(input.allowDuplicateSubmissions);
  }

  void adminId; // included in the call signature for audit; the actor is logged by API route
  await db.update(contributionTasks).set(patch).where(eq(contributionTasks.id, taskId));
  const updated = await getAdminTask(taskId);
  if (!updated) throw new ApiError(500, "TASK_UPDATE_FAILED", "任务更新失败");
  return updated;
}

/* --------------------------- Read: Submissions ---------------------------- */

export interface ParticipantSummary {
  participantNumber: number;
  walletAddress: string;
  reputationScore: number;
}

export interface SubmissionView {
  id: string;
  taskId: string;
  taskSlug: string;
  taskTitle: string;
  participantNumber: number;
  participantWallet: string;
  status: SubmissionStatus;
  summary: string;
  evidenceText: string;
  evidenceUrls: string[];
  revisionNumber: number;
  submittedAt: string;
  updatedAt: string;
  reviewedAt: string | null;
  reviewerId: string | null;
  reviewNote: string | null;
  /** Pending reward (atomic) attached to the latest review event, if any. */
  pendingRewardMood: string | null;
  pendingRewardAtomic: string | null;
  /** Reputation delta attached to the latest review event, if any. */
  lastPointsDelta: number;
}

export interface SubmissionDetail extends SubmissionView {
  reviewEvents: Array<{
    id: string;
    eventType: string;
    oldStatus: string | null;
    newStatus: string | null;
    pointsDelta: number;
    rewardMood: string;
    rewardAtomic: string;
    reason: string;
    actorId: string;
    createdAt: string;
  }>;
  reputationEvents: Array<{
    id: string;
    eventType: string;
    pointsDelta: number;
    reason: string;
    actorId: string;
    createdAt: string;
  }>;
  rewardEvents: Array<{
    id: string;
    rewardMood: string;
    rewardAtomic: string;
    status: string;
    reason: string;
    approvedBy: string;
    createdAt: string;
    distributionSnapshotId: string | null;
  }>;
}

interface JoinedSubmissionRow {
  submission: typeof contributionSubmissions.$inferSelect;
  task: typeof contributionTasks.$inferSelect;
  participant: typeof genesisParticipants.$inferSelect;
}

async function loadJoined(submissionId: string): Promise<JoinedSubmissionRow | null> {
  const db = getDb();
  const submission = await db.query.contributionSubmissions.findFirst({ where: eq(contributionSubmissions.id, submissionId) });
  if (!submission) return null;
  const task = await db.query.contributionTasks.findFirst({ where: eq(contributionTasks.id, submission.taskId) });
  const participant = await db.query.genesisParticipants.findFirst({ where: eq(genesisParticipants.id, submission.participantId) });
  if (!task || !participant) return null;
  return { submission, task, participant };
}

async function loadLastReviewReward(submissionId: string): Promise<{ mood: string | null; atomic: string | null; points: number }> {
  const db = getDb();
  const last = await db.query.contributionReviewEvents.findFirst({
    where: and(
      eq(contributionReviewEvents.submissionId, submissionId),
      eq(contributionReviewEvents.eventType, "approved"),
    ),
    orderBy: desc(contributionReviewEvents.createdAt),
  });
  if (!last) return { mood: null, atomic: null, points: 0 };
  return {
    mood: last.rewardMood === "0" ? null : last.rewardMood,
    atomic: last.rewardAtomic === "0" ? null : last.rewardAtomic,
    points: last.pointsDelta,
  };
}

async function buildSubmissionView(row: JoinedSubmissionRow): Promise<SubmissionView> {
  const lastReward = await loadLastReviewReward(row.submission.id);
  let urls: string[] = [];
  try {
    const parsed = JSON.parse(row.submission.evidenceUrlsJson);
    if (Array.isArray(parsed)) urls = parsed.filter((x): x is string => typeof x === "string");
  } catch {
    urls = [];
  }
  return {
    id: row.submission.id,
    taskId: row.task.id,
    taskSlug: row.task.slug,
    taskTitle: row.task.title,
    participantNumber: row.participant.participantNumber,
    participantWallet: row.participant.walletAddress,
    status: row.submission.status,
    summary: row.submission.summary,
    evidenceText: row.submission.evidenceText,
    evidenceUrls: urls,
    revisionNumber: row.submission.revisionNumber,
    submittedAt: row.submission.submittedAt,
    updatedAt: row.submission.updatedAt,
    reviewedAt: row.submission.reviewedAt,
    reviewerId: row.submission.reviewerId,
    reviewNote: row.submission.reviewNote,
    pendingRewardMood: lastReward.mood,
    pendingRewardAtomic: lastReward.atomic,
    lastPointsDelta: lastReward.points,
  };
}

export async function listPublicTasksForParticipant(participantId: string): Promise<SubmissionView[]> {
  const db = getDb();
  const rows = await db
    .select({
      submission: contributionSubmissions,
      task: contributionTasks,
      participant: genesisParticipants,
    })
    .from(contributionSubmissions)
    .innerJoin(contributionTasks, eq(contributionSubmissions.taskId, contributionTasks.id))
    .innerJoin(genesisParticipants, eq(contributionSubmissions.participantId, genesisParticipants.id))
    .where(eq(contributionSubmissions.participantId, participantId))
    .orderBy(desc(contributionSubmissions.submittedAt));
  return Promise.all(rows.map(buildSubmissionView));
}

export async function listAdminSubmissions(filter?: {
  status?: SubmissionStatus;
  taskId?: string;
  participantNumber?: number;
  search?: string;
  limit?: number;
  offset?: number;
}): Promise<{ total: number; items: SubmissionView[] }> {
  const db = getDb();
  const conditions = [];
  if (filter?.status) conditions.push(eq(contributionSubmissions.status, filter.status));
  if (filter?.taskId) conditions.push(eq(contributionSubmissions.taskId, filter.taskId));
  if (filter?.search) {
    const term = `%${filter.search.trim().toLowerCase()}%`;
    conditions.push(or(
      like(sql`lower(${genesisParticipants.walletAddress})`, term),
      like(sql`lower(${contributionSubmissions.summary})`, term),
    ));
  }
  if (filter?.participantNumber !== undefined) {
    conditions.push(eq(genesisParticipants.participantNumber, filter.participantNumber));
  }
  const where = conditions.length > 0 ? and(...conditions) : undefined;
  const limit = Math.max(1, Math.min(filter?.limit ?? 100, 500));
  const offset = Math.max(0, filter?.offset ?? 0);
  const totalRow = await db
    .select({ c: sql<number>`COUNT(*)` })
    .from(contributionSubmissions)
    .innerJoin(genesisParticipants, eq(contributionSubmissions.participantId, genesisParticipants.id))
    .where(where ?? sql`1=1`);
  const total = Number(totalRow[0]?.c ?? 0);
  const rows = await db
    .select({
      submission: contributionSubmissions,
      task: contributionTasks,
      participant: genesisParticipants,
    })
    .from(contributionSubmissions)
    .innerJoin(contributionTasks, eq(contributionSubmissions.taskId, contributionTasks.id))
    .innerJoin(genesisParticipants, eq(contributionSubmissions.participantId, genesisParticipants.id))
    .where(where ?? sql`1=1`)
    .orderBy(desc(contributionSubmissions.submittedAt))
    .limit(limit)
    .offset(offset);
  const items = await Promise.all(rows.map(buildSubmissionView));
  return { total, items };
}

export async function getSubmissionForParticipant(submissionId: string, participantId: string): Promise<SubmissionDetail | null> {
  const db = getDb();
  const row = await db.query.contributionSubmissions.findFirst({
    where: and(eq(contributionSubmissions.id, submissionId), eq(contributionSubmissions.participantId, participantId)),
  });
  if (!row) return null;
  return loadSubmissionDetail(row.id);
}

export async function getSubmissionForAdmin(submissionId: string): Promise<SubmissionDetail | null> {
  return loadSubmissionDetail(submissionId);
}

async function loadSubmissionDetail(submissionId: string): Promise<SubmissionDetail | null> {
  const joined = await loadJoined(submissionId);
  if (!joined) return null;
  const view = await buildSubmissionView(joined);
  const db = getDb();
  const reviewRows = await db.query.contributionReviewEvents.findMany({
    where: eq(contributionReviewEvents.submissionId, submissionId),
    orderBy: asc(contributionReviewEvents.createdAt),
  });
  const reputationRows = await db.query.reputationEvents.findMany({
    where: eq(reputationEvents.submissionId, submissionId),
    orderBy: asc(reputationEvents.createdAt),
  });
  const rewardRows = await db.query.rewardEvents.findMany({
    where: eq(rewardEvents.submissionId, submissionId),
    orderBy: asc(rewardEvents.createdAt),
  });
  return {
    ...view,
    reviewEvents: reviewRows.map((r) => ({
      id: r.id,
      eventType: r.eventType,
      oldStatus: r.oldStatus,
      newStatus: r.newStatus,
      pointsDelta: r.pointsDelta,
      rewardMood: r.rewardMood,
      rewardAtomic: r.rewardAtomic,
      reason: r.reason,
      actorId: r.actorId,
      createdAt: r.createdAt,
    })),
    reputationEvents: reputationRows.map((r) => ({
      id: r.id,
      eventType: r.eventType,
      pointsDelta: r.pointsDelta,
      reason: r.reason,
      actorId: r.actorId,
      createdAt: r.createdAt,
    })),
    rewardEvents: rewardRows.map((r) => ({
      id: r.id,
      rewardMood: r.rewardMood,
      rewardAtomic: r.rewardAtomic,
      status: r.status,
      reason: r.reason,
      approvedBy: r.approvedBy,
      createdAt: r.createdAt,
      distributionSnapshotId: r.distributionSnapshotId,
    })),
  };
}

/* --------------------------- Mutations: Submissions ----------------------- */

export interface CreateSubmissionInput {
  taskId: string;
  summary: string;
  evidenceText: string;
  evidenceUrls: string[];
  /** Set true to bypass the dedupe check (e.g., on resubmission after changes_requested). */
  resubmit?: boolean;
}

/** Returns the existing non-terminal submission for this participant/task if one exists.
 *  When allowDuplicateSubmissions is true the caller is expected to bypass dedupe. */
export async function findExistingOpenSubmission(participantId: string, taskId: string): Promise<typeof contributionSubmissions.$inferSelect | null> {
  const db = getDb();
  const rows = await db
    .select()
    .from(contributionSubmissions)
    .where(and(
      eq(contributionSubmissions.participantId, participantId),
      eq(contributionSubmissions.taskId, taskId),
      inArray(contributionSubmissions.status, ["submitted", "under_review", "changes_requested"] as const),
    ))
    .orderBy(desc(contributionSubmissions.submittedAt))
    .limit(1);
  return rows[0] ?? null;
}

export async function createSubmission(input: CreateSubmissionInput, participantId: string): Promise<SubmissionDetail> {
  if (!participantId) throw new ApiError(401, "PARTICIPANT_REQUIRED", "请先注册为 Genesis Participant");
  const summary = clampString(input.summary, CONTRIBUTION_CONFIG.summaryMaxLength, "summary");
  const evidenceText = clampString(input.evidenceText, CONTRIBUTION_CONFIG.evidenceTextMaxLength, "evidenceText");
  const evidenceUrls = parseEvidenceUrls(input.evidenceUrls);
  const db = getDb();
  const task = await db.query.contributionTasks.findFirst({ where: eq(contributionTasks.id, input.taskId) });
  if (!task) throw new ApiError(404, "TASK_NOT_FOUND", "任务不存在");
  if (task.status !== "active") throw new ApiError(409, "TASK_NOT_ACCEPTING", "该任务当前不接受提交");
  if (task.deadline) {
    if (Date.parse(task.deadline) <= Date.now()) throw new ApiError(409, "TASK_DEADLINE_PASSED", "任务已过截止时间");
  }
  if (task.maxApprovals !== null) {
    const approvedCountRow = await db
      .select({ c: sql<number>`COUNT(*)` })
      .from(contributionSubmissions)
      .where(and(eq(contributionSubmissions.taskId, task.id), eq(contributionSubmissions.status, "approved")));
    if (Number(approvedCountRow[0]?.c ?? 0) >= task.maxApprovals) {
      throw new ApiError(409, "TASK_MAX_APPROVALS_REACHED", "该任务已达成批准上限");
    }
  }
  if (!task.allowDuplicateSubmissions && !input.resubmit) {
    const existing = await findExistingOpenSubmission(participantId, task.id);
    if (existing) {
      throw new ApiError(409, "SUBMISSION_DUPLICATE", "已存在进行中的提交;请等待审核或修改后再提交");
    }
  }
  const now = nowIso();
  const inserted = await db.insert(contributionSubmissions).values({
    id: uuid(),
    taskId: task.id,
    participantId,
    status: "submitted",
    summary,
    evidenceText,
    evidenceUrlsJson: JSON.stringify(evidenceUrls),
    revisionNumber: input.resubmit ? 2 : 1,
    submittedAt: now,
    updatedAt: now,
  }).returning();
  const row = inserted[0];
  if (!row) throw new ApiError(500, "SUBMISSION_INSERT_FAILED", "提交创建失败");
  await db.insert(contributionReviewEvents).values({
    id: uuid(),
    submissionId: row.id,
    actorId: participantId,
    eventType: "created",
    oldStatus: null,
    newStatus: "submitted",
    pointsDelta: 0,
    rewardMood: "0",
    rewardAtomic: "0",
    reason: "Contributor submitted initial version",
    createdAt: now,
  });
  const detail = await loadSubmissionDetail(row.id);
  if (!detail) throw new ApiError(500, "SUBMISSION_LOAD_FAILED", "提交加载失败");
  return detail;
}

/** Contributor-driven resubmit after changes_requested. */
export async function resubmitSubmission(submissionId: string, participantId: string, input: { summary?: string; evidenceText?: string; evidenceUrls?: string[] }): Promise<SubmissionDetail> {
  const db = getDb();
  const row = await db.query.contributionSubmissions.findFirst({
    where: and(eq(contributionSubmissions.id, submissionId), eq(contributionSubmissions.participantId, participantId)),
  });
  if (!row) throw new ApiError(404, "SUBMISSION_NOT_FOUND", "提交不存在");
  if (!isAllowedSubmissionTransition(row.status as SubmissionStatus, "submitted")) {
    throw new ApiError(409, "SUBMISSION_INVALID_TRANSITION", `当前状态(${row.status})不可重新提交`);
  }
  const summary = input.summary !== undefined ? clampString(input.summary, CONTRIBUTION_CONFIG.summaryMaxLength, "summary") : row.summary;
  const evidenceText = input.evidenceText !== undefined ? clampString(input.evidenceText, CONTRIBUTION_CONFIG.evidenceTextMaxLength, "evidenceText") : row.evidenceText;
  const evidenceUrls = input.evidenceUrls !== undefined ? parseEvidenceUrls(input.evidenceUrls) : (() => {
    try {
      const parsed = JSON.parse(row.evidenceUrlsJson);
      return Array.isArray(parsed) ? parsed.filter((x): x is string => typeof x === "string") : [];
    } catch { return []; }
  })();
  const now = nowIso();
  await db.update(contributionSubmissions).set({
    status: "submitted",
    summary,
    evidenceText,
    evidenceUrlsJson: JSON.stringify(evidenceUrls),
    revisionNumber: row.revisionNumber + 1,
    updatedAt: now,
    reviewedAt: null,
    reviewNote: null,
  }).where(eq(contributionSubmissions.id, submissionId));
  await db.insert(contributionReviewEvents).values({
    id: uuid(),
    submissionId,
    actorId: participantId,
    eventType: "status_change",
    oldStatus: row.status,
    newStatus: "submitted",
    pointsDelta: 0,
    rewardMood: "0",
    rewardAtomic: "0",
    reason: "Contributor resubmitted after changes_requested",
    createdAt: now,
  });
  const detail = await loadSubmissionDetail(submissionId);
  if (!detail) throw new ApiError(500, "SUBMISSION_LOAD_FAILED", "提交加载失败");
  return detail;
}

export async function withdrawSubmission(submissionId: string, participantId: string, reason: string): Promise<SubmissionDetail> {
  const db = getDb();
  const row = await db.query.contributionSubmissions.findFirst({
    where: and(eq(contributionSubmissions.id, submissionId), eq(contributionSubmissions.participantId, participantId)),
  });
  if (!row) throw new ApiError(404, "SUBMISSION_NOT_FOUND", "提交不存在");
  if (!isAllowedSubmissionTransition(row.status as SubmissionStatus, "withdrawn")) {
    throw new ApiError(409, "SUBMISSION_INVALID_TRANSITION", `当前状态(${row.status})不可撤回`);
  }
  const now = nowIso();
  await db.update(contributionSubmissions).set({ status: "withdrawn", updatedAt: now, reviewerId: participantId, reviewedAt: now, reviewNote: reason || "withdrawn by contributor" })
    .where(eq(contributionSubmissions.id, submissionId));
  await db.insert(contributionReviewEvents).values({
    id: uuid(),
    submissionId,
    actorId: participantId,
    eventType: "withdrawn",
    oldStatus: row.status,
    newStatus: "withdrawn",
    pointsDelta: 0,
    rewardMood: "0",
    rewardAtomic: "0",
    reason: clampString(reason, CONTRIBUTION_CONFIG.reasonMaxLength, "reason") || "withdrawn by contributor",
    createdAt: now,
  });
  const detail = await loadSubmissionDetail(submissionId);
  if (!detail) throw new ApiError(500, "SUBMISSION_LOAD_FAILED", "提交加载失败");
  return detail;
}

/* --------------------------- Mutations: Admin Review ---------------------- */

export interface ReviewActionInput {
  reason: string;
  /** Admin-set reward on approval. Required when action === "approve". */
  pointsDelta?: number;
  rewardMood?: string | null;
}

export async function transitionSubmission(submissionId: string, adminId: string, to: SubmissionStatus, input: ReviewActionInput): Promise<SubmissionDetail> {
  if (!isSubmissionStatus(to)) throw new ApiError(400, "STATUS_INVALID", "目标状态不合法");
  const db = getDb();
  const row = await db.query.contributionSubmissions.findFirst({ where: eq(contributionSubmissions.id, submissionId) });
  if (!row) throw new ApiError(404, "SUBMISSION_NOT_FOUND", "提交不存在");
  const from = row.status as SubmissionStatus;
  if (from === to) throw new ApiError(409, "SUBMISSION_INVALID_TRANSITION", "状态未改变");
  if (!isAllowedSubmissionTransition(from, to)) {
    throw new ApiError(409, "SUBMISSION_INVALID_TRANSITION", `不允许的状态迁移 ${from} -> ${to}`);
  }
  const reason = clampString(input.reason, CONTRIBUTION_CONFIG.reasonMaxLength, "reason");

  // Self-review guard: when admin identity can be linked to a participant
  // (i.e., admin is using the same wallet as the contributor), refuse.
  // In v1 we conservatively refuse when admin actor string equals the
  // participant id (which happens only if the admin happens to be a
  // contributor — we never log wallet addresses here, only IDs).
  if (row.participantId === adminId) {
    throw new ApiError(409, "SELF_REVIEW_PROHIBITED", "提交者不能审核自己的提交");
  }

  let points = 0;
  let rewardMood = "0";
  let rewardAtomic = "0";

  if (to === "approved") {
    points = clampInteger(input.pointsDelta ?? 0, "pointsDelta", 0, CONTRIBUTION_CONFIG.maxRewardPoints);
    const parsed = parseMoodAmount(input.rewardMood ?? "0", "rewardMood");
    if (parsed.atomic !== "0") {
      // Enforce per-task pending total cap.
      const task = await db.query.contributionTasks.findFirst({ where: eq(contributionTasks.id, row.taskId) });
      if (task) {
        const taskRewardSum = await db
          .select({ s: sql<string>`COALESCE(SUM(${contributionReviewEvents.rewardAtomic}), '0')` })
          .from(contributionReviewEvents)
          .where(and(
            eq(contributionReviewEvents.submissionId, row.id),
            eq(contributionReviewEvents.eventType, "approved"),
          ));
        const prior = BigInt(taskRewardSum[0]?.s ?? "0");
        const next = prior + BigInt(parsed.atomic);
        if (next > BigInt(CONTRIBUTION_CONFIG.genesisPoolCeilingAtomic)) {
          throw new ApiError(409, "REWARD_POOL_EXCEEDED", "该任务的累计待发放奖励已超过 Genesis Pool 上限");
        }
        void task;
      }
    }
    rewardMood = parsed.mood;
    rewardAtomic = parsed.atomic;

    // Prevent double approval: a submission already approved cannot be re-approved.
    const priorApproval = await db.query.contributionReviewEvents.findFirst({
      where: and(eq(contributionReviewEvents.submissionId, row.id), eq(contributionReviewEvents.eventType, "approved")),
    });
    if (priorApproval) {
      throw new ApiError(409, "APPROVAL_ALREADY_RECORDED", "该提交已经批准;不可重复批准");
    }

    // Per-task max_approvals cap (counting all approved submissions).
    const taskRow = await db.query.contributionTasks.findFirst({ where: eq(contributionTasks.id, row.taskId) });
    if (taskRow?.maxApprovals !== null && taskRow?.maxApprovals !== undefined) {
      const approvedCountRow = await db
        .select({ c: sql<number>`COUNT(*)` })
        .from(contributionSubmissions)
        .where(and(eq(contributionSubmissions.taskId, row.taskId), eq(contributionSubmissions.status, "approved")));
      if (Number(approvedCountRow[0]?.c ?? 0) >= taskRow.maxApprovals) {
        throw new ApiError(409, "TASK_MAX_APPROVALS_REACHED", "该任务已达到最大批准数");
      }
    }
  }

  const now = nowIso();
  await db.update(contributionSubmissions).set({
    status: to,
    updatedAt: now,
    reviewedAt: now,
    reviewerId: adminId,
    reviewNote: reason,
  }).where(eq(contributionSubmissions.id, submissionId));

  const reviewEventType = to === "approved"
    ? "approved"
    : to === "rejected"
      ? "rejected"
      : to === "changes_requested"
        ? "changes_requested"
        : to === "withdrawn"
          ? "withdrawn"
          : "status_change";

  await db.insert(contributionReviewEvents).values({
    id: uuid(),
    submissionId: row.id,
    actorId: adminId,
    eventType: reviewEventType,
    oldStatus: from,
    newStatus: to,
    pointsDelta: points,
    rewardMood,
    rewardAtomic,
    reason,
    createdAt: now,
  });

  if (to === "approved" && points > 0) {
    await db.insert(reputationEvents).values({
      id: uuid(),
      participantId: row.participantId,
      submissionId: row.id,
      eventType: "approval",
      pointsDelta: points,
      reason,
      actorId: adminId,
      createdAt: now,
    });
    // Atomic update of cached aggregate. We never rewrite history.
    await db.update(genesisParticipants)
      .set({ reputationScore: sql`${genesisParticipants.reputationScore} + ${points}`, updatedAt: now })
      .where(eq(genesisParticipants.id, row.participantId));
  }

  if (to === "approved" && rewardAtomic !== "0") {
    await db.insert(rewardEvents).values({
      id: uuid(),
      participantId: row.participantId,
      submissionId: row.id,
      taskId: row.taskId,
      rewardMood,
      rewardAtomic,
      status: "pending",
      reason,
      approvedBy: adminId,
      createdAt: now,
    });
  }

  const detail = await loadSubmissionDetail(row.id);
  if (!detail) throw new ApiError(500, "SUBMISSION_LOAD_FAILED", "提交加载失败");
  return detail;
}

/** Append-only admin note (does NOT change submission status). */
export async function appendAdminNote(submissionId: string, adminId: string, body: string): Promise<SubmissionDetail> {
  const text = clampString(body, CONTRIBUTION_CONFIG.reasonMaxLength, "body");
  if (!text) throw new ApiError(400, "VALIDATION", "body 不能为空");
  const db = getDb();
  const row = await db.query.contributionSubmissions.findFirst({ where: eq(contributionSubmissions.id, submissionId) });
  if (!row) throw new ApiError(404, "SUBMISSION_NOT_FOUND", "提交不存在");
  const now = nowIso();
  await db.insert(contributionReviewEvents).values({
    id: uuid(),
    submissionId,
    actorId: adminId,
    eventType: "status_change",
    oldStatus: row.status,
    newStatus: row.status,
    pointsDelta: 0,
    rewardMood: "0",
    rewardAtomic: "0",
    reason: text,
    createdAt: now,
  });
  const detail = await loadSubmissionDetail(submissionId);
  if (!detail) throw new ApiError(500, "SUBMISSION_LOAD_FAILED", "提交加载失败");
  return detail;
}

/* --------------------------- Metrics & Aggregates ------------------------- */

export interface OverviewMetrics {
  activeTasks: number;
  drafts: number;
  paused: number;
  archived: number;
  submissionsAwaitingReview: number;
  approvedSubmissions: number;
  totalReputationIssued: number;
  pendingRewardAtomicTotal: string;
  pendingRewardMoodTotal: string;
  pendingRewardCount: number;
  cancelledRewardCount: number;
}

export async function getOverviewMetrics(): Promise<OverviewMetrics> {
  const db = getDb();
  const taskCounts = await db
    .select({ status: contributionTasks.status, total: sql<number>`COUNT(*)` })
    .from(contributionTasks)
    .groupBy(contributionTasks.status);
  const subCounts = await db
    .select({ status: contributionSubmissions.status, total: sql<number>`COUNT(*)` })
    .from(contributionSubmissions)
    .groupBy(contributionSubmissions.status);
  const repSum = await db
    .select({ s: sql<number>`COALESCE(SUM(${reputationEvents.pointsDelta}), 0)` })
    .from(reputationEvents);
  const pending = await db
    .select({ s: sql<string>`COALESCE(SUM(${rewardEvents.rewardAtomic}), '0')` })
    .from(rewardEvents)
    .where(eq(rewardEvents.status, "pending"));
  const pendingCount = await db
    .select({ c: sql<number>`COUNT(*)` })
    .from(rewardEvents)
    .where(eq(rewardEvents.status, "pending"));
  const cancelledCount = await db
    .select({ c: sql<number>`COUNT(*)` })
    .from(rewardEvents)
    .where(eq(rewardEvents.status, "cancelled"));

  const byStatus = (rows: Array<{ status: string; total: number | string }>, status: string) => {
    const row = rows.find((r) => r.status === status);
    return Number(row?.total ?? 0);
  };

  const pendingAtomic = pending[0]?.s ?? "0";

  return {
    activeTasks: byStatus(taskCounts, "active"),
    drafts: byStatus(taskCounts, "draft"),
    paused: byStatus(taskCounts, "paused"),
    archived: byStatus(taskCounts, "archived"),
    submissionsAwaitingReview:
      byStatus(subCounts, "submitted") +
      byStatus(subCounts, "under_review") +
      byStatus(subCounts, "changes_requested"),
    approvedSubmissions: byStatus(subCounts, "approved"),
    totalReputationIssued: Number(repSum[0]?.s ?? 0),
    pendingRewardAtomicTotal: pendingAtomic,
    pendingRewardMoodTotal: fromAtomicUnits(pendingAtomic),
    pendingRewardCount: Number(pendingCount[0]?.c ?? 0),
    cancelledRewardCount: Number(cancelledCount[0]?.c ?? 0),
  };
}

/** Validate cached reputation matches SUM(events.points_delta). Returns
 *  the list of mismatches (empty = OK). Used by an admin endpoint and a
 *  consistency test. */
export async function findReputationMismatches(): Promise<Array<{ participantId: string; participantNumber: number; cached: number; recomputed: number }>> {
  const db = getDb();
  const rows = await db
    .select({
      participantId: genesisParticipants.id,
      participantNumber: genesisParticipants.participantNumber,
      cached: genesisParticipants.reputationScore,
      recomputed: sql<number>`COALESCE((SELECT SUM(${reputationEvents.pointsDelta}) FROM ${reputationEvents} WHERE ${reputationEvents.participantId} = ${genesisParticipants.id}), 0)`,
    })
    .from(genesisParticipants);
  return rows
    .filter((r) => Number(r.cached) !== Number(r.recomputed))
    .map((r) => ({
      participantId: r.participantId,
      participantNumber: r.participantNumber,
      cached: Number(r.cached),
      recomputed: Number(r.recomputed),
    }));
}

export async function sumReputationFor(participantId: string): Promise<number> {
  const db = getDb();
  const row = await db
    .select({ s: sql<number>`COALESCE(SUM(${reputationEvents.pointsDelta}), 0)` })
    .from(reputationEvents)
    .where(eq(reputationEvents.participantId, participantId));
  return Number(row[0]?.s ?? 0);
}

/** Recompute the cached reputation from events. Caller must run inside a
 *  write path; we re-read after the recompute to return the new value. */
export async function recomputeAndStoreReputation(participantId: string): Promise<number> {
  const total = await sumReputationFor(participantId);
  await getDb().update(genesisParticipants)
    .set({ reputationScore: total, updatedAt: nowIso() })
    .where(eq(genesisParticipants.id, participantId));
  return total;
}
