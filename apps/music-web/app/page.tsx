"use client";

import { useEffect, useMemo, useRef, useState } from "react";

type Track = {
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
  const audioRef = useRef<HTMLAudioElement>(null);
  const visible = useMemo(
    () => tracks.filter((track) => !query || `${track.title}${track.artist}`.toLowerCase().includes(query.toLowerCase())),
    [query],
  );
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
    setActive((current) => (current + direction + tracks.length) % tracks.length);
    setCurrentTime(0);
    setPlaying(true);
  };
  const formatTime = (seconds: number) => {
    if (!Number.isFinite(seconds)) return "0:00";
    return `${Math.floor(seconds / 60)}:${Math.floor(seconds % 60).toString().padStart(2, "0")}`;
  };
  const toggleLike = (index: number) => setLiked((items) => items.includes(index) ? items.filter((item) => item !== index) : [...items, index]);

  return <main>
    <aside className="sidebar">
      <div className="brand"><img src="/moodify-logo.png" alt="Moodify" /><span>Moodify</span></div>
      <nav>
        <button className="nav-active">◉　发现音乐</button>
        <label className="nav-search">⌕　<input aria-label="搜索音乐" placeholder="搜索" value={query} onChange={(event) => setQuery(event.target.value)} /></label>
        <button>▥　我的音乐</button>
      </nav>
      <div className="nav-group"><span>你的音乐</span><button>♡　我喜欢的</button><button><span className="mini-plus">＋</span>创建歌单</button></div>
      <div className="profile"><div className="avatar">M</div><div><strong>Moodify</strong><span>创作者</span></div><button>•••</button></div>
    </aside>

    <section className="content">
      <header><div className="mobile-brand"><img src="/moodify-logo.png" alt="" />Moodify</div><div className="history"><button>‹</button><button>›</button></div><div className="header-actions"><button>上传作品</button><button className="round">◎</button></div></header>
      <div className="hero">
        <div className="hero-copy"><span className="eyebrow">CADEAU10 · 专辑 1</span><h1>{tracks[active].title}</h1><p>{tracks[active].artist}</p><div className="hero-buttons"><button onClick={() => setPlaying((value) => !value)} className="primary"><span>{playing ? "Ⅱ" : "▶"}</span>{playing ? "暂停" : "开始聆听"}</button><button className="glass" aria-label={liked.includes(active) ? "取消收藏" : "收藏"} onClick={() => toggleLike(active)}>{liked.includes(active) ? "♥" : "♡"}</button></div></div>
        <div className="orb-wrap"><div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="hero-vinyl"><RecordArtwork track={tracks[active]} spinning={playing} /></div><span className="floating-note note-a">♪</span><span className="floating-note note-b">♫</span></div>
      </div>

      <div className="section-head"><div><span className="eyebrow">CURATED FOR YOU</span><h2>此刻值得听</h2></div><button>查看全部 <span>→</span></button></div>
      <div className="filters">{["为你推荐", "Cadeau10", "专辑 1"].map((item) => <button key={item} onClick={() => setFilter(item)} className={filter === item ? "selected" : ""}>{item}</button>)}</div>
      {query && <p className="result-note">“{query}” 的搜索结果</p>}
      <div className="tracks">{visible.map((track) => { const index = tracks.indexOf(track); return <article key={track.title} className={active === index && playing ? "playing" : ""}><button className="cover" onClick={() => play(index)} aria-label={`播放 ${track.title}`}><RecordArtwork track={track} spinning={active === index && playing} /><span>{active === index && playing ? "Ⅱ" : "▶"}</span></button><div className="track-info"><h3>{track.title}</h3><p>{track.artist}</p></div><span className="tag">{track.tag}</span><span className="duration">{track.length}</span><button className={`like ${liked.includes(index) ? "is-liked" : ""}`} onClick={() => toggleLike(index)}>{liked.includes(index) ? "♥" : "♡"}</button><button className="more">•••</button></article>; })}</div>
    </section>

    <audio ref={audioRef} src={tracks[active].src} preload="metadata" onLoadedMetadata={(event) => setDuration(event.currentTarget.duration)} onTimeUpdate={(event) => setCurrentTime(event.currentTarget.currentTime)} onEnded={() => skip(1)} />
    <div className="player"><div className="now"><RecordArtwork track={tracks[active]} spinning={playing} /><div><strong>{tracks[active].title}</strong><span>{tracks[active].artist}</span></div><button onClick={() => toggleLike(active)}>{liked.includes(active) ? "♥" : "♡"}</button></div><div className="controls"><div><button>↝</button><button onClick={() => skip(-1)}>◀</button><button className="play" onClick={() => setPlaying(!playing)}>{playing ? "Ⅱ" : "▶"}</button><button onClick={() => skip(1)}>▶</button><button>↝</button></div><div className="timeline"><span>{formatTime(currentTime)}</span><input aria-label="播放进度" type="range" min="0" max={duration || 0} step="0.1" value={Math.min(currentTime, duration || 0)} onChange={(event) => { const nextTime = Number(event.target.value); if (audioRef.current) audioRef.current.currentTime = nextTime; setCurrentTime(nextTime); }} /><span>{duration ? formatTime(duration) : tracks[active].length}</span></div></div><div className="utilities"><button>DIY</button><button>☰</button><span>◉</span><div className="volume"><i /></div></div></div>
  </main>;
}
