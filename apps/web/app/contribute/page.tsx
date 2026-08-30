"use client";

/*** MOOD-GENESIS-006: Contribution Network — public /contribute page.
 *
 * Allows registered Genesis Participants to browse tasks, submit evidence,
 * and track their contributions.
 *
 * States:
 * - no wallet: guide to /genesis
 * - wallet connected but not registered: redirect to /genesis
 * - wallet connected + registered: show task catalog + submission flow
 *
 * MOOD rewards are always labeled as "Pending allocation" until actually
 * distributed (C-016 / spec §17). No automatic token transfer occurs. */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { GENESIS_CONFIG } from "../../lib/genesis-config";
import { checksumAddress, shortenAddress } from "../../lib/evm-address";
import { Button } from "../../components/ui/primitives";
import type { SubmissionStatus } from "../../lib/contribution-config";

type EthereumProvider = {
  request: (args: { method: string; params?: unknown[] }) => Promise<unknown>;
  on?: (event: string, handler: (...args: unknown[]) => void) => void;
  removeListener?: (event: string, handler: (...args: unknown[]) => void) => void;
};
declare global {
  interface Window { ethereum?: EthereumProvider; }
}

const BSC_HEX = "0x38";

function getProvider(): EthereumProvider | null {
  if (typeof window === "undefined") return null;
  return window.ethereum ?? null;
}

function explainError(error: unknown): string {
  if (error instanceof Error) {
    if (/User rejected|user rejected|ACTION_REJECTED|4001/i.test(error.message)) return "用户已拒绝签名";
    return error.message;
  }
  return "未知错误";
}

type Phase =
  | "loading"
  | "no-wallet"
  | "wallet-disconnected"
  | "connecting"
  | "wrong-network"
  | "checking-registration"
  | "not-registered"
  | "ready"
  | "submitting"
  | "submitted"
  | "error";

type Task = {
  id: string;
  slug: string;
  title: string;
  summary: string;
  category: string;
  status: string;
  rewardPointsDefault: number;
  rewardMoodDefault: string | null;
  deadline: string | null;
  maxApprovals: number | null;
  publishedAt: string | null;
};

type TaskDetail = Task & {
  description: string;
  requirements: string;
  evidenceInstructions: string;
  allowDuplicateSubmissions: boolean;
};

type Submission = {
  id: string;
  taskId: string;
  taskSlug: string;
  taskTitle: string;
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

type ParticipantInfo = {
  id: string;
  participantNumber: number;
  address: string;
  reputationScore: number;
  pendingRewardMood: string | null;
  submissionCount: number;
  approvedSubmissionCount: number;
};

const STATUS_LABELS: Record<string, string> = {
  submitted: "待审核",
  under_review: "审核中",
  changes_requested: "需要修改",
  approved: "已批准",
  rejected: "已拒绝",
  withdrawn: "已撤回",
};

const STATUS_COLORS: Record<string, string> = {
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
      <div style={{ display: "flex", alignItems: "baseline", gap: "var(--space-2)", flexWrap: "wrap" }}>
        <span style={{ fontSize: "var(--text-xs)", color: "var(--text-faint)", textTransform: "uppercase", letterSpacing: "0.1em" }}>
          {task.category}
        </span>
        <span style={{ fontSize: "var(--text-sm)", color: "var(--text-faint)" }}>
          {task.rewardPointsDefault > 0 ? `${task.rewardPointsDefault} pts` : ""}
          {task.rewardMoodDefault ? ` · ${task.rewardMoodDefault} MOOD` : ""}
        </span>
      </div>
      <h3 style={{ margin: 0, fontSize: "var(--text-lg)", color: "var(--text)", fontWeight: 600 }}>{task.title}</h3>
      <p style={{ margin: 0, fontSize: "var(--text-sm)", color: "var(--text-muted)", overflow: "hidden", display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical" }}>
        {task.summary}
      </p>
      {task.deadline && (
        <p style={{ margin: 0, fontSize: "var(--text-xs)", color: "var(--text-faint)" }}>
          截止: {new Date(task.deadline).toLocaleDateString()}
        </p>
      )}
    </article>
  );
}

function SubmissionRow({ sub }: { sub: Submission }) {
  const statusColor = STATUS_COLORS[sub.status] ?? "var(--text-muted)";
  return (
    <div style={{
      padding: "var(--space-3) var(--space-4)",
      borderBottom: "1px solid var(--line)",
      display: "grid",
      gap: "var(--space-1)",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", flexWrap: "wrap", gap: "var(--space-2)" }}>
        <strong style={{ fontSize: "var(--text-md)", color: "var(--text)" }}>{sub.taskTitle}</strong>
        <span style={{ fontSize: "var(--text-sm)", color: statusColor }}>{STATUS_LABELS[sub.status] ?? sub.status}</span>
      </div>
      <p style={{ margin: 0, fontSize: "var(--text-sm)", color: "var(--text-muted)" }}>{sub.summary}</p>
      {sub.status === "approved" && sub.lastPointsDelta > 0 && (
        <p style={{ margin: 0, fontSize: "var(--text-sm)", color: "var(--evidence)" }}>
          +{sub.lastPointsDelta} Reputation
        </p>
      )}
      {sub.status === "approved" && sub.pendingRewardMood && (
        <p style={{ margin: 0, fontSize: "var(--text-sm)", color: "var(--evidence)" }}>
          +{sub.pendingRewardMood} MOOD (待发放)
        </p>
      )}
      {sub.status === "changes_requested" && sub.reviewNote && (
        <p style={{ margin: 0, fontSize: "var(--text-sm)", color: "var(--attention)" }}>
          审核意见: {sub.reviewNote}
        </p>
      )}
      <p style={{ margin: 0, fontSize: "var(--text-xs)", color: "var(--text-faint)" }}>
        提交于 {new Date(sub.submittedAt).toLocaleString()} · v{sub.revisionNumber}
      </p>
    </div>
  );
}

function SubmitForm({
  task,
  participant,
  onSuccess,
  onCancel,
}: {
  task: TaskDetail;
  participant: ParticipantInfo;
  onSuccess: () => void;
  onCancel: () => void;
}) {
  const [summary, setSummary] = useState("");
  const [evidenceText, setEvidenceText] = useState("");
  const [evidenceUrlInput, setEvidenceUrlInput] = useState("");
  const [evidenceUrls, setEvidenceUrls] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addUrl = () => {
    const trimmed = evidenceUrlInput.trim();
    if (!trimmed) return;
    if (evidenceUrls.includes(trimmed)) { setEvidenceUrlInput(""); return; }
    if (evidenceUrls.length >= 10) { setError("最多 10 个链接"); return; }
    setEvidenceUrls((prev) => [...prev, trimmed]);
    setEvidenceUrlInput("");
  };

  const removeUrl = (url: string) => setEvidenceUrls((prev) => prev.filter((u) => u !== url));

  const handleSubmit = async () => {
    if (!summary.trim()) { setError("请填写摘要"); return; }
    setSubmitting(true);
    setError(null);
    try {
      const res = await fetch(`/api/contribution/submissions?address=${encodeURIComponent(participant.address)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ taskId: task.id, summary: summary.trim(), evidenceText: evidenceText.trim(), evidenceUrls }),
      });
      const data = await res.json() as { error?: { message?: string } };
      if (!res.ok) {
        setError(data.error?.message ?? "提交失败");
        return;
      }
      onSuccess();
    } catch {
      setError("网络错误，请稍后重试");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ display: "grid", gap: "var(--space-6)", maxWidth: 680 }}>
      <div>
        <h2 style={{ margin: 0, fontSize: "var(--text-2xl)", color: "var(--text)" }}>{task.title}</h2>
        <p style={{ margin: "var(--space-2) 0 0", fontSize: "var(--text-sm)", color: "var(--text-muted)" }}>
          {task.category}
          {task.rewardPointsDefault > 0 && ` · ${task.rewardPointsDefault} Reputation points`}
          {task.rewardMoodDefault && ` · ${task.rewardMoodDefault} MOOD (待发放)`}
        </p>
      </div>

      {task.description && (
        <div>
          <h3 style={{ margin: "0 0 var(--space-2)", fontSize: "var(--text-md)", color: "var(--text)" }}>描述</h3>
          <p style={{ margin: 0, fontSize: "var(--text-md)", color: "var(--text-muted)", whiteSpace: "pre-wrap" }}>{task.description}</p>
        </div>
      )}

      {task.requirements && (
        <div>
          <h3 style={{ margin: "0 0 var(--space-2)", fontSize: "var(--text-md)", color: "var(--text)" }}>要求</h3>
          <p style={{ margin: 0, fontSize: "var(--text-md)", color: "var(--text-muted)", whiteSpace: "pre-wrap" }}>{task.requirements}</p>
        </div>
      )}

      {task.evidenceInstructions && (
        <div>
          <h3 style={{ margin: "0 0 var(--space-2)", fontSize: "var(--text-md)", color: "var(--text)" }}>提交说明</h3>
          <p style={{ margin: 0, fontSize: "var(--text-md)", color: "var(--text-muted)", whiteSpace: "pre-wrap" }}>{task.evidenceInstructions}</p>
        </div>
      )}

      <div style={{ display: "grid", gap: "var(--space-3)", padding: "var(--space-4)", border: "1px solid var(--line)", borderRadius: "var(--radius-md)", background: "var(--surface-subtle)" }}>
        <h3 style={{ margin: 0, fontSize: "var(--text-lg)", color: "var(--text)" }}>提交内容</h3>

        <div>
          <label style={{ display: "block", fontSize: "var(--text-sm)", color: "var(--text-muted)", marginBottom: "var(--space-1)" }}>
            摘要 <span style={{ color: "var(--blocking)" }}>*</span>
          </label>
          <input
            type="text"
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            maxLength={400}
            placeholder="简要描述你完成了什么"
            style={{ width: "100%", boxSizing: "border-box", padding: "var(--space-3)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", background: "var(--surface)", color: "var(--text)", fontSize: "var(--text-md)", outline: "none" }}
          />
          <p style={{ margin: "var(--space-1) 0 0", fontSize: "var(--text-xs)", color: "var(--text-faint)" }}>{summary.length}/400</p>
        </div>

        <div>
          <label style={{ display: "block", fontSize: "var(--text-sm)", color: "var(--text-muted)", marginBottom: "var(--space-1)" }}>
            证据 / 成果说明
          </label>
          <textarea
            value={evidenceText}
            onChange={(e) => setEvidenceText(e.target.value)}
            maxLength={4000}
            rows={4}
            placeholder="详细说明你的贡献，或粘贴测试报告、文档链接等"
            style={{ width: "100%", boxSizing: "border-box", padding: "var(--space-3)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", background: "var(--surface)", color: "var(--text)", fontSize: "var(--text-md)", outline: "none", resize: "vertical" }}
          />
          <p style={{ margin: "var(--space-1) 0 0", fontSize: "var(--text-xs)", color: "var(--text-faint)" }}>{evidenceText.length}/4000</p>
        </div>

        <div>
          <label style={{ display: "block", fontSize: "var(--text-sm)", color: "var(--text-muted)", marginBottom: "var(--space-1)" }}>
            证据链接 (最多10个)
          </label>
          <div style={{ display: "flex", gap: "var(--space-2)" }}>
            <input
              type="url"
              value={evidenceUrlInput}
              onChange={(e) => setEvidenceUrlInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addUrl(); } }}
              placeholder="https://github.com/... 或 https://..."
              style={{ flex: 1, padding: "var(--space-3)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", background: "var(--surface)", color: "var(--text)", fontSize: "var(--text-md)", outline: "none" }}
            />
            <Button type="button" variant="ghost" size="sm" onClick={addUrl}>添加</Button>
          </div>
          {evidenceUrls.length > 0 && (
            <ul style={{ margin: "var(--space-2) 0 0", padding: 0, listStyle: "none", display: "grid", gap: "var(--space-1)" }}>
              {evidenceUrls.map((url) => (
                <li key={url} style={{ display: "flex", alignItems: "center", gap: "var(--space-2)", fontSize: "var(--text-sm)", color: "var(--text)" }}>
                  <span style={{ flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{url}</span>
                  <button type="button" onClick={() => removeUrl(url)} style={{ background: "none", border: "none", color: "var(--blocking)", cursor: "pointer", fontSize: "var(--text-sm)" }}>✕</button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {error && (
        <div role="alert" style={{ padding: "var(--space-3)", border: "1px solid var(--blocking)", borderRadius: "var(--radius-sm)", color: "var(--blocking)", fontSize: "var(--text-sm)" }}>
          {error}
        </div>
      )}

      <div style={{ display: "flex", gap: "var(--space-3)", flexWrap: "wrap" }}>
        <Button type="button" variant="primary" onClick={handleSubmit} loading={submitting} disabled={submitting}>
          {submitting ? "提交中……" : "提交"}
        </Button>
        <Button type="button" variant="ghost" onClick={onCancel}>取消</Button>
      </div>

      <p style={{ margin: 0, fontSize: "var(--text-xs)", color: "var(--text-faint)" }}>
        提交代表你确认贡献内容原创且符合任务要求。审核结果将更新到「我的贡献」。
        MOOD 奖励标记为「待发放」,实际发放需经 Moodify 协议批准。
      </p>
    </div>
  );
}

export default function ContributePage() {
  const [phase, setPhase] = useState<Phase>("loading");
  const [address, setAddress] = useState<string | null>(null);
  const [chainId, setChainId] = useState<number | null>(null);
  const [participant, setParticipant] = useState<ParticipantInfo | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedTask, setSelectedTask] = useState<TaskDetail | null>(null);
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [tab, setTab] = useState<"catalog" | "mine">("catalog");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const providerRef = useRef<EthereumProvider | null>(null);

  const hasWallet = useMemo(() => typeof window !== "undefined" && Boolean(window.ethereum), []);

  useEffect(() => {
    const provider = getProvider();
    providerRef.current = provider;
    if (!provider) { setPhase("no-wallet"); return; }
    const onAccountsChanged = (accounts: unknown) => {
      const list = accounts as string[];
      if (!list?.length) { setAddress(null); setPhase("wallet-disconnected"); }
      else { setAddress(checksumAddress(list[0])); setPhase("wallet-disconnected"); }
    };
    const onChainChanged = (raw: unknown) => {
      const hex = typeof raw === "string" ? raw : "";
      const parsed = parseInt(hex, 16);
      if (Number.isFinite(parsed)) setChainId(parsed);
    };
    provider.on?.("accountsChanged", onAccountsChanged);
    provider.on?.("chainChanged", onChainChanged);
    void (async () => {
      try {
        const accounts = (await provider.request({ method: "eth_accounts" })) as string[] | undefined;
        const hexChain = (await provider.request({ method: "eth_chainId" })) as string | undefined;
        if (Array.isArray(accounts) && accounts.length > 0) {
          setAddress(checksumAddress(accounts[0]));
          if (hexChain) {
            const parsed = parseInt(hexChain, 16);
            setChainId(Number.isFinite(parsed) ? parsed : null);
            if (parsed === GENESIS_CONFIG.chainId) setPhase("checking-registration");
            else setPhase("wrong-network");
          } else setPhase("checking-registration");
        } else setPhase("wallet-disconnected");
      } catch { setPhase("wallet-disconnected"); }
    })();
    return () => {
      provider.removeListener?.("accountsChanged", onAccountsChanged);
      provider.removeListener?.("chainChanged", onChainChanged);
    };
  }, []);

  const loadParticipant = useCallback(async (addr: string) => {
    const res = await fetch(`/api/contribution/me?address=${encodeURIComponent(addr)}`);
    if (res.ok) {
      const data = await res.json() as { participant: ParticipantInfo };
      setParticipant(data.participant);
      setPhase("ready");
    } else {
      setPhase("not-registered");
    }
  }, []);

  const loadTasks = useCallback(async () => {
    const res = await fetch("/api/contribution/tasks");
    if (res.ok) {
      const data = await res.json() as { tasks: Task[] };
      setTasks(data.tasks);
    }
  }, []);

  const loadSubmissions = useCallback(async (addr: string) => {
    const res = await fetch(`/api/contribution/submissions?address=${encodeURIComponent(addr)}`);
    if (res.ok) {
      const data = await res.json() as { submissions: Submission[] };
      setSubmissions(data.submissions);
    }
  }, []);

  useEffect(() => {
    if (phase === "checking-registration" && address) {
      void loadParticipant(address);
      void loadTasks();
    }
  }, [phase, address, loadParticipant, loadTasks]);

  const connect = useCallback(async () => {
    const provider = providerRef.current ?? getProvider();
    if (!provider) { setErrorMessage("未检测到 EVM 钱包"); setPhase("error"); return; }
    setPhase("connecting");
    try {
      const accounts = (await provider.request({ method: "eth_requestAccounts" })) as string[];
      const hexChain = (await provider.request({ method: "eth_chainId" })) as string;
      if (!Array.isArray(accounts) || !accounts.length) throw new Error("无账户");
      setAddress(checksumAddress(accounts[0]));
      const parsed = parseInt(hexChain, 16);
      setChainId(parsed);
      if (parsed !== GENESIS_CONFIG.chainId) { setPhase("wrong-network"); return; }
      setPhase("checking-registration");
    } catch (error) {
      setErrorMessage(explainError(error));
      setPhase("error");
    }
  }, []);

  const switchNetwork = useCallback(async () => {
    const provider = providerRef.current ?? getProvider();
    if (!provider) return;
    try {
      await provider.request({ method: "wallet_switchEthereumChain", params: [{ chainId: BSC_HEX }] });
    } catch { setErrorMessage("切换网络失败"); }
  }, []);

  const openTaskDetail = async (task: Task) => {
    const res = await fetch(`/api/contribution/tasks/${task.id}`);
    if (res.ok) {
      const data = await res.json() as { task: TaskDetail };
      setSelectedTask(data.task);
    }
  };

  const handleSubmitSuccess = () => {
    setSelectedTask(null);
    setTab("mine");
    if (address) void loadSubmissions(address);
  };

  useEffect(() => {
    if (tab === "mine" && address && participant) void loadSubmissions(address);
  }, [tab, address, participant, loadSubmissions]);

  return (
    <main style={{ minHeight: "100vh", background: "radial-gradient(circle at 70% 12%, rgba(36,66,154,.17), transparent 27%), linear-gradient(135deg, #070a22, #040719 70%)", padding: "0 clamp(20px, 4vw, 64px) var(--space-12)" }}>
      <nav aria-label="位置" style={{ paddingBlock: "var(--space-6)", color: "var(--text-faint)", fontSize: "var(--text-sm)" }}>
        <Link href="/" style={{ color: "inherit", textDecoration: "none" }}>← 返回 Moodify</Link>
      </nav>

      <header style={{ display: "grid", gap: "var(--space-4)", paddingBlock: "var(--space-8)", maxWidth: 800 }}>
        <span style={{ fontSize: "var(--text-xs)", letterSpacing: "0.18em", color: "var(--text-faint)", textTransform: "uppercase" }}>
          Protocol · Contribution
        </span>
        <h1 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "var(--text-4xl)", color: "var(--text)", lineHeight: "var(--leading-tight)" }}>
          Moodify 贡献网络
        </h1>
        <p style={{ margin: 0, fontSize: "var(--text-lg)", color: "var(--text-muted)", maxWidth: "52ch", lineHeight: "var(--leading-normal)" }}>
          通过代码、测试、数据集、研究、文档、翻译、漏洞报告或社区贡献Earn MOOD。
          贡献经审核后获得 Reputation 与待发放 MOOD 奖励。
        </p>
        <p style={{ margin: 0, fontSize: "var(--text-sm)", color: "var(--attention)" }}>
          MOOD 奖励为待发放状态,需经 Moodify 协议批准后实际发放。本流程不构成任何投资回报承诺。
        </p>
      </header>

      {/* Wallet / registration gate */}
      {(phase === "loading" || phase === "checking-registration") && (
        <div style={{ padding: "var(--space-6)", color: "var(--text-muted)", fontSize: "var(--text-md)" }}>
          正在检查注册状态……
        </div>
      )}

      {phase === "no-wallet" && (
        <div style={{ padding: "var(--space-6)", border: "1px solid var(--line)", borderRadius: "var(--radius-md)", background: "var(--surface-subtle)", display: "grid", gap: "var(--space-3)", maxWidth: 560 }}>
          <h2 style={{ margin: 0, fontSize: "var(--text-xl)", color: "var(--text)" }}>需要 EVM 钱包</h2>
          <p style={{ margin: 0, color: "var(--text-muted)" }}>请安装 MetaMask、Rabby 或其他 EIP-1193 钱包扩展。</p>
          <p style={{ margin: 0, color: "var(--text-faint)", fontSize: "var(--text-sm)" }}>仅支持 BNB Smart Chain (chainId {GENESIS_CONFIG.chainId})。</p>
        </div>
      )}

      {(phase === "wallet-disconnected" || phase === "connecting" || phase === "error") && (
        <div style={{ padding: "var(--space-6)", border: "1px solid var(--line)", borderRadius: "var(--radius-md)", background: "var(--surface-subtle)", display: "grid", gap: "var(--space-3)", maxWidth: 560 }}>
          <h2 style={{ margin: 0, fontSize: "var(--text-xl)", color: "var(--text)" }}>连接钱包</h2>
          {errorMessage && <p style={{ margin: 0, color: "var(--blocking)", fontSize: "var(--text-sm)" }}>{errorMessage}</p>}
          <Button type="button" variant="primary" onClick={connect} loading={phase === "connecting"} disabled={phase === "connecting"}>
            {phase === "connecting" ? "连接中……" : "连接钱包"}
          </Button>
        </div>
      )}

      {phase === "wrong-network" && (
        <div style={{ padding: "var(--space-6)", border: "1px solid var(--attention)", borderRadius: "var(--radius-md)", background: "var(--attention-soft)", display: "grid", gap: "var(--space-3)", maxWidth: 560 }}>
          <h2 style={{ margin: 0, fontSize: "var(--text-xl)", color: "var(--text)" }}>网络不匹配</h2>
          <p style={{ margin: 0, color: "var(--text-muted)" }}>请切换到 {GENESIS_CONFIG.network} (chainId {GENESIS_CONFIG.chainId})。</p>
          <Button type="button" variant="ghost" onClick={switchNetwork}>切换网络</Button>
        </div>
      )}

      {phase === "not-registered" && (
        <div style={{ padding: "var(--space-6)", border: "1px solid var(--evidence)", borderLeft: "3px solid var(--evidence)", borderRadius: "var(--radius-md)", background: "var(--evidence-soft)", display: "grid", gap: "var(--space-3)", maxWidth: 560 }}>
          <h2 style={{ margin: 0, fontSize: "var(--text-xl)", color: "var(--text)" }}>需要先注册 Genesis Participant</h2>
          <p style={{ margin: 0, color: "var(--text-muted)" }}>你的钱包尚未注册为 Genesis Participant。需要先注册才能参与贡献网络。</p>
          <Link href="/genesis">
            <Button type="button" variant="primary">前往 Genesis 注册 →</Button>
          </Link>
        </div>
      )}

      {/* Main content — only when registered */}
      {phase === "ready" && participant && (
        <div style={{ display: "grid", gap: "var(--space-8)" }}>
          {/* Participant summary */}
          <div style={{ display: "grid", gap: "var(--space-3)", padding: "var(--space-4)", border: "1px solid var(--line)", borderRadius: "var(--radius-md)", background: "var(--surface-subtle)", maxWidth: 640 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "var(--space-3)" }}>
              <div>
                <p style={{ margin: 0, fontSize: "var(--text-xs)", color: "var(--text-faint)", textTransform: "uppercase", letterSpacing: "0.1em" }}>
                  Genesis Participant #{String(participant.participantNumber).padStart(4, "0")}
                </p>
                <p style={{ margin: "var(--space-1) 0 0", fontSize: "var(--text-sm)", color: "var(--text-muted)" }}>
                  {shortenAddress(participant.address)}
                </p>
              </div>
              <div style={{ display: "grid", gap: "var(--space-2)", textAlign: "right" }}>
                <div>
                  <p style={{ margin: 0, fontSize: "var(--text-2xl)", color: "var(--evidence)", fontWeight: 700 }}>{participant.reputationScore}</p>
                  <p style={{ margin: 0, fontSize: "var(--text-xs)", color: "var(--text-faint)" }}>Reputation</p>
                </div>
                {participant.pendingRewardMood && (
                  <div>
                    <p style={{ margin: 0, fontSize: "var(--text-md)", color: "var(--attention)" }}>{participant.pendingRewardMood} MOOD</p>
                    <p style={{ margin: 0, fontSize: "var(--text-xs)", color: "var(--text-faint)" }}>待发放</p>
                  </div>
                )}
              </div>
            </div>
            <div style={{ display: "flex", gap: "var(--space-4)", fontSize: "var(--text-sm)", color: "var(--text-muted)" }}>
              <span>提交 {participant.submissionCount}</span>
              <span>批准 {participant.approvedSubmissionCount}</span>
            </div>
          </div>

          {/* Tabs */}
          <div style={{ display: "flex", gap: "var(--space-1)", borderBottom: "1px solid var(--line)", maxWidth: 640 }}>
            {([["catalog", "任务目录"], ["mine", "我的贡献"]] as const).map(([key, label]) => (
              <button
                key={key}
                onClick={() => setTab(key)}
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
                  transition: "color var(--duration-fast)",
                }}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Task catalog */}
          {tab === "catalog" && !selectedTask && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "var(--space-3)", maxWidth: 960 }}>
              {tasks.length === 0 && (
                <p style={{ gridColumn: "1/-1", color: "var(--text-muted)", fontSize: "var(--text-md)" }}>暂无开放任务。</p>
              )}
              {tasks.map((task) => (
                <TaskCard key={task.id} task={task} onClick={() => void openTaskDetail(task)} />
              ))}
            </div>
          )}

          {/* Task detail + submit */}
          {tab === "catalog" && selectedTask && (
            <div>
              <button
                onClick={() => setSelectedTask(null)}
                style={{ background: "none", border: "none", color: "var(--text-muted)", cursor: "pointer", fontSize: "var(--text-sm)", marginBottom: "var(--space-4)", display: "flex", alignItems: "center", gap: "var(--space-1)" }}
              >
                ← 返回目录
              </button>
              <SubmitForm task={selectedTask} participant={participant} onSuccess={handleSubmitSuccess} onCancel={() => setSelectedTask(null)} />
            </div>
          )}

          {/* My contributions */}
          {tab === "mine" && (
            <div style={{ maxWidth: 720 }}>
              {submissions.length === 0 ? (
                <p style={{ color: "var(--text-muted)", fontSize: "var(--text-md)" }}>你还没有提交任何贡献。浏览任务目录开始吧。</p>
              ) : (
                <div style={{ border: "1px solid var(--line)", borderRadius: "var(--radius-md)", overflow: "hidden" }}>
                  <div style={{ padding: "var(--space-3) var(--space-4)", borderBottom: "1px solid var(--line)", background: "var(--surface-subtle)" }}>
                    <p style={{ margin: 0, fontSize: "var(--text-sm)", color: "var(--text-muted)" }}>
                      共 {submissions.length} 条提交记录
                    </p>
                  </div>
                  {submissions.map((sub) => <SubmissionRow key={sub.id} sub={sub} />)}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <footer style={{ marginTop: "var(--space-12)", paddingTop: "var(--space-8)", borderTop: "1px solid var(--line)", color: "var(--text-faint)", fontSize: "var(--text-sm)", maxWidth: 640 }}>
        <p style={{ margin: 0, lineHeight: "var(--leading-normal)" }}>
          协议文档见 <code style={{ fontFamily: "ui-monospace" }}>docs/protocol/CONTRIBUTION_NETWORK.md</code>。
          MOOD 贡献奖励为待发放状态,不构成任何收益保证。
        </p>
      </footer>
    </main>
  );
}
