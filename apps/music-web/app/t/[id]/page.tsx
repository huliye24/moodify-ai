"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { api, BootstrapUser, TrackDto } from "../../../lib/music-client";

// Package 04: Legacy fallback — replace after play.rongjingmusic.com origin is live.
const audioBaseUrl = (process.env.NEXT_PUBLIC_AUDIO_BASE_URL ?? "https://play.rongjingmusic.com/audio").replace(/\/$/, "");

export default function TrackPage({ params }: { params: Promise<{ id: string }> }) {
  const [track, setTrack] = useState<TrackDto | null>(null);
  const [me, setMe] = useState<BootstrapUser | null>(null);
  const [favorited, setFavorited] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [licenseMsg, setLicenseMsg] = useState("");
  const audioRef = useRef<HTMLAudioElement>(null);
  const sessionId = useRef("");

  useEffect(() => {
    void params.then(({ id }) => {
      void Promise.all([api.track(id), api.bootstrap().catch(() => null)]).then(([t, user]) => {
        setTrack(t);
        setMe(user);
        setFavorited(false);
      }).catch(() => setTrack(null));
    });
  }, [params]);

  function onPlay() {
    if (!track) return;
    if (!sessionId.current) sessionId.current = crypto.randomUUID();
    setPlaying(true);
    void api.playEvent({ track_id: track.id, user_id: me?.id ?? null, session_id: sessionId.current, played_ms: 0, source: "track_page" }).catch(() => {});
  }

  async function toggleFavorite() {
    if (!me?.id || !track) return;
    if (favorited) await api.unfavorite(me.id, track.id);
    else await api.favorite(me.id, track.id);
    setFavorited(!favorited);
  }

  async function submitLicense(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!track) return;
    const form = new FormData(event.currentTarget);
    setLicenseMsg("正在提交授权意向…");
    try {
      await api.licenseIntent({
        track_id: track.id,
        license_type: String(form.get("licenseType") || "sync"),
        usage_description: String(form.get("usage") || ""),
        requester_name: form.get("name"),
        requester_email: form.get("email"),
        budget_amount_minor: Number(form.get("budget") || 0) || null,
        budget_currency: "CNY",
      });
      setLicenseMsg("已提交。创作者将在 Inbox 中看到这条授权意向。");
    } catch (error) {
      setLicenseMsg(error instanceof Error ? error.message : "提交失败");
    }
  }

  if (!track) return <main className="public-track"><Link href="/">← Moodify</Link><p>作品不存在或尚未发布。</p></main>;
  const audioUrl = track.version?.audio_asset_key ? `${audioBaseUrl}/${track.version.audio_asset_key}` : null;

  return (
    <main className="public-track">
      <Link href="/">← Moodify</Link>
      <article>
        <div className="hero-vinyl"><div className="vinyl is-spinning"><img src="/moodify-logo.png" alt="Moodify 默认黑胶" /><i /></div></div>
        <span className="eyebrow">PUBLISHED · {track.primary_language ?? "—"}</span>
        <h1>{track.title}</h1>
        <p className="result-note">{track.duration_ms ? `${Math.round(track.duration_ms / 1000)}s` : ""}</p>
        {audioUrl && (
          <audio ref={audioRef} controls preload="metadata" src={audioUrl} onPlay={onPlay} onPause={() => setPlaying(false)} />
        )}
        <div className="hero-buttons">
          {me?.capabilities?.account_actions && (
            <button className="glass" onClick={toggleFavorite}>{favorited ? "♥ 已收藏" : "♡ 收藏"}</button>
          )}
          {track.creator_handle && <Link className="glass" href={`/c/${track.creator_handle}`}>创作者</Link>}
        </div>
        <h2>授权此作品</h2>
        <form className="license-form" onSubmit={submitLicense}>
          <input name="licenseType" defaultValue="sync" placeholder="授权类型，如 sync（同步授权）" />
          <input name="usage" required placeholder="使用场景（必填），如 短视频/短片配乐" />
          <input name="name" placeholder="联系人（可选）" />
          <input name="email" type="email" placeholder="联系邮箱（可选）" />
          <input name="budget" type="number" min={0} placeholder="预算（人民币，可选）" />
          <button className="primary" type="submit">提交授权意向</button>
          <output>{licenseMsg}</output>
        </form>
        <p className="result-note">{playing ? "正在播放" : "▸ 播放会记录一次 play event"}</p>
      </article>
    </main>
  );
}
