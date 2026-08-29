# MFD-003 Acceptance Gate

## A. Contract

- [ ] Player API boundary exists
- [ ] API version exists
- [ ] Session contract exists
- [ ] Track contract exists
- [ ] Library contract exists
- [ ] PlaybackManifest exists
- [ ] Error contract exists

## B. Security

- [ ] user-level auth
- [ ] no service key in Desktop
- [ ] no DB credentials
- [ ] no OSS secret
- [ ] playback access authorized server-side
- [ ] signed/temporary media access
- [ ] sensitive logs redacted

## C. Desktop

- [ ] centralized API client
- [ ] typed responses
- [ ] typed errors
- [ ] timeout
- [ ] cancellation
- [ ] config-driven base URL
- [ ] renderer not scattered with direct fetch

## D. Backend

- [ ] no duplicate user authority
- [ ] no duplicate track authority
- [ ] no duplicate state machine
- [ ] internal Ear details hidden
- [ ] internal processing details hidden

## E. Verification

- [ ] contract tests pass
- [ ] auth tests pass
- [ ] authorization tests pass
- [ ] real track smoke pass
- [ ] real manifest smoke pass
- [ ] stream URL reachability verified
- [ ] expiry behavior verified or explicitly blocked

## F. Scope

- [ ] no full audio playback implementation
- [ ] no final player UI
- [ ] no DSP
- [ ] no WASAPI
- [ ] no system media integration

---

全部通过：

> **MFD-004 = GO**
