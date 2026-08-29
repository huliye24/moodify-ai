"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, lifecycle, DraftStage } from "../../lib/music-client";

export default function DraftsPage() {
  const [drafts, setDrafts] = useState<DraftStage[] | null>(null);
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState("");

  useEffect(() => {
    void api.bootstrap().then(async (user) => {
      if (!user.capabilities?.creator_writes) {
        setError("只读模式：草稿管理仅对受邀创作者开放。");
        setDrafts([]);
        return;
      }
      try {
        const creator = await api.creatorByHandle(user.demo_creator_handle ?? "");
        const list = await lifecycle.myDrafts(creator.id);
        setDrafts(list.drafts);
      } catch (e) {
        setError(e instanceof Error ? e.message : "无法读取草稿");
        setDrafts([]);
      }
    }).catch(() => setError("无法确认当前用户"));
  }, []);

  async function abandon(trackId: string) {
    setBusyId(trackId);
    try {
      await lifecycle.abandon(trackId);
      setDrafts((items) => (items ?? []).map((d) => d.track_id === trackId ? { ...d, stage: "archived", status: "archived" } : d));
    } catch (e) {
      setError(e instanceof Error ? e.message : "放弃失败");
    } finally {
      setBusyId("");
    }
  }

  const stageLabel: Record<string, string> = {
    draft: "待上传版本", version_ready: "待填来源声明", passport_ready: "待确认发布",
    published: "已发布", archived: "已放弃",
  };

  return (
    <main className="public-track">
      <Link href="/studio">← 返回创作者中心</Link>
      <article>
        <span className="eyebrow">MY DRAFTS</span>
        <h1>我的草稿</h1>
        <p className="result-note">服务器为状态权威；此处列出未完成作品及下一步。</p>
        {error && <p>{error}</p>}
        {drafts === null && !error && <p>加载中…</p>}
        {drafts && (
          <div className="inbox-list">
            {drafts.length === 0 && <p>暂无草稿。</p>}
            {drafts.map((draft) => (
              <div key={draft.track_id} className="inbox-item">
                <h3>{draft.title}</h3>
                <p>
                  <span className="tag">{stageLabel[draft.stage] ?? draft.stage}</span>
                  {draft.has_version ? " · 版本已就绪" : ""}
                  {draft.has_passport ? " · 护照已填" : ""}
                </p>
                <div className="hero-buttons">
                  {draft.stage !== "archived" && (
                    <Link className="glass" href={`/studio?draft=${draft.track_id}`}>继续</Link>
                  )}
                  {draft.stage !== "archived" && draft.stage !== "published" && (
                    <button className="glass" onClick={() => abandon(draft.track_id)} disabled={busyId === draft.track_id}>
                      {busyId === draft.track_id ? "处理中…" : "放弃草稿"}
                    </button>
                  )}
                  {draft.stage === "published" && <Link className="glass" href={`/t/${draft.track_id}`}>查看公开页</Link>}
                </div>
              </div>
            ))}
          </div>
        )}
      </article>
    </main>
  );
}
