"""SPEC-010: EDSR 校准数据分析 — Bradley-Terry 建模 + 相关性计算。

用法:
  python calibration/analyze.py \
    --ratings calibration/ratings_L01_2026-05-29.jsonl \
    --proxy calibration/proxy_scores.json \
    --output calibration/correlation_report.md
"""

import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.optimize import minimize
from scipy.stats import spearmanr, kendalltau

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def load_ratings(ratings_path: str) -> list[dict]:
    """加载 JSONL 格式的评价数据。"""
    ratings = []
    with open(ratings_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                ratings.append(json.loads(line))
    return ratings


def fit_bradley_terry(ratings: list[dict]) -> dict[str, float]:
    """从 A/B 比较数据拟合 Bradley-Terry 模型。

    只使用 choice ∈ {"A", "B"} 的比较。忽略 tie。
    """
    # 收集所有版本
    versions = set()
    for r in ratings:
        versions.add(r["version_a"])
        versions.add(r["version_b"])
    version_list = sorted(versions)
    idx = {v: i for i, v in enumerate(version_list)}
    n = len(version_list)

    # 过滤有效比较
    valid = [r for r in ratings if r["choice"] in ("A", "B")]

    def neg_ll(theta):
        ll = 0.0
        for r in valid:
            i = idx[r["version_a"]]
            j = idx[r["version_b"]]
            winner = i if r["choice"] == "A" else j
            loser = j if r["choice"] == "A" else i
            w = r.get("confidence", 3)
            prob = np.exp(theta[winner]) / (np.exp(theta[winner]) + np.exp(theta[loser]) + 1e-10)
            ll += np.log(max(prob, 1e-10)) * w
        return -ll

    result = minimize(neg_ll, np.zeros(n), method="L-BFGS-B")
    return {v: float(result.x[i]) for v, i in idx.items()}


def compute_listener_reliability(ratings: list[dict]) -> dict[str, dict]:
    """计算每位听众的信度: 重复一致性 + 锚定对准确率。"""
    by_listener = defaultdict(list)
    for r in ratings:
        by_listener[r["listener_id"]].append(r)

    reliability = {}
    for lid, rats in by_listener.items():
        # 重复一致性
        repeats = [r for r in rats if r.get("is_repeat")]
        consistent = 0
        for rep in repeats:
            original = next((r for r in rats
                           if r["version_a"] == rep["version_a"]
                           and r["version_b"] == rep["version_b"]
                           and not r.get("is_repeat")), None)
            if original and original["choice"] == rep["choice"]:
                consistent += 1
        repeat_rate = consistent / max(len(repeats), 1)

        # 锚定对准确率
        anchors = [r for r in rats if r.get("is_anchor")]
        anchor_correct = 0
        for a in anchors:
            # 锚定对: extreme vs preset, preset 应该被偏好
            if "extreme" in a["version_a"] and "preset" in a["version_b"] and a["choice"] == "B":
                anchor_correct += 1
            elif "extreme" in a["version_b"] and "preset" in a["version_a"] and a["choice"] == "A":
                anchor_correct += 1
        anchor_rate = anchor_correct / max(len(anchors), 1)

        reliability[lid] = {
            "total_pairs": len(rats),
            "repeat_consistency": round(repeat_rate, 3),
            "anchor_accuracy": round(anchor_rate, 3),
            "reliable": repeat_rate >= 0.6 and anchor_rate >= 0.5,
        }
    return reliability


def analyze_correlation(bt_theta: dict[str, float], proxy_scores: dict) -> dict:
    """计算 Bradley-Terry θ 与 EDSR_proxy 的秩相关。"""
    common = set(bt_theta.keys()) & set(proxy_scores.keys())
    if len(common) < 5:
        return {"error": f"Only {len(common)} common versions, need >= 5"}

    versions = sorted(common)
    bt_vals = [bt_theta[v] for v in versions]
    px_vals = [proxy_scores[v].get("whs", 50) for v in versions]

    rho, p_rho = spearmanr(bt_vals, px_vals)
    tau, p_tau = kendalltau(bt_vals, px_vals)

    verdict = "usable" if rho >= 0.5 else ("mixed" if rho >= 0.3 else "unusable")

    return {
        "n_versions": len(versions),
        "spearman_rho": round(rho, 3),
        "spearman_p": round(p_rho, 4),
        "kendall_tau": round(tau, 3),
        "kendall_p": round(p_tau, 4),
        "verdict": verdict,
    }


def find_failure_samples(bt_theta: dict, proxy_scores: dict, top_n: int = 10) -> list[dict]:
    """找出代理排名与 Bradley-Terry 排名差距最大的样本。"""
    versions = sorted(set(bt_theta.keys()) & set(proxy_scores.keys()))
    bt_rank = {v: i for i, v in enumerate(sorted(versions, key=lambda x: bt_theta[x], reverse=True))}
    px_rank = {v: i for i, v in enumerate(sorted(versions, key=lambda x: proxy_scores.get(x, {}).get("whs", 0), reverse=True))}

    failures = []
    for v in versions:
        gap = abs(bt_rank[v] - px_rank[v])
        if gap >= 3:
            failures.append({
                "version": v,
                "bt_theta": round(bt_theta[v], 3),
                "bt_rank": bt_rank[v],
                "proxy_whs": proxy_scores.get(v, {}).get("whs", 0),
                "px_rank": px_rank[v],
                "rank_gap": gap,
            })
    failures.sort(key=lambda x: x["rank_gap"], reverse=True)
    return failures[:top_n]


def generate_report(correlation: dict, reliability: dict, failures: list, output_path: str):
    """生成 Markdown 校准报告。"""
    lines = [
        "# EDSR 校准报告",
        "",
        "**日期**: 2026-05-29",
        f"**可用版本数**: {correlation.get('n_versions', 0)}",
        "",
        "## 1. 代理指标 vs 人耳偏好",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| Spearman ρ | {correlation.get('spearman_rho', 'N/A')} |",
        f"| Spearman p | {correlation.get('spearman_p', 'N/A')} |",
        f"| Kendall τ | {correlation.get('kendall_tau', 'N/A')} |",
        f"| Kendall p | {correlation.get('kendall_p', 'N/A')} |",
        f"| **判断** | **{correlation.get('verdict', 'N/A')}** |",
        "",
    ]

    verdict = correlation.get("verdict", "")
    if verdict == "usable":
        lines += ["✅ ρ ≥ 0.5 — 代理指标可用于搜索排序"]
    elif verdict == "mixed":
        lines += ["⚠ ρ ∈ [0.3, 0.5) — 代理指标只能用于粗筛(top-50)"]
    else:
        lines += ["❌ ρ < 0.3 — 代理指标需要重构, 不能用于排序"]

    lines += [
        "",
        "## 2. 听众信度",
        "",
        "| 听众 | 比较数 | 重复一致性 | 锚定准确率 | 可信 |",
        "|------|--------|-----------|-----------|------|",
    ]
    for lid, info in reliability.items():
        status = "✓" if info["reliable"] else "⚠"
        lines.append(f"| {lid} | {info['total_pairs']} | {info['repeat_consistency']} | {info['anchor_accuracy']} | {status} |")

    lines += [
        "",
        "## 3. 失败样本 (|proxy_rank - true_rank| ≥ 3)",
        "",
    ]
    if failures:
        lines += ["| 版本 | BT θ | BT rank | Proxy WHS | Proxy rank | 差距 |",
                  "|------|------|---------|-----------|------------|------|"]
        for f in failures:
            lines.append(f"| {f['version'][:40]} | {f['bt_theta']} | {f['bt_rank']} | {f['proxy_whs']} | {f['px_rank']} | {f['rank_gap']} |")
    else:
        lines += ["无显著失败样本"]

    report = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ratings", required=True, nargs="+", help="JSONL 评价文件")
    parser.add_argument("--proxy", required=True, help="proxy_scores.json")
    parser.add_argument("--output", default="calibration/correlation_report.md")
    args = parser.parse_args()

    # 加载数据
    all_ratings = []
    for path in args.ratings:
        all_ratings.extend(load_ratings(path))
    print(f"Loaded {len(all_ratings)} ratings from {len(args.ratings)} files")

    with open(args.proxy, "r", encoding="utf-8") as f:
        proxy_scores = json.load(f)
    print(f"Loaded proxy scores for {len(proxy_scores)} versions")

    # Bradley-Terry
    bt_theta = fit_bradley_terry(all_ratings)
    print(f"Bradley-Terry fitted: {len(bt_theta)} versions")

    # 听众信度
    reliability = compute_listener_reliability(all_ratings)
    reliable_count = sum(1 for r in reliability.values() if r["reliable"])
    print(f"Listener reliability: {reliable_count}/{len(reliability)} reliable")

    # 相关性
    correlation = analyze_correlation(bt_theta, proxy_scores)

    # 失败样本
    failures = find_failure_samples(bt_theta, proxy_scores)

    # 报告
    report = generate_report(correlation, reliability, failures, args.output)
    print(f"\n{report}")
    print(f"\nReport saved to {args.output}")


if __name__ == "__main__":
    main()
