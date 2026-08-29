# Android Ear Boundary — MFY-DATA-FOUNDATION-001-REV2 Phase A4

| 项 | 值 |
|---|---|
| Package | com.moodify.app（applicationId=com.moodify.app） |
| 技术 | Kotlin + Jetpack Compose + Media3/ExoPlayer |
| 导航 | MoodifyApp.kt 状态机：底部 3 tab（Home/ProcessingHub/Works）+ 全屏流程（UploadFlow → Processing → WorkDetail） |
| Screens（17） | Home/ProcessingHub/Processing/Works/WorkDetail/UploadFlow/Profile/Settings/About/NowPlaying/Search/DataCenter/NotificationCenter/SupportScreens/CreatorCenter/PublishWork/CollaborationHub/CopyrightCenter |
| Pairing | data/TokenStore.kt（Keystore AES/GCM）+ ConnectionRepository（/pair、/pair/revoke） |
| API client | data/MoodifyApiClient.kt（{baseUrl}/api/v1，BaseUrlStore 默认 127.0.0.1:8000） |
| 播放 | data/PlaybackManager.kt（Media3） |
| Ear 工作流 | UploadFlow（选音频）→ Processing（jobs）→ Works（结果）→ WorkDetail |

**边界声明（本阶段强制）**：
```
NO_MUSIC_DOMAIN_MIGRATION_IN_THIS_PHASE
```
CreatorCenter/PublishWork/CollaborationHub/CopyrightCenter = design evidence / UI experiments，不是生产商业能力。本阶段仅允许：编译修复、文档标注、契约说明；禁止改 Ear 导航/删除 pairing/替换 Ear API client。
