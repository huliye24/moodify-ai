"use client";

import { FormEvent, useState } from "react";
import { api } from "../../lib/music-client";

export default function BetaLoginPage() {
  const [message, setMessage] = useState("受邀创作者可使用邀请码进入 Beta。邀请码不会保存在浏览器中。");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    const code = String(new FormData(event.currentTarget).get("inviteCode") ?? "").trim();
    try {
      await api.signInWithInvite(code);
      location.assign("/studio");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "登录失败");
      setBusy(false);
    }
  }

  return (
    <main className="studio-shell">
      <a href="/">← 返回聆听</a>
      <section className="studio-card beta-login-card">
        <span className="eyebrow">INVITE-ONLY BETA</span>
        <h1>创作者登录</h1>
        <p>当前仅向受邀创作者开放发布与 Inbox。听歌无需登录。</p>
        <form onSubmit={submit}>
          <input name="inviteCode" type="password" autoComplete="one-time-code" required placeholder="输入邀请码" />
          <button className="primary" disabled={busy}>{busy ? "验证中…" : "进入 Beta"}</button>
        </form>
        <output aria-live="polite">{message}</output>
      </section>
    </main>
  );
}
