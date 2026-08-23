# Cloud Client Boundary

The current `BffClient` remains the only desktop network adapter. It has no Local Track preparation methods. W10 did not add `prepareTrack`, polling, cancel or source resolution methods because no live public contract exists.

Unblock contract must provide a public/scoped adapter surface such as request + status (+ source only if real), using existing configured endpoint and user/session auth. Fetch/upload code must remain inside one service adapter; renderer may receive normalized `CloudPreparation` states only. Track, Playback and Queue authorities must remain W02/W04/W05.
