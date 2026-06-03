"""
歌词生成模块 - 调用 DeepSeek API 生成歌词
"""
import os
import random
from typing import Optional, Dict, Any, List
from openai import OpenAI

from character import Character

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# 随机创意因子池 - 用于增加生成多样性，模拟摇色子的随机效果
RANDOM_CREATIVE_HINTS = [
    "想象你正站在一个陌生城市的路口，霓虹灯刚刚亮起",
    "回想起某个遥远的下午，阳光透过窗帘的缝隙",
    "此刻窗外的雨声让你想起了很久以前的某件事",
    "你在人群中独自走着，周围很嘈杂但你很安静",
    "一封从未寄出的信，一段没有说完的话",
    "午夜电台的 DJ 正在播放一首你从未听过的歌",
    "地铁在隧道里疾驰，窗外是无尽的黑暗和偶尔闪过的灯光",
    "老唱片在留声机上缓缓转动，时间仿佛慢了下来",
    "你站在海边，看着潮水一遍遍冲刷着沙滩上的脚印",
    "咖啡杯里的热气袅袅升起，像极了某段消散的记忆",
    "一个已经褪色的照片，让你想起那个再也回不去的夏天",
    "火车跨过大桥，远处的山峦在晨雾中若隐若现",
    "街角的路灯忽明忽暗，像是在等待什么人",
    "窗外飘落的樱花瓣，让你想起了某个人的笑容",
    "凌晨三点的便利店，店员在打瞌睡",
    "旧抽屉里翻出的车票，目的地已经模糊",
    "收音机里传出的老歌，每个音符都在说着再见",
    "雨后的街道反射着霓虹，像另一个世界的倒影",
    "一个人的电影院，银幕上在播别人的故事",
    "天台上的风很大，吹散了所有心事",
    "图书馆角落的窗边，阳光刚好落在翻开的书页上",
    "离别时没有说出口的话，化作了沉默",
    "那家老店的咖啡已经凉了，就像某些关系",
    "火车鸣笛驶过站台，带走了所有犹豫",
]

# 歌词开头风格库（按人物风格偏好映射）
LYRICS_OPENING_STYLES = {
    "内向敏感": [
        "轻声地", "静静地", "慢慢地", "轻轻地",
        "在深夜", "在角落", "在梦里", "在风里",
        "像影子一样", "独自地", "沉默地", "安静地"
    ],
    "开朗乐观": [
        "大步地", "欢快地", "阳光地", "飞扬地",
        "向前走", "抬起头", "迎着风", "唱起歌",
        "带着微笑", "奔向前方", "拥抱着", "跳动着"
    ],
    "深沉内敛": [
        "沉默地", "深沉地", "缓缓地", "静静地",
        "在远方", "在心底", "在黑暗", "在深处",
        "如深海", "若山岳", "似长夜", "如旧梦"
    ],
    "叛逆不羁": [
        "嘶吼地", "狂野地", "不羁地", "自由地",
        "打破", "挣脱", "燃烧", "冲破",
        "撕裂", "粉碎", "冲撞", "燃烧殆尽"
    ],
    "温柔细腻": [
        "柔软地", "温柔地", "细腻地", "温暖地",
        "像风", "像雨", "像光", "像你",
        "如初雪", "若暖阳", "似流水", "如花开"
    ],
    "热情奔放": [
        "热烈地", "奔放地", "激情地", "澎湃地",
        "燃烧", "绽放", "追逐", "拥抱",
        "席卷", "席卷", "燃烧", "绽放"
    ],
    "忧郁文艺": [
        "诗意地", "文艺地", "忧郁地", "哀伤地",
        "如诗", "如画", "如梦", "如烟",
        "似雾", "若风", "如雨", "若云"
    ],
    "理性冷静": [
        "冷静地", "理性地", "克制地", "有序地",
        "如同", "按照", "遵循", "经过",
        "审视着", "分析着", "记录着", "梳理着"
    ],
}

# 歌词意象库 - 用于增加意象多样性
LYRIC_IMAGERY = {
    "自然": [
        "月光", "星光", "夕阳", "晨雾", "细雨", "春风",
        "落叶", "樱花", "潮汐", "山峦", "森林", "沙漠",
        "雪花", "彩虹", "云朵", "雷电", "露珠", "枫叶",
        "海浪", "礁石", "河流", "飞鸟", "蝴蝶", "蜻蜓"
    ],
    "城市": [
        "霓虹灯", "路灯", "地铁站", "便利店", "天台",
        "咖啡馆", "天桥", "地下通道", "写字楼", "旧仓库",
        "公交站", "火车站", "机场", "停车场", "天桥"
    ],
    "物品": [
        "旧吉他", "老唱片", "褪色照片", "车票", "信封",
        "手表", "戒指", "围巾", "钥匙", "书本",
        "钢笔", "相机", "雨伞", "背包", "相框"
    ],
    "感官": [
        "汽笛声", "雨滴声", "心跳声", "脚步声", "叹息声",
        "咖啡香", "泥土味", "旧书香", "雨后气息",
        "暖阳", "凉风", "夜露", "热茶", "微光"
    ],
    "时间": [
        "凌晨三点", "黄昏时分", "午夜", "破晓", "日落",
        "四季更迭", "岁月流逝", "时光倒流", "刹那间",
        "漫长的夜", "短暂的春", "永恒的瞬间"
    ],
}

# 歌词结尾风格库
LYRICS_CLOSING_STYLES = [
    "留下余韵", "戛然而止", "渐行渐远", "回到原点",
    "开放式结局", "留下悬念", "归于平静", "情绪升华",
    "回归内心", "留白想象", "突然终止", "缓缓消散",
    "回到第一句的情绪", "从一个意象跳到另一个", "突然转向"
]

# 歌词转折点位置库
LYRIC_TURNING_POINTS = [
    "第一段主歌结尾", "副歌之后", "第二段主歌开头",
    "桥段之前", "最后一句前", "整首歌中间",
    "第一句就开始转折", "留到最后一句才揭示"
]

# 歌词视角变化库
LYRIC_PERSPECTIVE_CHANGES = [
    "无视角变化，从头到尾第一人称",
    "从第三人称旁观视角描述",
    "与另一个人对话的形式",
    "现在与回忆交织",
    "问句结尾，引发思考",
    "自我质疑和对话",
    "从你到我，视角转换"
]

# 歌词押韵风格库
RHYMING_STYLES = [
    "随性押韵，不刻意追求",
    "句尾押韵，读起来有节奏感",
    "每两句押一次韵",
    "段落内押韵，段落间换韵",
    "交叉押韵，ABAB格式",
    "近似押韵，不要求完全一致",
    "跳韵，隔句押不同韵"
]

# 歌词修辞手法库
LYRIC_RHETORIC = [
    "比喻：把抽象情绪具象化",
    "拟人：赋予自然万物情感",
    "排比：增强气势和节奏",
    "反复：强调核心情感",
    "设问：引发共鸣和思考",
    "通感：感官体验交织",
    "白描：简单直白却动人",
    "留白：不说完，让读者想象",
    "象征：用具体事物代表情感",
    "反讽：以乐写哀或以哀写乐"
]


class LyricsGenerator:
    """歌词生成器"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.client = None
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )

    def is_configured(self) -> bool:
        """检查是否已配置"""
        return self.client is not None

    def _generate_random_seed(self, character: Character) -> str:
        """生成随机种子字符串，模拟摇色子的随机效果"""
        seed_parts = [
            str(random.randint(1000, 9999)),
            random.choice(RANDOM_CREATIVE_HINTS),
        ]
        if character.background:
            bg_keywords = character.background[:80].replace("。", " ").replace("，", " ").replace("、", " ").split()
            if bg_keywords:
                seed_parts.append(random.choice([k for k in bg_keywords if len(k) > 1]))

        # 额外掷一个"色子"：随机选择意象类别
        imagery_category = random.choice(list(LYRIC_IMAGERY.keys()))
        imagery = random.choice(LYRIC_IMAGERY[imagery_category])
        seed_parts.append(f"意象关键词：{imagery}（来自{imagery_category}类）")

        return " | ".join(seed_parts)

    def _roll_dice_for_creative_variation(self) -> dict:
        """模拟掷多个色子，生成创意变化参数"""
        return {
            "closing_style": random.choice(LYRICS_CLOSING_STYLES),
            "turning_point": random.choice(LYRIC_TURNING_POINTS),
            "perspective": random.choice(LYRIC_PERSPECTIVE_CHANGES),
            "rhetoric": random.choice(LYRIC_RHETORIC),
            "imagery_count": random.randint(2, 5),
            "use_repetition": random.choice([True, False]),
            "line_length_variation": random.choice(["统一长度", "长短交错", "短句为主", "长句铺陈"]),
        }

    def _build_history_context(self, recent_o3ics: List[str]) -> str:
        """构建历史上下文，避免重复生成"""
        if not recent_o3ics:
            return ""

        context = "\n\n⚠️ 请注意：以下是你最近创作的歌词片段，请避免使用相同的意象、词汇和表达方式：\n"
        for i, o3ic in enumerate(recent_o3ics[:3], 1):
            preview = o3ic[:100] if len(o3ic) > 100 else o3ic
            context += f"\n{i}. {preview}..."
        context += "\n\n请创作一段全新的歌词，使用不同的意象和表达！"
        return context

    def _get_opening_hint(self, personality: str) -> str:
        """获取符合人物性格的开头提示（从扩充后的库中随机选择）"""
        openings = LYRICS_OPENING_STYLES.get(personality, ["静静地"])
        chosen = random.choice(openings)
        return f"歌词开头可以用「{chosen}」这样的方式，营造符合你性格的氛围。"

    def generate(
        self,
        character: Character,
        structure: str = "verse-chorus",
        length: str = "medium",
        rhyme_hint: str = "押大致相近的韵",
        custom_requirements: str = "",
        model: str = "deepseek-chat",
        recent_o3ics: List[str] = None,
        temperature: float = 0.95,
        top_p: float = 0.85
    ) -> str:
        """
        生成歌词

        Args:
            character: 虚拟人物对象
            structure: 歌词结构 (verse-chorus, simple, full)
            length: 长度 (short, medium, long)
            rhyme_hint: 韵脚提示
            custom_requirements: 自定义要求
            model: 使用的模型
            recent_o3ics: 最近生成的歌词列表（用于避免重复）
            temperature: 随机性参数，默认0.95更高
            top_p: 采样核概率，默认0.85

        Returns:
            生成的歌词文本
        """
        if not self.is_configured():
            raise ValueError("DeepSeek API 未配置或 API Key 无效")

        user_message = self._build_user_message(
            character=character,
            structure=structure,
            length=length,
            rhyme_hint=rhyme_hint,
            custom_requirements=custom_requirements,
            recent_o3ics=recent_o3ics or []
        )

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": character.get_system_prompt()},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            top_p=top_p,
            max_tokens=1200,
        )

        o3ics = response.choices[0].message.content.strip()
        return o3ics

    def _build_user_message(
        self,
        character: Character,
        structure: str,
        length: str,
        rhyme_hint: str,
        custom_requirements: str,
        recent_o3ics: List[str]
    ) -> str:
        """构建用户消息，融入掷色子产生的创意变化"""

        structure_map = {
            "verse-chorus": "两段主歌、一段副歌（重复两遍）、一段桥段。每段4行。",
            "simple": "一段主歌加一段副歌，每段4行。",
            "full": "两段主歌、两段副歌、一段桥段，每段4行。",
            "free": "一段自由形式的歌词，大约8-12行，不强制分段。",
        }
        structure_desc = structure_map.get(structure, structure_map["verse-chorus"])

        length_map = {
            "short": "简短精炼，4-8行",
            "medium": "中等长度，12-16行",
            "long": "较长篇幅，20-24行或更多",
        }
        length_desc = length_map.get(length, length_map["medium"])

        # 掷色子产生创意变化
        random_seed = self._generate_random_seed(character)
        opening_hint = self._get_opening_hint(character.personality)
        history_context = self._build_history_context(recent_o3ics)
        dice_result = self._roll_dice_for_creative_variation()

        message = f"""🎲 摇色子结果：本次创作的创意参数
━━━━━━━━━━━━━━━━━━
🎯 创意种子：{random_seed}
🎭 结尾风格：{dice_result['closing_style']}
🔄 转折位置：{dice_result['turning_point']}
👁️ 叙事视角：{dice_result['perspective']}
✍️ 修辞手法：{dice_result['rhetoric']}
📏 句长变化：{dice_result['line_length_variation']}
━━━━━━━━━━━━━━━━━━

情绪状态：{character.current_mood}

{opening_hint}

请以第一人称写一段歌词，表达此刻的心情。

要求：
- {structure_desc}
- 长度：{length_desc}
- 韵脚：{rhyme_hint}
- 歌词应该体现{character.name}的性格特点（{character.personality}）和音乐风格偏好（{character.music_style}）"""

        if character.o3ic_style:
            message += f"\n- 歌词风格：{character.o3ic_style}"

        if custom_requirements:
            message += f"\n- 额外要求：{custom_requirements}"

        message += f"\n\n请直接输出歌词，不要加标题或解释。{history_context}"

        return message

    def generate_with_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "deepseek-chat",
        temperature: float = 0.9
    ) -> str:
        """
        使用自定义提示词生成

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            model: 使用的模型
            temperature: 随机性参数

        Returns:
            生成的文本
        """
        if not self.is_configured():
            raise ValueError("DeepSeek API 未配置或 API Key 无效")

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=1000,
        )

        return response.choices[0].message.content.strip()


# 全局生成器实例
_generator: Optional[LyricsGenerator] = None


def get_generator() -> LyricsGenerator:
    """获取全局生成器实例"""
    global _generator
    if _generator is None:
        _generator = LyricsGenerator()
    return _generator


def reset_generator():
    """重置生成器（用于重新加载配置）"""
    global _generator
    _generator = None
