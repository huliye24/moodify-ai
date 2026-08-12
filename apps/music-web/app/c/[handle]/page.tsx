"use client";

import { useEffect, useState } from "react";

type Creator = { handle: string; displayName: string; bio: string };
type Work = { id: string; title: string; sourceType: string };

export default function CreatorPage({ params }: { params: Promise<{ handle: string }> }) {
  const [creator, setCreator] = useState<Creator | null>(null);
  const [works, setWorks] = useState<Work[]>([]);
  useEffect(() => { void params.then(({ handle }) => fetch(`/api/v1/creators/${encodeURIComponent(handle)}`).then((response) => response.ok ? response.json() : Promise.reject()).then((body) => { setCreator(body.creator); setWorks(body.tracks); }).catch(() => setCreator(null))); }, [params]);
  return <main className="public-track"><a href="/">← Moodify</a>{creator ? <article><div className="avatar creator-avatar">{creator.displayName.slice(0, 1)}</div><span className="eyebrow">@{creator.handle}</span><h1>{creator.displayName}</h1>{creator.bio && <p>{creator.bio}</p>}<h2>作品</h2><div className="creator-works">{works.map((work) => <a key={work.id} href={`/track/${work.id}`}><span>{work.title}</span><small>{work.sourceType}</small></a>)}</div></article> : <p>音乐馆不存在或尚未公开。</p>}</main>;
}
