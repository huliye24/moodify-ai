"use client";

import { FormEvent, useState } from "react";

type Result = { track?: { id: string; publicUrl?: string }; error?: { message?: string } };

export default function StudioPage() {
  const [message, setMessage] = useState("先建立音乐馆，再发布第一首作品。");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true);
    const form = new FormData(event.currentTarget);
    try {
      setMessage("正在确认音乐馆…");
      let creator = await api("/api/v1/me/creator", { method: "GET" });
      if (!creator.creator) creator = await api("/api/v1/me/creator", { method: "POST", body: JSON.stringify({ handle: form.get("handle"), displayName: form.get("displayName"), bio: form.get("bio") }) });
      setMessage("正在创建作品草稿…");
      const passport = { sourceType: form.get("sourceType"), rightsStatement: form.get("rightsStatement"), promptDisclosure: "private", aiTool: form.get("aiTool"), humanEditing: form.get("humanEditing") };
      const draft = await api("/api/v1/tracks", { method: "POST", body: JSON.stringify({ title: form.get("title"), description: form.get("description"), language: form.get("language"), licenseStatus: form.get("licenseStatus"), ...passport }) }) as Result;
      const trackId = draft.track?.id; const file = form.get("audio") as File;
      if (!trackId || !file?.size) throw new Error("请选择音频文件");
      setMessage("正在计算音频指纹…");
      const hash = await crypto.subtle.digest("SHA-256", await file.arrayBuffer());
      const sha256 = [...new Uint8Array(hash)].map((value) => value.toString(16).padStart(2, "0")).join("");
      setMessage("正在安全上传音频…");
      await api(`/api/v1/tracks/${trackId}/audio`, { method: "PUT", body: file, headers: { "content-type": file.type || "audio/wav", "x-filename": file.name, "x-content-sha256": sha256, "x-passport": encodeURIComponent(JSON.stringify(passport)) } });
      setMessage("正在发布…");
      const published = await api(`/api/v1/tracks/${trackId}/publish`, { method: "POST" }) as Result;
      setMessage(`发布成功：${location.origin}${published.track?.publicUrl}`);
    } catch (error) { setMessage(error instanceof Error ? error.message : "发布失败，草稿已保留"); }
    finally { setBusy(false); }
  }

  return <main className="studio-shell"><a href="/">← 返回聆听</a><section className="studio-card"><span className="eyebrow">CREATOR STUDIO</span><h1>发布作品</h1><p>封面可选。没有封面时，作品使用统一的 Moodify 黑胶视觉。</p><form onSubmit={submit}>
    <fieldset><legend>音乐馆</legend><input name="handle" required minLength={3} maxLength={32} placeholder="唯一 handle，如 cadeau10"/><input name="displayName" required maxLength={80} placeholder="创作者名称"/><textarea name="bio" maxLength={500} placeholder="一句简介（可选）"/></fieldset>
    <fieldset><legend>作品</legend><input name="title" required maxLength={160} placeholder="作品标题"/><textarea name="description" maxLength={2000} placeholder="作品简介（可选）"/><input name="language" maxLength={16} placeholder="语言，如 fr"/><input name="audio" type="file" accept="audio/wav,audio/mpeg,audio/flac,audio/mp4,audio/ogg,audio/aac" required/></fieldset>
    <fieldset><legend>创作护照</legend><select name="sourceType" defaultValue="hybrid"><option value="ai">AI</option><option value="human">Human</option><option value="hybrid">Hybrid</option></select><input name="aiTool" maxLength={200} placeholder="使用工具（可选）"/><textarea name="humanEditing" maxLength={2000} placeholder="人工修改（可选）"/><textarea name="rightsStatement" required maxLength={2000} placeholder="权利声明（必填）"/><select name="licenseStatus" defaultValue="not_available"><option value="not_available">暂不授权</option><option value="inquiry">可询价授权</option></select></fieldset>
    <button className="primary" disabled={busy}>{busy ? "处理中…" : "发布作品"}</button>
  </form><output aria-live="polite">{message}</output></section></main>;
}

async function api(url: string, init: RequestInit) {
  const response = await fetch(url, { ...init, headers: { "content-type": "application/json", ...init.headers } });
  const body = await response.json() as Result & Record<string, unknown>;
  if (response.status === 401) {
    location.assign(`/signin-with-chatgpt?return_to=${encodeURIComponent("/studio")}`);
    throw new Error("正在前往登录…");
  }
  if (!response.ok) throw new Error(body.error?.message ?? `请求失败 (${response.status})`);
  return body;
}
