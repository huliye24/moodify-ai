# MFD-001 Audit Checklist

本清单供 Codex 执行阶段 A。

## Repository

- [ ] 当前仓库 URL / remote
- [ ] 当前 branch
- [ ] HEAD SHA
- [ ] working tree 状态
- [ ] root directory inventory
- [ ] repository size / major large directories
- [ ] license
- [ ] CI workflows
- [ ] release workflows
- [ ] root AGENTS authority

## Product authority

- [ ] README
- [ ] AGENTS.md
- [ ] REPOSITORY_STATUS
- [ ] architecture docs
- [ ] product docs
- [ ] legacy policy
- [ ] historical product identity
- [ ] 当前 Player 定义是否已经存在
- [ ] Ear 是否仍被写成整个产品

## Client

- [ ] Android path
- [ ] Android build system
- [ ] Android API client
- [ ] auth model
- [ ] library model
- [ ] playback model
- [ ] queue model
- [ ] local persistence
- [ ] media URL assumptions
- [ ] existing desktop traces
- [ ] existing Electron traces

## Cloud / API

- [ ] BFF
- [ ] public API
- [ ] internal API
- [ ] auth endpoints
- [ ] service key usage
- [ ] tracks
- [ ] users
- [ ] library
- [ ] playlist
- [ ] queue
- [ ] playback URL
- [ ] playback manifest
- [ ] processed version identity
- [ ] OSS / object storage integration evidence
- [ ] CORS assumptions
- [ ] client origin assumptions

## Ear / Core

- [ ] canonical core
- [ ] experimental
- [ ] legacy
- [ ] research
- [ ] production runtime
- [ ] state machine authority
- [ ] evidence authority
- [ ] processing pipeline
- [ ] Audiolla integration location/status
- [ ] what Desktop must never duplicate

## Security

- [ ] secrets committed?
- [ ] service keys referenced in client?
- [ ] auth tokens handling
- [ ] internal endpoints accidentally public?
- [ ] direct DB access from app?
- [ ] unsafe assumptions for Electron client?

## Final classification

每项能力必须落入：

- `CANONICAL`
- `PRESENT`
- `PARTIAL`
- `UNRESOLVED`
- `MISSING`
- `EXPERIMENTAL`
- `LEGACY`
- `HISTORICAL`

不要使用模糊的 “基本完成”。
