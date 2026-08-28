"use client";

import { useState } from "react";
import Link from "next/link";
import { MOOD_TOKEN } from "../../lib/mood-token";
import { Button } from "../../components/ui/primitives";

// Token — MOOD-GENESIS-001: MOOD 协议资产信息页。
//   本页回答:MOOD 是什么、在哪条链、官方合约是什么、总量多少、
//   去哪里验证、去哪里交易、与 Moodify 是什么关系、有什么风险。
//   页面事实全部来自 lib/mood-token.ts(单一应用级权威,MOOD-GENESIS-001),
//   本文件不硬编码第二份合约地址。
//   Public Form 语言原则:诚实、克制、不承诺收益(Canon §6 / R6 / R10)。

/* 复制合约地址:成功给可见反馈,失败诚实回退(不假装复制成功)。 */
function CopyContract({ address }: { address: string }) {
  const [state, setState] = useState<"idle" | "copied" | "failed">("idle");

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(address);
      setState("copied");
    } catch {
      setState("failed");
    }
    window.setTimeout(() => setState("idle"), 2400);
  };

  return (
    <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "var(--space-3)" }}>
      <code
        style={{
          margin: 0,
          fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
          fontSize: "var(--text-sm)",
          color: "var(--text)",
          background: "var(--surface-subtle)",
          border: "1px solid var(--line)",
          borderRadius: "var(--radius-sm)",
          padding: "var(--space-2) var(--space-3)",
          wordBreak: "break-all",
          overflowWrap: "anywhere",
          lineHeight: "var(--leading-normal)",
        }}
      >
        {address}
      </code>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={copy}
        aria-label={`复制 MOOD 官方合约地址 ${address}`}
      >
        {state === "copied" ? "已复制 ✓" : state === "failed" ? "复制失败" : "复制地址"}
      </Button>
      <span aria-live="polite" style={{ fontSize: "var(--text-sm)", color: state === "failed" ? "var(--blocking)" : "var(--text-faint)" }}>
        {state === "copied"
          ? "合约地址已复制到剪贴板。"
          : state === "failed"
            ? "复制失败,请手动选中上方地址复制。"
            : ""}
      </span>
    </div>
  );
}

function FactRow({ term, children }: { term: string; children: React.ReactNode }) {
  return (
    <div style={{ display: "grid", gap: "var(--space-1)", paddingTop: "var(--space-3)", borderTop: "1px solid var(--line)" }}>
      <dt style={{ margin: 0, fontSize: "var(--text-xs)", letterSpacing: "0.18em", color: "var(--text-faint)", textTransform: "uppercase" }}>
        {term}
      </dt>
      <dd style={{ margin: 0, fontSize: "var(--text-md)", color: "var(--text)", lineHeight: "var(--leading-normal)" }}>
        {children}
      </dd>
    </div>
  );
}

const OFFICIAL_LINKS: { label: string; hint: string; href: string }[] = [
  { label: "BscScan · 验证合约", hint: "查看合约源码、持有与转账记录", href: MOOD_TOKEN.explorerUrl },
  { label: "PancakeSwap · 交易 MOOD", hint: `主要 DEX:${MOOD_TOKEN.dex.name} · ${MOOD_TOKEN.dex.pair}`, href: MOOD_TOKEN.tradeUrl },
  { label: "Moodify 官网", hint: "rongjingmusic.com · Product Home", href: MOOD_TOKEN.officialSite },
  { label: "GitHub · moodify-ai", hint: "Moodify 开源仓库", href: MOOD_TOKEN.githubUrl },
];

export default function TokenPage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        background: "radial-gradient(circle at 70% 12%, rgba(36,66,154,.17), transparent 27%), linear-gradient(135deg, #070a22, #040719 70%)",
        padding: "0 clamp(20px, 4vw, 64px) var(--space-12)",
      }}
    >
      <nav aria-label="位置" style={{ paddingBlock: "var(--space-6)", color: "var(--text-faint)", fontSize: "var(--text-sm)" }}>
        <Link href="/" style={{ color: "inherit", textDecoration: "none" }}>← 返回 Moodify</Link>
      </nav>

      {/* Hero */}
      <header style={{ display: "grid", gap: "var(--space-4)", paddingBlock: "var(--space-12) var(--space-8)", maxWidth: 720 }}>
        <span style={{ fontSize: "var(--text-xs)", letterSpacing: "0.18em", color: "var(--text-faint)", textTransform: "uppercase" }}>
          Protocol Asset · BEP-20
        </span>
        <h1 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "var(--text-4xl)", lineHeight: "var(--leading-tight)", letterSpacing: "-0.01em", color: "var(--text)" }}>
          MOOD.
        </h1>
        <p style={{ margin: 0, fontSize: "var(--text-lg)", color: "var(--text-muted)", maxWidth: "44ch", lineHeight: "var(--leading-normal)" }}>
          MOOD 是 Moodify 生态的协议资产,部署在 BNB Smart Chain 上的 BEP-20 标准代币。
          合约公开、可在区块浏览器验证,总量固定。
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "var(--space-3)" }}>
          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "var(--space-2)",
              padding: "var(--space-1) var(--space-4)",
              borderRadius: "var(--radius-pill)",
              border: "1px solid var(--line)",
              background: "var(--surface-subtle)",
              fontSize: "var(--text-sm)",
              color: "var(--text)",
            }}
          >
            <span aria-hidden style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--brand-violet)", flex: "none" }} />
            {MOOD_TOKEN.network} · Chain {MOOD_TOKEN.chainId}
          </span>
          <span style={{ fontSize: "var(--text-sm)", color: "var(--text-faint)" }}>官方合约地址:</span>
        </div>
        <CopyContract address={MOOD_TOKEN.address} />
      </header>

      {/* Token facts */}
      <section aria-label="MOOD 代币事实" style={{ display: "grid", gap: "var(--space-8)", maxWidth: 720 }}>
        <dl style={{ margin: 0, display: "grid", gap: "var(--space-3)", border: "1px solid var(--line)", borderRadius: "var(--radius-lg)", background: "var(--surface-subtle)", padding: "var(--space-6)" }}>
          <FactRow term="网络 / Network">BNB Smart Chain</FactRow>
          <FactRow term="Chain ID">{MOOD_TOKEN.chainId}</FactRow>
          <FactRow term="合约地址 / Contract">
            <CopyContract address={MOOD_TOKEN.address} />
          </FactRow>
          <FactRow term="小数位 / Decimals">{MOOD_TOKEN.decimals}</FactRow>
          <FactRow term="总量 / Total supply">{MOOD_TOKEN.totalSupplyDisplay}</FactRow>
          <FactRow term="主要 DEX">{MOOD_TOKEN.dex.name}</FactRow>
          <FactRow term="交易对 / Pair">{MOOD_TOKEN.dex.pair}</FactRow>
          <FactRow term="费率档 / Fee tier">{MOOD_TOKEN.dex.feeTier}</FactRow>
        </dl>

        {/* Official links */}
        <div style={{ display: "grid", gap: "var(--space-3)" }}>
          <h2 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "var(--text-2xl)", color: "var(--text)" }}>官方链接</h2>
          <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "var(--text-md)", lineHeight: "var(--leading-normal)" }}>
            与 MOOD 相关的一切操作,请只通过以下官方入口进行。
          </p>
          <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: "var(--space-2)" }}>
            {OFFICIAL_LINKS.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    alignItems: "baseline",
                    gap: "var(--space-2)",
                    padding: "var(--space-3) var(--space-4)",
                    border: "1px solid var(--line)",
                    borderRadius: "var(--radius-md)",
                    background: "var(--surface-subtle)",
                    textDecoration: "none",
                  }}
                >
                  <span style={{ fontSize: "var(--text-md)", color: "var(--text)", fontWeight: 600 }}>{link.label} ↗</span>
                  <span style={{ fontSize: "var(--text-sm)", color: "var(--text-faint)" }}>{link.hint}</span>
                </a>
              </li>
            ))}
          </ul>
        </div>

        {/* Protocol purpose */}
        <div style={{ display: "grid", gap: "var(--space-3)" }}>
          <h2 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "var(--text-2xl)", color: "var(--text)" }}>MOOD 与 Moodify</h2>
          <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "var(--text-md)", lineHeight: "var(--leading-normal)" }}>
            Moodify 的对外产品是音乐聆听体验——Listen. Then Play.。MOOD 属于 Moodify 生态的协议层资产,
            与产品内的聆听功能相互独立:持有 MOOD 不是使用 Moodify 的前提,使用 Moodify 也不需要持有 MOOD。
          </p>
          <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "var(--text-md)", lineHeight: "var(--leading-normal)" }}>
            本页面信息仅供参考,不构成投资建议、证券要约或任何形式的收益承诺。
          </p>
        </div>

        {/* Token allocation */}
        <div style={{ display: "grid", gap: "var(--space-3)" }}>
          <h2 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "var(--text-2xl)", color: "var(--text)" }}>代币分配</h2>
          <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "var(--text-md)", lineHeight: "var(--leading-normal)" }}>
            代币分配政策正在规范化过程中,并将在任何大规模分配之前通过 Moodify 协议文档公布。
          </p>
          <p style={{ margin: 0, color: "var(--text-faint)", fontSize: "var(--text-sm)", lineHeight: "var(--leading-normal)" }}>
            Token allocation policy is being formalized and will be published through Moodify protocol
            documentation before any large-scale distribution.
          </p>
        </div>

        {/* Risk notice */}
        <section
          aria-label="风险提示"
          style={{
            display: "grid",
            gap: "var(--space-3)",
            padding: "var(--space-6)",
            border: "1px solid var(--attention)",
            borderLeft: "3px solid var(--attention)",
            borderRadius: "var(--radius-md)",
            background: "var(--attention-soft)",
          }}
        >
          <h2 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "var(--text-2xl)", color: "var(--text)" }}>风险提示</h2>
          <ul style={{ margin: 0, paddingInlineStart: "var(--space-6)", display: "grid", gap: "var(--space-2)", color: "var(--text-muted)", fontSize: "var(--text-md)", lineHeight: "var(--leading-normal)" }}>
            <li>MOOD 为新上线代币,流动性可能较浅,大额交易可能造成明显滑点。</li>
            <li>加密资产价格可能剧烈波动,历史表现不代表未来。</li>
            <li>智能合约风险与市场风险客观存在,请在充分理解后自行决策。</li>
            <li>请务必通过本页官方地址与 BscScan 核实合约,警惕仿冒合约与钓鱼站点。</li>
            <li>MOOD 不提供任何形式的回报保证;任何声称保证收益的行为均与 Moodify 无关。</li>
          </ul>
        </section>
      </section>

      <footer style={{ marginTop: "var(--space-12)", paddingTop: "var(--space-8)", borderTop: "1px solid var(--line)", color: "var(--text-faint)", fontSize: "var(--text-sm)", maxWidth: 720 }}>
        <p style={{ margin: 0, lineHeight: "var(--leading-normal)" }}>
          协议文档与更新程序见 <code style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" }}>docs/protocol/MOOD_TOKEN.md</code>。
          合约事实的单一权威来源:<code style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" }}>apps/web/lib/mood-token.ts</code>。
        </p>
      </footer>
    </main>
  );
}
