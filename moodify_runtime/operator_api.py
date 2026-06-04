"""MHP-035: Operator Console API Server (FastAPI).

Start with:
    python3 -m uvicorn moodify_runtime.operator_api:app --host 0.0.0.0 --port 8700
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .config import load_config
from .craft_memory import list_craft_records, writeback_delivery_to_craft_record
from .operator_console import (
    attach_run_report_to_job,
    build_operator_report_bundle,
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

_PAGE = (Path(__file__).parent / "operator_console.html").read_text(encoding="utf-8")


def _get_app():
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import HTMLResponse
        from contextlib import asynccontextmanager

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            yield

        app = FastAPI(
            title="Moodify Operator Console API",
            version="0.1.0",
            lifespan=lifespan,
        )

        # ── System ──────────────────────────────────────────
        @app.get("/health")
        async def health():
            return {"status": "ok", "service": "moodify-operator"}

        @app.get("/studio-os/status")
        async def studio_os_status():
            cfg = load_config()
            jobs = list_operator_jobs(cfg)
            deliveries = list_delivery_records(cfg)
            return {
                "active_jobs": len([j for j in jobs if j["status"] not in ("delivered", "failed")]),
                "pending_gates": len([j for j in jobs if j["status"] == "gate_review"]),
                "delivered_jobs": len([j for j in jobs if j["status"] == "delivered"]),
                "total_jobs": len(jobs),
                "total_deliveries": len(deliveries),
            }

        # ── Jobs ────────────────────────────────────────────
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
            return create_operator_job(
                cfg,
                source_audio=source_audio,
                processing_depth=processing_depth,
                project_label=project_label,
                customer_label=customer_label,
                target_notes=target_notes,
                priority=priority,
            )

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

        @app.post("/operator/jobs/{job_id}/plan-runtime")
        async def api_plan_runtime(job_id: str):
            cfg = load_config()
            return plan_operator_runtime(cfg, job_id=job_id)

        @app.post("/operator/jobs/{job_id}/run")
        async def api_run_job(job_id: str, dry_run: bool = False):
            cfg = load_config()
            return run_operator_job(cfg, job_id=job_id, dry_run=dry_run)

        @app.post("/operator/jobs/{job_id}/attach-run")
        async def api_attach_run(
            job_id: str,
            run_id: str,
            run_dir: Optional[str] = None,
            report_path: Optional[str] = None,
            required_mrs_delta: float = 0.0,
        ):
            cfg = load_config()
            return attach_run_report_to_job(
                cfg,
                job_id=job_id,
                run_id=run_id,
                run_dir=run_dir,
                report_path=report_path,
                required_mrs_delta=required_mrs_delta,
            )

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

        @app.post("/operator/jobs/{job_id}/deliver")
        async def api_deliver(
            job_id: str,
            candidate_id: str,
            operator_decision: str = "approved",
            notes: str = "",
            override: bool = False,
        ):
            cfg = load_config()
            return create_delivery_record(
                cfg,
                job_id=job_id,
                candidate_id=candidate_id,
                operator_decision=operator_decision,
                notes=notes,
                override=override,
            )

        @app.get("/operator/jobs/{job_id}/delivery")
        async def api_get_delivery(job_id: str):
            cfg = load_config()
            return get_delivery_record(cfg, job_id=job_id)

        @app.post("/operator/jobs/{job_id}/writeback-craft")
        async def api_writeback_craft(
            job_id: str,
            candidate_id: str,
            adoption_status: str = "candidate",
            operator_notes: str = "",
        ):
            cfg = load_config()
            return writeback_delivery_to_craft_record(
                cfg,
                job_id=job_id,
                candidate_id=candidate_id,
                adoption_status=adoption_status,
                operator_notes=operator_notes,
            )

        # ── Delivery ────────────────────────────────────────
        @app.get("/operator/deliveries")
        async def api_list_deliveries():
            cfg = load_config()
            return {"deliveries": list_delivery_records(cfg)}

        # ── Static ──────────────────────────────────────────
        @app.get("/operator", response_class=HTMLResponse)
        async def operator_console():
            return _PAGE

        @app.get("/", response_class=HTMLResponse)
        async def root():
            return _PAGE

        # ── Scheduler placeholder (MHP-038) ─────────────────
        @app.get("/scheduler/runs")
        async def scheduler_runs():
            return {"runs": [], "note": "MHP-038 not yet implemented"}

        # ── Craft placeholder (MHP-037) ────────────────────
        @app.get("/craft/records")
        async def craft_records(adoption_status: Optional[str] = None):
            cfg = load_config()
            return {"records": list_craft_records(cfg, adoption_status=adoption_status)}

        return app

    except ImportError:
        return None


app = _get_app()
