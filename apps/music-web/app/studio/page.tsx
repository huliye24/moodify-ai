"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { api, lifecycle } from "../../lib/music-client";
import type { BootstrapUser, MediaUpload } from "../../lib/music-client";

type Attempt = {
  fingerprint: string;
  media?: MediaUpload;
  trackId?: string;
  keys: { creator: string; track: string; version: string; passport: string; publish: string };
};

const WORKFLOW_KEY = "mfy_workflow_v1";

const newAttempt = (fingerprint: string): Attempt => ({
  fingerprint,
  keys: {
    creator: crypto.randomUUID(), track: crypto.randomUUID(), version: crypto.randomUUID(),
    passport: crypto.randomUUID(), publish: crypto.randomUUID(),
  },
});

function loadAttempt(): Attempt | null {
  try {
    const raw = localStorage.getItem(WORKFLOW_KEY);
    return raw ? (JSON.parse(raw) as Attempt) : null;
  } catch {
    return null;
  }
}

function saveAttempt(attempt: Attempt) {
  try {
    localStorage.setItem(WORKFLOW_KEY, JSON.stringify(attempt));
  } catch {
    // storage unavailable — recovery hints degrade gracefully
  }
}

function clearAttempt() {
  try {
    localStorage.removeItem(WORKFLOW_KEY);
  } catch {
    // ignore
  }
}

export default function StudioPage() {
  const [message, setMessage] = useState("先建立音乐馆，再发布第一首作品。");
  const [busy, setBusy] = useState(false);
  const [me, setMe] = useState<BootstrapUser | null>(null);
  const [publishedUrl, setPublishedUrl] = useState("");
  const [confirm, setConfirm] = useState<{ title: string; fingerprint: string; rights: string; trackId: string } | null>(null);
  const attempt = useRef<Attempt | null>(null);

  useEffect(() => {
    api.bootstrap().then(setMe).catch(() => setMe(null));
    const saved = loadAttempt();
    if (saved?.trackId) {
      attempt.current = saved;
      void lifecycle.resume(saved.trackId).then((state) => {
        if (state.stage === "published") {
          setPublishedUrl(`${location.origin}/t/${saved.trackId}`);
          setMessage("该作品已发布。");
          clearAttempt();
        } else if (state.stage === "archived") {
          setMessage("上次作品已放弃。重新填写后可再次发布。");
          clearAttempt();
        } else {
          setMessage(`已恢复草稿「${state.track.title}」（${state.stage} → ${state.next_action}）。可继续发布或更换内容。`);
        }
      }).catch(() => setMessage(""));
    }
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
      let draft;
      if (current.trackId) {
        const state = await lifecycle.resume(current.trackId);
        if (state.stage === "published") {
          setPublishedUrl(`${location.origin}/t/${current.trackId}`);
          setMessage("该作品已发布。");
          clearAttempt();
          return;
        }
        if (state.stage === "archived") {
          current.trackId = undefined;
          draft = await api.createTrack({
            creator_id: creator.id,
            title: form.get("title"),
            primary_language: form.get("language"),
            duration_ms: Number(form.get("durationMs") || 0) || null,
          }, current.keys.track);
          current.trackId = draft.id;
        } else {
          draft = await api.track(current.trackId);
        }
      } else {
        draft = await api.createTrack({
          creator_id: creator.id,
          title: form.get("title"),
          primary_language: form.get("language"),
          duration_ms: Number(form.get("durationMs") || 0) || null,
        }, current.keys.track);
        current.trackId = draft.id;
      }
      saveAttempt(current);

      const resume = current.trackId ? await lifecycle.resume(current.trackId).catch(() => null) : null;
      if (!resume?.stage || resume.stage === "draft" || resume.stage === "media_ready") {
        setMessage("正在登记音频版本…");
        await api.createVersion(draft.id, {
          audio_asset_key: media.asset_key,
          duration_ms: Number(form.get("durationMs") || 0) || null,
          metadata_json: { sha256: media.sha256, bytes: media.bytes, mime_type: media.mime_type },
        }, current.keys.version);
      }
      if (!resume?.stage || resume.stage !== "passport_ready") {
        setMessage("正在登记创作护照…");
        await api.upsertPassport(draft.id, {
          origin_type: form.get("sourceType"),
          generation_tool: form.get("aiTool"),
          generation_model: form.get("model"),
          prompt_disclosure: "private",
          human_editing_notes: form.get("humanEditing"),
          rights_statement: form.get("rightsStatement"),
        }, current.keys.passport);
      }
      setMessage("请确认发布内容…");
      setConfirm({
        title: String(form.get("title") || ""),
        fingerprint: media.sha256 ? media.sha256.slice(0, 12) : "unknown",
        rights: String(form.get("rightsStatement") || ""),
        trackId: draft.id,
      });
    } catch (error) {
      setMessage(`${error instanceof Error ? error.message : "发布失败"}。可直接重试，已完成的步骤不会重复执行。`);
    } finally {
      setBusy(false);
    }
  }

  async function confirmPublish() {
    if (!confirm || !attempt.current) return;
    setBusy(true);
    try {
      setMessage("正在发布…");
      await api.publish(confirm.trackId, attempt.current.keys.publish);
      setPublishedUrl(`${location.origin}/t/${confirm.trackId}`);
      setMessage("发布成功");
      attempt.current = null;
      clearAttempt();
      setConfirm(null);
    } catch (error) {
      setMessage(`${error instanceof Error ? error.message : "发布失败"}。已确认的步骤不会重复执行。`);
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
        <nav className="hero-buttons" aria-label="创作者中心">
          {me?.capabilities?.creator_writes && <Link className="glass" href="/drafts">草稿</Link>}
          {me?.capabilities?.creator_writes && <Link className="glass" href="/console">控制台</Link>}
          {me?.capabilities?.account_actions && <Link className="glass" href="/inbox">授权意向</Link>}
        </nav>
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
          <button className="primary" disabled={busy || !me?.capabilities?.creator_writes}>{busy ? "处理中…" : "下一步：确认发布"}</button>
        </form>
        {me && !me.capabilities?.creator_writes && <p className="result-note">只读模式：聆听保持开放。<Link href="/beta-login">受邀创作者登录 →</Link></p>}
        {confirm && (
          <section className="studio-card confirm-card">
            <span className="eyebrow">CONFIRM PUBLICATION</span>
            <h2>确认发布</h2>
            <p>标题：<strong>{confirm.title}</strong></p>
            <p>音频指纹（SHA-256 前 12 位）：<code>{confirm.fingerprint}</code></p>
            <p>来源声明：<em>{confirm.rights}</em></p>
            <p className="result-note">发布后公开地址：<code>{location.origin}/t/{confirm.trackId}</code></p>
            <p className="result-note">创作者自行提供来源信息；Moodify 不将其视为版权认证。</p>
            <div className="hero-buttons">
              <button className="primary" onClick={confirmPublish} disabled={busy}>确认发布</button>
              <button className="glass" onClick={() => setConfirm(null)} disabled={busy}>返回修改</button>
            </div>
          </section>
        )}
        <output aria-live="polite">{message}{publishedUrl && <span> → <a href={publishedUrl}>{publishedUrl}</a></span>}</output>
        <p className="result-note">创作者自行提供来源信息；Moodify 不将其视为版权认证。</p>
      </section>
    </main>
  );
}
