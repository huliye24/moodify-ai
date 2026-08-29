"""Internal CWC compute-credit endpoints (credits are not currency)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select

from moodify_music import audit
from moodify_music.models import CwcAccount, CwcLedger, User
from moodify_music.api.deps import Db, error, service_key_required
from moodify_music.api.idem import idempotent_write, replay_response, request_id

router = APIRouter(prefix="/internal/v1/music", dependencies=[Depends(service_key_required)])


@router.post("/cwc/accounts", status_code=201)
def create_cwc_account(db: Db, request: Request, body: dict):
    user_id = body.get("user_id")
    if not user_id or db.get(User, user_id) is None:
        raise error(404, "RESOURCE_NOT_FOUND", "user not found")
    if db.scalar(select(CwcAccount).where(CwcAccount.user_id == user_id)):
        raise error(409, "CWC_ACCOUNT_EXISTS", "account already exists")
    acc = CwcAccount(user_id=user_id, balance_units=int(body.get("balance_units") or 0))
    db.add(acc)
    db.flush()
    payload = {"user_id": user_id}
    resp = {"id": acc.id, "user_id": user_id, "balance_units": acc.balance_units}
    row, replayed = idempotent_write(db, request, "cwc_mutation", payload, response=resp, resource_type="cwc_account", resource_id=acc.id)
    if replayed:
        db.rollback()
        return replay_response(row)
    audit.record(db, actor_type="system", actor_id=None, action="cwc.changed", resource_type="cwc_account", resource_id=acc.id, request_id=request_id(request), metadata={"delta": acc.balance_units})
    db.commit()
    return resp


@router.get("/cwc/accounts/{user_id}")
def get_cwc_account(user_id: str, db: Db):
    acc = db.scalar(select(CwcAccount).where(CwcAccount.user_id == user_id))
    if acc is None:
        raise error(404, "RESOURCE_NOT_FOUND", "cwc account not found")
    return {"id": acc.id, "user_id": user_id, "balance_units": acc.balance_units}


@router.post("/cwc/ledger", status_code=201)
def cwc_mutation(db: Db, request: Request, body: dict):
    """Atomic balance change with ledger row (integer units only)."""
    user_id = body.get("user_id")
    acc = db.scalar(select(CwcAccount).where(CwcAccount.user_id == user_id)) if user_id else None
    if acc is None:
        raise error(404, "RESOURCE_NOT_FOUND", "cwc account not found")
    delta = int(body.get("delta_units", 0))
    if delta == 0:
        raise error(400, "VALIDATION_ERROR", "delta_units must be non-zero integer")
    if acc.balance_units + delta < 0:
        raise error(409, "CWC_INSUFFICIENT", "insufficient balance")
    acc.balance_units += delta
    entry = CwcLedger(account_id=acc.id, delta_units=delta, reason=(body.get("reason") or "adjustment")[:128],
                      reference_type=body.get("reference_type"), reference_id=body.get("reference_id"))
    db.add(entry)
    db.flush()
    payload = {"user_id": user_id, "delta_units": delta, "reason": entry.reason}
    resp = {"account_id": acc.id, "balance_units": acc.balance_units, "ledger_id": entry.id}
    row, replayed = idempotent_write(db, request, "cwc_mutation", payload, response=resp, resource_type="cwc_ledger", resource_id=entry.id)
    if replayed:
        db.rollback()
        return replay_response(row)
    audit.record(db, actor_type="system", actor_id=None, action="cwc.changed", resource_type="cwc_ledger", resource_id=entry.id, request_id=request_id(request), metadata={"delta": delta, "balance": acc.balance_units})
    db.commit()
    return resp
