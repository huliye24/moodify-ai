"use client";

/*** MOOD-GENESIS-006: Admin Contribution Network Management.
 *
 * Secure admin interface for:
 * - Task management (create, edit, publish, pause, archive)
 * - Submission review queue
 * - Approval/Rejection with reputation points and MOOD rewards
 * - Audit timeline viewing
 *
 * Requires admin authentication via lib/admin-auth.ts */

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "../../../components/ui/primitives";
import type { SubmissionStatus, TaskStatus } from "../../../lib/contribution-config";

type Tab = "tasks" | "submissions" | "metrics";

type Task = {
  id: string;
  slug: string;
  title: string;
  summary: string;
  category: string;
  status: TaskStatus;
  rewardPointsDefault: number;
  rewardMoodDefault: string | null;
  deadline: string | null;
  maxApprovals: number | null;
  openSubmissionCount: number;
  approvedSubmissionCount: number;
  publishedAt: string | null;
};

type TaskDetail = Task & {
  description: string;
  requirements: string;
  evidenceInstructions: string;
  allowDuplicateSubmissions: boolean;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
};

type Submission = {
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
  pendingRewardMood: string | null;
  lastPointsDelta: number;
};

type SubmissionDetail = Submission & {
  reviewEvents: ReviewEvent[];
  reputationEvents: ReputationEvent[];
  rewardEvents: RewardEvent[];
};

type ReviewEvent = {
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
};

type ReputationEvent = {
  id: string;
  eventType: string;
  pointsDelta: number;
  reason: string;
  actorId: string;
  createdAt: string;
};

type RewardEvent = {
  id: string;
  rewardMood: string;
  rewardAtomic: string;
  status: string;
  reason: string;
  approvedBy: string;
  createdAt: string;
  distributionSnapshotId: string | null;
};

type Metrics = {
  activeTasks: number;
  drafts: number;
  paused: number;
  archived: number;
  submissionsAwaitingReview: number;
  approvedSubmissions: number;
  totalReputationIssued: number;
  pendingRewardMoodTotal: string;
  pendingRewardCount: number;
  cancelledRewardCount: number;
};

const CATEGORY_LABELS: Record<string, string> = {
  code: "代码",
  "audio-testing": "音频测试",
  dataset: "数据集",
  research: "研究",
  documentation: "文档",
  translation: "翻译",
  "bug-report": "漏洞报告",
  community: "社区",
  other: "其他",
};

const STATUS_LABELS: Record<string, string> = {
  draft: "草稿",
  active: "开放",
  paused: "暂停",
  completed: "完成",
  archived: "归档",
};

const SUBMISSION_STATUS_LABELS: Record<string, string> = {
  submitted: "待审核",
  under_review: "审核中",
  changes_requested: "需要修改",
  approved: "已批准",
  rejected: "已拒绝",
  withdrawn: "已撤回",
};

const STATUS_COLORS: Record<string, string> = {
  draft: "var(--text-faint)",
  active: "var(--evidence)",
  paused: "var(--attention)",
  completed: "var(--text-muted)",
  archived: "var(--text-faint)",
};

const SUBMISSION_STATUS_COLORS: Record<string, string> = {
  submitted: "var(--text-muted)",
  under_review: "var(--attention)",
  changes_requested: "var(--attention)",
  approved: "var(--evidence)",
  rejected: "var(--blocking)",
  withdrawn: "var(--text-faint)",
};

function TaskCard({ task, onClick }: { task: Task; onClick: () => void }) {
  return (
    <article
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") onClick(); }}
      style={{
        padding: "var(--space-4)",
        border: "1px solid var(--line)",
        borderRadius: "var(--radius-md)",
        background: "var(--surface-subtle)",
        cursor: "pointer",
        display: "grid",
        gap: "var(--space-2)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)", flexWrap: "wrap" }}>
        <span style={{
          fontSize: "var(--text-xs)",
          color: STATUS_COLORS[task.status],
          textTransform: "uppercase",
          letterSpacing: "0.1em",
          fontWeight: 600,
        }}>
          {STATUS_LABELS[task.status]}
        </span>
        <span style={{ fontSize: "var(--text-xs)", color: "var(--text-faint)" }}>
          {CATEGORY_LABELS[task.category] ?? task.category}
        </span>
      </div>
      <h3 style={{ margin: 0, fontSize: "var(--text-lg)", color: "var(--text)", fontWeight: 600 }}>{task.title}</h3>
      <p style={{ margin: 0, fontSize: "var(--text-sm)", color: "var(--text-muted)", overflow: "hidden", display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical" }}>
        {task.summary}
      </p>
      <div style={{ display: "flex", gap: "var(--space-3)", fontSize: "var(--text-xs)", color: "var(--text-faint)" }}>
        <span>待审: {task.openSubmissionCount}</span>
        <span>已批: {task.approvedSubmissionCount}</span>
        {task.rewardMoodDefault && <span>{task.rewardMoodDefault} MOOD</span>}
      </div>
    </article>
  );
}

function SubmissionRow({ sub, onClick }: { sub: Submission; onClick: () => void }) {
  const statusColor = SUBMISSION_STATUS_COLORS[sub.status] ?? "var(--text-muted)";
  return (
    <div
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") onClick(); }}
      style={{
        padding: "var(--space-3) var(--space-4)",
        borderBottom: "1px solid var(--line)",
        display: "grid",
        gap: "var(--space-1)",
        cursor: "pointer",
        background: "var(--surface)",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", flexWrap: "wrap", gap: "var(--space-2)" }}>
        <strong style={{ fontSize: "var(--text-md)", color: "var(--text)" }}>{sub.taskTitle}</strong>
        <span style={{ fontSize: "var(--text-sm)", color: statusColor }}>{SUBMISSION_STATUS_LABELS[sub.status] ?? sub.status}</span>
      </div>
      <p style={{ margin: 0, fontSize: "var(--text-sm)", color: "var(--text-muted)" }}>{sub.summary}</p>
      <div style={{ display: "flex", gap: "var(--space-4)", fontSize: "var(--text-xs)", color: "var(--text-faint)" }}>
        <span>Participant #{sub.participantNumber}</span>
        <span>{sub.participantWallet.slice(0, 6)}...{sub.participantWallet.slice(-4)}</span>
        <span>v{sub.revisionNumber}</span>
        {sub.pendingRewardMood && <span style={{ color: "var(--evidence)" }}>{sub.pendingRewardMood} MOOD</span>}
      </div>
    </div>
  );
}

function TaskForm({
  initial,
  onSave,
  onCancel,
}: {
  initial?: TaskDetail;
  onSave: (data: Record<string, unknown>) => void;
  onCancel: () => void;
}) {
  const [title, setTitle] = useState(initial?.title ?? "");
  const [slug, setSlug] = useState(initial?.slug ?? "");
  const [summary, setSummary] = useState(initial?.summary ?? "");
  const [description, setDescription] = useState(initial?.description ?? "");
  const [category, setCategory] = useState(initial?.category ?? "code");
  const [status, setStatus] = useState<TaskStatus>(initial?.status ?? "draft");
  const [requirements, setRequirements] = useState(initial?.requirements ?? "");
  const [evidenceInstructions, setEvidenceInstructions] = useState(initial?.evidenceInstructions ?? "");
  const [rewardPoints, setRewardPoints] = useState(initial?.rewardPointsDefault ?? 10);
  const [rewardMood, setRewardMood] = useState(initial?.rewardMoodDefault ?? "");
  const [deadline, setDeadline] = useState(initial?.deadline ?? "");
  const [maxApprovals, setMaxApprovals] = useState(initial?.maxApprovals ?? "");
  const [allowDuplicates, setAllowDuplicates] = useState(initial?.allowDuplicateSubmissions ?? false);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const isEditing = Boolean(initial);

  const handleSave = () => {
    if (!title.trim()) { setError("请填写标题"); return; }
    if (!isEditing && !slug.trim()) { setError("请填写 slug"); return; }
    setSaving(true);
    const payload: Record<string, unknown> = {
      title,
      summary,
      description,
      category,
      status,
      requirements,
      evidenceInstructions,
      rewardPointsDefault: rewardPoints,
      rewardMoodDefault: rewardMood || null,
      deadline: deadline || null,
      maxApprovals: maxApprovals ? Number(maxApprovals) : null,
      allowDuplicateSubmissions: allowDuplicates,
    };
    if (!isEditing) payload.slug = slug;
    onSave(payload);
    setSaving(false);
  };

  return (
    <div style={{ display: "grid", gap: "var(--space-4)", maxWidth: 720 }}>
      <h2 style={{ margin: 0, fontSize: "var(--text-xl)", color: "var(--text)" }}>
        {isEditing ? "编辑任务" : "新建任务"}
      </h2>

      {!isEditing && (
        <div>
          <label style={{ display: "block", fontSize: "var(--text-sm)", color: "var(--text-muted)", marginBottom: "var(--space-1)" }}>
            Slug <span style={{ color: "var(--blocking)" }}>*</span>
          </label>
          <input
            type="text"
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
            placeholder="task-slug-001"
            style={{ width: "100%", padding: "var(--space-3)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", background: "var(--surface)", color: "var(--text)" }}
          />
          <p style={{ margin: "var(--space-1) 0 0", fontSize: "var(--text-xs)", color: "var(--text-faint)" }}>3-81位英文、数字、连字符，用于URL</p>
        </div>
      )}

      <div>
        <label style={{ display: "block", fontSize: "var(--text-sm)", color: "var(--text-muted)", marginBottom: "var(--space-1)" }}>
          标题 <span style={{ color: "var(--blocking)" }}>*</span>
        </label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={200}
          style={{ width: "100%", padding: "var(--space-3)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", background: "var(--surface)", color: "var(--text)" }}
        />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-3)" }}>
        <div>
          <label style={{ display: "block", fontSize: "var(--text-sm)", color: "var(--text-muted)", marginBottom: "var(--space-1)" }}>分类</label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            style={{ width: "100%", padding: "var(--space-3)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", background: "var(--surface)", color: "var(--text)" }}
          >
            {Object.entries(CATEGORY_LABELS).map(([key, label]) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
        </div>
        <div>
          <label style={{ display: "block", fontSize: "var(--text-sm)", color: "var(--text-muted)", marginBottom: "var(--space-1)" }}>状态</label>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value as TaskStatus)}
            style={{ width: "100%", padding: "var(--space-3)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", background: "var(--surface)", color: "var(--text)" }}
          >
            <option value="draft">草稿</option>
            <option value="active">开放</option>
            <option value="paused">暂停</option>
            <option value="completed">完成</option>
            <option value="archived">归档</option>
          </select>
        </div>
      </div>

      <div>
        <label style={{ display: "block", fontSize: "var(--text-sm)", color: "var(--text-muted)", marginBottom: "var(--space-1)" }}>摘要</label>
        <input
          type="text"
          value={summary}
          onChange={(e) => setSummary(e.target.value)}
          maxLength={400}
          placeholder="一句话描述任务"
          style={{ width: "100%", padding: "var(--space-3)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", background: "var(--surface)", color: "var(--text)" }}
        />
      </div>

      <div>
        <label style={{ display: "block", fontSize: "var(--text-sm)", color: "var(--text-muted)", marginBottom: "var(--space-1)" }}>详细描述</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={4}
          maxLength={8000}
          style={{ width: "100%", padding: "var(--space-3)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", background: "var(--surface)", color: "var(--text)", resize: "vertical" }}
        />
      </div>

      <div>
        <label style={{ display: "block", fontSize: "var(--text-sm)", color: "var(--text-muted)", marginBottom: "var(--space-1)" }}>要求</label>
        <textarea
          value={requirements}
          onChange={(e) => setRequirements(e.target.value)}
          rows={3}
          maxLength={4000}
          placeholder="参与者需要满足的条件"
          style={{ width: "100%", padding: "var(--space-3)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", background: "var(--surface)", color: "var(--text)", resize: "vertical" }}
        />
      </div>

      <div>
        <label style={{ display: "block", fontSize: "var(--text-sm)", color: "var(--text-muted)", marginBottom: "var(--space-1)" }}>证据提交说明</label>
        <textarea
          value={evidenceInstructions}
          onChange={(e) => setEvidenceInstructions(e.target.value)}
          rows={3}
          maxLength={4000}
          placeholder="如何提交证据、需要包含什么"
          style={{ width: "100%", padding: "var(--space-3)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", background: "var(--surface)", color: "var(--text)", resize: "vertical" }}
        />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-3)" }}>
        <div>
          <label style={{ display: "block", fontSize: "var(--text-sm)", color: "var(--text-muted)", marginBottom: "var(--space-1)" }}>默认 Reputation 点数</label>
          <input
            type="number"
            value={rewardPoints}
            onChange={(e) => setRewardPoints(Number(e.target.value))}
            min={0}
            style={{ width: "100%", padding: "var(--space-3)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", background: "var(--surface)", color: "var(--text)" }}
          />
        </div>
        <div>
          <label style={{ display: "block", fontSize: "var(--text-sm)", color: "var(--text-muted)", marginBottom: "var(--space-1)" }}>默认 MOOD 奖励</label>
          <input
            type="text"
            value={rewardMood}
            onChange={(e) => setRewardMood(e.target.value)}
            placeholder="100.0"
            style={{ width: "100%", padding: "var(--space-3)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", background: "var(--surface)", color: "var(--text)" }}
          />
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-3)" }}>
        <div>
          <label style={{ display: "block", fontSize: "var(--text-sm)", color: "var(--text-muted)", marginBottom: "var(--space-1)" }}>截止时间 (ISO 8601)</label>
          <input
            type="datetime-local"
            value={deadline ? new Date(deadline).toISOString().slice(0, 16) : ""}
            onChange={(e) => setDeadline(e.target.value ? new Date(e.target.value).toISOString() : "")}
            style={{ width: "100%", padding: "var(--space-3)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", background: "var(--surface)", color: "var(--text)" }}
          />
        </div>
        <div>
          <label style={{ display: "block", fontSize: "var(--text-sm)", color: "var(--text-muted)", marginBottom: "var(--space-1)" }}>最大批准数</label>
          <input
            type="number"
            value={maxApprovals}
            onChange={(e) => setMaxApprovals(e.target.value)}
            min={1}
            placeholder="无限制"
            style={{ width: "100%", padding: "var(--space-3)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", background: "var(--surface)", color: "var(--text)" }}
          />
        </div>
      </div>

      <div>
        <label style={{ display: "flex", alignItems: "center", gap: "var(--space-2)", fontSize: "var(--text-sm)", color: "var(--text-muted)", cursor: "pointer" }}>
          <input
            type="checkbox"
            checked={allowDuplicates}
            onChange={(e) => setAllowDuplicates(e.target.checked)}
          />
          允许同一参与者多次提交
        </label>
      </div>

      {error && (
        <div role="alert" style={{ padding: "var(--space-3)", border: "1px solid var(--blocking)", borderRadius: "var(--radius-sm)", color: "var(--blocking)", fontSize: "var(--text-sm)" }}>
          {error}
        </div>
      )}

      <div style={{ display: "flex", gap: "var(--space-3)", flexWrap: "wrap" }}>
        <Button type="button" variant="primary" onClick={handleSave} loading={saving} disabled={saving}>
          {saving ? "保存中..." : "保存"}
        </Button>
        <Button type="button" variant="ghost" onClick={onCancel}>取消</Button>
      </div>
    </div>
  );
}

function ReviewPanel({
  submission,
  onAction,
}: {
  submission: SubmissionDetail;
  onAction: (action: SubmissionStatus, data: { reason: string; pointsDelta?: number; rewardMood?: string }) => void;
}) {
  const [action, setAction] = useState<SubmissionStatus | null>(null);
  const [reason, setReason] = useState("");
  const [points, setPoints] = useState(submission.lastPointsDelta || 10);
  const [reward, setReward] = useState(submission.pendingRewardMood || "");

  const submit = () => {
    if (!action) return;
    if (!reason.trim()) return;
    onAction(action, {
      reason,
      pointsDelta: action === "approved" ? points : undefined,
      rewardMood: action === "approved" ? reward : undefined,
    });
  };

  if (submission.status === "approved" || submission.status === "rejected" || submission.status === "withdrawn") {
    return (
      <div style={{ padding: "var(--space-4)", border: "1px solid var(--line)", borderRadius: "var(--radius-md)", background: "var(--surface-subtle)" }}>
        <p style={{ margin: 0, fontSize: "var(--text-sm)", color: "var(--text-muted)" }}>
          此提交已处于终态 <strong>{SUBMISSION_STATUS_LABELS[submission.status]}</strong>，无法再进行审核操作。
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: "grid", gap: "var(--space-4)", padding: "var(--space-4)", border: "1px solid var(--line)", borderRadius: "var(--radius-md)", background: "var(--surface-subtle)" }}>
      <h3 style={{ margin: 0, fontSize: "var(--text-lg)", color: "var(--text)" }}>审核操作</h3>

      <div style={{ display: "flex", gap: "var(--space-2)", flexWrap: "wrap" }}>
        {[
          { key: "under_review", label: "开始审核" },
          { key: "changes_requested", label: "要求修改" },
          { key: "approved", label: "批准" },
          { key: "rejected", label: "拒绝" },
        ].map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setAction(key as SubmissionStatus)}
            style={{
              padding: "var(--space-2) var(--space-4)",
              border: action === key ? "2px solid var(--evidence)" : "2px solid var(--line)",
              borderRadius: "var(--radius-sm)",
              background: action === key ? "var(--evidence-soft)" : "var(--surface)",
              color: "var(--text)",
              cursor: "pointer",
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {action === "approved" && (
        <div style={{ display: "grid", gap: "var(--space-3)" }}>
          <div>
            <label style={{ display: "block", fontSize: "var(--text-sm)", color: "var(--text-muted)", marginBottom: "var(--space-1)" }}>
              Reputation 点数
            </label>
            <input
              type="number"
              value={points}
              onChange={(e) => setPoints(Number(e.target.value))}
              min={0}
              style={{ width: "100%", padding: "var(--space-3)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", background: "var(--surface)", color: "var(--text)" }}
            />
          </div>
          <div>
            <label style={{ display: "block", fontSize: "var(--text-sm)", color: "var(--text-muted)", marginBottom: "var(--space-1)" }}>
              MOOD 奖励 (待发放)
            </label>
            <input
              type="text"
              value={reward}
              onChange={(e) => setReward(e.target.value)}
              placeholder="100.0"
              style={{ width: "100%", padding: "var(--space-3)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", background: "var(--surface)", color: "var(--text)" }}
            />
            <p style={{ margin: "var(--space-1) 0 0", fontSize: "var(--text-xs)", color: "var(--text-faint)" }}>实际发放需经后续 distribution snapshot</p>
          </div>
        </div>
      )}

      <div>
        <label style={{ display: "block", fontSize: "var(--text-sm)", color: "var(--text-muted)", marginBottom: "var(--space-1)" }}>
          审核意见 <span style={{ color: "var(--blocking)" }}>*</span>
        </label>
        <textarea
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          rows={3}
          maxLength={500}
          placeholder="说明审核理由..."
          style={{ width: "100%", padding: "var(--space-3)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", background: "var(--surface)", color: "var(--text)", resize: "vertical" }}
        />
      </div>

      <div>
        <Button type="button" variant="primary" onClick={submit} disabled={!action || !reason.trim()}>
          确认操作
        </Button>
      </div>
    </div>
  );
}

function AuditTimeline({ submission }: { submission: SubmissionDetail }) {
  const events = [
    ...submission.reviewEvents.map((e) => ({ ...e, kind: "review" as const })),
    ...submission.reputationEvents.map((e) => ({ ...e, kind: "reputation" as const })),
    ...submission.rewardEvents.map((e) => ({ ...e, kind: "reward" as const })),
  ].sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime());

  return (
    <div style={{ display: "grid", gap: "var(--space-3)" }}>
      <h3 style={{ margin: 0, fontSize: "var(--text-lg)", color: "var(--text)" }}>审计时间线</h3>
      <div style={{ display: "grid", gap: "var(--space-2)" }}>
        {events.length === 0 && <p style={{ color: "var(--text-muted)", fontSize: "var(--text-sm)" }}>暂无记录</p>}
        {events.map((e, i) => (
          <div key={i} style={{ padding: "var(--space-3)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", background: "var(--surface)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "var(--text-xs)", color: "var(--text-faint)", marginBottom: "var(--space-1)" }}>
              <span>{e.kind === "review" ? "审核事件" : e.kind === "reputation" ? "Reputation" : "Reward"}</span>
              <span>{new Date(e.createdAt).toLocaleString()}</span>
            </div>
            {"eventType" in e && <p style={{ margin: 0, fontSize: "var(--text-sm)", color: "var(--text)" }}>{e.eventType}</p>}
            {"status" in e && <p style={{ margin: 0, fontSize: "var(--text-sm)", color: "var(--text)" }}>status: {e.status}</p>}
            {"pointsDelta" in e && e.pointsDelta !== 0 && (
              <p style={{ margin: 0, fontSize: "var(--text-sm)", color: e.pointsDelta > 0 ? "var(--evidence)" : "var(--blocking)" }}>
                {e.pointsDelta > 0 ? "+" : ""}{e.pointsDelta} points
              </p>
            )}
            {"rewardMood" in e && e.rewardMood !== "0" && (
              <p style={{ margin: 0, fontSize: "var(--text-sm)", color: "var(--evidence)" }}>{e.rewardMood} MOOD</p>
            )}
            {"reason" in e && e.reason && <p style={{ margin: "var(--space-1) 0 0", fontSize: "var(--text-xs)", color: "var(--text-muted)" }}>{e.reason}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}

function MetricsPanel({ metrics }: { metrics: Metrics }) {
  return (
    <div style={{ display: "grid", gap: "var(--space-4)", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))" }}>
      <MetricCard label="活跃任务" value={metrics.activeTasks} color="var(--evidence)" />
      <MetricCard label="草稿任务" value={metrics.drafts} color="var(--text-muted)" />
      <MetricCard label="暂停任务" value={metrics.paused} color="var(--attention)" />
      <MetricCard label="归档任务" value={metrics.archived} color="var(--text-faint)" />
      <MetricCard label="待审提交" value={metrics.submissionsAwaitingReview} color="var(--attention)" />
      <MetricCard label="已批提交" value={metrics.approvedSubmissions} color="var(--evidence)" />
      <MetricCard label="总 Reputation" value={metrics.totalReputationIssued} color="var(--evidence)" />
      <MetricCard label="待发放 MOOD" value={metrics.pendingRewardMoodTotal} color="var(--attention)" suffix="MOOD" />
      <MetricCard label="待发放笔数" value={metrics.pendingRewardCount} color="var(--text-muted)" />
      <MetricCard label="已取消奖励" value={metrics.cancelledRewardCount} color="var(--blocking)" />
    </div>
  );
}

function MetricCard({ label, value, color, suffix }: { label: string; value: string | number; color: string; suffix?: string }) {
  return (
    <div style={{ padding: "var(--space-4)", border: "1px solid var(--line)", borderRadius: "var(--radius-md)", background: "var(--surface-subtle)" }}>
      <p style={{ margin: 0, fontSize: "var(--text-xs)", color: "var(--text-faint)", textTransform: "uppercase", letterSpacing: "0.1em" }}>{label}</p>
      <p style={{ margin: "var(--space-2) 0 0", fontSize: "var(--text-2xl)", color, fontWeight: 700 }}>
        {value}{suffix ? <span style={{ fontSize: "var(--text-sm)", marginLeft: "var(--space-1)" }}>{suffix}</span> : null}
      </p>
    </div>
  );
}

export default function AdminContributionsPage() {
  const [tab, setTab] = useState<Tab>("tasks");
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedTask, setSelectedTask] = useState<TaskDetail | null>(null);
  const [editingTask, setEditingTask] = useState<TaskDetail | null>(null);
  const [creatingTask, setCreatingTask] = useState(false);
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [selectedSubmission, setSelectedSubmission] = useState<SubmissionDetail | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [submissionFilter, setSubmissionFilter] = useState<SubmissionStatus | "">("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadTasks = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/contribution/admin/tasks");
      if (!res.ok) throw new Error("加载任务失败");
      const data = await res.json();
      setTasks(data.tasks);
    } catch (e) {
      setError(e instanceof Error ? e.message : "未知错误");
    } finally {
      setLoading(false);
    }
  }, []);

  const loadSubmissions = useCallback(async () => {
    setLoading(true);
    try {
      const url = new URL("/api/contribution/admin/submissions", window.location.href);
      if (submissionFilter) url.searchParams.set("status", submissionFilter);
      url.searchParams.set("limit", "100");
      const res = await fetch(url);
      if (!res.ok) throw new Error("加载提交失败");
      const data = await res.json();
      setSubmissions(data.items);
    } catch (e) {
      setError(e instanceof Error ? e.message : "未知错误");
    } finally {
      setLoading(false);
    }
  }, [submissionFilter]);

  const loadMetrics = useCallback(async () => {
    try {
      const res = await fetch("/api/contribution/admin/metrics");
      if (!res.ok) throw new Error("加载指标失败");
      const data = await res.json();
      setMetrics(data.metrics);
    } catch (e) {
      setError(e instanceof Error ? e.message : "未知错误");
    }
  }, []);

  const openTaskDetail = async (task: Task) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/contribution/admin/tasks/${task.id}`);
      if (!res.ok) throw new Error("加载任务详情失败");
      const data = await res.json();
      setSelectedTask(data.task);
    } catch (e) {
      setError(e instanceof Error ? e.message : "未知错误");
    } finally {
      setLoading(false);
    }
  };

  const openSubmissionDetail = async (sub: Submission) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/contribution/admin/submissions/${sub.id}`);
      if (!res.ok) throw new Error("加载提交详情失败");
      const data = await res.json();
      setSelectedSubmission(data.submission);
    } catch (e) {
      setError(e instanceof Error ? e.message : "未知错误");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (data: Record<string, unknown>) => {
    setLoading(true);
    try {
      const res = await fetch("/api/contribution/admin/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error("创建任务失败");
      setCreatingTask(false);
      await loadTasks();
    } catch (e) {
      setError(e instanceof Error ? e.message : "未知错误");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateTask = async (data: Record<string, unknown>) => {
    if (!editingTask) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/contribution/admin/tasks/${editingTask.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error("更新任务失败");
      setEditingTask(null);
      setSelectedTask(null);
      await loadTasks();
    } catch (e) {
      setError(e instanceof Error ? e.message : "未知错误");
    } finally {
      setLoading(false);
    }
  };

  const handleReviewAction = async (
    action: SubmissionStatus,
    data: { reason: string; pointsDelta?: number; rewardMood?: string },
  ) => {
    if (!selectedSubmission) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/contribution/admin/submissions/${selectedSubmission.id}/transition`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, ...data }),
      });
      if (!res.ok) throw new Error("审核操作失败");
      const result = await res.json();
      setSelectedSubmission(result.submission);
      await loadSubmissions();
      await loadMetrics();
    } catch (e) {
      setError(e instanceof Error ? e.message : "未知错误");
    } finally {
      setLoading(false);
    }
  };

  // Load data when tab changes - using void to handle async calls properly
  useEffect(() => {
    if (tab === "tasks") {
      void loadTasks();
    }
    if (tab === "submissions") {
      void loadSubmissions();
    }
    if (tab === "metrics") {
      void loadMetrics();
    }
  }, [tab, loadTasks, loadSubmissions, loadMetrics]);

  return (
    <main style={{ minHeight: "100vh", background: "radial-gradient(circle at 70% 12%, rgba(36,66,154,.17), transparent 27%), linear-gradient(135deg, #070a22, #040719 70%)", padding: "0 clamp(20px, 4vw, 64px) var(--space-12)" }}>
      <nav aria-label="位置" style={{ paddingBlock: "var(--space-6)", color: "var(--text-faint)", fontSize: "var(--text-sm)" }}>
        <Link href="/" style={{ color: "inherit", textDecoration: "none" }}>← 返回 Moodify</Link>
      </nav>

      <header style={{ display: "grid", gap: "var(--space-4)", paddingBlock: "var(--space-8)", maxWidth: 800 }}>
        <span style={{ fontSize: "var(--text-xs)", letterSpacing: "0.18em", color: "var(--text-faint)", textTransform: "uppercase" }}>
          Admin · Contribution Network
        </span>
        <h1 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "var(--text-4xl)", color: "var(--text)", lineHeight: "var(--leading-tight)" }}>
          贡献网络管理
        </h1>
        <p style={{ margin: 0, fontSize: "var(--text-lg)", color: "var(--text-muted)", maxWidth: "52ch", lineHeight: "var(--leading-normal)" }}>
          管理任务、审核提交、查看指标。
        </p>
      </header>

      {error && (
        <div role="alert" style={{ padding: "var(--space-3)", border: "1px solid var(--blocking)", borderRadius: "var(--radius-sm)", color: "var(--blocking)", fontSize: "var(--text-sm)", marginBottom: "var(--space-4)", maxWidth: 640 }}>
          {error}
          <button onClick={() => setError(null)} style={{ marginLeft: "var(--space-3)", background: "none", border: "none", color: "var(--blocking)", cursor: "pointer" }}>清除</button>
        </div>
      )}

      {/* Tabs */}
      <div style={{ display: "flex", gap: "var(--space-1)", borderBottom: "1px solid var(--line)", maxWidth: 640, marginBottom: "var(--space-6)" }}>
        {[
          ["tasks", "任务管理"],
          ["submissions", "审核队列"],
          ["metrics", "数据指标"],
        ].map(([key, label]) => (
          <button
            key={key}
            onClick={() => setTab(key as Tab)}
            style={{
              padding: "var(--space-2) var(--space-4)",
              background: "none",
              border: "none",
              borderBottom: tab === key ? "2px solid var(--evidence)" : "2px solid transparent",
              color: tab === key ? "var(--text)" : "var(--text-muted)",
              cursor: "pointer",
              fontSize: "var(--text-md)",
              fontWeight: tab === key ? 600 : 400,
              marginBottom: -1,
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Tasks Tab */}
      {tab === "tasks" && !selectedTask && !editingTask && !creatingTask && (
        <div style={{ maxWidth: 960 }}>
          <div style={{ marginBottom: "var(--space-4)" }}>
            <Button type="button" variant="primary" onClick={() => setCreatingTask(true)}>+ 新建任务</Button>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "var(--space-3)" }}>
            {tasks.map((task) => (
              <TaskCard key={task.id} task={task} onClick={() => void openTaskDetail(task)} />
            ))}
          </div>
          {tasks.length === 0 && !loading && <p style={{ color: "var(--text-muted)" }}>暂无任务</p>}
          {loading && <p style={{ color: "var(--text-muted)" }}>加载中...</p>}
        </div>
      )}

      {tab === "tasks" && selectedTask && !editingTask && (
        <div style={{ maxWidth: 720 }}>
          <button
            onClick={() => setSelectedTask(null)}
            style={{ background: "none", border: "none", color: "var(--text-muted)", cursor: "pointer", fontSize: "var(--text-sm)", marginBottom: "var(--space-4)", display: "flex", alignItems: "center", gap: "var(--space-1)" }}
          >
            ← 返回列表
          </button>
          <div style={{ display: "grid", gap: "var(--space-4)", padding: "var(--space-4)", border: "1px solid var(--line)", borderRadius: "var(--radius-md)", background: "var(--surface-subtle)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
              <h2 style={{ margin: 0, fontSize: "var(--text-2xl)", color: "var(--text)" }}>{selectedTask.title}</h2>
              <span style={{ fontSize: "var(--text-sm)", color: STATUS_COLORS[selectedTask.status] }}>{STATUS_LABELS[selectedTask.status]}</span>
            </div>
            <p style={{ margin: 0, color: "var(--text-muted)" }}>{selectedTask.summary}</p>
            <div style={{ display: "grid", gap: "var(--space-2)", fontSize: "var(--text-sm)", color: "var(--text-muted)" }}>
              <p><strong>分类:</strong> {CATEGORY_LABELS[selectedTask.category] ?? selectedTask.category}</p>
              <p><strong>默认 Reputation:</strong> {selectedTask.rewardPointsDefault}</p>
              {selectedTask.rewardMoodDefault && <p><strong>默认 MOOD:</strong> {selectedTask.rewardMoodDefault}</p>}
              {selectedTask.deadline && <p><strong>截止:</strong> {new Date(selectedTask.deadline).toLocaleString()}</p>}
              {selectedTask.maxApprovals && <p><strong>最大批准:</strong> {selectedTask.maxApprovals}</p>}
              <p><strong>允许重复提交:</strong> {selectedTask.allowDuplicateSubmissions ? "是" : "否"}</p>
            </div>
            {selectedTask.description && (
              <div>
                <h3 style={{ margin: "0 0 var(--space-2)", fontSize: "var(--text-md)", color: "var(--text)" }}>描述</h3>
                <p style={{ margin: 0, color: "var(--text-muted)", whiteSpace: "pre-wrap" }}>{selectedTask.description}</p>
              </div>
            )}
            {selectedTask.requirements && (
              <div>
                <h3 style={{ margin: "0 0 var(--space-2)", fontSize: "var(--text-md)", color: "var(--text)" }}>要求</h3>
                <p style={{ margin: 0, color: "var(--text-muted)", whiteSpace: "pre-wrap" }}>{selectedTask.requirements}</p>
              </div>
            )}
            {selectedTask.evidenceInstructions && (
              <div>
                <h3 style={{ margin: "0 0 var(--space-2)", fontSize: "var(--text-md)", color: "var(--text)" }}>证据说明</h3>
                <p style={{ margin: 0, color: "var(--text-muted)", whiteSpace: "pre-wrap" }}>{selectedTask.evidenceInstructions}</p>
              </div>
            )}
            <div style={{ display: "flex", gap: "var(--space-3)" }}>
              <Button type="button" variant="primary" onClick={() => setEditingTask(selectedTask)}>编辑</Button>
              <Button type="button" variant="ghost" onClick={() => setSelectedTask(null)}>返回</Button>
            </div>
          </div>
        </div>
      )}

      {tab === "tasks" && (creatingTask || editingTask) && (
        <div style={{ maxWidth: 720 }}>
          <button
            onClick={() => { setCreatingTask(false); setEditingTask(null); }}
            style={{ background: "none", border: "none", color: "var(--text-muted)", cursor: "pointer", fontSize: "var(--text-sm)", marginBottom: "var(--space-4)", display: "flex", alignItems: "center", gap: "var(--space-1)" }}
          >
            ← 返回
          </button>
          <TaskForm
            initial={editingTask ?? undefined}
            onSave={creatingTask ? handleCreateTask : handleUpdateTask}
            onCancel={() => { setCreatingTask(false); setEditingTask(null); }}
          />
        </div>
      )}

      {/* Submissions Tab */}
      {tab === "submissions" && !selectedSubmission && (
        <div style={{ maxWidth: 960 }}>
          <div style={{ display: "flex", gap: "var(--space-3)", marginBottom: "var(--space-4)", flexWrap: "wrap" }}>
            <select
              value={submissionFilter}
              onChange={(e) => setSubmissionFilter(e.target.value as SubmissionStatus | "")}
              style={{ padding: "var(--space-2)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", background: "var(--surface)", color: "var(--text)" }}
            >
              <option value="">全部状态</option>
              <option value="submitted">待审核</option>
              <option value="under_review">审核中</option>
              <option value="changes_requested">需要修改</option>
              <option value="approved">已批准</option>
              <option value="rejected">已拒绝</option>
              <option value="withdrawn">已撤回</option>
            </select>
            <Button type="button" variant="ghost" onClick={loadSubmissions}>刷新</Button>
          </div>
          <div style={{ border: "1px solid var(--line)", borderRadius: "var(--radius-md)", overflow: "hidden" }}>
            {submissions.length === 0 && !loading && (
              <div style={{ padding: "var(--space-4)", color: "var(--text-muted)" }}>暂无提交</div>
            )}
            {submissions.map((sub) => (
              <SubmissionRow key={sub.id} sub={sub} onClick={() => void openSubmissionDetail(sub)} />
            ))}
          </div>
          {loading && <p style={{ color: "var(--text-muted)", marginTop: "var(--space-4)" }}>加载中...</p>}
        </div>
      )}

      {tab === "submissions" && selectedSubmission && (
        <div style={{ maxWidth: 960 }}>
          <button
            onClick={() => setSelectedSubmission(null)}
            style={{ background: "none", border: "none", color: "var(--text-muted)", cursor: "pointer", fontSize: "var(--text-sm)", marginBottom: "var(--space-4)", display: "flex", alignItems: "center", gap: "var(--space-1)" }}
          >
            ← 返回列表
          </button>
          <div style={{ display: "grid", gap: "var(--space-6)", gridTemplateColumns: "1fr 1fr", maxWidth: "100%" }}>
            <div style={{ display: "grid", gap: "var(--space-4)" }}>
              <div style={{ padding: "var(--space-4)", border: "1px solid var(--line)", borderRadius: "var(--radius-md)", background: "var(--surface-subtle)" }}>
                <h2 style={{ margin: "0 0 var(--space-3)", fontSize: "var(--text-xl)", color: "var(--text)" }}>提交详情</h2>
                <div style={{ display: "grid", gap: "var(--space-2)", fontSize: "var(--text-sm)", color: "var(--text-muted)" }}>
                  <p><strong>任务:</strong> {selectedSubmission.taskTitle}</p>
                  <p><strong>Participant:</strong> #{selectedSubmission.participantNumber}</p>
                  <p><strong>钱包:</strong> {selectedSubmission.participantWallet}</p>
                  <p><strong>状态:</strong> <span style={{ color: SUBMISSION_STATUS_COLORS[selectedSubmission.status] }}>{SUBMISSION_STATUS_LABELS[selectedSubmission.status]}</span></p>
                  <p><strong>版本:</strong> v{selectedSubmission.revisionNumber}</p>
                  <p><strong>提交时间:</strong> {new Date(selectedSubmission.submittedAt).toLocaleString()}</p>
                </div>
              </div>
              <div style={{ padding: "var(--space-4)", border: "1px solid var(--line)", borderRadius: "var(--radius-md)", background: "var(--surface-subtle)" }}>
                <h3 style={{ margin: "0 0 var(--space-2)", fontSize: "var(--text-md)", color: "var(--text)" }}>摘要</h3>
                <p style={{ margin: 0, color: "var(--text)", fontSize: "var(--text-md)" }}>{selectedSubmission.summary}</p>
              </div>
              {selectedSubmission.evidenceText && (
                <div style={{ padding: "var(--space-4)", border: "1px solid var(--line)", borderRadius: "var(--radius-md)", background: "var(--surface-subtle)" }}>
                  <h3 style={{ margin: "0 0 var(--space-2)", fontSize: "var(--text-md)", color: "var(--text)" }}>证据说明</h3>
                  <p style={{ margin: 0, color: "var(--text-muted)", whiteSpace: "pre-wrap" }}>{selectedSubmission.evidenceText}</p>
                </div>
              )}
              {selectedSubmission.evidenceUrls.length > 0 && (
                <div style={{ padding: "var(--space-4)", border: "1px solid var(--line)", borderRadius: "var(--radius-md)", background: "var(--surface-subtle)" }}>
                  <h3 style={{ margin: "0 0 var(--space-2)", fontSize: "var(--text-md)", color: "var(--text)" }}>证据链接</h3>
                  <ul style={{ margin: 0, padding: 0, listStyle: "none", display: "grid", gap: "var(--space-1)" }}>
                    {selectedSubmission.evidenceUrls.map((url) => (
                      <li key={url}>
                        <a href={url} target="_blank" rel="noopener noreferrer" style={{ color: "var(--evidence)", fontSize: "var(--text-sm)" }}>
                          {url}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            <div style={{ display: "grid", gap: "var(--space-4)" }}>
              <ReviewPanel submission={selectedSubmission} onAction={handleReviewAction} />
              <AuditTimeline submission={selectedSubmission} />
            </div>
          </div>
        </div>
      )}

      {/* Metrics Tab */}
      {tab === "metrics" && metrics && (
        <div style={{ maxWidth: 960 }}>
          <MetricsPanel metrics={metrics} />
        </div>
      )}

      <footer style={{ marginTop: "var(--space-12)", paddingTop: "var(--space-8)", borderTop: "1px solid var(--line)", color: "var(--text-faint)", fontSize: "var(--text-sm)", maxWidth: 640 }}>
        <p style={{ margin: 0, lineHeight: "var(--leading-normal)" }}>
          协议文档见 <code style={{ fontFamily: "ui-monospace" }}>docs/protocol/CONTRIBUTION_NETWORK.md</code>。
        </p>
      </footer>
    </main>
  );
}
