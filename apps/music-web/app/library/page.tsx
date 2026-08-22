"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, library, type BootstrapUser, type TrackDto } from "../../lib/music-client";

export default function LibraryPage() {
  const [me, setMe] = useState<BootstrapUser | null>(null);
  const [tab, setTab] = useState<"favorites" | "recent">("favorites");
  const [tracks, setTracks] = useState<TrackDto[] | null>(null);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    void api.bootstrap().then(async (user) => {
      setMe(user);
      if (!user.capabilities?.account_actions || !user.id) {
        setError("音乐库需要登录。未登录时聆听保持开放。");
        setTracks([]);
        return;
      }
      await load(user.id, "favorites");
    }).catch(() => setError("无法确认当前用户"));
  }, []);

  async function load(userId: string, which: "favorites" | "recent", cursor?: string) {
    setError("");
    try {
      if (which === "favorites") {
        const r = await library.myFavorites(userId, cursor);
        setTracks((prev) => cursor && prev ? [...prev, ...r.tracks] : r.tracks);
        setNextCursor(r.next_cursor);
      } else {
        const r = await library.myRecentPlays(userId);
        setTracks(r.tracks);
        setNextCursor(null);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "读取失败");
      setTracks([]);
    }
  }

  function switchTab(which: "favorites" | "recent") {
    if (!me?.id) return;
    setTab(which);
    setTracks(null);
    void load(me.id, which);
  }

  // Package 04: Legacy fallback — replace after play.rongjingmusic.com origin is live.
  const audioBaseUrl = (process.env.NEXT_PUBLIC_AUDIO_BASE_URL ?? "https://play.rongjingmusic.com/audio").replace(/\/$/, "");

  return (
    <main className="public-track">
      <Link href="/">← Moodify</Link>
      <article>
        <span className="eyebrow">MY LIBRARY</span>
        <h1>音乐库</h1>
        {error && <p>{error}</p>}
        {me?.capabilities?.account_actions && (
          <>
            <div className="filters">
              <button className={tab === "favorites" ? "selected" : ""} onClick={() => switchTab("favorites")}>我喜欢的</button>
              <button className={tab === "recent" ? "selected" : ""} onClick={() => switchTab("recent")}>最近播放</button>
            </div>
            {tracks === null && <p>加载中…</p>}
            {tracks && tracks.length === 0 && <p>这里还没有内容{tab === "favorites" ? "。去首页收藏一首歌吧。" : "。播放过的歌曲会出现在这里。"}</p>}
            {tracks && tracks.length > 0 && (
              <div className="inbox-list">
                {tracks.map((t) => (
                  <div key={t.id} className="inbox-item">
                    <h3><Link href={`/t/${t.id}`}>{t.title}</Link></h3>
                    <p className="result-note">
                      {t.primary_language ?? "—"}
                      {t.duration_ms ? ` · ${Math.round(t.duration_ms / 1000)}s` : ""}
                      {"favorited_at" in t ? " · 已收藏" : ""}
                      {"last_played_at" in t ? " · 最近播放" : ""}
                    </p>
                    {t.audio_asset_key && (
                      <audio controls preload="none" src={`${audioBaseUrl}/${t.audio_asset_key}`} style={{ width: "100%", maxWidth: 430 }} />
                    )}
                  </div>
                ))}
              </div>
            )}
            {nextCursor && (
              <button className="glass" onClick={() => me.id && void load(me.id, "favorites", nextCursor)}>加载更多</button>
            )}
          </>
        )}
      </article>
    </main>
  );
}
