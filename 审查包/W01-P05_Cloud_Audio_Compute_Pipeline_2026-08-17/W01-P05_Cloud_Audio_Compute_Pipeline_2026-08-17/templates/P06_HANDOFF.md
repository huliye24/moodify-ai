# W01-P06 Handoff

P05 freezes the compute-output contract.

P06 must not redo audio processing.

## P06 Receives

- track_id
- ready/final render object identity
- duration
- codec/container
- sample rate/channels
- verification evidence
- access class
- pipeline/profile version
- playback metadata
- object storage locator

## P06 Question

> How does a verified READY audio object become a secure, stable PLAY experience in Android?

## P06 Scope

- playback metadata API
- signed/authorized delivery
- caching/range requests
- Android playback integration
- next/previous/swipe behavior
- delivery failure behavior
- playback evidence

Not P06:

- stem
- analysis
- DSP
- judgment
- render
