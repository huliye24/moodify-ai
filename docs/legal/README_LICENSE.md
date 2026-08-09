# Applying GPLv3 to Moodify

## Repository files

Place these files at the repository root:

- `LICENSE` — unmodified GNU GPL Version 3 text;
- `OPEN_SOURCE_NOTICE.md` — Moodify scope and boundary notice;
- `COPYRIGHT` — copyright ownership notice;
- `TRADEMARKS.md` — brand-use boundary;
- `THIRD_PARTY_NOTICES.md` — dependency and attribution records.

## Recommended SPDX choice

This package uses:

```text
SPDX-License-Identifier: GPL-3.0-only
```

This means recipients may use GNU GPL Version 3, but are not automatically
authorized to move the work to a future GPL version. Changing the identifier
to `GPL-3.0-or-later` is a separate governance decision.

## Minimal source-file header

```text
This file is part of Moodify.
Copyright (C) 2024–2026 荣景文川（深圳）科技有限公司
SPDX-License-Identifier: GPL-3.0-only
```

Use the comment syntax appropriate for the language.

## Architecture recommendation

Do not rely on one repository-level label to describe every Moodify asset.
Maintain an explicit license map:

| Layer | Suggested treatment |
|---|---|
| Desktop application and auditable processing code | GPL-3.0-only |
| Network server where network reciprocity is required | Consider AGPL-3.0-only |
| Public SDK or API client intended for broad embedding | Consider Apache-2.0 |
| Private models, weights, datasets, rules, validation corpora | Separate proprietary or model/data terms |
| Documentation | Explicit documentation license |
| Music, artwork, UI assets and fonts | Separate asset licenses |
| Moodify name and logo | Trademark/brand policy |

## Before publishing

1. Confirm the correct copyright owner and first copyrightable year.
2. Audit every dependency and generated artifact.
3. Remove credentials, customer data, private evidence and restricted assets.
4. Decide whether contributions require a CLA or DCO.
5. Decide whether commercial dual licensing will be offered.
6. Obtain jurisdiction-specific legal review before a major commercial release.
