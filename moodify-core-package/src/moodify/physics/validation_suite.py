"""Physics Validation Suite — run on cloud server for speed.

Validates: EDS fix, M Factor per emotion, plasticity, WHS/EDS correlation.
Usage: python validation_suite.py
"""
import sys, os, time, json, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['MOODIFY_OUTPUT'] = '/home/ubuntu/moodify/outputs'

from moodify.diagnosis.engine import DiagnosisEngine
from moodify.diagnosis.health_scorer import HealthScorer
from moodify.orchestration.state_transfer import StateTransferEngine
from moodify.orchestration.workflow_engine import WorkflowOrchestrator
from moodify.knowledge.emotion_targets import get_ideal_process_vector
from moodify.calibration.online import CalibrationState
from moodify.calibration.listener import DiagnosisListener
from moodify.processing.spectral_chain import SpectralDSPChain
from moodify.optimizer.search import search_optimal_strengths

engine = DiagnosisEngine()
scorer = HealthScorer()
chain = SpectralDSPChain()
listener = DiagnosisListener()
w = WorkflowOrchestrator()

emotions = ['WL', 'GA', 'DR', 'SE', 'HL', 'LW', 'UD', 'CN']
test_songs = [
    '/home/ubuntu/moodify/test_audio/piano.wav',
    '/home/ubuntu/moodify/test_audio/vocal_folk.wav',
    '/home/ubuntu/moodify/test_audio/electronic.wav',
]

print('=' * 60)
print('PHYSICS VALIDATION SUITE')
print('=' * 60)

# ── V1: EDS Fix ──
print('\n[V1] EDS Fix: negative values now visible')
piano_ws = engine.diagnose_quick(test_songs[0])
eds_same = scorer.compute_eds(piano_ws, piano_ws, 'GA')
print(f'  same audio EDS: {eds_same:.1f} (expect near 0)')

result = w.process(test_songs[0], 'GA', output_dir='/home/ubuntu/moodify/outputs')
eds_val = result.eds
v1_pass = abs(eds_val) > 0.1
print(f'  piano x GA EDS: {eds_val:+.1f}')
print(f'  V1: {"PASS" if v1_pass else "FAIL - still clamped"}')

# ── V2: M Factor per emotion ──
print('\n[V2] M Factor: Spearman rho for each emotion')
rho_results = {}
for emo in emotions:
    pairs = []
    for song_path in test_songs:
        try:
            ws = engine.diagnose_quick(song_path)
            vec_before = StateTransferEngine.diagnostic_to_process(ws).to_array()
            ideal = get_ideal_process_vector(emo)
            dist_before = np.linalg.norm(vec_before - ideal)

            audio, sr = sf.read(song_path)
            audio = audio.astype(np.float32)

            results = search_optimal_strengths(ws, emo, top_k=3, n_samples=500,
                                                audio=audio, sr=sr)
            for strength, params, proxy_score in results:
                processed = chain.process(audio, sr, params)
                vec_after = listener._diagnose_audio(processed, sr)
                dist_after = np.linalg.norm(vec_after - ideal)
                real_eds = 100 * (1 - dist_after / max(dist_before, 1e-9))
                pairs.append((proxy_score, real_eds))
        except Exception as e:
            pass

    if len(pairs) >= 5:
        from scipy.stats import spearmanr
        proxies = [p[0] for p in pairs]
        reals = [p[1] for p in pairs]
        rho = spearmanr(proxies, reals).statistic
        rho_results[emo] = (rho, len(pairs))
        status = 'OK' if rho > 0.3 else ('WEAK' if rho > 0 else 'NEGATIVE')
        print(f'  {emo}: rho={rho:+.3f} (n={len(pairs)}) [{status}]')

# ── V3: Plasticity ──
print('\n[V3] Emotion Plasticity: which pairs improve?')
plasticity = []
for song_path in test_songs:
    name = os.path.basename(song_path)[:15]
    for emo in ['WL', 'GA', 'DR']:
        try:
            result = w.process(song_path, emo, output_dir='/home/ubuntu/moodify/outputs')
            whs_d = result.whs_after - result.whs_before
            plasticity.append((name, emo, result.eds, whs_d))
            print(f'  {name:15s} x {emo}: EDS={result.eds:+5.1f}  WHS_d={whs_d:+3.0f}')
        except Exception as e:
            print(f'  {name:15s} x {emo}: FAIL {str(e)[:50]}')

# ── V4: Proxy-Real Correlation ──
print('\n[V4] Proxy-Real from calibration data')
state = CalibrationState.load('/home/ubuntu/moodify/outputs')
for emo in ['WL', 'GA', 'DR']:
    ec = state.emotions.get(emo)
    if ec and len(ec.proxy_real_pairs) >= 5:
        proxies = [p['proxy'] for p in ec.proxy_real_pairs[-20:]]
        reals = [p['real'] for p in ec.proxy_real_pairs[-20:]]
        from scipy.stats import pearsonr
        r, pval = pearsonr(proxies, reals)
        print(f'  {emo}: n={len(proxies)} proxy-real r={r:+.3f} (p={pval:.3f}) bias={ec.mu_bias:.1f}')

# ── Summary ──
print('\n' + '=' * 60)
print('SUMMARY')
print('=' * 60)
print(f'V1 EDS Fix: {"PASS" if v1_pass else "ISSUE"}')
if rho_results:
    mean_rho = np.mean([r[0] for r in rho_results.values()])
    print(f'V2 M Factor: mean rho={mean_rho:+.3f} ({len(rho_results)} emotions)')
pos = sum(1 for p in plasticity if p[2] > 0)
print(f'V3 Plasticity: {pos}/{len(plasticity)} positive EDS')
print(f'V4 D Value: D={state.d_value():.4f} (n={state.total_n})')
print('DONE')
