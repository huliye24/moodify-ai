# Moodify Official Website Blueprint

**Document ID:** MFY-OFFICIAL-WEBSITE-BLUEPRINT-001  
**Version:** 1.0  
**Date:** 2026-08-14  
**Status:** HISTORICAL WEBSITE BASELINE — superseded by Public Brand v0.1

**Product role:** Public brand and product-family entrance

**Approval record:** approved 2026-08-14 by human product authority (huliye24) as Phase 1 baseline, no modification; see DECISION_LOG D-003 and GOVERNANCE_RECONCILIATION_REPORT.

> **SUPERSEDED — `docs/canon/*` and `docs/brand/public/*` govern the current website identity, language and three-site roles. The current public product is Moodify Music / Player; Ear is internal. This document is retained as the 2026-08-14 historical baseline and must not drive current public pages.**

## 1. Website mission

The official website must make one idea clear:

> **AI can generate sound. Moodify asks whether it can hear.**

The site introduces Moodify as **The Ear of AI**, explains the difference between generation and auditory intelligence, presents Moodify Ear and Moodify Music as distinct products, and demonstrates credibility without overstating experimental results.

The website is not a feature catalogue, an Ear workstation, or a Music feed.

## 2. Primary audiences

### 2.1 AI and audio builders

They need to understand the auditory intelligence problem, system loop, evidence model, and integration direction.

Primary destination: **Moodify Ear**.

### 2.2 Producers, researchers, and critical listeners

They need to see how Moodify measures, judges, verifies, exposes uncertainty, and preserves listening authority.

Primary destination: **Moodify Ear / Evidence**.

### 2.3 Listeners and creators

They need to understand Moodify Music as a place for works, creators, provenance, and listening—not as an engineering dashboard.

Primary destination: **Moodify Music**.

### 2.4 Partners and institutions

They need a credible statement of mission, boundaries, maturity, research assets, and contact path.

Primary destination: **Evidence / About**.

## 3. Communication hierarchy

The website should communicate in this order:

1. Moodify is The Ear of AI.
2. Generating audio and hearing audio are different capabilities.
3. Moodify turns listening into an inspectable learning loop.
4. Moodify Ear develops auditory intelligence.
5. Moodify Music brings that philosophy into a real music environment.
6. Claims are supported by evidence and qualified by maturity.

Technical architecture must appear only after the visitor understands the product category.

## 4. Site map

```text
/
├── /ear
├── /music
├── /evidence
├── /about
└── /contact
```

Optional later additions:

```text
/research
/journal
/developers
/status
```

These should not launch until there is enough maintained content to justify them.

## 5. Homepage blueprint

### 5.1 Global navigation

Left: Moodify wordmark.  
Center/right: Ear, Music, Evidence, About.  
Primary action: **Enter Moodify Ear** or a neutral **Explore Moodify**, depending on readiness.  
Secondary action: **Listen on Moodify Music**.

Avoid crowded product menus and premature developer navigation.

### 5.2 Hero

**Eyebrow:** MOODIFY  
**Headline:** THE EAR OF AI  
**Supporting line:** An auditory intelligence system that helps machines listen, represent, judge, intervene, verify, and learn from sound.  
**Chinese supporting line:** 让机器不只会生成声音，也真正学会听。

Primary action: **Explore Moodify Ear**  
Secondary action: **Discover Moodify Music**

Visual direction: one restrained auditory field or waveform-derived evidence object. It must suggest listening and state, not decorative music visualization.

### 5.3 Problem statement

Headline:

> Generation is not hearing.

Content should explain that a generative model may produce audio without reliably answering:

- What happened in the waveform, spectrum, dynamics, phase, or structure?
- What is measurable and what remains uncertain?
- If a change was made, did it achieve the intended result?
- Can evidence from this case improve the next one?

### 5.4 Canonical loop

Present the six stages as one continuous instrument state:

```text
Listen -> Represent -> Judge -> Intervene -> Verify -> Learn
```

Each stage receives one short sentence. Do not turn this section into six unrelated marketing cards.

### 5.5 Product pair

#### Moodify Ear

**Promise:** auditory judgment with traceable evidence.  
**Shows:** source, representation, judgment, intervention, verification, learning.  
**CTA:** Explore Ear.

#### Moodify Music

**Promise:** a listening environment centered on works, creators, and provenance.  
**Shows:** discover, listen, collect, follow, publish, connect.  
**CTA:** Enter Music.

The two products should feel related but not visually interchangeable.

### 5.6 Evidence section

Show a small number of real, publish-safe evidence objects:

- a versioned measurement record;
- a before/after comparison with a clearly stated question;
- a reproducibility or benchmark result;
- a case whose uncertainty or failure is visible.

Each item must include:

- claim;
- method/version;
- authority state: experimental, verified, or human-reviewed;
- limitation;
- date.

Do not publish internal file paths, private audio, prompts, or unreviewed judgment logs.

### 5.7 Philosophy / disciplines

Briefly introduce:

- **WSE:** what happened in the sound?
- **MSE:** what is the musical structure?
- **PPE:** how is the result produced, verified, and recovered reliably?

This section signals depth without making the homepage read like a paper.

### 5.8 Closing statement

Suggested closing:

> The future of audio intelligence is not only better generation. It is better hearing.

Repeat the two product actions without introducing new claims.

### 5.9 Footer

Include product links, evidence, contact, legal/privacy, repository or research link if public, and status only when maintained.

## 6. Product landing pages

### 6.1 `/ear`

Order:

1. Ear definition and target users.
2. The six-stage loop.
3. A single end-to-end Production Case.
4. Evidence and authority model.
5. Auditory Intervention Laboratory as a subsystem.
6. Current capability and honest limitations.
7. Entry or access request.

The page must not lead with DSP effects, mastering language, or aggregate quality scores.

### 6.2 `/music`

Order:

1. Music definition for listeners and creators.
2. Discovery and listening experience.
3. Work, version, and creator relationships.
4. Creation Passport with an explicit non-certification statement.
5. Creator publishing journey.
6. Current capability and honest limitations.
7. Enter Music.

The page must not expose private Ear evidence or treat experimental metrics as music ranking.

### 6.3 `/evidence`

Organize by questions and cases, not by a pile of charts.

Suggested filters:

- WSE / MSE / PPE;
- experimental / verified / human-reviewed;
- measurement / comparison / benchmark / failure case;
- method version.

Each evidence page should be reproducible from a stable reference where public release permits it.

### 6.4 `/about`

Explain the founding question, product thesis, disciplines, learning loop, product boundaries, and the commitment to evidence and human authority. Keep biographies and institutional material subordinate to the mission.

## 7. Visual system

### 7.1 Character

- quiet authority;
- technical precision without intimidation;
- low fatigue;
- durable rather than fashionable;
- recognizable without relying on the logo.

### 7.2 Palette

- graphite field rather than pure black;
- mineral white for primary text;
- muted gray for hierarchy;
- one desaturated mineral green for active evidence or progress;
- amber only for required human attention;
- red only for blocking failure.

### 7.3 Typography and layout

- modest font weights and generous line height;
- tabular numerals for evidence;
- decisive alignment and substantial negative space;
- 8/12/16 px radius system;
- pills reserved for compact states;
- hierarchy from spacing, luminance, and hairline boundaries rather than shadows.

### 7.4 Motion

Motion should indicate state transition or reveal detail. No bounce, ornamental loops, reactive particle field, or autoplay sound. Respect reduced-motion preferences.

## 8. Content and claim governance

Every public claim must have one of these states:

| State | Meaning | Public treatment |
|---|---|---|
| Concept | Product or research direction | Clearly framed as intent |
| Experimental | Observed in limited tests | Method and limitation required |
| Verified | Passed declared verification | Verification scope required |
| Human-reviewed | Reviewed by designated human authority | Review date and scope required |

Forbidden public claims include:

- universal sound quality;
- guaranteed improvement;
- copyright ownership certification;
- scientific validation without defined method and evidence;
- algorithmic superiority inferred from one case;
- a roadmap item presented as available functionality.

## 9. Conversion model

The site should optimize for qualified entry, not generic engagement.

Primary conversions:

- enter or request access to Ear;
- enter Music as a listener;
- begin creator onboarding;
- inspect evidence;
- contact Moodify for a relevant partnership.

Avoid popularity counters, artificial urgency, and email capture without a clear benefit.

## 10. Accessibility, performance, and trust gates

Before launch:

- keyboard navigation works end to end;
- semantic heading and landmark order is valid;
- contrast and focus states are verified;
- all meaningful visuals have accessible alternatives;
- autoplay audio is prohibited;
- reduced motion is respected;
- mobile reading and actions are complete;
- first content remains useful if animation or WebGL fails;
- privacy and analytics behavior are disclosed;
- every product capability shown exists at the stated maturity.

## 11. Initial deliverable boundary

The first website release needs only:

- homepage;
- Ear landing page;
- Music landing page;
- evidence index with a small curated set;
- about/contact and legal basics;
- shared responsive design system.

It does not need a CMS, blog, complex animation system, personalization, public API portal, or multilingual expansion before the core narrative is coherent.

## 12. Acceptance questions

The official website is ready for implementation only when a reviewer can answer yes to all:

- Can a new visitor explain Moodify in one sentence?
- Is the difference between Ear and Music unmistakable?
- Does every important claim show its maturity honestly?
- Is the auditory loop more memorable than any individual feature?
- Does the site avoid presenting Moodify as mastering software or a generic music platform?
- Are the next actions appropriate to product readiness?
- Would the site remain credible without decorative effects?
