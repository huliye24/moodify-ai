"""Blinding / session engine (MFY_MOBILE_LISTENING_VALIDATION_001).

The machine owns randomisation, order consistency, dedup and assignment
bookkeeping. Randomisation is seeded and deterministic: the same protocol +
seed produces the same sessions (auditable), but the A/B order and the
Original/Moodify label mapping are unknown to the reviewer until revealed.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from moodify.listening.protocol import ListeningProtocol


@dataclass(frozen=True)
class Assignment:
    """One A/B trial as the reviewer sees it (blinded, no labels)."""

    trial_id: str
    sample_id: str
    play_a: str  # audio file played as A (either original or processed)
    play_b: str
    order_randomized: bool
    label_a: str  # ORIGINAL / PROCESSED (revealed only after judgment)
    label_b: str
    session_seed: int


@dataclass(frozen=True)
class SessionPlan:
    session_id: str
    seed: int
    assignments: tuple[Assignment, ...]


def randomize_assignment(trial_id: str, sample_id: str, audio_a: str, audio_b: str, seed: int) -> Assignment:
    """Deterministic blind assignment: same inputs -> same assignment."""
    rng = random.Random(seed)
    swap = rng.random() < 0.5
    play_a, play_b = (audio_b, audio_a) if swap else (audio_a, audio_b)
    label_a, label_b = ("PROCESSED", "ORIGINAL") if swap else ("ORIGINAL", "PROCESSED")
    return Assignment(
        trial_id=trial_id,
        sample_id=sample_id,
        play_a=play_a,
        play_b=play_b,
        order_randomized=swap,
        label_a=label_a,
        label_b=label_b,
        session_seed=seed,
    )


def build_sessions(protocol: ListeningProtocol, seed: int, sessions_per_sample: int = 1) -> list[SessionPlan]:
    """Build blinded sessions: every sample repeated `sessions_per_sample` times,
    deduped by (sample_id, seed) so a reviewer never hears the same pair twice.
    """
    rng = random.Random(seed)
    seen: set[str] = set()
    plans: list[SessionPlan] = []
    for s_idx, sample in enumerate(protocol.samples):
        for rep in range(sessions_per_sample):
            session_seed = rng.randint(0, 2**31 - 1)
            dedup_key = f"{sample.sample_id}:{session_seed}"
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
            processed = sample.processed_wav or sample.input_wav  # placebo replays input
            assignment = randomize_assignment(
                trial_id=f"trial_{s_idx}_{rep}",
                sample_id=sample.sample_id,
                audio_a=sample.input_wav,
                audio_b=processed,
                seed=session_seed,
            )
            plans.append(
                SessionPlan(
                    session_id=f"session_{len(plans):03d}",
                    seed=session_seed,
                    assignments=(assignment,),
                )
            )
    return plans
