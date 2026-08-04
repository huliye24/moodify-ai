"""MHP-041: Operator Console API Server (FastAPI) — all subsystems live.

Start with:
    python3 -m uvicorn moodify_runtime.operator_api:app --host 0.0.0.0 --port 8700

Subsystems:
    /operator/*      — Jobs, Gates, Reports, Delivery (MHP-031–034)
    /studio/*        — Studio Back Office (MHP-036)
    /scheduler/*     — Cloud GPU Scheduler (MHP-038)
    /calibration/*   — MRS Calibration Lab (MHP-039)
    /craft/*         — Craft Library (MHP-037)
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .config import load_config
from .craft_memory import list_craft_records, writeback_delivery_to_craft_record
from .operator_console import (
    attach_run_report_to_job,
    authorize_operator_job_source,
    build_operator_report_bundle,
    check_storage_health,
    compact_operator_jobs,
    create_delivery_record,
    create_operator_job,
    get_delivery_record,
    get_operator_job,
    get_operator_job_detail,
    list_delivery_records,
    list_operator_jobs,
    plan_operator_runtime,
    run_operator_job,
)
from .studio import (
    create_client,
    create_order,
    create_project,
    create_staff_note,
    get_order_context,
    link_job_to_order,
    list_clients,
    list_orders,
    list_projects,
    list_staff_notes,
)
from .scheduler import (
    allocate_lease,
    list_scheduler_costs,
    list_scheduler_leases,
    list_scheduler_requests,
    list_scheduler_runs,
    record_compute_run,
    schedule_job,
)
from .mrs_calibration import (
    create_calibration_sample_set,
    list_calibration_audits,
    list_calibration_reviews,
    list_calibration_sample_sets,
    list_calibration_thresholds,
    propose_threshold,
    run_gate_audit,
    submit_calibration_review,
)

_PAGE = (Path(__file__).parent / "operator_console.html").read_text(encoding="utf-8")


def _get_app():
    try:
        from contextlib import asynccontextmanager

        from fastapi import FastAPI, HTTPException
        from fastapi.responses import HTMLResponse

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            yield

        app = FastAPI(
            title="Moodify Operator Console API",
            version="0.1.0",
            lifespan=lifespan,
        )

        # ═══════════════════════════════════════════════════════════════
        # System
        # ═══════════════════════════════════════════════════════════════

        @app.get("/health")
        async def health():
            return {"status": "ok", "service": "moodify-operator"}

        @app.get("/studio-os/status")
        async def studio_os_status():
            cfg = load_config()
            jobs = list_operator_jobs(cfg)
            deliveries = list_delivery_records(cfg)
            storage = check_storage_health(cfg)
            return {
                "active_jobs": len([j for j in jobs if j["status"] not in ("delivered", "failed")]),
                "pending_gates": len([j for j in jobs if j["status"] == "gate_review"]),
                "delivered_jobs": len([j for j in jobs if j["status"] == "delivered"]),
                "total_jobs": len(jobs),
                "total_deliveries": len(deliveries),
                "storage": storage["storage"],
            }

        # ═══════════════════════════════════════════════════════════════
        # Runtime (MHP-114)
        # ═══════════════════════════════════════════════════════════════

        @app.get("/runtime/heartbeat")
        async def api_runtime_heartbeat():
            """Return runner liveness status."""
            from .runtime_state import Heartbeat
            cfg = load_config()
            hb = Heartbeat(path=cfg.project_root / "runtime_heartbeat.json")
            return {
                "alive": hb.is_alive(max_age=60),
                "age_seconds": round(hb.age_seconds(), 1) if hb.path.exists() else None,
            }

        @app.get("/runtime/status")
        async def api_runtime_status():
            """Full runtime status: heartbeat + jobs + SLO health."""
            from .runtime_state import Heartbeat
            cfg = load_config()
            hb = Heartbeat(path=cfg.project_root / "runtime_heartbeat.json")
            jobs = list_operator_jobs(cfg)
            active = len([j for j in jobs if j["status"] not in ("delivered", "failed")])
            return {
                "heartbeat_alive": hb.is_alive(max_age=60),
                "heartbeat_age_s": round(hb.age_seconds(), 1) if hb.path.exists() else None,
                "active_jobs": active,
                "total_jobs": len(jobs),
                "slo": {
                    "uptime_target": 0.99,
                    "success_rate_target": 0.95,
                    "p99_latency_target_s": 120,
                },
            }

        @app.post("/operator/compact")
        async def api_compact(keep: int = 100):
            """Deduplicate and prune operator_jobs.jsonl. Keeps most recent `keep` jobs."""
            cfg = load_config()
            try:
                result = compact_operator_jobs(cfg, keep_last_n=keep)
                return {"status": "ok", **result}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"compaction failed: {e}")

        # ═══════════════════════════════════════════════════════════════
        # Operator Jobs (MHP-031)
        # ═══════════════════════════════════════════════════════════════

        @app.post("/operator/jobs")
        async def api_create_job(
            source_audio: str,
            processing_depth: str = "quick_scan",
            project_label: str = "",
            customer_label: str = "",
            target_notes: str = "",
            priority: int = 5,
        ):
            cfg = load_config()
            try:
                return create_operator_job(
                    cfg,
                    source_audio=source_audio,
                    processing_depth=processing_depth,
                    project_label=project_label,
                    customer_label=customer_label,
                    target_notes=target_notes,
                    priority=priority,
                )
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        @app.get("/operator/jobs")
        async def api_list_jobs(status: Optional[str] = None):
            cfg = load_config()
            return {"jobs": list_operator_jobs(cfg, status=status)}

        @app.get("/operator/jobs/{job_id}")
        async def api_get_job(job_id: str):
            cfg = load_config()
            try:
                return get_operator_job_detail(cfg, job_id=job_id)
            except KeyError:
                raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

        # ── Runtime (MHP-032) ─────────────────────────────────

        @app.post("/operator/jobs/{job_id}/plan-runtime")
        async def api_plan_runtime(job_id: str):
            cfg = load_config()
            try:
                return plan_operator_runtime(cfg, job_id=job_id)
            except FileNotFoundError as e:
                raise HTTPException(status_code=400, detail=str(e))

        @app.post("/operator/jobs/{job_id}/run")
        async def api_run_job(
            job_id: str,
            dry_run: bool = True,
            rights_manifest: Optional[str] = None,
            rights_asset_id: str = "",
        ):
            cfg = load_config()
            return run_operator_job(
                cfg,
                job_id=job_id,
                dry_run=dry_run,
                rights_manifest=rights_manifest,
                rights_asset_id=rights_asset_id,
            )

        @app.post("/operator/jobs/{job_id}/authorize-rights")
        async def api_authorize_rights(
            job_id: str,
            rights_manifest: str,
            rights_asset_id: str,
        ):
            cfg = load_config()
            try:
                return authorize_operator_job_source(
                    cfg, job_id, rights_manifest, rights_asset_id
                )
            except (KeyError, ValueError) as e:
                raise HTTPException(status_code=400, detail=str(e))

        @app.post("/operator/jobs/{job_id}/attach-run")
        async def api_attach_run(
            job_id: str,
            run_id: str,
            run_dir: Optional[str] = None,
            report_path: Optional[str] = None,
            required_mrs_delta: float = 0.0,
            genre: str = "",
        ):
            cfg = load_config()
            try:
                return attach_run_report_to_job(
                    cfg,
                    job_id=job_id,
                    run_id=run_id,
                    run_dir=run_dir,
                    report_path=report_path,
                    required_mrs_delta=required_mrs_delta,
                    genre=genre,
                )
            except KeyError:
                raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

        # ── Reports (MHP-033) ─────────────────────────────────

        @app.post("/operator/jobs/{job_id}/report")
        async def api_build_report(job_id: str):
            cfg = load_config()
            return build_operator_report_bundle(cfg, job_id=job_id)

        @app.get("/operator/jobs/{job_id}/report")
        async def api_get_report(job_id: str):
            cfg = load_config()
            job = get_operator_job(cfg, job_id)
            rp = job.get("report_path", "")
            if not rp:
                raise HTTPException(status_code=404, detail="No report for this job")
            return {"job_id": job_id, "report_path": rp}

        # ── Delivery (MHP-034) ────────────────────────────────

        @app.post("/operator/jobs/{job_id}/deliver")
        async def api_deliver(
            job_id: str,
            candidate_id: str,
            operator_decision: str = "approved",
            notes: str = "",
            override: bool = False,
            human_approved: bool = False,
            approved_by: str = "",
        ):
            cfg = load_config()
            try:
                return create_delivery_record(
                    cfg,
                    job_id=job_id,
                    candidate_id=candidate_id,
                    operator_decision=operator_decision,
                    notes=notes,
                    override=override,
                    human_approved=human_approved,
                    approved_by=approved_by,
                )
            except (KeyError, ValueError) as e:
                raise HTTPException(status_code=400, detail=str(e))

        @app.get("/operator/jobs/{job_id}/delivery")
        async def api_get_delivery(job_id: str):
            cfg = load_config()
            return get_delivery_record(cfg, job_id=job_id)

        @app.get("/operator/deliveries")
        async def api_list_deliveries():
            cfg = load_config()
            return {"deliveries": list_delivery_records(cfg)}

        # ═══════════════════════════════════════════════════════════════
        # Craft Library (MHP-037)
        # ═══════════════════════════════════════════════════════════════

        @app.post("/operator/jobs/{job_id}/writeback-craft")
        async def api_writeback_craft(
            job_id: str,
            candidate_id: str,
            adoption_status: str = "candidate",
            operator_notes: str = "",
        ):
            cfg = load_config()
            try:
                return writeback_delivery_to_craft_record(
                    cfg,
                    job_id=job_id,
                    candidate_id=candidate_id,
                    adoption_status=adoption_status,
                    operator_notes=operator_notes,
                )
            except (KeyError, ValueError) as e:
                raise HTTPException(status_code=400, detail=str(e))

        @app.get("/craft/records")
        async def craft_records(adoption_status: Optional[str] = None):
            cfg = load_config()
            return {"records": list_craft_records(cfg, adoption_status=adoption_status)}

        # ═══════════════════════════════════════════════════════════════
        # Studio Back Office (MHP-036)
        # ═══════════════════════════════════════════════════════════════

        @app.post("/studio/clients")
        async def api_create_client(name: str, contact: str = "", notes: str = ""):
            cfg = load_config()
            return create_client(cfg, name=name, contact=contact, notes=notes)

        @app.get("/studio/clients")
        async def api_list_clients():
            cfg = load_config()
            return {"clients": list_clients(cfg)}

        @app.post("/studio/projects")
        async def api_create_project(client_id: str, name: str, description: str = ""):
            cfg = load_config()
            return create_project(cfg, client_id=client_id, name=name, description=description)

        @app.get("/studio/projects")
        async def api_list_projects(client_id: Optional[str] = None):
            cfg = load_config()
            return {"projects": list_projects(cfg, client_id=client_id)}

        @app.post("/studio/orders")
        async def api_create_order(
            project_id: str,
            client_id: str,
            description: str = "",
            processing_package: str = "standard",
            deadline: str = "",
            priority: int = 5,
        ):
            cfg = load_config()
            return create_order(
                cfg, project_id=project_id, client_id=client_id,
                description=description, processing_package=processing_package,
                deadline=deadline, priority=priority,
            )

        @app.get("/studio/orders")
        async def api_list_orders(project_id: Optional[str] = None):
            cfg = load_config()
            return {"orders": list_orders(cfg, project_id=project_id)}

        @app.post("/studio/orders/{order_id}/link-job")
        async def api_link_job(order_id: str, job_id: str):
            cfg = load_config()
            try:
                return link_job_to_order(cfg, order_id=order_id, job_id=job_id)
            except KeyError:
                raise HTTPException(status_code=404, detail=f"Order not found: {order_id}")

        @app.get("/studio/orders/{order_id}/context")
        async def api_order_context(order_id: str):
            cfg = load_config()
            try:
                return get_order_context(cfg, order_id=order_id)
            except KeyError:
                raise HTTPException(status_code=404, detail=f"Order not found: {order_id}")

        @app.post("/studio/notes")
        async def api_create_note(
            target_type: str,
            target_id: str,
            content: str,
            author: str = "operator",
        ):
            cfg = load_config()
            return create_staff_note(cfg,
                target_type=target_type, target_id=target_id,
                content=content, author=author,
            )

        @app.get("/studio/notes")
        async def api_list_notes(target_type: Optional[str] = None, target_id: Optional[str] = None):
            cfg = load_config()
            return {"notes": list_staff_notes(cfg, target_type=target_type, target_id=target_id)}

        # ═══════════════════════════════════════════════════════════════
        # Cloud GPU Scheduler (MHP-038)
        # ═══════════════════════════════════════════════════════════════

        @app.post("/scheduler/requests")
        async def api_schedule_request(
            job_id: str,
            compute_class: str = "cpu_standard",
            priority: int = 5,
        ):
            cfg = load_config()
            try:
                return schedule_job(cfg, job_id=job_id, compute_class=compute_class, priority=priority)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        @app.get("/scheduler/requests")
        async def api_list_requests():
            cfg = load_config()
            return {"requests": list_scheduler_requests(cfg)}

        @app.post("/scheduler/leases/{request_id}")
        async def api_allocate_lease(request_id: str, node_id: str, ttl_minutes: int = 120):
            cfg = load_config()
            try:
                return allocate_lease(cfg, request_id=request_id, node_id=node_id, ttl_minutes=ttl_minutes)
            except KeyError:
                raise HTTPException(status_code=404, detail=f"Request not found: {request_id}")

        @app.post("/scheduler/runs")
        async def api_record_run(
            lease_id: str,
            request_id: str,
            job_id: str,
            status: str = "completed",
            exit_code: int = 0,
            error: str = "",
            node_id: str = "",
            duration_seconds: float = 0.0,
        ):
            cfg = load_config()
            return record_compute_run(cfg,
                lease_id=lease_id, request_id=request_id, job_id=job_id,
                status=status, exit_code=exit_code, error=error,
                node_id=node_id, duration_seconds=duration_seconds,
            )

        @app.get("/scheduler/runs")
        async def api_list_runs():
            cfg = load_config()
            return {"runs": list_scheduler_runs(cfg)}

        @app.get("/scheduler/costs")
        async def api_list_costs():
            cfg = load_config()
            return {"costs": list_scheduler_costs(cfg)}

        # ═══════════════════════════════════════════════════════════════
        # MRS Calibration Lab (MHP-039)
        # ═══════════════════════════════════════════════════════════════

        @app.post("/calibration/sample-sets")
        async def api_create_sample_set(
            name: str, description: str = "",
        ):
            cfg = load_config()
            return create_calibration_sample_set(cfg, name=name, description=description)

        @app.get("/calibration/sample-sets")
        async def api_list_sample_sets():
            cfg = load_config()
            return {"sample_sets": list_calibration_sample_sets(cfg)}

        @app.post("/calibration/reviews")
        async def api_submit_review(
            set_id: str,
            candidate_id: str,
            human_decision: str,
            gate_decision: str,
            notes: str = "",
            reviewer: str = "operator",
        ):
            cfg = load_config()
            try:
                return submit_calibration_review(cfg,
                    set_id=set_id, candidate_id=candidate_id,
                    human_decision=human_decision, gate_decision=gate_decision,
                    notes=notes, reviewer=reviewer,
                )
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        @app.get("/calibration/reviews")
        async def api_list_reviews(set_id: Optional[str] = None):
            cfg = load_config()
            return {"reviews": list_calibration_reviews(cfg, set_id=set_id)}

        @app.post("/calibration/audits/{set_id}")
        async def api_run_audit(set_id: str):
            cfg = load_config()
            return run_gate_audit(cfg, set_id=set_id)

        @app.get("/calibration/audits")
        async def api_list_audits():
            cfg = load_config()
            return {"audits": list_calibration_audits(cfg)}

        @app.post("/calibration/thresholds")
        async def api_propose_threshold(
            parameter: str,
            current_value: float,
            proposed_value: float,
            justification: str = "",
        ):
            cfg = load_config()
            return propose_threshold(cfg,
                parameter=parameter,
                current_value=current_value,
                proposed_value=proposed_value,
                justification=justification,
            )

        @app.get("/calibration/thresholds")
        async def api_list_thresholds():
            cfg = load_config()
            return {"thresholds": list_calibration_thresholds(cfg)}

        # ═══════════════════════════════════════════════════════════════
        # Static
        # ═══════════════════════════════════════════════════════════════

        @app.get("/operator", response_class=HTMLResponse)
        async def operator_console():
            return _PAGE

        @app.get("/", response_class=HTMLResponse)
        async def root():
            return _PAGE

        return app

    except ImportError:
        return None


app = _get_app()
