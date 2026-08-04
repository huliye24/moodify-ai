"""
Processing subsystem — DSP 算子 (工作流 B)
"""
from moodify.processing.operators import (
    OPERATOR_REGISTRY,
    apply_eq, apply_compressor, apply_reverb,
    apply_stereo_enhancer, apply_limiter, apply_chain,
)
from moodify.processing.pedalboard_chain import (
    MoodifyDSPChain, create_chain_from_code,
)
from moodify.processing.rbj_eq import (
    COEFF_FUNCTIONS,
    apply_rbj_eq,
    compute_freq_response,
    cascade_freq_response,
    rbj_low_shelf_coeffs,
    rbj_high_shelf_coeffs,
    rbj_peaking_coeffs,
    rbj_highpass_coeffs,
    rbj_lowpass_coeffs,
)
from moodify.processing.spectral_chain import SpectralDSPChain
from moodify.processing.limiter import (
    LimiterAudit,
    apply_limiter_tp,
    apply_limiter_legacy,
    measure_true_peak,
    measure_low_freq_thd,
)
