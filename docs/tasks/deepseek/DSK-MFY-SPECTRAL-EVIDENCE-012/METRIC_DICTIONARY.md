# Spectral Evidence Metric Dictionary v0.1

| Metric | Unit | Definition | Null / failure rule |
|---|---|---|---|
| peak_db | dBFS | `20 log10(max(abs(samples)))` after declared analysis conversion | load/alignment failure |
| rms_db | dBFS | `20 log10(sqrt(mean(samples²)))` | load/alignment failure |
| rms_delta_db | dB | after RMS dB − before RMS dB | either RMS unavailable |
| crest_factor | dB | peak dB − RMS dB | either component unavailable |
| band_energy_db | dB | mean normalized STFT-bin power in declared band | invalid/empty band or load failure |
| band_delta_db | dB | after band energy − before band energy | either side unavailable |
| spectral_diff_*_db | dB | after absolute-reference STFT dB − before absolute-reference STFT dB over active bins | alignment failure |

All metrics carry input hashes, source sample rate/channel count, analysis parameters and explicit conversion actions. A positive delta means an increase in that measurement only; it is not a quality judgment.

