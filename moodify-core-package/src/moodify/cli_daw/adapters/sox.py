"""SoX adapter — subprocess-based, CLI-native."""
import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class AdapterEvidence:
    tool: str; action: str; command: list[str] = field(default_factory=list)
    exit_code: int = -1; stdout: str = ""; stderr: str = ""
    output_path: str = ""; elapsed_s: float = 0.0

class SoXAdapter:
    name = "sox"
    def _find(self) -> str:
        import shutil
        p = shutil.which("sox")
        if p: return p
        for root in [r"C:\Users\Administrator\AppData\Local\Microsoft\WinGet\Packages"]:
            for dirpath, _, files in os.walk(root):
                if "sox.exe" in files: return os.path.join(dirpath, "sox.exe")
        return ""

    def probe(self) -> dict:
        exe = self._find()
        if not exe: return {"status":"UNAVAILABLE","tool":"sox","error":"not found"}
        try:
            r = subprocess.run([exe,"--version"],capture_output=True,text=True,timeout=10)
            return {"status":"available","tool":"sox","version":r.stdout.splitlines()[0] if r.stdout else "14.4.2","path":exe}
        except Exception as e: return {"status":"UNAVAILABLE","tool":"sox","error":str(e)}

    def capabilities(self) -> dict:
        return {"tool":"sox","actions":["gain","norm","compand","trim","fade","silence","info","resample","convert"]}

    def execute(self, action: str, params: dict, output_dir: Path) -> AdapterEvidence:
        exe = self._find()
        if not exe: return AdapterEvidence(tool="sox",action=action,exit_code=-1,stderr="SoX not available")
        t0 = time.perf_counter()
        inp = params.get("input",""); out = str(output_dir / params.get("output","out.wav"))
        output_dir.mkdir(parents=True, exist_ok=True)
        # Build: sox [input] [output] [effect] [params...]
        effects = []
        if action == "gain": effects = ["gain", str(params.get("gain_db",0))]
        elif action == "norm": effects = ["norm"]
        elif action == "compand": effects = ["compand", str(params.get("attack",0.1)), str(params.get("decay",0.3)), str(params.get("threshold","-60,-60,-12")), str(params.get("ratio",2))]
        elif action == "trim": effects = ["trim", str(params.get("start_s",0)), str(params.get("duration_s",0))]
        elif action == "info": effects = ["--i"]
        else: effects = []
        cmd = [exe, inp] + ([out] if action != "info" else []) + effects
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            return AdapterEvidence(tool="sox",action=action,command=cmd,exit_code=r.returncode,stdout=r.stdout[:2000],stderr=r.stderr[:2000],output_path=out,elapsed_s=round(time.perf_counter()-t0,3))
        except Exception as e: return AdapterEvidence(tool="sox",action=action,exit_code=-1,stderr=str(e))
