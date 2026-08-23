"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { api, playlists, type BootstrapUser, type PlaylistDto } from "../../lib/music-client";

export default function PlaylistsPage() {
  const [me, setMe] = useState<BootstrapUser | null>(null);
  const [list, setList] = useState<PlaylistDto[] | null>(null);
  const [error, setError] = useState("");
  const [open, setOpen] = useState<PlaylistDto | null>(null);
  const [addTrackId, setAddTrackId] = useState("");

  useEffect(() => {
    void api.bootstrap().then(async (user) => {
      setMe(user);
      if (!user.capabilities?.account_actions || !user.id) {
        setError("歌单需要登录。未登录时聆听保持开放。");
        setList([]);
        return;
      }
      await load(user.id);
    }).catch(() => setError("无法确认当前用户"));
  }, []);

  async function load(userId: string) {
    try {
      const r = await playlists.mine(userId);
      setList(r.playlists);
    } catch (e) {
      setError(e instanceof Error ? e.message : "读取失败");
      setList([]);
    }
  }

  async function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!me?.id) return;
    const title = (event.currentTarget.elements.namedItem("title") as HTMLInputElement).value;
    await playlists.create({ owner_user_id: me.id, title, visibility: "private" });
    await load(me.id);
  }

  async function addItem(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!open || !addTrackId.trim()) return;
    try {
      await playlists.addItem(open.id, addTrackId.trim());
      setAddTrackId("");
      setOpen(await playlists.get(open.id));
    } catch (e) {
      setError(e instanceof Error ? e.message : "添加失败");
    }
  }

  async function removeItem(trackId: string) {
    if (!open) return;
    await playlists.removeItem(open.id, trackId);
    setOpen(await playlists.get(open.id));
  }

  async function toggleVisibility(p: PlaylistDto) {
    const userId = me?.id;
    if (!userId) return;
    await playlists.update(p.id, { visibility: p.visibility === "private" ? "public" : "private" });
    await load(userId);
    if (open?.id === p.id) setOpen(await playlists.get(p.id));
  }

  async function removePlaylist(p: PlaylistDto) {
    const userId = me?.id;
    if (!userId) return;
    if (!confirm(`删除歌单「${p.title}」？仅删除歌单容器，曲目与媒体不受影响。`)) return;
    await playlists.remove(p.id);
    if (open?.id === p.id) setOpen(null);
    await load(userId);
  }

  return (
    <main className="public-track">
      <Link href="/">← Moodify</Link>
      <article>
        <span className="eyebrow">MY PLAYLISTS</span>
        <h1>歌单</h1>
        {error && <p>{error}</p>}
        {me?.capabilities?.account_actions && (
          <>
            <form className="license-form" onSubmit={create}>
              <input name="title" placeholder="新歌单名称" maxLength={200} required />
              <button className="primary" type="submit">创建私有歌单</button>
            </form>
            {list === null && <p>加载中…</p>}
            {list && list.length === 0 && <p>还没有歌单。创建一个吧。</p>}
            <div className="inbox-list">
              {list?.map((p) => (
                <div key={p.id} className="inbox-item">
                  <h3>{p.title} <span className="tag">{p.visibility === "private" ? "私有" : "公开"}</span></h3>
                  <div className="hero-buttons">
                    <button className="glass" onClick={() => setOpen(open?.id === p.id ? null : p)}>{open?.id === p.id ? "收起" : "查看"}</button>
                    <button className="glass" onClick={() => toggleVisibility(p)}>设为{p.visibility === "private" ? "公开" : "私有"}</button>
                    <button className="glass" onClick={() => removePlaylist(p)}>删除歌单</button>
                  </div>
                </div>
              ))}
            </div>
            {open && (
              <section className="studio-card">
                <h2>{open.title} · {open.items.length} 首</h2>
                <form className="license-form" onSubmit={addItem}>
                  <input name="trackId" value={addTrackId} onChange={(e) => setAddTrackId(e.target.value)} placeholder="曲目 ID（从公开页 /t/{id} 获取）" />
                  <button className="primary" type="submit">添加曲目（重复会被拒绝）</button>
                </form>
                {open.items.length === 0 && <p className="result-note">歌单为空。</p>}
                {open.items.map((item) => (
                  <div key={item.track_id} className="inbox-item">
                    <p><Link href={`/t/${item.track_id}`}>#{item.position} · {item.track_id.slice(0, 8)}</Link></p>
                    <button className="glass" onClick={() => removeItem(item.track_id)}>移除</button>
                  </div>
                ))}
              </section>
            )}
          </>
        )}
      </article>
    </main>
  );
}
