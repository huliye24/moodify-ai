import Link from "next/link";

export const metadata = {
  title: "MOOD Library — Coming in Package 014",
  description: "Whitepaper, Constitution, Protocol, Governance and Research archive. Package 014 in progress.",
};

export default function LibraryLandingPage() {
  return (
    <main className="public-track">
      <Link href="/">← Moodify</Link>
      <article>
        <span className="eyebrow">MOOD LIBRARY</span>
        <h1>协议文档图书馆</h1>
        <p>
          MOOD Library 是 MOOD WORLD + PROTOCOL + PORTAL 的权威文档馆：
          Whitepaper / Constitution / Protocol / Governance / Economics / Security / Research。
        </p>
        <p>
          当前路由由 <code>codex/mood-portal-013</code> 建立为占位入口。
          <strong> 实际文档注册表、阅读器、版本、Hash 由 Package 014 落地。</strong>
        </p>
        <p>
          状态：<code>Coming in Package 014</code> · 详见{" "}
          <a href="https://github.com/huliye24/moodify-ai/blob/main/docs/mood/portal/013_FINAL_REPORT.md">
            docs/mood/portal/013_FINAL_REPORT.md
          </a>
          。
        </p>
        <h2>013 已建立的 IA 入口</h2>
        <ul>
          <li><Link href="/world">/world</Link> — MOOD 世界首页（PLANNED）</li>
          <li><Link href="/protocol">/protocol</Link> — Moodify Protocol 协议层</li>
          <li><Link href="/portal">/portal</Link> — MOOD Portal（连接后空间）</li>
          <li><Link href="/library">/library</Link> — 当前页（014 待填充）</li>
        </ul>
        <h2>013 不做的事</h2>
        <ul>
          <li>不写文档注册表（014）</li>
          <li>不写 metadata schema（014）</li>
          <li>不计算 SHA-256（014）</li>
          <li>不引入 IPFS CID（014）</li>
          <li>不渲染宪法 / Tokenomics 正文（014）</li>
        </ul>
      </article>
    </main>
  );
}