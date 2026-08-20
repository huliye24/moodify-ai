"use client";

import { useEffect, useState } from "react";
import { api, BootstrapUser, LicenseIntentDto } from "../../lib/music-client";

export default function InboxPage() {
  const [me, setMe] = useState<BootstrapUser | null>(null);
  const [intents, setIntents] = useState<LicenseIntentDto[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    void api.bootstrap().then(async (user) => {
      setMe(user);
      if (!user.capabilities?.account_actions) {
        setError("只读模式：创作者 Inbox 仅向已登录的受邀创作者开放。");
        setIntents([]);
        return;
      }
      try {
        const creator = await api.creatorByHandle(user.demo_creator_handle ?? "");
        const inbox = await api.creatorInbox(creator.id);
        setIntents(inbox.intents);
      } catch (e) {
        setError(e instanceof Error ? e.message : "无法读取收件箱");
        setIntents([]);
      }
    }).catch(() => setError("无法确认当前用户"));
  }, []);

  return (
    <main className="public-track">
      <a href="/studio">← 返回创作者中心</a>
      <article>
        <span className="eyebrow">CREATOR INBOX</span>
        <h1>授权意向</h1>
        <p className="result-note">听众在你的作品页提交的授权需求。接受仅代表继续推进，不自动签署许可。</p>
        {error && <p>{error}</p>}
        {intents === null && !error && <p>加载中…</p>}
        {intents && (
          <div className="inbox-list">
            {intents.length === 0 && <p>暂无授权意向。</p>}
            {intents.map((intent) => (
              <div key={intent.id} className="inbox-item">
                <h3>{intent.license_type} · <a href={`/t/${intent.track_id}`}>作品 #{intent.track_id.slice(0, 8)}</a></h3>
                <p>{intent.usage_description}</p>
                <p className="result-note">
                  {intent.requester_name ?? "匿名"} · {intent.budget_amount_minor ? `¥${(intent.budget_amount_minor / 100).toFixed(0)} 起` : "未填预算"} · {intent.status}
                  {intent.created_at ? ` · ${new Date(intent.created_at).toLocaleString("zh-CN")}` : ""}
                </p>
              </div>
            ))}
          </div>
        )}
      </article>
    </main>
  );
}
