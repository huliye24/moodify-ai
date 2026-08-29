"""RAG prompt 组装: 诊断 + 相似案例 + 用户意图 → LLM prompt"""
import json


def assemble_rag_prompt(
    diagnosis_dict: dict,
    defects_list: list[dict],
    emotion_name: str,
    user_intent: str,
    similar_cases: list[dict],
) -> str:
    parts = []

    parts.append("## 当前诊断\n")
    parts.append("```json\n" + json.dumps(diagnosis_dict, ensure_ascii=False, indent=2) + "\n```\n")

    if defects_list:
        parts.append("## 检测到的缺陷\n")
        for d in defects_list:
            parts.append(f"- {d['parameter']}: severity={d['severity']}\n")

    parts.append(f"\n## 目标情绪\n{emotion_name}\n")

    if user_intent:
        parts.append(f"\n## 用户意图\n{user_intent}\n")
    else:
        parts.append(f"\n## 用户意图\n自动推断: 向{emotion_name}方向处理\n")

    if similar_cases:
        parts.append(f"\n## 相似案例 (共{len(similar_cases)}个, 来自本地处理历史)\n")
        for i, case in enumerate(similar_cases):
            sim = case.get("similarity", 0)
            params = case.get("params", {})
            feedback = case.get("feedback", "")
            whs_d = case.get("whs_delta", 0)
            satisfied = case.get("satisfied", True)
            strength = case.get("strength_vector", {})

            status = "满意" if satisfied else "不满意"
            parts.append(f"### 案例 {i+1} (相似度: {sim:.2f}, 用户{status})\n")
            parts.append(f"WHS变化: +{whs_d}\n")
            if feedback:
                parts.append(f"用户反馈: {feedback}\n")
            if strength:
                sp = strength.get("spectrum", 0)
                dy = strength.get("dynamic", 0)
                sc = strength.get("space", 0)
                la = strength.get("layer", 0)
                parts.append(f"5D强度: spectrum={sp:.2f}, dynamic={dy:.2f}, space={sc:.2f}, layer={la:.2f}\n")

            non_zero = {k: round(v, 2) for k, v in params.items() if abs(v) > 0.01}
            if non_zero:
                parts.append("使用的参数:\n")
                for k, v in list(non_zero.items())[:8]:
                    parts.append(f"  {k} = {v}\n")
            parts.append("\n")
    else:
        parts.append("\n## 相似案例\n无 (知识库为空, 请基于诊断数据推理)\n")

    parts.append("请基于以上信息, 输出推荐的处理强度和参数。输出严格的 JSON 格式。\n")
    return "".join(parts)


def format_cases_for_prompt(
    similar: list[tuple],
) -> list[dict]:
    """ProcessingHistory.find_similar() 输出 → prompt 可用格式"""
    cases = []
    for rec, sim in similar:
        cases.append({
            "similarity": round(sim, 3),
            "params": rec.params,
            "strength_vector": rec.strength_vector,
            "whs_delta": round(rec.whs_after - rec.whs_before, 1),
            "satisfied": rec.satisfied is None or rec.satisfied,
            "feedback": rec.user_feedback or "",
        })
    return cases
