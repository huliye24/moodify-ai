"""MAMSE-003 — wavelet & scattering-inspired auditory texture (experimental).

Texture representation operator: Morlet-like analytic carrier bank +
envelope decimation + low-frequency modulation bank. Default disabled;
explicit experimental invocation only. Scattering-inspired prototype, not
a full Kymatio/Mallat implementation.
"""

from .config import (
    CONFIG_VERSION,
    FEATURE_SCHEMA_VERSION,
    MANIFEST_SCHEMA_VERSION,
    OPERATOR_ID,
    OPERATOR_VERSION,
    TextureConfig,
)
from .sketch import TextureResult, analyze_texture
from .evidence import build_manifest, load_case, save_case

__all__ = [
    "OPERATOR_ID",
    "OPERATOR_VERSION",
    "CONFIG_VERSION",
    "FEATURE_SCHEMA_VERSION",
    "MANIFEST_SCHEMA_VERSION",
    "TextureConfig",
    "TextureResult",
    "analyze_texture",
    "build_manifest",
    "save_case",
    "load_case",
]
