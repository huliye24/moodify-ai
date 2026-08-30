import Link from "next/link";

export const metadata = {
  title: "MOOD World — Coming in Package 013",
  description: "MOOD World Home (PLANNED). Package 013 placeholder.",
};

export default function WorldPage() {
  return (
    <main className="public-track">
      <Link href="/">← Moodify</Link>
      <article>
        <span className="eyebrow">MOOD WORLD</span>
        <h1>MOOD — A Digital Home for Free Spirits</h1>
        <p>在这里，成为你自己。</p>
        <p>
          状态：<code>PLANNED</code>。013 在此路由上仅提供占位入口；
          完整的 WORLD Home、Manifesto、World Map、Listening、Creation、Community、Moodify Gate 由后续 package 落地。
        </p>
        <p>入口域名：<code>crestwavecoin.com</code>（未上线 — G1 + G9 完成后由人类决定）</p>
        <ul>
          <li><Link href="/protocol">/protocol</Link></li>
          <li><Link href="/portal">/portal</Link></li>
          <li><Link href="/library">/library</Link></li>
        </ul>
      </article>
    </main>
  );
}