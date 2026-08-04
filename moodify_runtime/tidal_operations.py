"""Tidal Operations — operator control surface for the tidal cycle.

ECHAIN-MOODIFY-TIDAL-OPERATIONS-010 / NEM-030/031/032.
MHP-593: Tidal Control API
MHP-594: Tidal Console Dashboard
MHP-595: Cycle Timeline View
MHP-596: Morning Brief Inbox
MHP-597: Operator Approval Engine
MHP-599: Tidal Alert Writer
MHP-601: Emergency Pause Workflow
MHP-602: Operator Notes Writeback
"""

from __future__ import annotations

import json
import os
import signal
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ═══════════════════════════════════════════════════════════════════════════
# MHP-593: Tidal Control API — state, start, stop, pause, resume
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TidalControlState:
    running: bool = False
    pid: Optional[int] = None
    current_cycle: int = 0
    started_at: str = ""
    last_heartbeat: str = ""
    total_tasks: int = 0
    total_succeeded: int = 0
    total_failed: int = 0
    free_disk_gb: float = 0.0
    free_mem_gb: float = 0.0
    alert_count: int = 0
    uptime_s: float = 0.0
    phase: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def get_tidal_state(
    pid_file: str = "outputs/tidal/tidal.pid",
    hb_file: str = "outputs/tidal/tidal_heartbeat.json",
    events_file: str = "outputs/tidal/tidal_events.jsonl",
) -> TidalControlState:
    state = TidalControlState()
    pid_path = PROJECT_ROOT / pid_file
    if pid_path.exists():
        try:
            pid = int(pid_path.read_text().strip())
            os.kill(pid, 0)
            state.running = True
            state.pid = pid
            try:
                import subprocess
                out = subprocess.check_output(["ps", "-o", "etime=", "-p", str(pid)],
                                              text=True).strip()
                state.uptime_s = _parse_etime(out)
            except Exception:
                pass
        except (ValueError, OSError, ProcessLookupError):
            state.running = False
    hb_path = PROJECT_ROOT / hb_file
    if hb_path.exists():
        try:
            hb = json.loads(hb_path.read_text())
            state.current_cycle = hb.get("cycle", 0)
            state.last_heartbeat = hb.get("timestamp", "")
            state.total_tasks = hb.get("total_tasks", 0)
            state.total_succeeded = hb.get("total_succeeded", 0)
            state.total_failed = hb.get("total_failed", 0)
            state.free_disk_gb = hb.get("free_disk_gb", 0.0)
            state.free_mem_gb = hb.get("free_mem_gb", 0.0)
        except (json.JSONDecodeError, IOError):
            pass
    ev_path = PROJECT_ROOT / events_file
    if ev_path.exists():
        try:
            lines = ev_path.read_text().strip().split("\n")
            for line in reversed(lines[-20:]):
                try:
                    e = json.loads(line)
                    if e.get("event_type") == "PHASE":
                        state.phase = e.get("message", "").split(":")[0].strip()
                        break
                except json.JSONDecodeError:
                    continue
        except IOError:
            pass
    # Count alerts
    if ev_path.exists():
        try:
            state.alert_count = sum(
                1 for l in ev_path.read_text().strip().split("\n")
                if "ALERT" in l or "HEALTH_FAIL" in l or "CYCLE_ERROR" in l)
        except IOError:
            pass
    return state


def _parse_etime(etime: str) -> float:
    """Parse ps etime format (DD-HH:MM:SS or HH:MM:SS) to seconds."""
    parts = etime.strip().split("-")
    if len(parts) == 2:
        days = int(parts[0])
        h, m, s = map(int, parts[1].split(":"))
        return float(days * 86400 + h * 3600 + m * 60 + s)
    h, m, s = map(int, parts[0].split(":"))
    return float(h * 3600 + m * 60 + s)


def request_tidal_pause(reason: str = "") -> Dict[str, Any]:
    """Request a tidal cycle pause by creating a pause marker file."""
    marker = PROJECT_ROOT / "outputs" / "tidal" / "pause_requested"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps({"reason": reason, "requested_at": _utc_now()}))
    return {"ok": True, "marker": str(marker), "reason": reason}


def request_tidal_resume() -> Dict[str, Any]:
    """Remove pause marker to resume tidal cycles."""
    marker = PROJECT_ROOT / "outputs" / "tidal" / "pause_requested"
    if marker.exists():
        marker.unlink()
        return {"ok": True, "was_paused": True}
    return {"ok": True, "was_paused": False}


def send_tidal_signal(sig: int = signal.SIGTERM) -> Dict[str, Any]:
    """Send a signal to the running tidal process."""
    state = get_tidal_state()
    if not state.running or state.pid is None:
        return {"ok": False, "error": "Tidal not running"}
    try:
        os.kill(state.pid, sig)
        sig_names = {signal.SIGTERM: "SIGTERM", signal.SIGINT: "SIGINT"}
        if hasattr(signal, "SIGUSR1"):
            sig_names[signal.SIGUSR1] = "SIGUSR1"
        sig_name = sig_names.get(sig, str(sig))
        return {"ok": True, "signal": sig_name, "pid": state.pid}
    except OSError as e:
        return {"ok": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
# MHP-594: Tidal Console Dashboard
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class DashboardSnapshot:
    generated_at: str = field(default_factory=_utc_now)
    tidal: TidalControlState = field(default_factory=TidalControlState)
    recent_cycles: List[Dict[str, Any]] = field(default_factory=list)
    recent_events: List[Dict[str, Any]] = field(default_factory=list)
    health: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "tidal": self.tidal.to_dict(),
            "recent_cycles": self.recent_cycles,
            "recent_events": self.recent_events,
            "health": self.health,
        }


def get_dashboard_snapshot(
    records_file: str = "outputs/tidal/tidal_records.jsonl",
    events_file: str = "outputs/tidal/tidal_events.jsonl",
    max_records: int = 10, max_events: int = 20,
) -> DashboardSnapshot:
    snap = DashboardSnapshot()
    snap.tidal = get_tidal_state()

    # Health summary
    snap.health = {"tidal": "🟢 running" if snap.tidal.running else "⚫ stopped"}
    if snap.tidal.free_disk_gb < 3:
        snap.health["disk"] = f"🔴 {snap.tidal.free_disk_gb}GB"
    elif snap.tidal.free_disk_gb < 10:
        snap.health["disk"] = f"🟡 {snap.tidal.free_disk_gb}GB"
    else:
        snap.health["disk"] = f"🟢 {snap.tidal.free_disk_gb}GB"
    fail_rate = (snap.tidal.total_failed / max(snap.tidal.total_tasks, 1)) * 100
    if fail_rate > 20:
        snap.health["fail_rate"] = f"🔴 {fail_rate:.0f}%"
    elif fail_rate > 5:
        snap.health["fail_rate"] = f"🟡 {fail_rate:.0f}%"
    else:
        snap.health["fail_rate"] = f"🟢 {fail_rate:.0f}%"

    # Recent cycles
    rp = PROJECT_ROOT / records_file
    if rp.exists():
        try:
            lines = rp.read_text().strip().split("\n")
            for line in lines[-max_records:]:
                snap.recent_cycles.append(json.loads(line))
        except (IOError, json.JSONDecodeError):
            pass

    # Recent events
    ep = PROJECT_ROOT / events_file
    if ep.exists():
        try:
            lines = ep.read_text().strip().split("\n")
            for line in lines[-max_events:]:
                snap.recent_events.append(json.loads(line))
        except (IOError, json.JSONDecodeError):
            pass

    return snap


# ═══════════════════════════════════════════════════════════════════════════
# MHP-595: Cycle Timeline View
# ═══════════════════════════════════════════════════════════════════════════

def get_cycle_timeline(
    records_file: str = "outputs/tidal/tidal_records.jsonl",
    max_cycles: int = 20,
) -> List[Dict[str, Any]]:
    """Return a simplified timeline of cycle results for dashboard rendering."""
    rp = PROJECT_ROOT / records_file
    if not rp.exists():
        return []
    timeline = []
    try:
        for line in rp.read_text().strip().split("\n"):
            r = json.loads(line)
            timeline.append({
                "cycle": r.get("cycle_number", 0),
                "phase": r.get("phase", "?"),
                "succeeded": r.get("tasks_succeeded", 0),
                "failed": r.get("tasks_failed", 0),
                "errors": len(r.get("errors", [])),
                "elapsed_s": r.get("elapsed_s", 0),
                "started": r.get("started_at", ""),
            })
    except (IOError, json.JSONDecodeError):
        pass
    return timeline[-max_cycles:]


# ═══════════════════════════════════════════════════════════════════════════
# MHP-596: Morning Brief Inbox
# ═══════════════════════════════════════════════════════════════════════════

def get_brief_inbox(brief_dir: str = "outputs/tidal/briefs") -> List[Dict[str, Any]]:
    """List all saved morning briefs for operator review."""
    bp = PROJECT_ROOT / brief_dir
    if not bp.exists():
        return []
    briefs = []
    for f in sorted(bp.glob("*.md"), reverse=True)[:10]:
        briefs.append({"file": str(f.relative_to(PROJECT_ROOT)),
                       "size": f.stat().st_size,
                       "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()})
    return briefs


def save_morning_brief(markdown: str, brief_dir: str = "outputs/tidal/briefs") -> str:
    """Save a morning brief to the inbox."""
    bp = PROJECT_ROOT / brief_dir
    bp.mkdir(parents=True, exist_ok=True)
    name = f"brief_{_utc_now().replace(':','-')[:16]}.md"
    path = bp / name
    path.write_text(markdown)
    return str(path.relative_to(PROJECT_ROOT))


# ═══════════════════════════════════════════════════════════════════════════
# MHP-597: Operator Approval Engine
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ApprovalRequest:
    request_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    request_type: str = ""
    status: str = "pending"
    reason: str = ""
    requested_at: str = field(default_factory=_utc_now)
    resolved_at: str = ""
    resolved_by: str = ""
    resolution_note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def create_approval(request_type: str, reason: str) -> ApprovalRequest:
    return ApprovalRequest(request_type=request_type, reason=reason)


def resolve_approval(
    request: ApprovalRequest, approved: bool, resolved_by: str = "operator",
    note: str = "",
) -> ApprovalRequest:
    request.status = "approved" if approved else "denied"
    request.resolved_at = _utc_now()
    request.resolved_by = resolved_by
    request.resolution_note = note
    return request


# ═══════════════════════════════════════════════════════════════════════════
# MHP-599: Tidal Alert Writer
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class OperatorAlert:
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    level: str = "info"
    title: str = ""
    message: str = ""
    source: str = "tidal"
    created_at: str = field(default_factory=_utc_now)
    acknowledged: bool = False
    acknowledged_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


_ALERT_STORE: List[OperatorAlert] = []


def create_alert(level: str, message: str, title: str = "",
                 source: str = "tidal") -> OperatorAlert:
    valid = {"info", "warn", "critical"}
    a = OperatorAlert(
        level=level if level in valid else "info",
        message=message, title=title or message[:60], source=source)
    _ALERT_STORE.append(a)
    return a


def get_active_alerts(include_acked: bool = False) -> List[OperatorAlert]:
    if include_acked:
        return list(_ALERT_STORE)
    return [a for a in _ALERT_STORE if not a.acknowledged]


def acknowledge_alert(alert_id: str) -> Optional[OperatorAlert]:
    for a in _ALERT_STORE:
        if a.alert_id == alert_id:
            a.acknowledged = True
            a.acknowledged_at = _utc_now()
            return a
    return None


# ═══════════════════════════════════════════════════════════════════════════
# MHP-601: Emergency Pause Workflow
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class EmergencyPause:
    pause_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    reason: str = ""
    triggered_by: str = ""
    triggered_at: str = field(default_factory=_utc_now)
    auto_resume: bool = False
    auto_resume_after_s: int = 0
    status: str = "active"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def emergency_pause(reason: str, triggered_by: str = "operator",
                    auto_resume: bool = False,
                    auto_resume_after_s: int = 0) -> EmergencyPause:
    """Execute emergency pause: signal tidal, create alert, write marker."""
    ep = EmergencyPause(reason=reason, triggered_by=triggered_by,
                        auto_resume=auto_resume,
                        auto_resume_after_s=auto_resume_after_s)
    # Signal the process
    pause_signal = getattr(signal, "SIGUSR1", signal.SIGTERM)
    send_tidal_signal(pause_signal)
    # Write pause marker
    request_tidal_pause(reason=reason)
    # Create alert
    create_alert("critical", reason, title="🚨 EMERGENCY PAUSE",
                 source=triggered_by)
    # Save pause record
    pp = PROJECT_ROOT / "outputs" / "tidal" / "emergency_pauses.jsonl"
    pp.parent.mkdir(parents=True, exist_ok=True)
    with open(pp, "a") as f:
        f.write(json.dumps(ep.to_dict()) + "\n")
    return ep


# ═══════════════════════════════════════════════════════════════════════════
# MHP-602: Operator Notes Writeback
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class OperatorNote:
    note_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    target: str = ""
    target_type: str = ""
    content: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=_utc_now)
    author: str = "operator"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


_NOTES_FILE = PROJECT_ROOT / "outputs" / "tidal" / "operator_notes.jsonl"


def write_operator_note(target: str, content: str, target_type: str = "task",
                        tags: Optional[List[str]] = None,
                        author: str = "operator") -> OperatorNote:
    note = OperatorNote(target=target, target_type=target_type, content=content,
                        tags=tags or [], author=author)
    _NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_NOTES_FILE, "a") as f:
        f.write(json.dumps(note.to_dict()) + "\n")
    return note


def read_operator_notes(target: str = "", limit: int = 50) -> List[OperatorNote]:
    if not _NOTES_FILE.exists():
        return []
    notes = []
    for line in _NOTES_FILE.read_text().strip().split("\n"):
        try:
            d = json.loads(line)
            n = OperatorNote(note_id=d.get("note_id", ""), target=d.get("target", ""),
                            target_type=d.get("target_type", ""), content=d.get("content", ""),
                            tags=d.get("tags", []), created_at=d.get("created_at", ""),
                            author=d.get("author", ""))
            if not target or n.target == target:
                notes.append(n)
        except json.JSONDecodeError:
            continue
    return notes[-limit:]


# ═══════════════════════════════════════════════════════════════════════════
# MHP-604: Integration Smoke
# ═══════════════════════════════════════════════════════════════════════════

def run_operations_smoke() -> Dict[str, Any]:
    """End-to-end smoke test of all TIDAL-OPERATIONS subsystems."""
    results: Dict[str, Any] = {}

    # Control API
    state = get_tidal_state()
    results["control_state"] = state.to_dict()
    results["control_api_ok"] = isinstance(state, TidalControlState)

    # Alerts
    a1 = create_alert("warn", "test alert", title="Smoke Test")
    results["alert_created"] = a1.alert_id is not None
    active = get_active_alerts()
    results["active_alerts"] = len(active)
    ack = acknowledge_alert(a1.alert_id)
    results["alert_ack"] = ack is not None and ack.acknowledged

    # Approvals
    ar = create_approval("gate_override", "smoke test")
    results["approval_created"] = ar.status == "pending"
    resolved = resolve_approval(ar, True, note="auto-approved")
    results["approval_resolved"] = resolved.status == "approved"

    # Dashboard
    snap = get_dashboard_snapshot()
    results["dashboard"] = snap.health

    # Timeline
    tl = get_cycle_timeline()
    results["timeline_entries"] = len(tl)

    # Notes
    note = write_operator_note("smoke-test", "smoke test note", tags=["smoke"])
    results["note_written"] = note.note_id is not None
    notes = read_operator_notes("smoke-test")
    results["notes_read"] = len(notes)

    # Pause/resume
    pause = request_tidal_pause("smoke test")
    results["pause_ok"] = pause["ok"]
    resume = request_tidal_resume()
    results["resume_ok"] = resume["ok"]

    results["smoke_ok"] = all([
        results["control_api_ok"], results["alert_created"],
        results["alert_ack"], results["approval_created"],
        results["approval_resolved"], results["note_written"],
        results["notes_read"] > 0, results["pause_ok"], results["resume_ok"],
    ])
    return results


def cli_operations_report(run_id: str = "") -> Dict[str, Any]:
    return run_operations_smoke()
