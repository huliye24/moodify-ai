"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "../../../lib/music-client";
import type { BootstrapUser, CreatorPage as CreatorPageDto } from "../../../lib/music-client";

export default function CreatorPage({ params }: { params: Promise<{ handle: string }> }) {
  const [page, setPage] = useState<CreatorPageDto | null>(null);
  const [me, setMe] = useState<BootstrapUser | null>(null);
  const [following, setFollowing] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    void params.then(({ handle }) => {
      void api.creatorByHandle(handle).then(async (profile) => {
        const [creatorPage, user] = await Promise.all([api.creatorPage(profile.id), api.bootstrap().catch(() => null)]);
        setPage(creatorPage);
        setMe(user);
        setFollowing(Boolean(creatorPage.viewer_following));
      }).catch(() => setPage(null));
    });
  }, [params]);

  async function toggleFollow() {
    if (!me?.id || !page) return;
    setBusy(true);
    try {
      if (following) await api.unfollow(me.id, page.profile.id);
      else await api.follow(me.id, page.profile.id);
      setFollowing(!following);
    } finally {
      setBusy(false);
    }
  }

  if (!page) return <main className="public-track"><Link href="/">← Moodify</Link><p>音乐馆不存在或尚未公开。</p></main>;
  const { profile } = page;
  return (
    <main className="public-track">
      <Link href="/">← Moodify</Link>
      <article>
        <div className="avatar creator-avatar">{profile.display_name.slice(0, 1)}</div>
        <span className="eyebrow">@{profile.handle}</span>
        <h1>{profile.display_name}</h1>
        {profile.bio && <p>{profile.bio}</p>}
        <p className="result-note">{page.follower_count} 关注</p>
        {me?.capabilities?.account_actions && (
          <button className="primary" onClick={toggleFollow} disabled={busy}>
            {following ? "取消关注" : "关注"}
          </button>
        )}
        <h2>作品</h2>
        <div className="creator-works">
          {page.tracks.map((track) => (
            <Link key={track.id} href={`/t/${track.id}`}>
              <span>{track.title}</span>
              <small>{track.primary_language ?? "—"}</small>
            </Link>
          ))}
        </div>
      </article>
    </main>
  );
}
