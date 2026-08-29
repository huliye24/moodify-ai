"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { api, consoleApi, ConsoleTrack } from "../../lib/music-client";
import type { BootstrapUser } from "../../lib/music-client";

export default function ConsolePage() {
  const [me, setMe] = useState<BootstrapUser | null>(null);
  const [creatorId, setCreatorId] = useState("");
  const [tracks, setTracks] = useState<ConsoleTrack[] | null>(null);
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState("");
  const [editing, setEditing] = useState<{ id: string; title: string; updatedAt: string } | null>(null);

  useEffect(() => {
    void api.bootstrap().then(async (user) => {
      setMe(user);
      if (!user.capabilities?.creator_writes) {
        setError("创作者控制台仅对受邀创作者开放。");
        setTracks([]);
        return;
      }
      try {
        const creator = await api.creatorByHandle(user.demo_creator_handle ?? "");
        setCreatorId(creator.id);
        await load(creator.id);
      } catch (e) {
        setError(e instanceof Error ? e.message : "无法读取作品");
        setTracks([]);
      }
    }).catch(() => setError("无法确认当前用户"));
  }, []);

  async function load(cid: string) {
    const r = await consoleApi.myTracks(cid);
    setTracks(r.tracks);
  }

  async function unpublish(track: ConsoleTrack) {
    if (!confirm(`下架「${track.title}」？公开链接将立即失效，版本、护照与媒体保留。`)) return;
    setBusyId(track.id);
    try {
      await consoleApi.unpublish(track.id);
      await load(creatorId);
    } catch (e) {
      setError(e instanceof Error ? e.message : "下架失败");
    } finally {
      setBusyId("");
    }
  }

  async function republish(track: ConsoleTrack) {
    setBusyId(track.id);
    try {
      await api.publish(track.id);
      await load(creatorId);
    } catch (e) {
      setError(e instanceof Error ? e.message : "重新发布失败（需版本与护照完整）");
    } finally {
      setBusyId("");
    }
  }

  async function saveEdit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!editing) return;
    setBusyId(editing.id);
    try {
      const body = { title: (event.currentTarget.elements.namedItem("title") as HTMLInputElement).value };
      await consoleApi.updateTrack(editing.id, body, editing.updatedAt);
      setEditing(null);
      await load(creatorId);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "保存失败";
      setError(msg.includes("PRECONDITION") ? "该作品已被他人修改，请刷新后重试。" : msg);
    } finally {
      setBusyId("");
    }
  }

  const groups: Record<string, ConsoleTrack[]> = { draft: [], published: [], archived: [] };
  for (const t of tracks ?? []) if (groups[t.status]) groups[t.status].push(t);
  const groupLabel: Record<string, string> = { draft: "草稿", published: "已发布", archived: "已下架" };

  return (
    <main className="public-track">
      <Link href="/studio">← 返回创作者中心</Link>
      <article>
        <span className="eyebrow">CREATOR CONSOLE</span>
        <h1>创作者控制台</h1>
        {error && <p>{error}</p>}
        {tracks === null && !error && <p>加载中…</p>}
        {tracks && (
          <>
            <div className="inbox-list">
              {tracks.length === 0 && <p>还没有作品。去 <Link href="/studio">Studio</Link> 发布第一首。</p>}
              {(["published", "draft", "archived"] as const).map((status) => groups[status].length > 0 && (
                <section key={status}>
                  <h2 className="result-note">{groupLabel[status]} · {groups[status].length}</h2>
                  {groups[status].map((t) => (
                    <div key={t.id} className="inbox-item">
                      <h3>
                        {t.status === "published" ? <Link href={`/t/${t.id}`}>{t.title}</Link> : t.title}
                      </h3>
                      <p className="result-note">
                        {t.status} · {t.primary_language ?? "—"}
                        {t.published_at ? ` · 发布 ${new Date(t.published_at).toLocaleDateString("zh-CN")}` : ""}
                      </p>
                      <div className="hero-buttons">
                        {t.status === "draft" && <Link className="glass" href={`/studio?draft=${t.id}`}>继续</Link>}
                        {t.status === "published" && (
                          <button className="glass" onClick={() => unpublish(t)} disabled={busyId === t.id}>下架</button>
                        )}
                        {t.status === "archived" && (
                          <button className="glass" onClick={() => republish(t)} disabled={busyId === t.id}>重新发布</button>
                        )}
                        <button className="glass" onClick={() => setEditing({ id: t.id, title: t.title, updatedAt: t.updated_at ?? "" })}>
                          编辑标题
                        </button>
                      </div>
                    </div>
                  ))}
                </section>
              ))}
            </div>
            {editing && (
              <form className="license-form" onSubmit={saveEdit}>
                <legend>编辑标题（并发保护：若他人已修改将提示刷新）</legend>
                <input name="title" defaultValue={editing.title} maxLength={300} required />
                <div className="hero-buttons">
                  <button className="primary" type="submit" disabled={busyId === editing.id}>保存</button>
                  <button className="glass" type="button" onClick={() => setEditing(null)}>取消</button>
                </div>
              </form>
            )}
          </>
        )}
      </article>
    </main>
  );
}
