"""Rubber Band adapter — subprocess-based time-stretch/pitch-shift."""
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class AdapterEvidence:
    tool: str; action: str; command: list[str] = field(default_factory=list)
    exit_code: int = -1; stdout: str = ""; stderr: str = ""
    output_path: str = ""; elapsed_s: float = 0.0

class RubberBandAdapter:
    name = "rubberband"
    def _find(self) -> str:
        import os; p = shutil.which("rubberband")
        if p: return p
        for r in ["E:/moodify/tools/third_party/rubberband-4.0.0"]:
            for d,_,fs in os.walk(r):
                if "rubberband.exe" in fs: return os.path.join(d,"rubberband.exe")
        return ""

    def probe(self) -> dict:
        exe = self._find()
        if not exe: return {"status":"UNAVAILABLE","tool":"rubberband","error":"not found"}
        try:
            r = subprocess.run([exe,"--version"],capture_output=True,text=True,timeout=10)
            return {"status":"available","tool":"rubberband","version":(r.stdout or r.stderr).strip(),"path":exe}
        except Exception: return {"status":"UNAVAILABLE","tool":"rubberband"}

    def capabilities(self) -> dict:
        return {"tool":"rubberband","actions":["time_stretch","pitch_shift"]}

    def execute(self, action: str, params: dict, output_dir: Path) -> AdapterEvidence:
        exe = self._find()
        if not exe: return AdapterEvidence(tool="rubberband",action=action,exit_code=-1,stderr="Rubber Band not available")
        t0 = time.perf_counter()
        inp = params["input"]; out = str(output_dir/params.get("output","stretched.wav"))
        cmd = [exe, "-q"]
        if action == "time_stretch": cmd += ["--tempo",str(params.get("ratio",1.0))]
        elif action == "pitch_shift": cmd += ["--pitch",str(params.get("semitones",0))]
        cmd += [inp, out]
        try:
            r = subprocess.run(cmd,capture_output=True,text=True,timeout=120)
            return AdapterEvidence(tool="rubberband",action=action,command=cmd,exit_code=r.returncode,stdout=r.stdout[:2000],stderr=r.stderr[:2000],output_path=out,elapsed_s=round(time.perf_counter()-t0,3))
        except Exception as e: return AdapterEvidence(tool="rubberband",action=action,exit_code=-1,stderr=str(e))
