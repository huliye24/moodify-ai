"""
Knowledge subsystem — 情绪工艺库 + 风险模型 (工作流 C)
"""
from moodify.knowledge.emotion_targets import (
    EMOTION_TARGETS_V2, EMOTION_ALIASES,
    resolve_emotion, get_emotion_target, get_safety_bounds,
    get_ideal_process_vector, list_all_emotions,
)
from moodify.knowledge.craft_chains import (
    CRAFT_CHAINS_15PARAMS,
    get_chain_params, get_recommended_params,
)
from moodify.knowledge.craft_chain_match import (
    CraftChainMatch, MatchResult, generate_craft_cards_from_data,
)
from moodify.knowledge.risk_model import (
    RiskModel, RiskAssessment, RiskBenefitDecider,
)
from moodify.knowledge.mpl_library import (
    MoodifyParameterLibrary, MPLEntry,
    initialize_mpl_from_craft_cards,
)
