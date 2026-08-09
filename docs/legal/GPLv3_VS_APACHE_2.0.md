# GPLv3 and Apache License 2.0 — Moodify Decision Note

`APL 2.0` is interpreted here as **Apache License 2.0**, whose standard SPDX
identifier is `Apache-2.0`.

| Question | GPL-3.0-only | Apache-2.0 |
|---|---|---|
| License model | Strong copyleft | Permissive |
| Commercial use | Permitted | Permitted |
| Closed-source modified distribution | Generally not permitted for GPL-covered derivative/combined work | Permitted if license and notice duties are met |
| Source on binary distribution | Complete corresponding source must be made available as required by GPLv3 | No general duty to publish source |
| Proprietary embedding | Usually unsuitable when the combined work must remain proprietary | Commonly suitable |
| Modification notices | Required | Required for modified files |
| Patent provisions | Contains patent protections and anti-discriminatory patent measures | Express contributor patent grant and patent-litigation termination |
| User-product installation information | May be required in covered circumstances | Not required |
| Network-only use | No automatic source disclosure merely because it is offered as a service | No automatic source disclosure |
| Brand permission | Not automatically granted | Not automatically granted |
| Compatibility | Can absorb compatible Apache-2.0 code into a GPLv3 distribution | Apache-2.0 code may be combined into GPLv3, but the combined distribution is governed by GPLv3 obligations |

## Practical recommendation for Moodify

Use GPLv3 when the goal is to ensure that distributed improvements to the
covered application remain open. Use Apache-2.0 when the goal is broad
adoption, proprietary integration, SDK embedding, or infrastructure ecosystem
growth.

For Moodify's current architecture, a layered policy is stronger than applying
one license indiscriminately:

- GPL-3.0-only for the auditable desktop application and processing framework;
- AGPL-3.0-only for a server component only when network users should receive
  source rights;
- Apache-2.0 for a deliberately permissive SDK or protocol client;
- separate terms for models, weights, datasets, private measurement evidence,
  creative assets and cloud services;
- a separate trademark policy for the Moodify identity.

A community GPL edition plus a separately negotiated commercial license is
possible only when the necessary copyrights and contributor permissions are
controlled by the party granting the commercial license.
