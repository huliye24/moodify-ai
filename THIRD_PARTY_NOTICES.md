# Third-Party Notices

Maintain one entry for every redistributed dependency or asset whose license
requires attribution or inclusion of notices.

Moodify distributes its own source code under GPL-3.0-only. Third-party
dependencies are installed through standard package managers or invoked as
external tools; their original license texts and notices are shipped with
the corresponding packages and must be preserved.

## Python runtime dependencies (moodify-core-package)

- Component: numpy
  License/SPDX identifier: BSD-3-Clause
  Role: array computation (core analysis)
  Modified by Moodify: no
  Distribution obligations: preserve BSD notice (present in installed package)

- Component: scipy
  License/SPDX identifier: BSD-3-Clause
  Role: signal processing
  Modified by Moodify: no

- Component: librosa
  License/SPDX identifier: ISC
  Role: audio feature extraction
  Modified by Moodify: no

- Component: pyloudnorm
  License/SPDX identifier: MIT
  Role: loudness measurement (EBU R128 / ITU BS.1770)
  Modified by Moodify: no

- Component: pydantic
  License/SPDX identifier: MIT
  Role: canonical contract models
  Modified by Moodify: no

- Component: PyYAML
  License/SPDX identifier: MIT
  Role: policy configuration
  Modified by Moodify: no

- Component: fastapi
  License/SPDX identifier: MIT
  Role: HTTP API server
  Modified by Moodify: no

## External tools (invoked, not redistributed)

- Component: FFmpeg / FFprobe
  License: LGPL-2.1+ / GPL-2.0+ (build-dependent)
  Role: audio decode and spectrogram generation (external binary)
  Modified by Moodify: no
  Note: Moodify does not ship FFmpeg binaries; users install their own.

- Component: MuseScore
  License/SPDX identifier: GPL-3.0
  Role: optional score backend (experimental MSE adapter)
  Modified by Moodify: no
  Note: optional external tool; not required for the canonical pipeline.

- Component: basic-pitch
  License/SPDX identifier: Apache-2.0
  Role: optional stem/transcription backend
  Modified by Moodify: no

- Component: whisperX
  License/SPDX identifier: MIT
  Role: optional lyric alignment backend
  Modified by Moodify: no

## Android dependencies (apps/android)

- Component: Media3 (ExoPlayer)
  License/SPDX identifier: Apache-2.0
  Role: playback engine
  Modified by Moodify: no

- Component: Jetpack Compose
  License/SPDX identifier: Apache-2.0
  Role: UI framework
  Modified by Moodify: no

## Assets

- Music samples, scores, lyrics, and other creative material in the
  repository are not licensed by the GPL. They are stored for internal
  verification and demo use only and must not be redistributed without
  separate written authorization.

## Review status

- Reviewed by: huliye24 (maintainer)
- Review date: 2026-08-09
- Checklist: docs/legal/LEGAL_REVIEW_CHECKLIST.md
