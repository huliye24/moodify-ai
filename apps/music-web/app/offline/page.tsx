"use client";

import Link from "next/link";

export default function OfflinePage() {
  return (
    <main className="public-track">
      <Link href="/">← Moodify</Link>
      <article>
        <div className="hero-vinyl"><div className="vinyl"><img src="/moodify-logo.png" alt="Moodify" /><i /></div></div>
        <span className="eyebrow">OFFLINE</span>
        <h1>当前没有网络连接</h1>
        <p className="result-note">应用外壳已离线可用，但曲库、登录与私人页面需要网络。
          恢复连接后请刷新页面，我们会从服务器重新读取状态。</p>
        <p className="result-note">此处不会展示缓存中的伪曲库数据。</p>
      </article>
    </main>
  );
}
