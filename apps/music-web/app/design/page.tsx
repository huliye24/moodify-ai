/* Moodify design system showcase — MFY_SHARED_DESIGN_SYSTEM_AND_SHELL_001.
   Storybook-equivalent gallery: every component in every documented state.
   This page is the visual evidence surface for the design system. */

"use client";

import { useState } from "react";
import { Button, Dialog, Field, Link, Select, TextArea, TextInput, Toast } from "../../components/ui/primitives";
import { EvidenceBadge, Panel, ProgressStepper, StateLabel, type ClaimMaturity, type SystemState } from "../../components/ui/status";
import { AudioTransport } from "../../components/ui/audio";
import { BrandMark, NavLink, PageShell, ProductSwitcher, type ProductEntry } from "../../components/ui/surfaces";
import { ChartFrame, DataTable, DefinitionList } from "../../components/ui/data";
import { EmptyState, ErrorState, RecoverySurface } from "../../components/ui/states";

const swatch: React.CSSProperties = {
  width: 96,
  height: 48,
  borderRadius: 8,
  display: "grid",
  placeItems: "center",
  fontSize: 10,
  color: "#05081e",
  fontWeight: 700,
};

const sectionTitle: React.CSSProperties = { margin: "40px 0 12px", fontSize: 20, fontWeight: 700, color: "var(--text)", borderBottom: "1px solid var(--line)", paddingBottom: 8 };

export default function DesignShowcase() {
  const [playing, setPlaying] = useState(false);
  const [position, setPosition] = useState(37);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [toastTone, setToastTone] = useState<"success" | "attention" | "error" | "info">("info");
  const [currentProduct, setCurrentProduct] = useState<ProductEntry>("music");

  return (
    <PageShell
      header={
        <>
          <BrandMark />
          <ProductSwitcher current={currentProduct} onNavigate={setCurrentProduct} />
        </>
      }
      footer={<>Moodify design tokens v1 — MFY_SHARED_DESIGN_SYSTEM_AND_SHELL_001. Token source: docs/design/design_tokens_v1.md</>}
    >
      <h1 style={{ fontSize: 32, fontWeight: 700, margin: "8px 0 4px" }}>Design System</h1>
      <p style={{ color: "var(--text-muted)", fontSize: 13 }}>Component gallery — every control accepts state; none derives business judgment.</p>

      <h2 style={sectionTitle}>Tokens</h2>
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
        <span style={{ ...swatch, background: "var(--bg)", border: "1px solid var(--line)", color: "var(--text-muted)" }}>bg</span>
        <span style={{ ...swatch, background: "var(--surface)", color: "var(--text-muted)" }}>surface</span>
        <span style={{ ...swatch, background: "var(--evidence)", color: "#05081e" }}>evidence</span>
        <span style={{ ...swatch, background: "var(--attention)", color: "#05081e" }}>attention</span>
        <span style={{ ...swatch, background: "var(--blocking)", color: "#05081e" }}>blocking</span>
        <span style={{ ...swatch, background: "var(--focus)", color: "#fff" }}>focus</span>
        <span style={{ ...swatch, background: "linear-gradient(100deg, var(--brand-violet), var(--brand-cyan))", color: "#fff" }}>brand</span>
      </div>

      <h2 style={sectionTitle}>Buttons / Links</h2>
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
        <Button variant="primary">Primary</Button>
        <Button variant="ghost">Ghost</Button>
        <Button variant="danger">Danger</Button>
        <Button variant="brand">Brand</Button>
        <Button variant="primary" disabled>Disabled</Button>
        <Button variant="primary" loading>Loading</Button>
        <Button variant="ghost" size="sm">Small ghost</Button>
        <Link href="/design">Default link</Link>
        <Link href="/design" variant="muted">Muted link</Link>
        <Link href="/design" variant="evidence">Evidence link</Link>
      </div>

      <h2 style={sectionTitle}>Fields</h2>
      <div style={{ display: "grid", gap: 16, maxWidth: 480 }}>
        <Field label="Track title" required hint="Public name of the work">
          <TextInput placeholder="Untitled work" />
        </Field>
        <Field label="Statement" error="Statement is required before publish">
          <TextArea placeholder="Describe the work…" />
        </Field>
        <Field label="Visibility">
          <Select defaultValue="published">
            <option value="draft">Draft</option>
            <option value="published">Published</option>
            <option value="unlisted">Unlisted</option>
          </Select>
        </Field>
      </div>

      <h2 style={sectionTitle}>State labels / maturity badges</h2>
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
        {(Object.keys({
          ready: "ready", processing: "processing", human_required: "human_required",
          inconclusive: "inconclusive", failed: "failed", offline: "offline",
        }) as SystemState[]).map((s) => (
          <StateLabel key={s} state={s} />
        ))}
      </div>
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: 12 }}>
        {(Object.keys({
          concept: "concept", experimental: "experimental", verified: "verified", human_reviewed: "human_reviewed",
        }) as ClaimMaturity[]).map((m) => (
          <EvidenceBadge key={m} maturity={m} scope={m === "verified" ? "MFY-WSE-SCAN-PROFILE-001" : undefined} />
        ))}
      </div>

      <h2 style={sectionTitle}>Progress stepper</h2>
      <ProgressStepper
        ariaLabel="Case progress"
        steps={[
          { label: "Listen", state: "done" },
          { label: "Represent", state: "done" },
          { label: "Judge", state: "human" },
          { label: "Intervene", state: "pending" },
          { label: "Verify", state: "pending" },
        ]}
      />

      <h2 style={sectionTitle}>Audio transport</h2>
      <Panel title="A/B/C comparison transport">
        <AudioTransport
          playing={playing}
          onToggle={() => setPlaying(!playing)}
          positionSeconds={position}
          durationSeconds={213}
          onSeek={setPosition}
          volume={0.6}
          onVolume={() => {}}
        />
      </Panel>

      <h2 style={sectionTitle}>Dialogs / Toasts</h2>
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
        <Button variant="ghost" onClick={() => setDialogOpen(true)}>Open dialog</Button>
        {(["success", "attention", "error", "info"] as const).map((tone) => (
          <Button key={tone} variant="ghost" onClick={() => setToastTone(tone)}>Toast {tone}</Button>
        ))}
      </div>
      <div style={{ display: "grid", gap: 10, marginTop: 16, maxWidth: 440 }}>
        <Toast tone={toastTone} message={toastTone === "attention" ? "Waiting for human review" : toastTone === "error" ? "Blocking failure — cannot verify" : "Toast message"} onDismiss={() => {}} />
      </div>

      <h2 style={sectionTitle}>Data display</h2>
      <DataTable
        columns={[
          { key: "metric", header: "Metric" },
          { key: "value", header: "Value", numeric: true },
          { key: "state", header: "State" },
        ]}
        rows={[
          { metric: "Short-term LUFS", value: "-14.2", state: <EvidenceBadge maturity="verified" /> },
          { metric: "True peak", value: "-1.3 dBTP", state: <EvidenceBadge maturity="verified" /> },
          { metric: "Spectral centroid", value: "2140 Hz", state: <StateLabel state="processing" /> },
        ]}
      />
      <div style={{ marginTop: 16 }}>
        <DefinitionList
          items={[
            { term: "Source hash", detail: "a3f9…e7c1 (SHA-256)" },
            { term: "Method", detail: "MFY-WSE-SCAN-PROFILE-001" },
            { term: "Authority", detail: <EvidenceBadge maturity="experimental" /> },
          ]}
        />
      </div>
      <div style={{ marginTop: 16 }}>
        <ChartFrame title="Before / after loudness" question="Did the candidate change the declared target?" note="Measured change, not perceptual preference">
          <div style={{ display: "flex", alignItems: "flex-end", gap: 8, height: 80 }}>
            <div style={{ width: 40, height: 40, background: "var(--text-muted)", borderRadius: 4 }} />
            <div style={{ width: 40, height: 62, background: "var(--evidence)", borderRadius: 4 }} />
          </div>
        </ChartFrame>
      </div>

      <h2 style={sectionTitle}>Empty / error / recovery</h2>
      <EmptyState title="No cases yet" hint="Introduce one sound to begin the first Production Case." action={<Button size="sm">Introduce a sound</Button>} />
      <div style={{ marginTop: 16 }}>
        <ErrorState title="Upload failed" detail="The server did not accept the media file." requestId="req-7f2a-91cd" onRetry={() => {}} />
      </div>
      <div style={{ marginTop: 16 }}>
        <RecoverySurface
          title="Publish interrupted"
          description="The publish request was lost. Read the authoritative track state before continuing."
          steps={[{ label: "Track state was read from the server", action: "resume" }, { label: "Replay with the same idempotency key" }]}
          requestId="req-c3b8-22de"
        />
      </div>

      <h2 style={sectionTitle}>Shell / navigation</h2>
      <div style={{ display: "flex", gap: 24 }}>
        <nav style={{ width: 200, display: "grid", gap: 4, alignContent: "start" }}>
          <NavLink href="/design" active>Discover</NavLink>
          <NavLink href="/design">Search</NavLink>
          <NavLink href="/design">Library</NavLink>
          <NavLink href="/design">Creator Studio</NavLink>
        </nav>
        <div style={{ display: "grid", gap: 8 }}>
          <BrandMark size="sm" />
          <BrandMark size="md" />
          <BrandMark size="lg" />
        </div>
      </div>
    </PageShell>
  );
}
