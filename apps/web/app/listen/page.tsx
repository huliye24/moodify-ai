"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { EmptyState } from "../../components/ui/states";
import { AudioTransport } from "../../components/ui/audio";

// Listen — Public Form §4 公共证明原则:
//   Original -> Listen   与   Moodify -> Listen
// 用户先听,再决定 Moodify 是否有价值。
// 本页不展示 LUFS / 频段 / 评分等 Tier C 工程字段(宪法 §9):
// 若去掉品牌故事、界面、参数、技术报告和功能列表,
// 只剩声音本身,Moodify 仍然应该值得使用。

type Side = "original" | "moodify";

interface Comparison {
  id: string;
  title: string;
  artist: string;
  caption: string;
  original: { src: string; label: string } | null;
  moodify: { src: string; label: string } | null;
}

// 在听之前先告诉用户:这一页是做什么的。
// 公共证明顺序 §11: Belief -> Sound -> Play -> Proof
// /listen 落在 Sound 这一段。
function BeliefHeader() {
  return (
    <header style={{ display: "grid", gap: "var(--space-4)", paddingBlock: "var(--space-12) var(--space-8)" }}>
      <span style={{ fontSize: "var(--text-xs)", letterSpacing: "0.18em", color: "var(--text-faint)", textTransform: "uppercase" }}>
        Public Form · §11 Sound
      </span>
      <h1 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "var(--text-4xl)", lineHeight: "var(--leading-tight)", letterSpacing: "-0.01em", color: "var(--text)" }}>
        Listen.
      </h1>
      <p style={{ margin: 0, fontSize: "var(--text-lg)", color: "var(--text-muted)", maxWidth: "44ch", lineHeight: "var(--leading-normal)" }}>
        Moodify 不是一个分析仪表盘。它先把声音听完,再让你听一次。
        这里放的是同一段音乐,先原声,再 Moodify。
      </p>
      <p style={{ margin: 0, fontSize: "var(--text-md)", color: "var(--text-faint)", maxWidth: "44ch", lineHeight: "var(--leading-normal)" }}>
        每一种声音,都值得被世界听见。<span style={{ marginLeft: "var(--space-2)", color: "var(--text-muted)" }}>Every voice deserves to be heard.</span>
      </p>
    </header>
  );
}

function BeforeAfterPlayer({ comparison }: { comparison: Comparison }) {
  const [active, setActive] = useState<Side>("original");
  const [playing, setPlaying] = useState(false);
  const [position, setPosition] = useState(0);
  const [duration, setDuration] = useState(0);
  const ref = useRef<HTMLAudioElement>(null);

  const source = active === "original" ? comparison.original : comparison.moodify;

  useEffect(() => {
    const audio = ref.current;
    if (!audio) return;
    audio.pause();
    setPosition(0);
    setDuration(0);
    if (playing && source) {
      void audio.play().catch(() => setPlaying(false));
    }
  }, [active, source?.src]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <article
      aria-label={`${comparison.title} 对比`}
      style={{
        border: "1px solid var(--line)",
        borderRadius: "var(--radius-lg)",
        background: "var(--surface-subtle)",
        padding: "var(--space-6)",
        display: "grid",
        gap: "var(--space-6)",
      }}
    >
      <header style={{ display: "grid", gap: "var(--space-2)" }}>
        <span style={{ fontSize: "var(--text-xs)", letterSpacing: "0.18em", color: "var(--text-faint)", textTransform: "uppercase" }}>
          Comparison
        </span>
        <h2 style={{ margin: 0, fontFamily: "var(--font-display)", fontSize: "var(--text-2xl)", color: "var(--text)" }}>
          {comparison.title}
        </h2>
        <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "var(--text-md)" }}>{comparison.artist}</p>
      </header>

      <div role="tablist" aria-label="选择声道" style={{ display: "inline-flex", gap: "var(--space-1)", padding: 3, background: "var(--surface)", borderRadius: "var(--radius-pill)", border: "1px solid var(--line)", width: "fit-content" }}>
        {(["original", "moodify"] as const).map((side) => {
          const isActive = active === side;
          const available = side === "original" ? comparison.original : comparison.moodify;
          return (
            <button
              key={side}
              role="tab"
              type="button"
              aria-selected={isActive}
              aria-controls={`player-${comparison.id}`}
              disabled={!available}
              onClick={() => setActive(side)}
              style={{
                padding: "var(--space-1) var(--space-4)",
                borderRadius: "var(--radius-pill)",
                border: 0,
                background: isActive ? "var(--surface-subtle)" : "transparent",
                color: isActive ? "var(--text)" : "var(--text-muted)",
                fontSize: "var(--text-sm)",
                fontWeight: isActive ? 600 : 400,
                cursor: available ? "pointer" : "not-allowed",
                opacity: available ? 1 : 0.4,
              }}
            >
              {side === "original" ? "Original" : "Moodify"}
            </button>
          );
        })}
      </div>

      <div id={`player-${comparison.id}`} role="tabpanel" aria-label={`${active === "original" ? "原声" : "Moodify 处理后"}`}>
        {source ? (
          <>
            <AudioTransport
              playing={playing}
              onToggle={() => setPlaying((value) => !value)}
              positionSeconds={position}
              durationSeconds={duration}
              onSeek={(seconds) => {
                if (ref.current) ref.current.currentTime = seconds;
                setPosition(seconds);
              }}
              labels={{
                play: `播放 ${active === "original" ? "原声" : "Moodify 处理后"}`,
                pause: `暂停 ${active === "original" ? "原声" : "Moodify 处理后"}`,
                position: "播放进度",
              }}
            />
            <audio
              ref={ref}
              src={source.src}
              preload="metadata"
              onLoadedMetadata={(event) => setDuration(event.currentTarget.duration)}
              onTimeUpdate={(event) => setPosition(event.currentTarget.currentTime)}
              onEnded={() => setPlaying(false)}
              style={{ display: "none" }}
            />
          </>
        ) : (
          <EmptyState
            title="对比素材正在准备"
            hint={`「${active === "original" ? "原声" : "Moodify 处理后"}」对应的公开音频尚未就绪。Moodify 不在没有真实素材时伪造结果——这一份对比会在证据就位后开放。`}
            action={
              <Link
                href="/evidence"
                style={{
                  display: "inline-block",
                  padding: "var(--space-1) var(--space-4)",
                  border: "1px solid var(--line)",
                  borderRadius: "var(--radius-pill)",
                  color: "var(--text)",
                  fontSize: "var(--text-sm)",
                  textDecoration: "none",
                }}
              >
                查看已有证据 →
              </Link>
            }
          />
        )}
      </div>

      <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "var(--text-md)", lineHeight: "var(--leading-normal)" }}>
        {comparison.caption}
      </p>
    </article>
  );
}

export default function ListenPage() {
  // Public Form §4 公共证明原则: Original -> Listen  与  Moodify -> Listen
  // 用户先听,再决定 Moodify 是否有价值。
  // §13 Test C(听觉可证):任一 src 缺失,EmptyState 诚实回退,
  // 不在没有真实素材时伪造"播放成功"。
  // 真实 src 来自 apps/web/assets/cadeau10-album1.json
  // (Original) 与 apps/web/assets/cadeau10-album1-moodify.json
  // (Moodify 处理后)。两份 manifest 与 LA 主媒体根共享同一公开 URL 前缀,
  // 见 ops/web_origin/PRODUCTION_TOPOLOGY.md §21。
  const audioBaseUrl =
    (process.env.NEXT_PUBLIC_AUDIO_BASE_URL ?? "https://play.rongjingmusic.com/audio").replace(/\/$/, "");

  // Production-readiness 探针(不展示给用户):
  //   对 10 个 src 各发 HEAD,若任一首 moodify-* 404,
  //   说明 ops 还没部署 Listen Demo v0.1 音频二进制,
  //   本页 UI 已通过 EmptyState 兜底诚实回退(§13 Test C)。
  //   警告只在浏览器 devtools console 输出,不破坏用户路径。
  //   文件名与 apps/web/assets/cadeau10-album1.json 同步;
  //   这里是离线硬编码,避免 useEffect 引用后续声明的 comparisons。
  useEffect(() => {
    if (typeof window === "undefined") return;
    const fileNames = [
      "je-ne-veux-pas-enfermer-ton-aujourdhui.wav",
      "ne-vivons-pas-seulement-de-souvenirs.wav",
      "nous-pouvons-nous-reconnaitre-encore.wav",
      "ou-es-tu-maintenant.wav",
      "vieillir-et-devenir-nouveau-avec-toi.wav",
    ];
    const urls: string[] = [];
    for (const name of fileNames) {
      urls.push(`${audioBaseUrl}/cadeau10-album1/${name}`);
      urls.push(`${audioBaseUrl}/cadeau10-album1-moodify/${name}`);
    }
    const probe = async () => {
      const missing: string[] = [];
      await Promise.all(
        urls.map(async (url) => {
          try {
            const res = await fetch(url, { method: "HEAD" });
            if (!res.ok) missing.push(url);
          } catch {
            missing.push(url);
          }
        }),
      );
      if (missing.length > 0) {
        // eslint-disable-next-line no-console
        console.warn(
          "[listen-demo] missing audio origins (UI will fall back to EmptyState per §13 Test C):",
          missing,
        );
      } else {
        // eslint-disable-next-line no-console
        console.info("[listen-demo] all 10 audio origins reachable.");
      }
    };
    void probe();
  }, [audioBaseUrl]);

  const comparisons: Comparison[] = useMemo(
    () => [
      {
        id: "track-001",
        title: "Je ne veux pas enfermer ton aujourd'hui",
        artist: "Cadeau10 · 专辑 1",
        caption:
          "Moodify listens before you do. Original 是艺术家提交的原声;Moodify 是 Moodify 理解之后的版本。先听后判断。",
        original: {
          src: `${audioBaseUrl}/cadeau10-album1/je-ne-veux-pas-enfermer-ton-aujourdhui.wav`,
          label: "Original",
        },
        moodify: {
          src: `${audioBaseUrl}/cadeau10-album1-moodify/je-ne-veux-pas-enfermer-ton-aujourdhui.wav`,
          label: "Moodify",
        },
      },
      {
        id: "track-002",
        title: "Ne vivons pas seulement de souvenirs",
        artist: "Cadeau10 · 专辑 1",
        caption:
          "Same song. First as it was. Then as Moodify hears it.",
        original: {
          src: `${audioBaseUrl}/cadeau10-album1/ne-vivons-pas-seulement-de-souvenirs.wav`,
          label: "Original",
        },
        moodify: {
          src: `${audioBaseUrl}/cadeau10-album1-moodify/ne-vivons-pas-seulement-de-souvenirs.wav`,
          label: "Moodify",
        },
      },
      {
        id: "track-003",
        title: "Nous pouvons nous reconnaître encore",
        artist: "Cadeau10 · 专辑 1",
        caption:
          "同源、同时长。区别是 Moodify 在你按 Play 之前先听了一次。",
        original: {
          src: `${audioBaseUrl}/cadeau10-album1/nous-pouvons-nous-reconnaitre-encore.wav`,
          label: "Original",
        },
        moodify: {
          src: `${audioBaseUrl}/cadeau10-album1-moodify/nous-pouvons-nous-reconnaitre-encore.wav`,
          label: "Moodify",
        },
      },
      {
        id: "track-004",
        title: "Où es-tu maintenant",
        artist: "Cadeau10 · 专辑 1",
        caption:
          "如果你听不出区别,这是 Moodify 没有做好。Press Play。",
        original: {
          src: `${audioBaseUrl}/cadeau10-album1/ou-es-tu-maintenant.wav`,
          label: "Original",
        },
        moodify: {
          src: `${audioBaseUrl}/cadeau10-album1-moodify/ou-es-tu-maintenant.wav`,
          label: "Moodify",
        },
      },
      {
        id: "track-005",
        title: "Vieillir et devenir nouveau avec toi",
        artist: "Cadeau10 · 专辑 1",
        caption:
          "每一种声音,都值得被世界听见。这一首听过之后,你怎么决定?",
        original: {
          src: `${audioBaseUrl}/cadeau10-album1/vieillir-et-devenir-nouveau-avec-toi.wav`,
          label: "Original",
        },
        moodify: {
          src: `${audioBaseUrl}/cadeau10-album1-moodify/vieillir-et-devenir-nouveau-avec-toi.wav`,
          label: "Moodify",
        },
      },
    ],
    [audioBaseUrl],
  );

  return (
    <main
      style={{
        minHeight: "100vh",
        background: "radial-gradient(circle at 70% 12%, rgba(36,66,154,.17), transparent 27%), linear-gradient(135deg, #070a22, #040719 70%)",
        padding: "0 clamp(20px, 4vw, 64px) var(--space-12)",
      }}
    >
      <nav aria-label="位置" style={{ paddingBlock: "var(--space-6)", color: "var(--text-faint)", fontSize: "var(--text-sm)" }}>
        <Link href="/" style={{ color: "inherit", textDecoration: "none" }}>← 返回 Moodify</Link>
      </nav>

      <BeliefHeader />

      <section aria-label="对比" style={{ display: "grid", gap: "var(--space-8)", maxWidth: 720 }}>
        {comparisons.map((comparison) => (
          <BeforeAfterPlayer key={comparison.id} comparison={comparison} />
        ))}
      </section>

      <footer style={{ marginTop: "var(--space-12)", paddingTop: "var(--space-8)", borderTop: "1px solid var(--line)", color: "var(--text-faint)", fontSize: "var(--text-sm)", maxWidth: 720 }}>
        <p style={{ margin: 0, lineHeight: "var(--leading-normal)" }}>
          想要听到证据而不是承诺?看 <Link href="/evidence" style={{ color: "var(--text-muted)" }}>Evidence</Link>。
        </p>
      </footer>
    </main>
  );
}
