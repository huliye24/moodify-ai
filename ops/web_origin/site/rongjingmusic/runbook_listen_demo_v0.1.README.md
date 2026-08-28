# Listen Demo v0.1 — Ops Runbook

`runbook_listen_demo_v0.1.sh` is the operational runbook for deploying Listen Demo v0.1 to `rongjingmusic.com`.

This runbook is **not** a continuous loop or background process.
It is an **end-to-end playbook** that an ops operator runs once when shipping the first public Listen Demo.

The script is fail-closed at every irreversible step and gates Step 6 onward on a human listening review (Step 5).

## Inputs and outputs

| Input | Where | In git? |
|---|---|---|
| Original audio (5 tracks) | `/opt/moodify/music-media/audio/cadeau10-album1/` | No (deployment asset) |
| Original manifest | `apps/web/assets/cadeau10-album1.json` | Yes |
| Profile v1 parameters | `moodify-core-package/scripts/listen_demo_render.py` (constant `LISTEN_DEMO_PROFILE_V1`) | Yes |
| Render script | `moodify-core-package/scripts/listen_demo_render.py` | Yes |

| Output | Where | In git? |
|---|---|---|
| Moodify processed wav (5) | `/opt/moodify/music-media/audio/cadeau10-album1-moodify/` | No |
| Public manifest sidecar | `apps/web/assets/cadeau10-album1-moodify.json` | Yes (after human gate) |

## Step index

| Step | Action | Reversible? | Gate |
|---|---|---|---|
| 1 | `git pull --rebase origin main` | yes | — |
| 2 | verify Cadeau10 original audio dir + manifest | yes | fail-closed if missing |
| 3 | mkdir moodify audio dir | yes | — |
| 4 | run render script → 5 wav + sidecar JSON | partial (wav) | fail-closed on DSP error |
| 5 | human A/B review (≥ 80% identification) | n/a | **mandatory** |
| 6 | commit manifest sidecar | yes | human gate passes |
| 7 | rebuild apps/web (Node) | yes | — |
| 8 | Range probe all 5 URLs (expect 206) | yes | fail-closed if any ≠ 206 |
| 9 | Brand Home `/listen` link awareness (manual fallback hint) | yes | — |
| 10 | Brand Home Listen copy edit (separate PR) | yes | — |

## Why a human gate at Step 5

The `moodify-core-package` engine can produce an output that **mathematically** differs from the input but **acoustically** sounds identical, or worse, sounds like a generic AI mastering result.

Step 5 prevents both:

- "Looks processed but sounds the same" → silent demo failure
- "Sounds aggressively mastered" → off-brand with `Listen. Then Play.`

Pass criterion: ≥ 80% of 5 blind A/B trials, a careful listener can identify which track is `Moodify` and articulate what changed.

If the criterion is not met, edit `LISTEN_DEMO_PROFILE_V1` in `moodify-core-package/scripts/listen_demo_render.py` and rerun from Step 4. **Do not bypass this gate to ship.**

## Why the manifest sidecar waits until Step 6

Per Public Form §13 Test C (听觉可证), a public comparison without real audio is a fabricated claim.

Therefore the public manifest sidecar (`apps/web/assets/cadeau10-album1-moodify.json`) is created by the render script and only committed after Step 5 confirms audibility. A pre-created placeholder JSON would invite the very failure mode that §13 Test C rules out.

## What the runbook does not do

- It does not modify `Brand Home` (`ops/web_origin/site/rongjingmusic/index.html`).
- It does not modify `apps/web/app/listen/page.tsx`.
- It does not touch the `Cloud-prepared Track Pipeline` (`moodify-core-package/src/moodify/data_plane/pipeline.py`).
- It does not change `Canon` files.
- It does not modify databases.
- It does not introduce new audio storage media — only the existing LA media root + nginx alias.

Step 10 (Brand Home Listen copy edit) is **explicitly out of band** so that copy edits do not block audio deployment.

## Environment variables

| Var | Default | Purpose |
|---|---|---|
| `MOODIFY_REPO_ROOT` | `/opt/moodify` | git repo root |
| `MOODIFY_MEDIA_ROOT` | `/opt/moodify/music-media/audio` | media root under nginx alias |
| `MOODIFY_PUBLIC_BASE_URL` | `https://play.rongjingmusic.com/audio/cadeau10-album1-moodify` | public URL prefix |

All defaults assume the production topology in `ops/web_origin/PRODUCTION_TOPOLOGY.md` §21.

## Failure modes and recovery

| Failure | Recovery |
|---|---|
| Step 4 DSP error | fix script, rerun |
| Step 5 fail | tune profile, rerun from Step 4 |
| Step 6 git push rejected | pull + rebase + resolve |
| Step 7 build error | check `apps/web/README.md` requirements |
| Step 8 partial 206 | check nginx alias + media root permission |
| Step 8 zero 206 | check that wav files exist at expected paths |
| /listen route 404 | use Step 9 fallback (hash anchor `#listen` in Brand Home) |

## Related evidence

- `apps/web/assets/cadeau10-album1.json` — original audio manifest
- `moodify-core-package/scripts/listen_demo_render.py` — render implementation
- `apps/web/app/listen/page.tsx` — `/listen` page consumer (5 src URLs)
- `ops/web_origin/PRODUCTION_TOPOLOGY.md` §21 — LA media root + nginx alias
- `ops/web_origin/MUSIC_CLOUD_RUNBOOK_2_0.md` — Cadeau10 original audio sync
- `apps/web/README.md` §33 — "Audio binaries are deployment assets and must not enter ordinary Git history"
