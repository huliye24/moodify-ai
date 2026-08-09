"""DeepSeek API 客户端 — NL 情绪映射 + 诊断解读生成"""

from __future__ import annotations

import os
import json
from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════
#  Pydantic 模型
# ═══════════════════════════════════════════════════════════════

class EmotionInterpretation(BaseModel):
    emotion_code: str = Field(description="最接近的 8 情绪原型代码: GA/SE/UD/LW/HL/DR/WL/CN")
    emotion_name: str = Field(description="情绪原型中文名")
    intensity: float = Field(ge=0.3, le=1.0, description="情绪强度")
    vector_bias: dict[str, float] = Field(description="5D 理想向量微调偏置, 每维 [-0.10, 0.10]")
    reasoning: str = Field(description="推理过程, 50 字以内中文")


class DiagnosisNarrative(BaseModel):
    narrative_zh: str = Field(description="自然语言诊断报告, 2-3 句中文")
    risks: list[str] = Field(description="风险提示列表")
    suggestions: list[str] = Field(description="改进建议列表")


# ═══════════════════════════════════════════════════════════════
#  Prompt 常量
# ═══════════════════════════════════════════════════════════════

EMOTION_INTERPRETER_SYSTEM = """\
你是 Moodify 情绪波场显影引擎的情绪语义解释器。

## 已知 8 种情绪原型
| 代码 | 名称 | 核心特征 |
|------|------|---------|
| GA | 温柔觉醒 | 温暖、柔和、亲密、低频饱满、高频克制 |
| SE | 神圣空灵 | 超然、宏大、轻盈、混响深远、低频收敛 |
| UD | 都市危险 | 压迫、紧张、暗黑、压缩重、低频冲击强 |
| LW | 孤独留白 | 内省、距离、稀疏、混响深远但克制 |
| HL | 治愈温暖 | 安慰、饱满、平滑、低频温暖、谐波丰富 |
| DR | 黑暗浪漫 | 深沉、性感、神秘、中低频突出、氛围感强 |
| WL | 废土机械 | 粗粝、冲击、工业、极限压缩、高失真 |
| CN | 电影感 | 宏大、叙事、史诗、大动态、宽声场 |

## 任务
用户输入自然语言描述。你必须:
1. 映射到最接近的 8 种情绪原型之一 (不允许创造新情绪)
2. 给出强度建议
3. 给出 5D 理想向量微调偏置

## 5D 向量维度说明
- E (频率均衡度): +偏置=更明亮, -偏置=更暗沉
- D (动态呼吸感): +偏置=更起伏, -偏置=更平整
- S (空间层次感): +偏置=更宏大, -偏置=更紧致
- T (瞬态清晰度): +偏置=更锋利, -偏置=更柔和
- H (谐波丰富度): +偏置=更饱满, -偏置=更纯净

## 输出格式 (严格 JSON, 无额外文字)
{"emotion_code":"GA","emotion_name":"温柔觉醒","intensity":0.65,"vector_bias":{"E":0.03,"D":0.0,"S":-0.02,"T":0.0,"H":0.02},"reasoning":"..."}
"""

DIAGNOSIS_NARRATOR_SYSTEM = """\
你是 Moodify 的音频诊断解读师。你的任务是将处理前后的技术数据转化为用户可理解的自然语言报告。

## 输入
- 处理前的 18 参数诊断数据
- 处理后的 18 参数诊断数据
- 实际应用的 15 个 DSP 参数
- WHS/EDS 变化数值

## 输出要求
- narrative_zh: 2-3 句中文。第一句描述原始状态, 第二句描述改善效果, 第三句(可选)提示注意事项
- risks: 风险列表。如果 WHS 下降或 EDS < 40, 诚实指出
- suggestions: 改进建议。如果结果良好, 可以建议"可尝试更强的XX效果"或"可尝试不同的情绪目标"

## 约束
- 所有文字用中文
- 使用具体数值增强可信度 (如 "低频从 -6.2dB 提升到 -3.7dB")
- 风险和改善必须基于数据, 不编造
- 面向普通音乐爱好者, 避免术语堆砌

## 输出格式 (严格 JSON)
{"narrative_zh":"...","risks":["..."],"suggestions":["..."]}
"""


# ═══════════════════════════════════════════════════════════════
#  DeepSeekClient
# ═══════════════════════════════════════════════════════════════

class DeepSeekClient:
    """DeepSeek API 客户端.

    所有公开方法失败时返回 None (不抛异常).
    调用方检查返回值是否为 None 决定是否回退.
    """

    def __init__(self):
        key = os.getenv("DEEPSEEK_API_KEY")
        self._client = None
        self._model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        if key:
            try:
                from openai import OpenAI
            except ImportError:
                return
            self._client = OpenAI(
                api_key=key,
                base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            )

    @property
    def available(self) -> bool:
        return self._client is not None

    # ── 公开 API ─────────────────────────────────

    def interpret_emotion(self, nl_text: str) -> dict | None:
        """自然语言 → 结构化情绪目标."""
        user = json.dumps({"user_input": nl_text}, ensure_ascii=False)
        raw = self._call(EMOTION_INTERPRETER_SYSTEM, user)
        if raw is None:
            return None
        try:
            result = EmotionInterpretation(**raw)
            return result.model_dump()
        except Exception:
            return None

    def narrate_diagnosis(
        self,
        before_dict: dict,
        after_dict: dict,
        params: dict,
        whs_before: float,
        whs_after: float,
        eds: float,
        emotion_name: str,
    ) -> dict | None:
        """生成诊断解读."""
        user = json.dumps({
            "diagnosis_before": before_dict,
            "diagnosis_after": after_dict,
            "params_applied": {k: round(v, 2) for k, v in params.items()},
            "whs_before": round(whs_before, 1),
            "whs_after": round(whs_after, 1),
            "eds": round(eds, 1),
            "emotion_name": emotion_name,
        }, ensure_ascii=False)
        raw = self._call(DIAGNOSIS_NARRATOR_SYSTEM, user)
        if raw is None:
            return None
        try:
            result = DiagnosisNarrative(**raw)
            return result.model_dump()
        except Exception:
            return None

    def recommend_params(self, prompt: str) -> dict | None:
        """RAG-enhanced 参数推荐。输入是 assemble_rag_prompt() 的输出。

        Returns:
            {"parameters": [...], "strength_vector": {...}, "confidence": 0.82, "reasoning": "..."}
            失败返回 None
        """
        system = """\
你是 Moodify 情绪波场显影引擎的参数推荐师。

基于当前诊断数据、目标情绪、用户意图和相似历史案例, 推荐最优的处理参数和强度。

## 输出格式 (严格 JSON)
{
  "parameters": [
    {"param_name": "P01_vocal_presence_freq", "value": 3000.0},
    {"param_name": "P02_vocal_presence_gain", "value": 2.5},
    ... 共15个, 必须全部包含
  ],
  "strength_vector": {"spectrum": 0.52, "dynamic": 0.48, "space": 0.45, "layer": 0.50, "master": 0.50},
  "confidence": 0.82,
  "reasoning": "推理过程, 100字以内中文",
  "reference_case_ids": [1, 3]
}

## 规则
- 如果有相似案例, 案例参数是主要参考。需根据当前诊断的差异做调整。
- 用户不满意的案例要反向参考 (避免复现)。
- 所有值必须在安全范围内。参数值的单位遵循标准定义。
- 强度向量每维 ∈ [0.15, 0.85]。
"""
        return self._call(system, prompt)

    # ── 内部 ────────────────────────────────────

    def _call(self, system_prompt: str, user_content: str) -> dict | None:
        """调用 LLM API, 带 3 次重试. 失败返回 None.

        两种模式:
          - 如果 MODEL_SUPPORTS_SYSTEM=true: 标准 system + user 消息
          - 否则: 将 system prompt 合并到 user 消息前 (兼容不支持 system 角色的 API)
        """
        if not self.available:
            return None

        use_system_role = os.getenv("MODEL_SUPPORTS_SYSTEM", "true").lower() == "true"

        for attempt in range(3):
            try:
                if use_system_role:
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content},
                    ]
                else:
                    merged = f"[System Instruction]\n{system_prompt}\n\n[User Input]\n{user_content}"
                    messages = [{"role": "user", "content": merged}]

                r = self._client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    response_format={"type": "json_object"},
                    timeout=15.0,
                    temperature=0.2,
                )
                text = r.choices[0].message.content
                return json.loads(text)
            except Exception:
                if attempt == 2:
                    return None
        return None
