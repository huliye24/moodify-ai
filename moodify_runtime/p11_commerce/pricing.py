# MFY-CR-P11 — Server-Side Pricing Policy
"""
All prices are server-side configurable.
Android MUST NOT hardcode or trust any price.

Pricing versioning ensures historical orders can always be reconstructed
with the exact rules that were in effect at the time of the transaction.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Dict, Optional

from .models import CNY, DEFAULT_PRICING_VERSION


@dataclass
class PricingRule:
    """A single versioned pricing rule."""
    version: str = DEFAULT_PRICING_VERSION
    currency: str = CNY
    unit_amount_minor: int = 100  # 1 CNY in fen (分)
    description: str = "Default v0.1 pricing"
    active: bool = True
    created_at: float = 0.0

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "currency": self.currency,
            "unit_amount_minor": self.unit_amount_minor,
            "description": self.description,
            "active": self.active,
            "created_at": self.created_at,
        }


class PricingPolicy:
    """Thread-safe server-side pricing authority.

    Usage:
        policy = PricingPolicy()
        policy.set_rule(PricingRule(version="v0.1.0", unit_amount_minor=100))
        rule = policy.get_active_rule()  # -> PricingRule
        historical = policy.get_rule("v0.1.0")  # for old order audit
    """

    _instance: Optional["PricingPolicy"] = None
    _lock: threading.Lock = threading.Lock()

    def __init__(self):
        self._rules: Dict[str, PricingRule] = {}
        self._default_version = DEFAULT_PRICING_VERSION

    @classmethod
    def get_instance(cls) -> "PricingPolicy":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def set_rule(self, rule: PricingRule) -> None:
        """Register a pricing rule. Overwrites existing version."""
        with self._lock:
            self._rules[rule.version] = rule

    def get_active_rule(self) -> Optional[PricingRule]:
        """Get the currently active pricing rule."""
        with self._lock:
            for rule in self._rules.values():
                if rule.active:
                    return rule
            return None

    def get_rule(self, version: str) -> Optional[PricingRule]:
        """Get a specific version (for historical order reconstruction)."""
        with self._lock:
            return self._rules.get(version)

    def list_rules(self) -> list:
        """List all registered rules."""
        with self._lock:
            return [r.to_dict() for r in self._rules.values()]

    def quote_amount(self, quantity: int = 1, version: Optional[str] = None) -> int:
        """Calculate total amount for a given quantity.

        Returns amount in minor units (fen for CNY).
        """
        rule = self.get_rule(version) if version else self.get_active_rule()
        if rule is None:
            raise ValueError("No active pricing rule configured")
        return rule.unit_amount_minor * quantity

    def activate_version(self, version: str) -> bool:
        """Activate a specific version, deactivating all others."""
        with self._lock:
            found = False
            for rule in self._rules.values():
                if rule.version == version:
                    rule.active = True
                    found = True
                else:
                    rule.active = False
            return found


# ---------------------------------------------------------------------------
# Default bootstrap: register v0.1 pricing on first import
# ---------------------------------------------------------------------------

def _bootstrap_default_pricing() -> PricingPolicy:
    """Initialize with default v0.1 pricing rule."""
    import time as _time
    policy = PricingPolicy.get_instance()
    default_rule = PricingRule(
        version=DEFAULT_PRICING_VERSION,
        currency=CNY,
        unit_amount_minor=100,  # ¥1.00
        description="Moodify Reconstruction v0.1 — single track",
        active=True,
        created_at=_time.time(),
    )
    policy.set_rule(default_rule)
    return policy


_bootstrap_default_pricing()
