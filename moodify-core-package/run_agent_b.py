"""Agent B: Phase 2 system validation — B1, B3, B4, B5. Adapted to actual APIs."""
import sys
import json
import time
import traceback
from pathlib import Path
sys.path.insert(0, 'src')
import numpy as np

OUT = Path('outputs/phase2_agent_b')
OUT.mkdir(parents=True, exist_ok=True)
results = {}

# ── B3: Diagnosis Stability (50 repeats, 5D process vector) ──
print('=' * 60)
print('B3: Diagnosis Stability — 50 repeats (5D process vector)')
print('=' * 60)

from moodify.diagnosis.engine import DiagnosisEngine
from moodify.orchestration.state_transfer import StateTransferEngine

audio = 'tests/baseline/test_audio/piano.wav'
n_repeats = 50
e_vals, d_vals, s_vals, t_vals, h_vals = [], [], [], [], []

for i in range(n_repeats):
    ws = DiagnosisEngine().diagnose_quick(audio)
    vec = StateTransferEngine.diagnostic_to_process(ws)
    e_vals.append(vec.E)
    d_vals.append(vec.D)
    s_vals.append(vec.S)
    t_vals.append(vec.T)
    h_vals.append(vec.H)

stability_lines = [
    '# B3: 诊断引擎稳定性报告', '',
    f'**测试音频**: {audio}', f'**重复次数**: {n_repeats}', '',
    '## 5D Process Vector 稳定性', '',
    '| 维度 | Mean | Std | CV | 评级 |',
    '|------|------|-----|-----|------|',
]
stability_data = {}
for name, vals in [('E(能量)', e_vals), ('D(动态)', d_vals), ('S(空间)', s_vals), ('T(时域)', t_vals), ('H(和声)', h_vals)]:
    arr = np.array(vals)
    cv = np.std(arr) / (np.mean(arr) + 1e-10) * 100
    rating = '非常稳定' if cv < 5 else ('基本稳定' if cv < 15 else '不稳定(!)')
    stability_lines.append(f'| {name} | {np.mean(arr):.4f} | {np.std(arr):.4f} | {cv:.1f}% | **{rating}** |')
    stability_data[name] = {'mean': round(float(np.mean(arr)), 4), 'std': round(float(np.std(arr)), 4), 'cv_pct': round(cv, 1)}
    print(f'  {name}: mean={np.mean(arr):.4f}, std={np.std(arr):.4f}, CV={cv:.1f}% -> {rating}')

with open(OUT / 'diagnosis_stability_report.md', 'w') as f:
    f.write('\n'.join(stability_lines))
results['B3_stability'] = {'n_repeats': n_repeats, 'audio': audio, 'dimensions': stability_data}
print('  B3 done.')

# ── B4: CalibrationState inspection ──────────────────────
print()
print('=' * 60)
print('B4: CalibrationState D value')
print('=' * 60)

from moodify.calibration.online import CalibrationState

try:
    state = CalibrationState.load(str(Path('outputs').resolve()))
    d_val = state.d_value()
    total_n = state.total_n
    print(f'  D值: {d_val:.4f}')
    print(f'  总样本数: {total_n}')

    conf_data = {}
    for code in ['GA', 'SE', 'DR', 'WL', 'HL', 'LW', 'UD', 'CN']:
        try:
            c = state.get_confidence(code)
            conf_data[code] = round(c, 3)
            print(f'  {code}: confidence={c:.3f}')
        except Exception as e:
            conf_data[code] = f'error: {str(e)[:40]}'
            print(f'  {code}: {e}')

    with open(OUT / 'calibration_d_value.json', 'w') as f:
        json.dump({'D_value': round(d_val, 4), 'total_n': total_n, 'confidence': conf_data}, f, indent=2)
    results['B4_calibration'] = {'D_value': d_val, 'total_n': total_n, 'confidence': conf_data}
except Exception as e:
    print(f'  B4 FAILED: {e}')
    results['B4_calibration'] = {'error': str(e)}
    with open(OUT / 'calibration_d_value.json', 'w') as f:
        json.dump({'error': str(e)}, f)

print('  B4 done.')

# ── B5: Bottleneck Analysis ──────────────────────────────
print()
print('=' * 60)
print('B5: Bottleneck Analysis')
print('=' * 60)

from moodify.optimizer.search import search_optimal_strengths
from moodify.processing.spectral_chain import SpectralDSPChain
from moodify.audio_io import load_audio

t0 = time.time()
ws = DiagnosisEngine().diagnose_quick(audio)
t_diag = time.time() - t0
print(f'  诊断引擎: {t_diag*1000:.0f}ms')

t0 = time.time()
r = search_optimal_strengths(ws, 'GA', top_k=1, n_samples=2000)
t_search = time.time() - t0
print(f'  搜索(2000样本): {t_search*1000:.0f}ms')

audio_data, sr = load_audio(audio)
params = r[0][1] if r else {}
t0 = time.time()
chain = SpectralDSPChain()
if params:
    processed = chain.process(audio_data, sr, params)
t_dsp = time.time() - t0
print(f'  DSP处理: {t_dsp*1000:.0f}ms')

t_total = t_diag + t_search + t_dsp
bottleneck_lines = [
    '# B5: 系统瓶颈分析', '',
    f'**测试音频**: {audio}', '',
    '## 各环节耗时', '',
    '| 环节 | 耗时(ms) | 占比 |',
    '|------|---------|------|',
    f'| 诊断 | {t_diag*1000:.0f} | {t_diag/t_total*100:.1f}% |',
    f'| 搜索(2000样本) | {t_search*1000:.0f} | {t_search/t_total*100:.1f}% |',
    f'| DSP处理 | {t_dsp*1000:.0f} | {t_dsp/t_total*100:.1f}% |',
    f'| **总计** | **{t_total*1000:.0f}** | **100%** |',
    '',
]
if t_diag/t_total > 0.5:
    bottleneck_lines.append(f'**瓶颈**: 诊断引擎占{t_diag/t_total*100:.0f}%，可能是模型初始化开销。')
elif t_search/t_total > 0.5:
    bottleneck_lines.append(f'**瓶颈**: 搜索环节占{t_search/t_total*100:.0f}%，建议减少样本数或优化LHS采样。')
else:
    bottleneck_lines.append('各环节占比均衡。')

with open(OUT / 'bottleneck_report.md', 'w') as f:
    f.write('\n'.join(bottleneck_lines))
results['B5_bottleneck'] = {'diag_ms': round(t_diag*1000), 'search_ms': round(t_search*1000), 'dsp_ms': round(t_dsp*1000), 'total_ms': round(t_total*1000)}
print('  B5 done.')

# ── B1: E2E Pipeline (5 emotions, simplified gate) ──────
print()
print('=' * 60)
print('B1: E2E Pipeline — 5 emotions')
print('=' * 60)

import soundfile as sf
from moodify.diagnosis.defect_classifier import DefectClassifier
from moodify.diagnosis.health_scorer import HealthScorer

gate_results = []
classifier = DefectClassifier()
scorer = HealthScorer()

for emo in ['GA', 'DR', 'WL', 'SE', 'HL']:
    print(f'\n  [{emo}] ...', end=' ', flush=True)
    try:
        t0 = time.time()
        ws = DiagnosisEngine().diagnose_quick(audio)
        defects_before = classifier.classify(ws, emo)
        whs_before = scorer.compute_whs(ws, defects_before)

        r = search_optimal_strengths(ws, emo, top_k=1, n_samples=1000)
        if not r:
            gate_results.append({'emotion': emo, 'proxy_score': -999, 'gate': 'FAIL', 'reason': 'no search results'})
            print('FAIL: no search results')
            continue

        vec, params, proxy_score = r[0]

        audio_data, sr = load_audio(audio)
        chain = SpectralDSPChain()
        processed = chain.process(audio_data, sr, params)
        out_path = str(OUT / f'e2e_gate_{emo}.wav')
        sf.write(out_path, processed, sr)

        ws2 = DiagnosisEngine().diagnose_quick(out_path)
        defects_after = classifier.classify(ws2, emo)
        whs_after = scorer.compute_whs(ws2, defects_after)

        whs_b = whs_before.get('WHS', 0)
        whs_a = whs_after.get('WHS', 0)
        n_defects_before = whs_before.get('defect_count', 0)
        n_defects_after = whs_after.get('defect_count', 0)

        # Simplified gate: WHS didn't drop too far + defects didn't spike
        gate_passed = whs_a >= whs_b * 0.7 and n_defects_after <= n_defects_before + 2
        gate_reason = f"WHS {whs_b:.0f}->{whs_a:.0f}, defects {n_defects_before}->{n_defects_after}"

        gate_results.append({
            'emotion': emo,
            'proxy_score': round(proxy_score, 1),
            'WHS_before': round(whs_b, 1),
            'WHS_after': round(whs_a, 1),
            'defects_before': n_defects_before,
            'defects_after': n_defects_after,
            'gate': 'PASS' if gate_passed else 'FAIL',
            'gate_reason': gate_reason,
        })
        icon = 'PASS' if gate_passed else 'FAIL'
        print(f'{icon} proxy={proxy_score:.1f}, WHS: {whs_b:.1f}->{whs_a:.1f}')
    except Exception as e:
        gate_results.append({'emotion': emo, 'proxy_score': -999, 'gate': 'CRASH', 'reason': str(e)[:120]})
        print(f'CRASH: {e}')
        traceback.print_exc()

n_pass = sum(1 for g in gate_results if g['gate'] == 'PASS')
report_lines = [
    '# E2E 管道验证报告', '',
    f'**测试音频**: {audio}', '**搜索样本**: 1000', '',
    '## 结果汇总', '',
    '| 情绪 | proxy_score | WHS | Defects | 判定 |',
    '|------|------------|-----|---------|------|',
]
for g in gate_results:
    whs_str = f"{g.get('WHS_before','?')}->{g.get('WHS_after','?')}"
    def_str = f"{g.get('defects_before','?')}->{g.get('defects_after','?')}"
    report_lines.append(f"| {g['emotion']} | {g['proxy_score']} | {whs_str} | {def_str} | {g['gate']} |")
report_lines += [
    '',
    f'**通过率**: {n_pass}/{len(gate_results)}',
    '',
    '## 备注',
    '质量门规则: WHS后 >= WHS前 × 0.7 且 缺陷增加 <= 2',
]

with open(OUT / 'e2e_quality_gate_report.md', 'w') as f:
    f.write('\n'.join(report_lines))
results['B1_pipeline'] = {'n_pass': n_pass, 'n_total': len(gate_results), 'details': gate_results}
print(f'\n  B1 done: {n_pass}/{len(gate_results)} passed.')

# ── Summary ──────────────────────────────────────────────
summary = {
    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    'audio': audio,
    'results': results,
}
with open(OUT / 'agent_b_summary.json', 'w') as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print()
print('=' * 60)
print('Agent B run complete')
for k, v in results.items():
    print(f'  {k}: {json.dumps(v, ensure_ascii=False, default=str)[:120]}')
print(f'Output: {OUT}')
print('=' * 60)
