"use client";

import Link from "next/link";
import { EvidenceBadge, type ClaimMaturity } from "../../components/ui/status";
import { EmptyState } from "../../components/ui/states";

// Evidence — Public Form §9 Tier B:
//   "Evidence / Before / After / Original / Moodify"
// 只能在用户已经理解产品之后出现。
// §11 公共证明顺序: Belief -> Sound -> Play -> Proof -> Explanation -> Technology
// 本页是 Proof 这一段。

interface EvidenceEntry {
  id: string;
  title: string;
  summary: string;
  maturity: ClaimMaturity;
  scope: string;
  source: string;
}

// 全部条目摘录自仓库内已完成的证据包
// (artifacts/phase1_launch/EVIDENCE_INDEX.md)。
// Canon §6 / R6 / R10:不虚构未验证能力。
// Tier B 文案;不出现 LUFS / 频段等 Tier C 工程字段。
const ENTRIES: EvidenceEntry[] = [
  {
    id: "evidence-listening-first-web",
    title: "聆听优先 Web 收敛",
    summary: "apps/web 的公共主路径收敛到 Listening-first:Hero 由当前曲目承载,主 CTA 是 Play。creator 操作被移出公共首屏。",
    maturity: "verified",
    scope: "apps/web · public surface",
    source: "MFY_MUSIC_LISTENING_FIRST_WEB_001",
  },
  {
    id: "evidence-listening-product-v1",
    title: "聆听产品 v1 验收",
    summary: "Player 在媒体错误时给出诚实提示而非静默 spinner;自动播放不会冒充成功;Range 请求矩阵 5/5 通过。",
    maturity: "verified",
    scope: "apps/web · player",
    source: "MFY_MUSIC_LISTENING_PRODUCT_V1_001",
  },
  {
    id: "evidence-design-system",
    title: "设计系统 v1(深色石墨 + evidence 绿 + attention amber)",
    summary: "设计 token 单一来源;apps/web 与 ops/web_origin 共用同一套色板与字体;七项迁移测试全部通过。",
    maturity: "verified",
    scope: "design tokens v1",
    source: "phase1_launch/design_system_001",
  },
  {
    id: "evidence-official-site",
    title: "荣景文川官网七页面",
    summary: "rongjingmusic.com 的 Home / Ear / Music / Evidence / About / Contact / Privacy 已就位,六项自动检查通过。",
    maturity: "verified",
    scope: "ops/web_origin/site/rongjingmusic",
    source: "phase1_launch/official_site_001",
  },
  {
    id: "evidence-ear-workbench",
    title: "Ear 工作台(内部工具,非对外产品)",
    summary: "内部审查工具的真实全链路已跑通:job 入队 → case 完成 → evidence 落盘,manifest sha256 校验通过。Ear 是内部系统(Canon §1.2),不在公开面作为产品出现。",
    maturity: "verified",
    scope: "apps/ear-workbench(内部)",
    source: "phase1_launch/ear_workbench_001",
  },
  {
    id: "evidence-eve-pilot",
    title: "Ear 50 case 试点",
    summary: "Ear 在仓库侧完成 50/50 试点;试点结论是内部实验,不构成对外产品承诺。",
    maturity: "experimental",
    scope: "Ear pipeline · 内部",
    source: "artifacts/ear_pilot_001",
  },
];

function EntryCard({ entry }: { entry: EvidenceEntry }) {
  return (
    <article
      style={{
        border: "1px solid var(--line)",
        borderRadius: "var(--radius-lg)",
        background: "var(--surface-subtle)",
        padding: "var(--space-6)",
        display: "grid",
        gap: "var(--space-3)",
      }}
    >
      <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "var(--space-3)", flexWrap: "wrap" }}>
        <EvidenceBadge maturity={entry.maturity} scope={entry.scope} />
        <span style={{ fontSize: "var(--text-xs)", color: "var(--text-faint)", fontVariantNumeric: "tabular-nums" }}>{entry.source}</span>
      </header>
      <h2 style={{ margin: 0, fontSize: "var(--text-lg)", fontWeight: 600, color: "var(--text)" }}>{entry.title}</h2>
      <p style={{ margin: 0, fontSize: "var(--text-md)", color: "var(--text-muted)", lineHeight: "var(--leading-normal)" }}>{entry.summary}</p>
    </article>
  );
}

export default function EvidencePage() {
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

      <header style={{ display: "grid", gap: "var(--space-4)", paddingBlock: "var(--space-8) var(--space-8)", maxWidth: 720 }}>
        <span style={{ fontSize: "var(--text-xs)", letterSpacing: "0.18em", color: "var(--text-faint)", textTransform: "uppercase" }}>
          Public Form · §11 Proof
        </span>
        <h1 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "var(--text-4xl)", lineHeight: "var(--leading-tight)", letterSpacing: "-0.01em", color: "var(--text)" }}>
          Evidence.
        </h1>
        <p style={{ margin: 0, fontSize: "var(--text-lg)", color: "var(--text-muted)", maxWidth: "44ch", lineHeight: "var(--leading-normal)" }}>
          Moodify 已经做出来的、和还没做出来的,在这里都被标明。
        </p>
        <p style={{ margin: 0, fontSize: "var(--text-md)", color: "var(--text-faint)", maxWidth: "52ch", lineHeight: "var(--leading-normal)" }}>
          每一条都注明证据成熟度(maturity)与适用范围(scope)。Verified 表示已通过验证;
          Experimental 表示这是内部研究结论,不构成对外产品承诺。
        </p>
      </header>

      <section aria-label="证据列表" style={{ display: "grid", gap: "var(--space-6)", maxWidth: 720 }}>
        {ENTRIES.length > 0 ? (
          ENTRIES.map((entry) => <EntryCard key={entry.id} entry={entry} />)
        ) : (
          <EmptyState title="尚无证据" hint="Moodify 不在没有证据时假装有。" />
        )}
      </section>

      <footer style={{ marginTop: "var(--space-12)", paddingTop: "var(--space-8)", borderTop: "1px solid var(--line)", color: "var(--text-faint)", fontSize: "var(--text-sm)", maxWidth: 720 }}>
        <p style={{ margin: 0, lineHeight: "var(--leading-normal)" }}>
          想直接听 Moodify?回到 <Link href="/" style={{ color: "var(--text-muted)" }}>Listen. Then Play.</Link>
        </p>
      </footer>
    </main>
  );
}
