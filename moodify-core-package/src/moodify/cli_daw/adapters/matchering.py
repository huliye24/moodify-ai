"""matchering adapter — Python API, reference mastering."""
import time
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class AdapterEvidence:
    tool: str; action: str; command: list[str] = field(default_factory=list)
    exit_code: int = -1; stdout: str = ""; stderr: str = ""
    output_path: str = ""; elapsed_s: float = 0.0

class MatcheringAdapter:
    name = "matchering"
    def probe(self) -> dict:
        try:
            import matchering
            return {"status":"available","tool":"matchering","version":getattr(matchering,'__version__','2.0.6')}
        except ImportError: return {"status":"UNAVAILABLE","tool":"matchering","error":"not installed"}

    def capabilities(self) -> dict:
        return {"tool":"matchering","actions":["match_reference"]}

    def execute(self, action: str, params: dict, output_dir: Path) -> AdapterEvidence:
        if action != "match_reference":
            return AdapterEvidence(tool="matchering",action=action,exit_code=-1,stderr=f"Unknown action: {action}")
        try:
            import matchering as m
            t0 = time.perf_counter()
            target = params["target"]
            reference = params["reference"]
            out = str(output_dir / params.get("output","mastered.wav"))
            m.process(target=target, reference=reference, results=[m.pcm24(out)])
            return AdapterEvidence(tool="matchering",action=action,output_path=out,exit_code=0,elapsed_s=round(time.perf_counter()-t0,3))
        except Exception as e: return AdapterEvidence(tool="matchering",action=action,exit_code=-1,stderr=str(e))
