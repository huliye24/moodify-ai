"""Run MAMSE-012 on real cases: three graphs + structural evidence.

Usage: python scripts/mamse012_run_real_cases.py <source.wav ...> --out <dir>
For each track: band graph (band-profile signal), temporal event graph
(canonical events), positive-correlation graph (MAMSE-011 clean subset).
Emits graph evidence per family + a summary comparing smoothness and
local variation. Recording only; no canonical change.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.auditory.events.engine import run_temporal_hearing
from moodify.auditory.representation.build import build_representation
from moodify_experimental.mamse012 import (
    build_band_adjacency_graph,
    build_positive_correlation_graph,
    build_temporal_event_graph,
    dirichlet_energy,
    graph_spectral_energy,
    local_variation,
    save_graph_evidence,
)

BANDS = [
    ("sub", 20, 60), ("bass", 60, 120), ("low_mid", 120, 250), ("mid", 250, 500),
    ("core_mid", 500, 2000), ("presence", 2000, 5000), ("brilliance", 5000, 10000),
    ("air", 10000, 16000),
]
CLEAN_FEATURES = ["rms_db", "peak_db", "stereo_correlation", "spectral_centroid_hz",
                  "band_sub", "band_bass", "band_low_mid", "band_mid", "band_core_mid",
                  "band_presence", "band_brilliance", "band_air"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    summary: dict = {"schema_version": "mamse-012-real-cases-v1", "cases": []}

    for src in args.sources:
        path = Path(src)
        samples, sr = sf.read(path, always_2d=True)
        samples = samples.astype(np.float32)
        case_name = path.stem
        case_dir = out_root / case_name
        case_dir.mkdir(parents=True, exist_ok=True)
        rep = build_representation(samples, sr, source_sha256=f"real:{case_name}")
        plane = rep.planes["S1"]
        names = list(plane.feature_names)
        idx = [names.index(c) for c in CLEAN_FEATURES]
        X = np.asarray(plane.values, dtype=np.float64)[:, idx]
        mean_profile = np.median(X, axis=0)

        # 1. band graph with mean band-profile signal
        g_band = build_band_adjacency_graph(BANDS)
        band_profile = mean_profile[[CLEAN_FEATURES.index(f"band_{b[0]}") for b in BANDS]]
        band_profile = (band_profile - band_profile.min()) / (band_profile.max() - band_profile.min() + 1e-12)
        save_graph_evidence(g_band, case_dir / "band_graph", signal=band_profile)
        band_energy = graph_spectral_energy(g_band, band_profile)

        # 2. temporal event graph
        hearing = run_temporal_hearing(samples, sr)
        events = [e.to_dict() if hasattr(e, "to_dict") else e for e in hearing.events]
        g_event = build_temporal_event_graph(events)
        event_signal = np.zeros(len(g_event.nodes))
        for i, n in enumerate(g_event.nodes):
            event_signal[i] = n.metadata.get("localization_precision_ms", 0) / 1000.0
        save_graph_evidence(g_event, case_dir / "event_graph", signal=event_signal)

        # 3. positive-correlation graph (MAMSE-011 clean subset)
        Z = (X - np.median(X, axis=0)) / (1.4826 * np.median(np.abs(X - np.median(X, axis=0)), axis=0) + 1e-12)
        C = np.corrcoef(Z, rowvar=False)
        g_corr = build_positive_correlation_graph(C, CLEAN_FEATURES, threshold=0.5)
        corr_signal = np.ones(len(g_corr.nodes))
        save_graph_evidence(g_corr, case_dir / "correlation_graph", signal=corr_signal)

        entry = {
            "case": case_name,
            "source": str(path),
            "duration_s": round(len(samples) / sr, 3),
            "band_graph": {
                "graph_id": g_band.graph_id,
                "dirichlet_energy": round(dirichlet_energy(g_band, band_profile), 6),
                "high_graph_frequency_ratio": round(band_energy["high_graph_frequency_ratio"], 4),
                "dc_energy_ratio": round(band_energy["dc_energy_ratio"], 4),
                "max_local_variation_node": int(np.argmax(local_variation(g_band, band_profile))),
            },
            "event_graph": {
                "graph_id": g_event.graph_id,
                "nodes": len(g_event.nodes),
                "edges": len(g_event.edges),
                "connected_components": g_event.connected_components()[0],
            },
            "correlation_graph": {
                "graph_id": g_corr.graph_id,
                "nodes": len(g_corr.nodes),
                "edges": len(g_corr.edges),
                "edge_authority": g_corr.edge_authority,
            },
        }
        summary["cases"].append(entry)
        print(f"done {case_name}: band_hf={entry['band_graph']['high_graph_frequency_ratio']:.3f} "
              f"dc={entry['band_graph']['dc_energy_ratio']:.3f} "
              f"event_n={entry['event_graph']['nodes']} corr_edges={entry['correlation_graph']['edges']}")

    (out_root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"summary -> {out_root / 'summary.json'}")


if __name__ == "__main__":
    main()
