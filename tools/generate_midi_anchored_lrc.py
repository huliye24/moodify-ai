"""Generate a line-level LRC from lyrics and a vocal MIDI timing scaffold."""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from score_asset_pipeline import parse_notes


LYRICS = """Nous pouvons nous reconnaître encore
Non parce que le passé ne compte pas
Mais parce qu'il serait dommage
D'en faire une carte trop ancienne
Dis-moi ce que tu aimes maintenant
Ce qui te fatigue, ce qui t'appelle
Les phrases que tu ne veux plus entendre
Les souhaits qui ont poussé plus tard
Si nous ne mettons pas nos cartes à jour
Nous heurterons les vieux murs
En croyant nous connaître assez
Nous manquerons nos saisons nouvelles
Nous pouvons nous reconnaître encore
Comme au début, mais plus doucement
Demander : comment vas-tu vraiment ?
Et attendre une réponse vivante
Nous pouvons nous reconnaître encore
Je t'offrirai le nouveau moi aussi
Pas caché derrière : tu devrais savoir
Mais remis dans tes mains avec soin
J'ai changé dans certains endroits
Je suis moins pressé, peut-être plus fermé
J'ai des blessures qui parlent bas
Et des courages qui commencent à pousser
Toi aussi, tu as tes nouveaux contours
Tes silences, tes détours, tes besoins
Et si nous voulons rester proches
Il faudra apprendre ces chemins
L'intimité n'est pas
Ne plus jamais se présenter
C'est revenir plusieurs fois
Avec la vérité du moment
Nous pouvons nous reconnaître encore
Et le temps ne nous éloignera pas seulement
Il nous donnera plusieurs chances
De nous rencontrer dans la même personne
Nous pouvons nous reconnaître encore
Si tu veux, recommençons très simplement
Dis-moi où tu es aujourd'hui
Je veux approcher sans te perdre""".splitlines()


def midi_segments(midi: Path, cluster_window: float = 0.12) -> list[tuple[float, float, float]]:
    notes = sorted(parse_notes(midi), key=lambda note: (note.start, note.end))
    raw = sorted((note.start / 960.0, note.end / 960.0) for note in notes if note.end > note.start)
    clustered: list[list[float]] = []
    for start, end in raw:
        if not clustered or start - clustered[-1][0] > cluster_window:
            clustered.append([start, end])
        else:
            clustered[-1][1] = max(clustered[-1][1], end)
    result = []
    previous_active_end = clustered[0][0]
    for start, end in clustered:
        result.append((start, end, max(0.0, start - previous_active_end)))
        previous_active_end = max(previous_active_end, end)
    return result


def line_weights(lines: list[str]) -> list[float]:
    # Character count is a useful weak prior for sung French line duration.
    return [max(16.0, len(line.replace(" ", "")) ** 0.82) for line in lines]


def select_starts(segments: list[tuple[float, float, float]], lines: list[str]) -> list[float]:
    candidates = [segment for segment in segments if segment[0] < 170.0]
    count = len(lines)
    weights = line_weights(lines)
    first = 0
    # The vocal-MIDI events after 170 s are low-confidence outro artifacts.
    last = min(range(len(candidates)), key=lambda i: abs(candidates[i][0] - 163.18))
    total = candidates[last][0] - candidates[first][0]
    scale = total / sum(weights[:-1])
    expected = [weight * scale for weight in weights[:-1]]

    inf = float("inf")
    dp = [[inf] * len(candidates) for _ in range(count)]
    prev = [[-1] * len(candidates) for _ in range(count)]
    dp[0][first] = 0.0

    for line_index in range(1, count):
        expected_gap = expected[line_index - 1]
        for current in range(line_index, last + 1):
            current_time = candidates[current][0]
            silence = candidates[current][2]
            stanza_bonus = 0.6 if line_index % 4 == 0 else 0.0
            for prior in range(line_index - 1, current):
                if math.isinf(dp[line_index - 1][prior]):
                    continue
                gap = current_time - candidates[prior][0]
                if gap < 1.35 or gap > 7.5:
                    continue
                duration_cost = ((gap - expected_gap) / max(1.2, expected_gap)) ** 2
                boundary_reward = min(silence, 1.5) * (0.32 + stanza_bonus)
                cost = dp[line_index - 1][prior] + duration_cost - boundary_reward
                if cost < dp[line_index][current]:
                    dp[line_index][current] = cost
                    prev[line_index][current] = prior

    cursor = last
    chosen = [cursor]
    for line_index in range(count - 1, 0, -1):
        cursor = prev[line_index][cursor]
        if cursor < 0:
            raise RuntimeError("Unable to align all lyric lines to MIDI candidates")
        chosen.append(cursor)
    chosen.reverse()
    return [candidates[index][0] for index in chosen]


def lrc_stamp(seconds: float) -> str:
    minutes = int(seconds // 60)
    remainder = seconds - minutes * 60
    return f"[{minutes:02d}:{remainder:05.2f}]"


def main() -> None:
    midi = next(Path(r"E:\moodify\pre-music").glob("*/*_vocals_28.mid"))
    starts = select_starts(midi_segments(midi), LYRICS)
    rows = [
        "[ti:Nous pouvons nous reconnaître encore]",
        "[by:Moodify MIDI + vocal alignment]",
        "[offset:0]",
        "",
    ]
    rows.extend(f"{lrc_stamp(start)}{line}" for start, line in zip(starts, LYRICS))
    print("\n".join(rows))


if __name__ == "__main__":
    main()
