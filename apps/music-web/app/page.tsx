"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { BootstrapUser } from "../lib/music-client";

type Track = {
  id?: string;
  title: string;
  artist: string;
  length: string;
  tag: string;
  src: string;
  creatorCover?: string;
  userCover?: string;
};

const audioBaseUrl = (process.env.NEXT_PUBLIC_AUDIO_BASE_URL ?? "https://rongjinwenchuan.xyz/audio").replace(/\/$/, "");
const albumAudio = (file: string) => `${audioBaseUrl}/cadeau10-album1/${file}`;

const tracks: Track[] = [
  { title: "Je ne veux pas enfermer ton aujourd'hui", artist: "Cadeau10", length: "2:44", tag: "专辑 1", src: albumAudio("je-ne-veux-pas-enfermer-ton-aujourdhui.wav") },
  { title: "Ne vivons pas seulement de souvenirs", artist: "Cadeau10", length: "3:39", tag: "专辑 1", src: albumAudio("ne-vivons-pas-seulement-de-souvenirs.wav") },
  { title: "Nous pouvons nous reconnaître encore", artist: "Cadeau10", length: "2:59", tag: "专辑 1", src: albumAudio("nous-pouvons-nous-reconnaitre-encore.wav") },
  { title: "Où es-tu maintenant", artist: "Cadeau10", length: "3:04", tag: "专辑 1", src: albumAudio("ou-es-tu-maintenant.wav") },
  { title: "Vieillir et devenir nouveau avec toi", artist: "Cadeau10", length: "3:02", tag: "专辑 1", src: albumAudio("vieillir-et-devenir-nouveau-avec-toi.wav") },
];

function RecordArtwork({ track, spinning = false }: { track: Track; spinning?: boolean }) {
  const cover = track.userCover ?? track.creatorCover;
  return (
    <div className={`vinyl ${spinning ? "is-spinning" : ""}`}>
      {cover ? (
        <img src={cover} alt={`${track.title} 自定义封面`} />
      ) : (
        <img src="/moodify-logo.png" alt="Moodify 默认黑胶" />
      )}
      <i />
    </div>
  );
}

export default function Home() {
  const [active, setActive] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [liked, setLiked] = useState<number[]>([1]);
  const [filter, setFilter] = useState("为你推荐");
  const [query, setQuery] = useState("");
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [liveTracks, setLiveTracks] = useState<Track[] | null>(null);
  const [me, setMe] = useState<BootstrapUser | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const [sessionId] = useState(() => `s${Date.now().toString(36)}${Math.random().toString(36).slice(2)}`);
  const all = liveTracks ?? tracks;
  const visible = useMemo(
    () => all.filter((track) => !query || `${track.title}${track.artist}`.toLowerCase().includes(query.toLowerCase())),
    [query, all],
  );
  useEffect(() => {
    void import("../lib/music-client").then(({ api }) => {
      void api.bootstrap().then((user) => setMe(user)).catch(() => null);
      void api.catalogue().then((c) => setLiveTracks(c.tracks.map((t) => ({
        id: t.id,
        title: t.title,
        artist: t.creator_handle ?? "Moodify",
        length: t.duration_ms ? `${Math.floor(t.duration_ms / 60000)}:${String(Math.floor((t.duration_ms % 60000) / 1000)).padStart(2, "0")}` : "--:--",
        tag: t.primary_language ?? t.status,
        src: t.version?.audio_asset_key ? `${audioBaseUrl}/${t.version.audio_asset_key}` : albumAudio("je-ne-veux-pas-enfermer-ton-aujourdhui.wav"),
      })))).catch(() => setLiveTracks(null));
    });
  }, []);
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    if (playing) void audio.play().catch(() => setPlaying(false));
    else audio.pause();
  }, [active, playing]);

  const play = (index: number) => {
    if (index === active) setPlaying((value) => !value);
    else { setActive(index); setCurrentTime(0); setPlaying(true); }
  };
  const skip = (direction: -1 | 1) => {
    setActive((current) => (current + direction + all.length) % all.length);
    setCurrentTime(0);
    setPlaying(true);
  };
  const formatTime = (seconds: number) => {
    if (!Number.isFinite(seconds)) return "0:00";
    return `${Math.floor(seconds / 60)}:${Math.floor(seconds % 60).toString().padStart(2, "0")}`;
  };
  const toggleLike = (index: number) => {
    const track = all[index];
    setLiked((items) => items.includes(index) ? items.filter((item) => item !== index) : [...items, index]);
    if (track?.id && me?.id && me.capabilities?.account_actions) {
      const userId = me.id;
      void import("../lib/music-client").then(({ api }) => {
        if (liked.includes(index)) void api.unfavorite(userId, track.id as string).catch(() => {});
        else void api.favorite(userId, track.id as string).catch(() => {});
      });
    }
  };
  const onPlay = () => {
    const track = all[active];
    if (track?.id) {
      void import("../lib/music-client").then(({ api }) =>
        api.playEvent({ track_id: track.id as string, user_id: me?.id ?? null, session_id: sessionId, played_ms: 0, source: "discover" }).catch(() => {}),
      );
    }
  };

  return <main>
    <aside className="sidebar">
      <div className="brand"><img src="/moodify-logo.png" alt="Moodify" /><span>Moodify</span></div>
      <nav>
        <button className="nav-active" aria-current="page">◉　发现音乐</button>
        <label className="nav-search">⌕　<input aria-label="搜索音乐" placeholder="搜索" value={query} onChange={(event) => setQuery(event.target.value)} /></label>
        <a href="/library" className="nav-link">▥　我的音乐</a>
      </nav>
      <div className="nav-group"><span>你的音乐</span><a href="/inbox" className="nav-link">✉　授权意向</a><a href="/studio" className="nav-link">＋　创作者中心</a></div>
      <div className="profile"><div className="avatar">M</div><div><strong>Moodify</strong><span>创作者</span></div><button>•••</button></div>
    </aside>

    <section className="content">
      <header><div className="mobile-brand"><img src="/moodify-logo.png" alt="" />Moodify</div><div className="history"><button>‹</button><button>›</button></div><div className="header-actions"><a href="/studio">上传作品</a><button className="round">◎</button></div></header>
      <div className="hero">
        <div className="hero-copy"><span className="eyebrow">CADEAU10 · 专辑 1</span><h1>{all[active].title}</h1><p>{all[active].artist}</p><div className="hero-buttons"><button onClick={() => setPlaying((value) => !value)} className="primary"><span>{playing ? "Ⅱ" : "▶"}</span>{playing ? "暂停" : "开始聆听"}</button><button className="glass" aria-label={liked.includes(active) ? "取消收藏" : "收藏"} onClick={() => toggleLike(active)}>{liked.includes(active) ? "♥" : "♡"}</button></div></div>
        <div className="orb-wrap"><div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="hero-vinyl"><RecordArtwork track={all[active]} spinning={playing} /></div><span className="floating-note note-a">♪</span><span className="floating-note note-b">♫</span></div>
      </div>

      <div className="section-head"><div><span className="eyebrow">CURATED FOR YOU</span><h2>此刻值得听</h2></div></div>
      <div className="filters">{["为你推荐", "Cadeau10", "专辑 1"].map((item) => <button key={item} onClick={() => setFilter(item)} className={filter === item ? "selected" : ""}>{item}</button>)}</div>
      {query && <p className="result-note">“{query}” 的搜索结果</p>}
      <div className="tracks">{visible.map((track) => { const index = all.indexOf(track); return <article key={track.title} className={active === index && playing ? "playing" : ""}><button className="cover" onClick={() => play(index)} aria-label={`播放 ${track.title}`} aria-pressed={active === index && playing}><RecordArtwork track={track} spinning={active === index && playing} /><span>{active === index && playing ? "Ⅱ" : "▶"}</span></button><div className="track-info"><h3>{track.title}</h3><p>{track.artist}</p></div><span className="duration">{track.length}</span><button className={`like ${liked.includes(index) ? "is-liked" : ""}`} onClick={() => toggleLike(index)} aria-label={liked.includes(index) ? `取消收藏 ${track.title}` : `收藏 ${track.title}`}>{liked.includes(index) ? "♥" : "♡"}</button></article>; })}</div>
    </section>

    <audio ref={audioRef} src={all[active].src} preload="metadata" onPlay={onPlay} onLoadedMetadata={(event) => setDuration(event.currentTarget.duration)} onTimeUpdate={(event) => setCurrentTime(event.currentTarget.currentTime)} onEnded={() => skip(1)} />
    <div className="player"><div className="now"><RecordArtwork track={all[active]} spinning={playing} /><div><strong>{all[active].title}</strong><span>{all[active].artist}</span></div><button onClick={() => toggleLike(active)} aria-label={liked.includes(active) ? "取消收藏" : "收藏"}>{liked.includes(active) ? "♥" : "♡"}</button></div><div className="controls"><div><button onClick={() => skip(-1)} aria-label="上一首">◀</button><button className="play" onClick={() => setPlaying(!playing)} aria-label={playing ? "暂停" : "播放"}>{playing ? "Ⅱ" : "▶"}</button><button onClick={() => skip(1)} aria-label="下一首">▶</button></div><div className="timeline"><span>{formatTime(currentTime)}</span><input aria-label="播放进度" type="range" min="0" max={duration || 0} step="0.1" value={Math.min(currentTime, duration || 0)} onChange={(event) => { const nextTime = Number(event.target.value); if (audioRef.current) audioRef.current.currentTime = nextTime; setCurrentTime(nextTime); }} /><span>{duration ? formatTime(duration) : all[active].length}</span></div></div><div className="utilities"><span aria-hidden="true">◉</span></div></div>
  </main>;
}
