# Moodify Glossary

## Project Codes

| Code | Full Name | Description |
|------|-----------|-------------|
| **MHP** | Moodify Human Pipeline | Sprint/feature tracking system. Each MHP is a defined engineering task. |
| **MTP** | Moodify Technical Protocol | Technical design documents for specific subsystems. |
| **SPEC** | Specification | Detailed technical specification for a capability. |
| **PHYS** | Physics | Physics-informed audio analysis experiments (B-matrix, etc.). |

## Organizations

| Name | Role |
|------|------|
| **Wen Chuan Yuan** | Moodify parent organization / research institute |
| **Gong Chuan Shu** | Engineering division responsible for implementation |
| **Ying Yan Laboratory** | Audio research laboratory |

## Audio Terms

| Term | Definition |
|------|------------|
| **WHS** | Wave Health Score. Composite health metric (0-100) for audio quality. |
| **EDS** | Emotional Distance Score. Measures how close processed audio is to the emotion target (-100 to +100). |
| **MRS** | Moodify Reality Score. Distance-to-real metric (0-100). Higher = closer to real audio distribution. |
| **D-value** | Calibration metric measuring proxy-vs-real score alignment. Lower D = better calibration. |
| **LRA** | Loudness Range. Measure of loudness variation in LU. |
| **PLR** | Peak-to-Loudness Ratio. |
| **RT60** | Reverberation Time (60 dB decay). |
| **Crest Factor** | Peak / RMS ratio. Measures dynamic headroom. |
| **LUFS** | Loudness Units relative to Full Scale. Standard loudness measure. |

## Architecture Terms

| Term | Definition |
|------|------------|
| **v01** | Current product mainline. Minimal, stable DSP pipeline. |
| **legacy** | Research pipeline with full 6-phase workflow, LLM/RAG, B-matrix, etc. |
| **mainline** | The active, supported code path. Currently v01. |
| **pipeline** | End-to-end processing chain: analyze -> diagnose -> process -> export. |

## Design Philosophy

| Term | Meaning |
|------|---------|
| **v01 = product, legacy = research** | Two parallel systems; never merge. |
| **louder != better** | Loudness bias in A/B testing must be controlled via matched-loudness comparison. |
| **presets over parameters** | Users choose named presets, not individual DSP knobs. |
| **treatment records as memory** | Human feedback on processed audio is stored as structured engineering data. |
| **rule-based before model-based** | Simple rules first; ML models only when rules are insufficient and data is sufficient. |
