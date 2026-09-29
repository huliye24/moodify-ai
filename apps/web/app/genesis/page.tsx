"use client";

/* /genesis — MOOD-GENESIS-002: Wallet-signature Genesis Participant
   registration. No token transfer, no approval, no gas. The only wallet
   action is `personal_sign` on a human-readable message reconstructed by
   the server. The page reuses the existing Moodify visual system
   (hero + surface + risk notice) and the shared `components/ui/primitives`
   for accessible buttons and fields.

   All states are explicit: idle, wallet disconnected, connecting,
   wrong network, ready to sign, nonce loading, signature requested,
   verifying, already registered, registered successfully, rejected,
   expired nonce, server unavailable. No spinner-only dead states.

   The injected provider is used only for connect (eth_requestAccounts),
   network detection (eth_chainId / wallet_switchEthereumChain), and the
   personal_sign RPC. Wallet RPCs that could authorize transfers or
   transactions are never invoked. */

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { GENESIS_CONFIG } from "../../lib/genesis-config";
import { checksumAddress, shortenAddress } from "../../lib/evm-address";
import { Button } from "../../components/ui/primitives";

type Phase =
  | "idle"
  | "wallet-disconnected"
  | "connecting"
  | "wrong-network"
  | "ready-to-sign"
  | "nonce-loading"
  | "signature-requested"
  | "verifying"
  | "registered"
  | "already-registered"
  | "rejected"
  | "expired"
  | "server-error";

type Participant = {
  id: string;
  participantNumber: number;
  address: string;
  joinedAt: string;
  status: string;
  signatureVersion: string;
  termsVersion: string;
};

type NonceChallenge = {
  nonce: string;
  issuedAt: string;
  expiresAt: string;
  termsVersion: string;
  signatureVersion: string;
  chainId: number;
  domain: string;
  message: string;
};

/* EIP-1193 minimal type — we don't pull in ethers/viem just for a handful of
   calls. Any injected EVM wallet (MetaMask, Rabby, OKX, Coinbase, Trust)
   exposes this shape. */
type EthereumProvider = {
  request: (args: { method: string; params?: unknown[] }) => Promise<unknown>;
  on?: (event: string, handler: (...args: unknown[]) => void) => void;
  removeListener?: (event: string, handler: (...args: unknown[]) => void) => void;
};

declare global {
  interface Window {
    ethereum?: EthereumProvider;
  }
}

const BSC_HEX = "0x38"; // chainId 56
const BSC_PARAMS = { chainId: BSC_HEX, chainName: "BNB Smart Chain", nativeCurrency: { name: "BNB", symbol: "BNB", decimals: 18 }, rpcUrls: ["https://bsc-dataseed.binance.org/"], blockExplorerUrls: ["https://bscscan.com"] } as const;

function getProvider(): EthereumProvider | null {
  if (typeof window === "undefined") return null;
  return window.ethereum ?? null;
}

function explainError(error: unknown): string {
  if (error instanceof Error) {
    // EIP-1193 user rejection code
    if (/User rejected|user rejected|ACTION_REJECTED|4001/i.test(error.message)) return "用户已拒绝签名";
    return error.message;
  }
  return "未知错误";
}

function CopyableAddress({ address }: { address: string }) {
  const [state, setState] = useState<"idle" | "copied" | "failed">("idle");
  const copy = async () => {
    try { await navigator.clipboard.writeText(address); setState("copied"); }
    catch { setState("failed"); }
    window.setTimeout(() => setState("idle"), 2400);
  };
  return (
    <span style={{ display: "inline-flex", flexWrap: "wrap", alignItems: "center", gap: "var(--space-2)" }}>
      <code style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace", fontSize: "var(--text-sm)", color: "var(--text)", background: "var(--surface-subtle)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", padding: "var(--space-1) var(--space-3)", wordBreak: "break-all", overflowWrap: "anywhere" }}>{address}</code>
      <Button type="button" variant="ghost" size="sm" onClick={copy} aria-label={`复制钱包地址 ${address}`}>{state === "copied" ? "已复制 ✓" : state === "failed" ? "复制失败" : "复制地址"}</Button>
    </span>
  );
}

function PhaseBanner({ phase, errorMessage }: { phase: Phase; errorMessage: string | null }) {
  if (phase === "registered" || phase === "already-registered") return null;
  const map: Partial<Record<Phase, { tone: "info" | "attention" | "error"; text: string }>> = {
    "wallet-disconnected": { tone: "info", text: "请先连接钱包。" },
    "connecting": { tone: "info", text: "正在连接钱包……" },
    "wrong-network": { tone: "attention", text: `请切换到 ${GENESIS_CONFIG.network} (chainId ${GENESIS_CONFIG.chainId})。` },
    "ready-to-sign": { tone: "info", text: "已就绪。请仔细阅读下方签名内容,然后点击「签名并注册」。" },
    "nonce-loading": { tone: "info", text: "正在向 Moodify 后端申请一次性 nonce……" },
    "signature-requested": { tone: "info", text: "请在钱包中确认签名。签名不授权任何代币转账或链上交易。" },
    "verifying": { tone: "info", text: "正在验证签名并创建 Genesis Participant 记录……" },
    "rejected": { tone: "attention", text: errorMessage ?? "你已取消签名。可以随时重试。" },
    "expired": { tone: "attention", text: "Nonce 已过期。点击下方按钮重新申请。" },
    "server-error": { tone: "error", text: errorMessage ?? "后端暂时不可用,请稍后重试。" },
  };
  const item = map[phase];
  if (!item) return null;
  const color = item.tone === "error" ? "var(--blocking)" : item.tone === "attention" ? "var(--attention)" : "var(--text-muted)";
  const bg = item.tone === "error" ? "var(--blocking-soft)" : item.tone === "attention" ? "var(--attention-soft)" : "var(--surface-subtle)";
  return (
    <div role={item.tone === "error" ? "alert" : "status"} aria-live={item.tone === "error" ? "assertive" : "polite"} style={{ display: "flex", alignItems: "center", gap: "var(--space-3)", padding: "var(--space-3) var(--space-4)", border: `1px solid ${color}`, borderLeft: `3px solid ${color}`, borderRadius: "var(--radius-md)", background: bg, color: "var(--text)", fontSize: "var(--text-md)" }}>
      <span aria-hidden style={{ width: 8, height: 8, borderRadius: "50%", background: color, flex: "none" }} />
      <span>{item.text}</span>
    </div>
  );
}

function ParticipantCard({ participant, isNew }: { participant: Participant; isNew: boolean }) {
  const bscscan = `https://bscscan.com/address/${participant.address}`;
  const [copyId, setCopyId] = useState<"idle" | "copied" | "failed">("idle");
  const onCopyId = async () => {
    try { await navigator.clipboard.writeText(participant.id); setCopyId("copied"); }
    catch { setCopyId("failed"); }
    window.setTimeout(() => setCopyId("idle"), 2400);
  };
  const padded = String(participant.participantNumber).padStart(4, "0");
  return (
    <section aria-label="Genesis Participant" style={{ display: "grid", gap: "var(--space-3)", padding: "var(--space-6)", border: "1px solid var(--evidence)", borderLeft: "3px solid var(--evidence)", borderRadius: "var(--radius-md)", background: "var(--evidence-soft)" }}>
      <h2 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "var(--text-2xl)", color: "var(--text)" }}>
        Genesis Participant #{padded}
      </h2>
      <p style={{ margin: 0, fontSize: "var(--text-sm)", color: "var(--text-faint)", letterSpacing: "0.18em", textTransform: "uppercase" }}>
        {isNew ? "已注册" : "已存在(欢迎回来)"}
      </p>
      <dl style={{ margin: 0, display: "grid", gap: "var(--space-3)" }}>
        <div style={{ display: "grid", gap: "var(--space-1)" }}>
          <dt style={{ fontSize: "var(--text-xs)", color: "var(--text-faint)", letterSpacing: "0.18em", textTransform: "uppercase" }}>钱包地址</dt>
          <dd style={{ margin: 0 }}><CopyableAddress address={participant.address} /></dd>
        </div>
        <div style={{ display: "grid", gap: "var(--space-1)" }}>
          <dt style={{ fontSize: "var(--text-xs)", color: "var(--text-faint)", letterSpacing: "0.18em", textTransform: "uppercase" }}>注册时间</dt>
          <dd style={{ margin: 0, fontSize: "var(--text-md)", color: "var(--text)" }}>{new Date(participant.joinedAt).toLocaleString()}</dd>
        </div>
        <div style={{ display: "grid", gap: "var(--space-1)" }}>
          <dt style={{ fontSize: "var(--text-xs)", color: "var(--text-faint)", letterSpacing: "0.18em", textTransform: "uppercase" }}>状态</dt>
          <dd style={{ margin: 0, fontSize: "var(--text-md)", color: "var(--text)" }}>{participant.status}</dd>
        </div>
        <div style={{ display: "grid", gap: "var(--space-1)" }}>
          <dt style={{ fontSize: "var(--text-xs)", color: "var(--text-faint)", letterSpacing: "0.18em", textTransform: "uppercase" }}>Participant ID</dt>
          <dd style={{ margin: 0, display: "flex", flexWrap: "wrap", alignItems: "center", gap: "var(--space-2)" }}>
            <code style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace", fontSize: "var(--text-sm)", color: "var(--text)", background: "var(--surface-subtle)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", padding: "var(--space-1) var(--space-3)", wordBreak: "break-all", overflowWrap: "anywhere" }}>{participant.id}</code>
            <Button type="button" variant="ghost" size="sm" onClick={onCopyId} aria-label="复制 Participant ID">{copyId === "copied" ? "已复制 ✓" : copyId === "failed" ? "复制失败" : "复制 ID"}</Button>
          </dd>
        </div>
      </dl>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--space-3)" }}>
        <a href={bscscan} target="_blank" rel="noopener noreferrer" style={{ display: "inline-flex", alignItems: "center", height: 36, padding: "0 var(--space-4)", borderRadius: "var(--radius-pill)", border: "1px solid var(--line)", background: "var(--surface-subtle)", color: "var(--text)", textDecoration: "none", fontSize: "var(--text-sm)" }}>在 BscScan 查看 ↗</a>
        <Link href="/token" style={{ display: "inline-flex", alignItems: "center", height: 36, padding: "0 var(--space-4)", borderRadius: "var(--radius-pill)", border: "1px solid var(--line)", background: "var(--surface-subtle)", color: "var(--text)", textDecoration: "none", fontSize: "var(--text-sm)" }}>查看 MOOD · 协议资产</Link>
      </div>
    </section>
  );
}

export default function GenesisPage() {
  // First render must match between server and client — `window` is undefined
  // during SSR, so we always start with the "idle / no wallet" defaults and
  // detect the injected provider inside a post-hydration effect. State
  // updates after hydration are not subject to the hydration check.
  const [phase, setPhase] = useState<Phase>("idle");
  const [hasWallet, setHasWallet] = useState(false);
  const [address, setAddress] = useState<string | null>(null);
  const [chainId, setChainId] = useState<number | null>(null);
  const [challenge, setChallenge] = useState<NonceChallenge | null>(null);
  const [participant, setParticipant] = useState<Participant | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const providerRef = useRef<EthereumProvider | null>(null);
  const accountsHandlerRef = useRef<((...args: unknown[]) => void) | null>(null);
  const chainHandlerRef = useRef<((...args: unknown[]) => void) | null>(null);

  // Post-hydration detection: decide whether an injected wallet exists and
  // update `hasWallet` / `phase` to match. This effect also attaches and
  // detaches provider event listeners. We never auto-connect (per spec:
  // explicit user action).
  useEffect(() => {
    const provider = getProvider();
    providerRef.current = provider;
    if (!provider) {
      setHasWallet(false);
      return;
    }
    setHasWallet(true);
    setPhase((p) => (p === "registered" || p === "already-registered") ? p : "wallet-disconnected");
    const onAccountsChanged = (accounts: unknown) => {
      const list = accounts as string[];
      if (!list || list.length === 0) {
        setAddress(null);
        setChainId(null);
        setChallenge(null);
        setPhase((p) => (p === "registered" || p === "already-registered") ? p : "wallet-disconnected");
      } else {
        setAddress(checksumAddress(list[0]));
        setPhase((p) => (p === "registered" || p === "already-registered") ? p : "ready-to-sign");
      }
    };
    const onChainChanged = (raw: unknown) => {
      const hex = typeof raw === "string" ? raw : "";
      const parsed = parseInt(hex, 16);
      if (Number.isFinite(parsed)) {
        setChainId(parsed);
        setPhase((p) => {
          if (p === "registered" || p === "already-registered") return p;
          return parsed === GENESIS_CONFIG.chainId ? "ready-to-sign" : "wrong-network";
        });
      }
    };
    accountsHandlerRef.current = onAccountsChanged as (...args: unknown[]) => void;
    chainHandlerRef.current = onChainChanged as (...args: unknown[]) => void;
    provider.on?.("accountsChanged", onAccountsChanged);
    provider.on?.("chainChanged", onChainChanged);
    return () => {
      provider.removeListener?.("accountsChanged", onAccountsChanged);
      provider.removeListener?.("chainChanged", onChainChanged);
    };
  }, []);

  // If the user is already connected and has a registered participant, show it.
  useEffect(() => {
    if (!address) return;
    let cancelled = false;
    void fetch(`/api/genesis/me?address=${encodeURIComponent(address)}`)
      .then((res) => res.ok ? res.json() as Promise<{ participant: Participant | null }> : Promise.resolve({ participant: null }))
      .then((data) => {
        if (cancelled) return;
        if (data.participant) {
          setParticipant(data.participant);
          setPhase("already-registered");
        }
      })
      .catch(() => undefined);
    return () => { cancelled = true; };
  }, [address]);

  const connect = useCallback(async () => {
    const provider = providerRef.current ?? getProvider();
    if (!provider) {
      setErrorMessage("未检测到 EVM 钱包。请安装 MetaMask、Rabby 或其他 EIP-1193 钱包扩展。");
      setPhase("server-error");
      return;
    }
    setPhase("connecting");
    setErrorMessage(null);
    try {
      const accounts = (await provider.request({ method: "eth_requestAccounts" })) as string[];
      const hexChain = (await provider.request({ method: "eth_chainId" })) as string;
      const parsedChain = parseInt(hexChain, 16);
      if (!Array.isArray(accounts) || accounts.length === 0) throw new Error("钱包未返回任何账户");
      const addr = checksumAddress(accounts[0]);
      setAddress(addr);
      setChainId(parsedChain);
      if (parsedChain !== GENESIS_CONFIG.chainId) {
        setPhase("wrong-network");
        return;
      }
      setPhase("ready-to-sign");
    } catch (error) {
      setErrorMessage(explainError(error));
      setPhase("wallet-disconnected");
    }
  }, []);

  const switchNetwork = useCallback(async () => {
    const provider = providerRef.current ?? getProvider();
    if (!provider) return;
    try {
      await provider.request({ method: "wallet_switchEthereumChain", params: [{ chainId: BSC_HEX }] });
    } catch (switchError) {
      // 4902 = chain not added to wallet; ask the wallet to add it.
      if (switchError instanceof Error && /4902|Unrecognized chain/i.test(switchError.message)) {
        try {
          await provider.request({ method: "wallet_addEthereumChain", params: [BSC_PARAMS] });
          return;
        } catch (addError) {
          setErrorMessage(explainError(addError));
          return;
        }
      }
      setErrorMessage(explainError(switchError));
    }
  }, []);

  const requestChallenge = useCallback(async () => {
    if (!address) return;
    setPhase("nonce-loading");
    setErrorMessage(null);
    try {
      const res = await fetch("/api/genesis/nonce", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ address, chainId: GENESIS_CONFIG.chainId }) });
      const data = await res.json() as NonceChallenge | { error?: { message?: string } };
      if (!res.ok) {
        const message = (data as { error?: { message?: string } }).error?.message ?? "无法获取 nonce";
        setErrorMessage(message);
        setPhase("server-error");
        return;
      }
      setChallenge(data as NonceChallenge);
      setPhase("ready-to-sign");
    } catch (error) {
      setErrorMessage(explainError(error));
      setPhase("server-error");
    }
  }, [address]);

  const signAndRegister = useCallback(async () => {
    if (!address || !challenge) return;
    const provider = providerRef.current ?? getProvider();
    if (!provider) {
      setErrorMessage("钱包不可用");
      setPhase("server-error");
      return;
    }
    setPhase("signature-requested");
    setErrorMessage(null);
    let signature: string;
    try {
      signature = (await provider.request({ method: "personal_sign", params: [challenge.message, address] })) as string;
    } catch (error) {
      const message = explainError(error);
      setErrorMessage(message);
      setPhase("rejected");
      return;
    }
    if (typeof signature !== "string" || !/^0x[0-9a-fA-F]+$/.test(signature)) {
      setErrorMessage("钱包返回的签名格式不正确");
      setPhase("rejected");
      return;
    }
    setPhase("verifying");
    try {
      const res = await fetch("/api/genesis/register", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ address, chainId: GENESIS_CONFIG.chainId, nonce: challenge.nonce, signature }) });
      const data = await res.json() as { participant?: Participant; error?: { code?: string; message?: string } };
      if (!res.ok || !data.participant) {
        const code = data.error?.code ?? "";
        const message = data.error?.message ?? "注册失败";
        if (code === "NONCE_EXPIRED") { setErrorMessage(message); setPhase("expired"); return; }
        if (code === "NONCE_USED") { setErrorMessage(message); setPhase("expired"); return; }
        setErrorMessage(message);
        setPhase("server-error");
        return;
      }
      setParticipant(data.participant);
      setPhase("registered");
    } catch (error) {
      setErrorMessage(explainError(error));
      setPhase("server-error");
    }
  }, [address, challenge]);

  // Render helpers
  const connectControl = !hasWallet
    ? <Button type="button" disabled aria-label="未检测到钱包">未检测到 EVM 钱包</Button>
    : phase === "connecting"
      ? <Button type="button" loading aria-busy="true" disabled>连接中……</Button>
      : <Button type="button" variant="primary" onClick={connect}>连接钱包</Button>;

  const networkControl = phase === "wrong-network"
    ? <Button type="button" variant="ghost" onClick={switchNetwork}>切换到 BNB Smart Chain</Button>
    : null;

  const actionControl = (() => {
    if (!address) return null;
    if (chainId !== null && chainId !== GENESIS_CONFIG.chainId) return null;
    if (phase === "nonce-loading" || phase === "signature-requested" || phase === "verifying") {
      return <Button type="button" loading aria-busy="true" disabled>处理中……</Button>;
    }
    if (phase === "registered" || phase === "already-registered") return null;
    if (!challenge || phase === "expired" || phase === "rejected") {
      return <Button type="button" variant="primary" onClick={requestChallenge}>{(phase === "expired" || phase === "rejected") ? "重新申请 nonce" : "申请签名并注册"}</Button>;
    }
    return <Button type="button" variant="primary" onClick={signAndRegister}>签名并注册</Button>;
  })();

  return (
    <main style={{ minHeight: "100vh", background: "radial-gradient(circle at 70% 12%, rgba(36,66,154,.17), transparent 27%), linear-gradient(135deg, #070a22, #040719 70%)", padding: "0 clamp(20px, 4vw, 64px) var(--space-12)" }}>
      <nav aria-label="位置" style={{ paddingBlock: "var(--space-6)", color: "var(--text-faint)", fontSize: "var(--text-sm)" }}>
        <Link href="/" style={{ color: "inherit", textDecoration: "none" }}>← 返回 Moodify</Link>
      </nav>

      <header style={{ display: "grid", gap: "var(--space-4)", paddingBlock: "var(--space-12) var(--space-8)", maxWidth: 760 }}>
        <span style={{ fontSize: "var(--text-xs)", letterSpacing: "0.18em", color: "var(--text-faint)", textTransform: "uppercase" }}>
          Protocol · Genesis
        </span>
        <h1 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "var(--text-4xl)", lineHeight: "var(--leading-tight)", letterSpacing: "-0.01em", color: "var(--text)" }}>
          Moodify Genesis
        </h1>
        <p style={{ margin: 0, fontSize: "var(--text-lg)", color: "var(--text-muted)", maxWidth: "44ch", lineHeight: "var(--leading-normal)" }}>
          注册为 Moodify Genesis Participant。整个过程只需要一次钱包签名:无需购买代币、无需授权转账、无需支付 Gas。
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "var(--space-3)" }}>
          <span style={{ display: "inline-flex", alignItems: "center", gap: "var(--space-2)", padding: "var(--space-1) var(--space-4)", borderRadius: "var(--radius-pill)", border: "1px solid var(--line)", background: "var(--surface-subtle)", fontSize: "var(--text-sm)", color: "var(--text)" }}>
            <span aria-hidden style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--brand-violet)", flex: "none" }} />
            {GENESIS_CONFIG.network} · Chain {GENESIS_CONFIG.chainId}
          </span>
          <span style={{ fontSize: "var(--text-sm)", color: "var(--text-faint)" }}>签名版本:{GENESIS_CONFIG.signatureVersion} · 条款版本:{GENESIS_CONFIG.termsVersion}</span>
        </div>
      </header>

      <section aria-label="Genesis 说明" style={{ display: "grid", gap: "var(--space-8)", maxWidth: 760 }}>
        <div style={{ display: "grid", gap: "var(--space-3)" }}>
          <h2 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "var(--text-2xl)", color: "var(--text)" }}>什么是 Genesis Participant</h2>
          <ul style={{ margin: 0, paddingInlineStart: "var(--space-6)", display: "grid", gap: "var(--space-2)", color: "var(--text-muted)", fontSize: "var(--text-md)", lineHeight: "var(--leading-normal)" }}>
            <li>Moodify Protocol Genesis 是早期参与者登记簿,记录在 BNB Smart Chain 上某个 EVM 钱包地址的参与意愿。</li>
            <li>注册不代表任何形式的金融价值承诺,也不构成投资、证券或回报保证。</li>
            <li>注册不需要购买、转移或授权 MOOD 代币,也不需要支付任何链上费用。</li>
            <li>钱包签名仅证明钱包所有权;签名内容明确写明不授权任何代币转账或交易。</li>
            <li>未来 Moodify 协议可能基于此登记册进行分配/空投等机制,但本流程不执行这些动作。</li>
          </ul>
        </div>

        <PhaseBanner phase={phase} errorMessage={errorMessage} />

        <div style={{ display: "grid", gap: "var(--space-4)", padding: "var(--space-6)", border: "1px solid var(--line)", borderRadius: "var(--radius-lg)", background: "var(--surface-subtle)" }}>
          <h2 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "var(--text-2xl)", color: "var(--text)" }}>注册流程</h2>
          <ol style={{ margin: 0, paddingInlineStart: "var(--space-6)", display: "grid", gap: "var(--space-2)", color: "var(--text-muted)", fontSize: "var(--text-md)", lineHeight: "var(--leading-normal)" }}>
            <li>连接你的 EVM 钱包(MetaMask、Rabby、OKX、Trust 等)。</li>
            <li>确认钱包当前网络为 BNB Smart Chain (chainId {GENESIS_CONFIG.chainId});若不是,使用钱包提供的切换按钮。</li>
            <li>点击「申请签名并注册」,Moodify 后端会生成一次性 nonce 并向你展示完整签名内容。</li>
            <li>在钱包中确认 `personal_sign`;签名内容明确写明不授权任何代币转账或交易。</li>
            <li>后端验证签名成功后,返回你的 Genesis Participant 编号与记录。</li>
          </ol>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--space-3)", alignItems: "center" }}>
            {!address ? connectControl : <span style={{ fontSize: "var(--text-sm)", color: "var(--text-muted)" }}>已连接:{address ? shortenAddress(address) : ""}</span>}
            {networkControl}
            {actionControl}
          </div>
          {address && (
            <div style={{ display: "grid", gap: "var(--space-2)", fontSize: "var(--text-sm)", color: "var(--text-faint)" }}>
              <span>当前 Chain ID:{chainId ?? "—"} · 期望:{GENESIS_CONFIG.chainId}</span>
              {address && <CopyableAddress address={address} />}
            </div>
          )}
        </div>

        {challenge && (phase === "ready-to-sign" || phase === "signature-requested" || phase === "verifying") && (
          <section aria-label="待签名内容" style={{ display: "grid", gap: "var(--space-3)", padding: "var(--space-6)", border: "1px solid var(--line)", borderLeft: "3px solid var(--focus)", borderRadius: "var(--radius-md)", background: "var(--surface-subtle)" }}>
            <h3 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "var(--text-xl)", color: "var(--text)" }}>请仔细阅读下方签名内容</h3>
            <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "var(--text-md)", lineHeight: "var(--leading-normal)" }}>
              这是一次标准的 EIP-191 <code style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" }}>personal_sign</code>。钱包会原样展示以下文字,不会要求任何链上交易或代币授权。
            </p>
            <pre style={{ margin: 0, whiteSpace: "pre-wrap", wordBreak: "break-word", overflowWrap: "anywhere", fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace", fontSize: "var(--text-sm)", color: "var(--text)", background: "var(--bg)", border: "1px solid var(--line)", borderRadius: "var(--radius-sm)", padding: "var(--space-4)" }}>{challenge.message}</pre>
            <div style={{ display: "grid", gap: "var(--space-1)", fontSize: "var(--text-sm)", color: "var(--text-faint)" }}>
              <span>Nonce 有效期至:{new Date(challenge.expiresAt).toLocaleString()}</span>
              <span>签名版本:{challenge.signatureVersion} · 条款版本:{challenge.termsVersion}</span>
            </div>
          </section>
        )}

        {participant && (phase === "registered" || phase === "already-registered") && (
          <ParticipantCard participant={participant} isNew={phase === "registered"} />
        )}

        <section aria-label="风险提示" style={{ display: "grid", gap: "var(--space-3)", padding: "var(--space-6)", border: "1px solid var(--attention)", borderLeft: "3px solid var(--attention)", borderRadius: "var(--radius-md)", background: "var(--attention-soft)" }}>
          <h2 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "var(--text-2xl)", color: "var(--text)" }}>重要说明</h2>
          <ul style={{ margin: 0, paddingInlineStart: "var(--space-6)", display: "grid", gap: "var(--space-2)", color: "var(--text-muted)", fontSize: "var(--text-md)", lineHeight: "var(--leading-normal)" }}>
            <li>本注册不收取任何费用,不要求转移代币,不要求授权代币,不要求支付 Gas。</li>
            <li>注册即表示你确认自己所在司法辖区允许此类参与,并接受当前的签名版本与条款版本。</li>
            <li>Moodify 不会询问你的助记词、私钥或任何敏感信息;请只在官方页面进行签名。</li>
            <li>注册编号不可转让;每个钱包地址只能登记一次。</li>
            <li>未来是否基于此登记册进行分配、空投或激励,属于 Moodify 协议后续决定,本流程不构成任何承诺。</li>
          </ul>
        </section>
      </section>

      <footer style={{ marginTop: "var(--space-12)", paddingTop: "var(--space-8)", borderTop: "1px solid var(--line)", color: "var(--text-faint)", fontSize: "var(--text-sm)", maxWidth: 760 }}>
        <p style={{ margin: 0, lineHeight: "var(--leading-normal)" }}>
          协议文档与签名格式见 <code style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" }}>docs/protocol/GENESIS_REGISTRATION.md</code>。
          单一权威来源:<code style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" }}>apps/web/lib/genesis-config.ts</code>。
        </p>
      </footer>
    </main>
  );
}
