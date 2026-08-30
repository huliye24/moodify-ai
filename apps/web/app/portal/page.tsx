"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type BootstrapUser = {
  id: string | null;
  capabilities?: { account_actions?: boolean };
};

export default function PortalPage() {
  const [me, setMe] = useState<BootstrapUser | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    void import("../lib/music-client").then(({ api }) => {
      void api.bootstrap().then((u) => {
        setMe(u);
        setConnected(Boolean(u.id));
      }).catch(() => null);
    });
  }, []);

  return (
    <main className="public-track">
      <Link href="/">← Moodify</Link>
      <article>
        <span className="eyebrow">MOOD PORTAL</span>
        <h1>{connected ? "Welcome Home" : "Welcome to MOOD"}</h1>
        <p>
          {connected
            ? <>Status: <code>connected</code> · {me?.id ? <code>{`${me.id.slice(0, 6)}…${me.id.slice(-4)}`}</code> : null}</>
            : <>Status: <code>Visitor</code></>}
        </p>
        <h2>{connected ? "Available" : "Explore"}</h2>
        <ul>
          <li><Link href="/world">/world</Link></li>
          <li><Link href="/protocol">/protocol</Link></li>
          <li><Link href="/library">/library</Link> — Protocol documents (014)</li>
          <li><Link href="/portal/passport">/portal/passport</Link> — Resident identity (015)</li>
        </ul>
        <h2>Passport</h2>
        <ul>
          <li><Link href="/portal/passport">Passport</Link></li>
          <li>Contributions <span style={{ opacity: 0.55 }}>(016)</span></li>
          <li>Reputation <span style={{ opacity: 0.55 }}>(016 / 020)</span></li>
          <li><Link href="/portal/passport/settings">Settings</Link></li>
        </ul>
        <h2>Coming Next</h2>
        <ul>
          <li>Contributions (016)</li>
          <li>Agents (018)</li>
          <li>Nodes (019)</li>
          <li>Governance (020)</li>
        </ul>
        <p>
          Portal 当前 <strong>不依赖</strong> MOOD Token CA / Buy / Trade。foundation state 安全。
        </p>
      </article>
    </main>
  );
}