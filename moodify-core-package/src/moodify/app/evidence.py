"""EvidenceAggregator: unify scattered evidence sources into one bundle."""
from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class EvidenceBundle:
    schema_version: str = "1.0.0"; run_id: str = ""; aggregated_at: str = ""
    sources: dict = field(default_factory=dict)
    aggregated_hashes: dict[str,str] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)

def aggregate_evidence(run_id: str, sources: dict[str,Path|None]) -> EvidenceBundle:
    bundle = EvidenceBundle(run_id=run_id, aggregated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()))
    for name, path in sources.items():
        if path and Path(path).exists():
            try:
                data = json.loads(Path(path).read_text(encoding="utf-8"))
                bundle.sources[name] = {"path":str(path),"data":data}
                bundle.aggregated_hashes[name] = hashlib.sha256(Path(path).read_bytes()).hexdigest()
            except Exception: bundle.limitations.append(f"{name}: unreadable at {path}")
        else: bundle.limitations.append(f"{name}: not available")
    return bundle

def write_evidence_bundle(bundle: EvidenceBundle, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    p = output_dir / "evidence_bundle.json"
    p.write_text(json.dumps({"schema_version":bundle.schema_version,"run_id":bundle.run_id,"aggregated_at":bundle.aggregated_at,"sources":{k:{"path":v["path"]} for k,v in bundle.sources.items()},"aggregated_hashes":bundle.aggregated_hashes,"limitations":bundle.limitations}, indent=2, ensure_ascii=False))
    return p
