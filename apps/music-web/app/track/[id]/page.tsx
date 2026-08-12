"use client";

import { useEffect, useState } from "react";

type PublicTrack = { id: string; title: string; description: string; sourceType: string; licenseStatus: string; creatorHandle: string; creatorName: string };

export default function TrackPage({ params }: { params: Promise<{ id: string }> }) {
  const [track, setTrack] = useState<PublicTrack | null>(null);
  const [id, setId] = useState("");
  useEffect(() => { void params.then(({ id }) => { setId(id); void fetch(`/api/v1/tracks/${id}`).then((response) => response.ok ? response.json() : Promise.reject()).then((body) => setTrack(body.track)).catch(() => setTrack(null)); }); }, [params]);
  return <main className="public-track"><a href="/">← Moodify</a>{track ? <article><div className="hero-vinyl"><div className="vinyl"><img src="/moodify-logo.png" alt="Moodify 默认黑胶"/><i/></div></div><span className="eyebrow">{track.sourceType.toUpperCase()}</span><h1>{track.title}</h1><p><a href={`/c/${track.creatorHandle}`}>{track.creatorName} · @{track.creatorHandle}</a></p>{track.description && <p>{track.description}</p>}<audio controls preload="metadata" src={`/api/v1/tracks/${id}/audio`}/>{track.licenseStatus === "inquiry" && <button className="primary">授权此作品</button>}</article> : <p>作品不存在或尚未发布。</p>}</main>;
}
