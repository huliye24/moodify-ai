import Link from "next/link";
import {
  PortalShell,
  StatusBadge,
  SectionHeading,
  ComingSoonModule,
} from "@/components/ui/portal-shell";

export const metadata = {
  title: "MOOD World — An Open Web3 World",
  description:
    "MOOD is an open digital world built by people and AI. Explore the manifesto, mission, and how to enter.",
};

const MANIFESTO_LINES = [
  "A free spirit does not wait for permission.",
  "A digital world should belong to its builders.",
  "We believe identity is earned through contribution,",
  "not allocated by a founding team.",
  "We believe reputation is verified by the network,",
  "not declared in a whitepaper.",
  "We believe the world we want",
  "is built by the people inside it.",
];

const WORLD_SECTIONS = [
  {
    id: "manifesto",
    icon: "✦",
    title: "Manifesto",
    description:
      "The beliefs that shape every decision in MOOD — from governance to protocol design.",
    href: "#manifesto",
  },
  {
    id: "listen",
    icon: "◉",
    title: "Listening",
    description:
      "Sound is how we think. Moodify, the Genesis Application, is proof that this world can produce things worth hearing.",
    href: "#listen",
  },
  {
    id: "create",
    icon: "◈",
    title: "Creation",
    description:
      "Every contributor leaves a trace. The protocol records what you build, not who you know.",
    href: "#create",
  },
  {
    id: "community",
    icon: "◐",
    title: "Community",
    description:
      "Residents, not consumers. The people who build this world define its character.",
    href: "#community",
  },
  {
    id: "moodify",
    icon: "◑",
    title: "Moodify Gate",
    description:
      "Enter through the Genesis Application. Moodify is where the protocol becomes real.",
    href: "/",
  },
];

export default function WorldPage() {
  return (
    <PortalShell activeArea="world">
      {/* Hero */}
      <section style={{ textAlign: "center", padding: "var(--space-12) 0 var(--space-12)" }}>
        <StatusBadge status="Foundation" since="Package 013" />
        <h1
          style={{
            margin: "var(--space-6) auto",
            fontSize: "clamp(32px, 6vw, 64px)",
            fontWeight: 700,
            lineHeight: "var(--leading-tight)",
            fontFamily: "var(--font-display)",
            maxWidth: 760,
            color: "var(--text)",
          }}
        >
          MOOD
          <br />
          <span
            style={{
              fontSize: "clamp(16px, 2.5vw, 24px)",
              fontWeight: 400,
              color: "var(--text-muted)",
              letterSpacing: "0.02em",
            }}
          >
            A Digital Home for Free Spirits
          </span>
        </h1>
        <p
          style={{
            margin: "0 auto var(--space-8)",
            color: "var(--text-muted)",
            fontSize: "var(--text-lg)",
            maxWidth: 520,
            lineHeight: "var(--leading-normal)",
          }}
        >
          在这里，成为你自己。
        </p>
        <div style={{ display: "flex", gap: "var(--space-3)", justifyContent: "center", flexWrap: "wrap" }}>
          <Link
            href="/protocol"
            style={{
              display: "inline-flex",
              alignItems: "center",
              padding: "var(--space-3) var(--space-6)",
              borderRadius: "var(--radius-pill)",
              background: "linear-gradient(100deg, var(--brand-violet), var(--brand-cyan))",
              color: "var(--on-accent)",
              textDecoration: "none",
              fontWeight: 600,
              fontSize: "var(--text-md)",
            }}
          >
            Explore Protocol →
          </Link>
          <Link
            href="/portal"
            style={{
              display: "inline-flex",
              alignItems: "center",
              padding: "var(--space-3) var(--space-6)",
              borderRadius: "var(--radius-pill)",
              background: "var(--surface-subtle)",
              border: "1px solid var(--line)",
              color: "var(--text)",
              textDecoration: "none",
              fontWeight: 600,
              fontSize: "var(--text-md)",
            }}
          >
            Enter Portal
          </Link>
        </div>
      </section>

      {/* Spatial Divider */}
      <div
        aria-hidden
        style={{
          height: 1,
          background:
            "linear-gradient(to right, transparent, var(--line), transparent)",
          margin: "var(--space-8) 0",
        }}
      />

      {/* World Sections Grid */}
      <section aria-label="MOOD World sections">
        <SectionHeading
          eyebrow="MOOD WORLD"
          title="Explore the World"
          description="MOOD is more than pages, apps, or a token. It is an open space shaped by belief, protocol, identity, and real contribution."
        />
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: "var(--space-4)",
          }}
        >
          {WORLD_SECTIONS.map((section) => (
            <a
              key={section.id}
              href={section.href}
              style={{
                display: "block",
                padding: "var(--space-6)",
                border: "1px solid var(--line)",
                borderRadius: "var(--radius-md)",
                background: "var(--surface-subtle)",
                textDecoration: "none",
                color: "inherit",
                transition: "border-color var(--duration-fast), background var(--duration-fast)",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = "var(--brand-violet)";
                e.currentTarget.style.background = "rgba(108, 72, 255, 0.05)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = "var(--line)";
                e.currentTarget.style.background = "var(--surface-subtle)";
              }}
            >
              <span
                aria-hidden
                style={{
                  display: "block",
                  fontSize: "var(--text-2xl)",
                  marginBottom: "var(--space-3)",
                  color: "var(--brand-cyan)",
                }}
              >
                {section.icon}
              </span>
              <h3
                style={{
                  margin: "0 0 var(--space-2)",
                  fontSize: "var(--text-xl)",
                  fontWeight: 600,
                  color: "var(--text)",
                }}
              >
                {section.title}
              </h3>
              <p
                style={{
                  margin: 0,
                  color: "var(--text-muted)",
                  fontSize: "var(--text-md)",
                  lineHeight: "var(--leading-normal)",
                }}
              >
                {section.description}
              </p>
            </a>
          ))}
        </div>
      </section>

      {/* Manifesto */}
      <section
        id="manifesto"
        aria-label="MOOD Manifesto"
        style={{
          marginTop: "var(--space-12)",
          padding: "var(--space-8)",
          border: "1px solid var(--line)",
          borderRadius: "var(--radius-lg)",
          background: "var(--surface-subtle)",
          textAlign: "center",
        }}
      >
        <p
          style={{
            margin: "0 0 var(--space-4)",
            fontSize: "var(--text-xs)",
            fontWeight: 700,
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            color: "var(--text-muted)",
          }}
        >
          Manifesto
        </p>
        <blockquote
          style={{
            margin: "0 auto",
            maxWidth: 600,
            fontFamily: "var(--font-display)",
            fontSize: "clamp(18px, 2.5vw, 24px)",
            lineHeight: "var(--leading-loose)",
            color: "var(--text)",
            fontStyle: "italic",
          }}
        >
          {MANIFESTO_LINES.map((line, i) => (
            <span key={i}>
              {line}
              <br />
            </span>
          ))}
        </blockquote>
      </section>

      {/* Listening section */}
      <section
        id="listen"
        aria-label="Listening — Moodify Genesis Application"
        style={{
          marginTop: "var(--space-12)",
        }}
      >
        <SectionHeading
          eyebrow="GENESIS APPLICATION"
          title="Moodify — Where the Protocol Becomes Real"
          description="Moodify is the first application built inside MOOD. It proves that this world can produce something worth listening to."
          action={
            <Link
              href="/"
              style={{
                padding: "var(--space-2) var(--space-4)",
                borderRadius: "var(--radius-pill)",
                border: "1px solid var(--line)",
                color: "var(--text-muted)",
                textDecoration: "none",
                fontSize: "var(--text-sm)",
              }}
            >
              Open Moodify →
            </Link>
          }
        />
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
            gap: "var(--space-4)",
          }}
        >
          <div
            style={{
              padding: "var(--space-6)",
              border: "1px solid var(--line)",
              borderRadius: "var(--radius-md)",
              background: "var(--surface-subtle)",
            }}
          >
            <h3 style={{ margin: "0 0 var(--space-2)", fontSize: "var(--text-lg)", fontWeight: 600 }}>
              Just Play
            </h3>
            <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "var(--text-md)" }}>
              Moodify is built around a single action: Play. Everything else serves the music.
            </p>
          </div>
          <div
            style={{
              padding: "var(--space-6)",
              border: "1px solid var(--line)",
              borderRadius: "var(--radius-md)",
              background: "var(--surface-subtle)",
            }}
          >
            <h3 style={{ margin: "0 0 var(--space-2)", fontSize: "var(--text-lg)", fontWeight: 600 }}>
              Genesis Application
            </h3>
            <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "var(--text-md)" }}>
              Moodify exists to prove the protocol. Every track played is evidence that MOOD can produce real value.
            </p>
          </div>
          <div
            style={{
              padding: "var(--space-6)",
              border: "1px solid var(--line)",
              borderRadius: "var(--radius-md)",
              background: "var(--surface-subtle)",
            }}
          >
            <h3 style={{ margin: "0 0 var(--space-2)", fontSize: "var(--text-lg)", fontWeight: 600 }}>
              Evidence Loop
            </h3>
            <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "var(--text-md)" }}>
              Moodify contributes listening data back to the network. What you hear shapes the world.
            </p>
          </div>
        </div>
      </section>

      {/* Coming next placeholders */}
      <section
        aria-label="Coming next in MOOD World"
        style={{
          marginTop: "var(--space-12)",
        }}
      >
        <SectionHeading
          eyebrow="COMING NEXT"
          title="What's Still Being Built"
          description="These areas are planned. They do not yet exist — no metrics, no residents, no TVL."
        />
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: "var(--space-4)",
          }}
        >
          <ComingSoonModule
            package="Package 015"
            label="MOOD Passport"
            description="A persistent identity layer tied to your wallet — not your token balance."
          />
          <ComingSoonModule
            package="Package 016"
            label="Contribution Network"
            description="Task, submission, review — a verifiable record of what builders contribute."
          />
          <ComingSoonModule
            package="Package 017"
            label="Network Observatory"
            description="Real network status and metrics, not fabricated dashboard numbers."
          />
        </div>
      </section>
    </PortalShell>
  );
}
