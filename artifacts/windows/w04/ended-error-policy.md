# Ended and Error Policy

On ended, the current snapshot first becomes ENDED with final position. The existing renderer subscriber requests `next`. If context has a next Track it loads and autoplays; otherwise next is a no-op and ENDED/current Track remain visible. Stale ended is discarded and cannot skip the new Track.

Errors do not auto-skip in W04. Source unavailable, load/decode failure and play rejection become recoverable ERROR states with current Track retained. A later valid load clears the error. This avoids error loops before W05 owns formal Queue advancement.
