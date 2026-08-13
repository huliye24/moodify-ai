"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { api } from "../../lib/music-client";
import type { BootstrapUser, MediaUpload } from "../../lib/music-client";

type Attempt = {
  fingerprint: string;
  media?: MediaUpload;
  trackId?: string;
  keys: { creator: string; track: string; version: string; passport: string; publish: string };
};

const newAttempt = (fingerprint: string): Attempt => ({
  fingerprint,
  keys: {
    creator: crypto.randomUUID(), track: crypto.randomUUID(), version: crypto.randomUUID(),
    passport: crypto.randomUUID(), publish: crypto.randomUUID(),
  },
});

export default function StudioPage() {
  const [message, setMessage] = useState("先建立音乐馆，再发布第一首作品。");
  const [busy, setBusy] = useState(false);
  const [me, setMe] = useState<BootstrapUser | null>(null);
  const [publishedUrl, setPublishedUrl] = useState("");
  const attempt = useRef<Attempt | null>(null);

  useEffect(() => {
    api.bootstrap().then(setMe).catch(() => setMe(null));
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setPublishedUrl("");
    const form = new FormData(event.currentTarget);
    try {
      if (!me?.capabilities?.creator_writes) throw new Error("创作者发布仅对受邀账户开放");
      if (!me.id) throw new Error("无法确认当前账户身份");
      const file = form.get("audio") as File;
      if (!file?.size) throw new Error("请选择音频文件");
      const fingerprint = `${file.name}:${file.size}:${file.lastModified}`;
      if (!attempt.current || attempt.current.fingerprint !== fingerprint) attempt.current = newAttempt(fingerprint);
      const current = attempt.current;

      setMessage("正在确认音乐馆…");
      let creator;
      try {
        creator = await api.creatorByHandle(String(form.get("handle") || "").trim().toLowerCase());
      } catch {
        creator = await api.createCreator({
          user_id: me.id,
          handle: String(form.get("handle") || "").trim().toLowerCase(),
          display_name: form.get("displayName"),
          bio: form.get("bio"),
        }, current.keys.creator);
      }

      let media = current.media;
      if (!media) {
        setMessage("正在安全上传音频 · 0%");
        media = await api.uploadAudio(file, (loaded, total) => {
          const percent = total > 0 ? Math.min(100, Math.round(loaded * 100 / total)) : 0;
          setMessage(`正在安全上传音频 · ${percent}%`);
        });
        current.media = media;
      } else {
        setMessage("音频已上传，继续上次发布…");
      }

      setMessage("正在创建作品草稿…");
      const draft = current.trackId
        ? await api.track(current.trackId)
        : await api.createTrack({
            creator_id: creator.id,
            title: form.get("title"),
            primary_language: form.get("language"),
            duration_ms: Number(form.get("durationMs") || 0) || null,
          }, current.keys.track);
      current.trackId = draft.id;

      setMessage("正在登记音频版本…");
      await api.createVersion(draft.id, {
        audio_asset_key: media.asset_key,
        duration_ms: Number(form.get("durationMs") || 0) || null,
        metadata_json: { sha256: media.sha256, bytes: media.bytes, mime_type: media.mime_type },
      }, current.keys.version);
      setMessage("正在登记创作护照…");
      await api.upsertPassport(draft.id, {
        origin_type: form.get("sourceType"),
        generation_tool: form.get("aiTool"),
        generation_model: form.get("model"),
        prompt_disclosure: "private",
        human_editing_notes: form.get("humanEditing"),
        rights_statement: form.get("rightsStatement"),
      }, current.keys.passport);
      setMessage("正在发布…");
      await api.publish(draft.id, current.keys.publish);
      setPublishedUrl(`${location.origin}/t/${draft.id}`);
      setMessage("发布成功");
      attempt.current = null;
    } catch (error) {
      setMessage(`${error instanceof Error ? error.message : "发布失败"}。可直接重试，已完成的步骤不会重复执行。`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="studio-shell">
      <Link href="/">← 返回聆听</Link>
      <section className="studio-card">
        <span className="eyebrow">CREATOR STUDIO</span>
        <h1>发布作品</h1>
        <p>封面可选。没有封面时，作品使用统一的 Moodify 黑胶视觉。音频将流式上传并记录 SHA-256。</p>
        <form onSubmit={submit}>
          <fieldset><legend>音乐馆</legend>
            <input name="handle" required minLength={3} maxLength={64} placeholder="唯一 handle，如 cadeau10" />
            <input name="displayName" required maxLength={120} placeholder="创作者名称" />
            <textarea name="bio" maxLength={2000} placeholder="一句简介（可选）" />
          </fieldset>
          <fieldset><legend>作品</legend>
            <input name="title" required maxLength={300} placeholder="作品标题" />
            <input name="language" maxLength={16} placeholder="语言，如 fr" />
            <input name="durationMs" type="number" min={0} placeholder="时长（毫秒，可选）" />
            <input name="audio" type="file" accept="audio/wav,audio/mpeg,audio/flac,audio/ogg,audio/mp4,audio/aac" required />
          </fieldset>
          <fieldset><legend>创作护照（来源声明，非版权确权）</legend>
            <select name="sourceType" defaultValue="ai_human_hybrid"><option value="ai">AI</option><option value="human">Human</option><option value="ai_human_hybrid">Hybrid</option></select>
            <input name="aiTool" maxLength={128} placeholder="使用工具（可选）" />
            <input name="model" maxLength={128} placeholder="模型/版本（可选）" />
            <textarea name="humanEditing" maxLength={4000} placeholder="人工修改说明（可选）" />
            <textarea name="rightsStatement" required maxLength={4000} placeholder="权利声明（必填）" />
          </fieldset>
          <button className="primary" disabled={busy || !me?.capabilities?.creator_writes}>{busy ? "处理中…" : "发布作品"}</button>
        </form>
        {me && !me.capabilities?.creator_writes && <p className="result-note">只读模式：聆听保持开放。<Link href="/beta-login">受邀创作者登录 →</Link></p>}
        <output aria-live="polite">{message}{publishedUrl && <span> → <a href={publishedUrl}>{publishedUrl}</a></span>}</output>
        <p className="result-note">创作者自行提供来源信息；Moodify 不将其视为版权认证。</p>
      </section>
    </main>
  );
}
