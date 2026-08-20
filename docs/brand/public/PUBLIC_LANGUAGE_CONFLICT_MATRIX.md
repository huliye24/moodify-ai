# Public Language Conflict Matrix — Package 01

**Scope:** current tracked public surfaces, live home pages, public README/authority documents, and deployment verification scripts. Historical/artifact occurrences are not deleted; representative authoritative or production-affecting occurrences are recorded below.

| Phrase | File / live surface | Route | Current role | Desired tier | Later action |
|---|---|---|---|---|---|
| Auditory Intelligence Infrastructure | live `rongjingwenchuan.com`; `ops/web_origin/verify_origins.sh`; older product-framework documents | Company `/` | Company Hero/title and deployment assertion | D — retired from primary narrative | P03 replace Company Hero/SEO; update verification marker after deployment. |
| Give machines the ability to hear. | live Company Home; older product-framework language | Company `/` | First-page claim | D | P03 move out of first identity or retain only in clearly historical/research context. |
| The Ear of AI | `ops/web_origin/site/rongjingmusic/*.html`; `docs/product-framework/TERMINOLOGY_AND_CLAIMS.md`; `01_MOODIFY_PRODUCT_CONSTITUTION.md` | Product Home footer; `/about.html`; `/ear.html`; docs | Footer/OG/product identity | D | P02 remove from public Header/Footer/SEO/Hero; preserve internal/historical references with classification. |
| Build with Moodify | live `rongjingwenchuan.com`; verification marker | Company `/` | Developer CTA | D | P03 remove as primary CTA; update probe. |
| ACU | live `rongjingwenchuan.com`; older docs | Company `/` | Public product/infrastructure concept | D | P03 remove from first-layer navigation and Hero; retain technical archive if needed. |
| API | live Company Home; `ops/web_origin/nginx/moodify-sites.conf`; public contracts | Company `/`; `/api/*` | Public CTA plus real service routes | D for branding; technical-only for runtime | P03 remove branding prominence; do not delete service routes. |
| Developers | live Company Home | Company `/` | Primary navigation/audience | D | P03 demote/remove from primary navigation. |
| Creator / Creator Center | `apps/music-web/app/page.tsx`, `/studio`, `/console`, `/c/[handle]`; Product Home `music.html` | Player and Product Home | Gated public navigation, profiles, publishing | D as current primary identity | P02 remove creator-first product copy; P04 hide/demote routes from public Play journey without deleting backend. |
| Creator Center | `apps/music-web/app/page.tsx` (`创作者中心`) | Player `/` when capability enabled | Sidebar navigation | D | P04 remove from primary Player navigation. |
| Upload | `apps/music-web/app/page.tsx`, `app/studio/page.tsx` | Player `/`, `/studio` | `上传作品` action | D | P04 hide/demote from Play surface; preserve gated workflow pending product decision. |
| 授权 | `apps/music-web/app/t/[id]/page.tsx`, `app/inbox/page.tsx` | Track and Inbox | Public licensing-intent journey | D / subordinate capability | P04 remove from primary listening path; preserve data/contract integrity. |
| Can machines learn to hear? | `ops/web_origin/site/rongjingmusic/about.html`; product-framework docs | Product `/about.html` | About Hero / old origin identity | B — Research only | P02 place after product comprehension or link to Company Research. |
| Listen. Then Play. | `ops/web_origin/site/rongjingmusic/index.html`; Package authority | Product `/` | Hero/product principle | A | P02 retain, normalize casing to authority form, pair with brand belief and Play. |
| Moodify Music | root `README.md`; product site; player metadata/manifest; Android/release docs | Multiple | Public product name | A (`Moodify` primary; Music qualifier allowed) | P02–P04 make use consistent; resolve stale download versions. |
| AI music / AI audio product category | older website blueprint, docs, research/engineering descriptions | Docs and technical pages | Category/technical audience wording | C or D depending context | Keep in technical/historical context only; remove from first public definition. |
| Listen / Represent / Judge / Intervene / Verify / Learn | Product Home `index.html`, `about.html`, `ear.html` | Product Home and subpages | Prominent process explanation | C — technical/research | P02 remove from Home prominence; move to Evidence/Research. |
| Evidence / Verification | Product Home nav and home sections | Product `/`, `/evidence.html` | Primary navigation and large section | B | P02 make subordinate to Sound/Play; retain bounded claims. |

## SEO / OG conflicts

- Product Home `about.html` OG title and all tracked footers retain `The Ear of AI`.
- Company Home live title and description retain `Auditory Intelligence Infrastructure` and `Give machines the ability to hear.`
- Player metadata lacks canonical/OG alignment and its manifest retains a creator-oriented description.
