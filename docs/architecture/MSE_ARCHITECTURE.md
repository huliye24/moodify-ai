# MSE Architecture

MSE 回答“音乐结构是什么”。自动输出必须允许人工校正，保留原估计、校正者和置信度。

| 子模块 | 输出 | 自动可靠级别 | 当前状态 | 验收方式 |
|---|---|---|---|---|
| BPM and beat grid | BPM、beat times | 可在限定曲风自动候选，需低置信度门 | Experimental | 与人工网格的 tempo/beat 偏差分布 |
| Key and tonal estimation | key/mode/probability | 需人工校正 | Experimental | 标注集 accuracy + 相邻调混淆 |
| Section segmentation | section IDs/bounds/labels | 边界候选可自动，标签需人审 | Planned/Experimental | boundary F1 与容差 |
| Phrase segmentation | phrase bounds | 需人工校正 | Planned | 专家间一致性与模型偏差 |
| Melody extraction | pitch events/contour | 研究目标 | Planned | note onset/pitch metrics；保留失败 |
| Chord estimation | chord timeline | 研究目标/人审 | Planned | chord symbol recall 与 no-chord |
| Vocal/instrument roles | role/time/confidence | 需人工校正 | Experimental | stem/专家标注混淆矩阵 |
| Lyrics alignment | token/line timeline | 有歌词时实验；需人工校正 | v0.1 implemented (2026-08-08) | `lyric_align/`：heuristic（DRAFT_ONLY）+ WhisperX 适配器 + LRC/SRT/ASS 导出 + 质量门；验证集待采集（Phase E），详见 `docs/verification/lyric_align_verification_set.md` |
| MIDI reconstruction | notes/tracks/roles | 研究目标，不承诺完整扒谱 | Planned | 分轨 note metrics + 可编辑性 |
| Score representation | bars/voices/notation assets | 人工主导 | v0.1 implemented (2026-08-02) | `score_engine/`：MoodifyScore v0.1 canonical JSON → MusicXML 4.0 → MuseScore PDF/SVG；详见 `SCORE_ENGINE_ARCHITECTURE.md` |
| Structural confidence | per-field confidence/provenance | 必须可靠生成 | Schema partial | 每个字段有 backend/version/reason |

可靠自动完成、需人工校正、研究目标不是永久分类；只有经过 Golden Set 验证和 ADR 决策才能升级。当前生产合同位于 bridge 的 `SymbolicAnchor` 与新增 `StructuralRecord`；算法实现不得用占位值伪造。

