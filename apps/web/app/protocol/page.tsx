import Link from "next/link";

export const metadata = {
  title: "Moodify Protocol — Coming in Package 013",
  description: "Moodify Protocol shell. Package 013 placeholder.",
};

const modules = [
  "Architecture",
  "Identity",
  "Contribution",
  "Reputation",
  "Agents",
  "Nodes",
  "Governance",
  "Transparency",
  "Security",
  "Economics",
];

export default function ProtocolPage() {
  return (
    <main className="public-track">
      <Link href="/">← Moodify</Link>
      <article>
        <span className="eyebrow">MOOD PROTOCOL</span>
        <h1>Moodify Protocol</h1>
        <p>MPF-001 Mainnet Facts · MPF-002 Contribution Core · MPF-003 Reputation · MPF-004 Node Registry · MPF-005 Protocol API</p>
        <p>
          状态：<code>PROTOCOL modules implemented in repository; canonical archive coming via Package 014.</code>
        </p>
        <h2>模块</h2>
        <ul>
          {modules.map((m) => <li key={m}>{m}</li>)}
        </ul>
        <p>
          每个模块的 docs / source / version 由 Package 014 Library 统一登记。当前模块尚未对外提供
          <code>Mainnet Active</code> 描述；阅读入口见 <Link href="/library">/library</Link>。
        </p>
      </article>
    </main>
  );
}