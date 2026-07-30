"""Atomic pair writer for co-generated artifacts (JSON + Markdown).

Ensures that a pair of co-generated files is always presented atomically:
either the complete previous pair or the complete new pair, never a mixed
current pair from different generations.

Uses a transaction-marker protocol with a run-scoped staging directory.

Part of DSK-MFY-AUX-HARDENING-002 Batch B.
"""

from __future__ import annotations

import json
import os
import shutil
import uuid
from pathlib import Path
from typing import Any


class AtomicPairWriter:
    """Write a JSON/Markdown pair atomically with transaction recovery.

    Usage::

        writer = AtomicPairWriter(output_dir)
        writer.write(
            json_data={"key": "value"},
            json_filename="summary.json",
            md_content="# Title\\n\\nContent",
            md_filename="summary.md",
        )

    On interruption, the next ``write()`` or explicit ``recover()`` call
    detects orphaned transactions and completes or rolls them back.
    """

    def __init__(self, output_dir: Path | str):
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    # ── Public API ──────────────────────────────────────────────────

    def write(
        self,
        json_data: dict[str, Any],
        json_filename: str,
        md_content: str,
        md_filename: str,
    ) -> dict[str, Any]:
        """Write a JSON/Markdown pair atomically.

        Returns a result dict with ``status``, ``json_path``, ``md_path``,
        and any ``recovery`` details.
        """
        result: dict[str, Any] = {
            "status": "ok",
            "json_path": str(self._output_dir / json_filename),
            "md_path": str(self._output_dir / md_filename),
            "recovery": None,
        }

        # 1. Recover any orphaned transaction from a prior run
        recovery_info = self.recover(json_filename, md_filename)
        if recovery_info:
            result["recovery"] = recovery_info

        # 2. Create run-scoped staging directory
        stage_id = uuid.uuid4().hex[:12]
        stage_dir = self._output_dir / f".pair_tmp_{stage_id}"
        stage_dir.mkdir(parents=True, exist_ok=False)

        # 3. Target paths (computed early for exception-scope access)
        json_target = self._output_dir / json_filename
        md_target = self._output_dir / md_filename

        json_stage = stage_dir / json_filename
        md_stage = stage_dir / md_filename

        tx_marker = stage_dir / ".tx_active"
        try:

            json_stage.write_text(
                json.dumps(json_data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            md_stage.write_text(md_content, encoding="utf-8")

            # 4. Validate both artifacts exist and are non-empty
            if json_stage.stat().st_size == 0:
                raise ValueError(f"Staged JSON is empty: {json_stage}")
            if md_stage.stat().st_size == 0:
                raise ValueError(f"Staged Markdown is empty: {md_stage}")

            # Validate JSON is parseable
            try:
                json.loads(json_stage.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                raise ValueError(f"Staged JSON is not valid JSON: {e}")

            # 5. Set transaction marker
            tx_marker.write_text(
                json.dumps({
                    "stage_id": stage_id,
                    "json_filename": json_filename,
                    "md_filename": md_filename,
                    "status": "committing",
                }),
                encoding="utf-8",
            )

            # 6. Backup existing files (preserve previous complete pair)
            json_bak = self._output_dir / f"{json_filename}.prev"
            md_bak = self._output_dir / f"{md_filename}.prev"

            for target, bak in [(json_target, json_bak), (md_target, md_bak)]:
                if target.exists():
                    if bak.exists():
                        bak.unlink()
                    target.rename(bak)

            # 7. Move staged files to target
            shutil.move(str(json_stage), str(json_target))
            shutil.move(str(md_stage), str(md_target))

            # 8. Clear transaction marker → transaction complete
            tx_marker.unlink()

        except Exception:
            # A staged file that no longer exists was already promoted
            # (shutil.move succeeded). Both must be promoted for the new
            # generation to be current; otherwise restore from .prev.
            json_promoted = not json_stage.exists()
            md_promoted = not md_stage.exists()
            if not (json_promoted and md_promoted):
                self._restore_previous_pair(
                    json_filename, md_filename,
                    json_promoted=json_promoted,
                    md_promoted=md_promoted,
                )
            if tx_marker.exists():
                tx_marker.unlink()
            if stage_dir.exists():
                shutil.rmtree(str(stage_dir), ignore_errors=True)
            raise
        finally:
            if stage_dir.exists():
                shutil.rmtree(str(stage_dir), ignore_errors=True)

        return result

    def read_current_pair(
        self, json_filename: str, md_filename: str
    ) -> tuple[dict[str, Any], str]:
        """Recover first, then expose both current artifacts or neither."""
        self.recover(json_filename, md_filename)
        json_path = self._output_dir / json_filename
        md_path = self._output_dir / md_filename
        if not json_path.is_file() or not md_path.is_file():
            raise RuntimeError("No complete current artifact pair is available")
        data = json.loads(json_path.read_text(encoding="utf-8"))
        markdown = md_path.read_text(encoding="utf-8")
        if not markdown:
            raise RuntimeError("Current Markdown artifact is empty")
        return data, markdown

    def _restore_previous_pair(
        self,
        json_filename: str,
        md_filename: str,
        json_promoted: bool = False,
        md_promoted: bool = False,
    ) -> bool:
        """Restore a complete previous generation after partial promotion.

        Promoted targets (staging gone) are overwritten with their .prev
        backup. Unpromoted targets are left untouched when they exist (old
        version), or restored from .prev when they were already renamed
        during backup.
        """
        items = (
            (
                self._output_dir / json_filename,
                self._output_dir / f"{json_filename}.prev",
                json_promoted,
            ),
            (
                self._output_dir / md_filename,
                self._output_dir / f"{md_filename}.prev",
                md_promoted,
            ),
        )
        for target, previous, promoted in items:
            if promoted:
                # New version at target — overwrite from backup
                if not previous.is_file():
                    continue
            else:
                # Not promoted — leave as-is if target exists (old version),
                # restore from .prev if target was renamed during backup
                if target.exists():
                    continue
                if not previous.is_file():
                    return False
            restore_tmp = target.with_name(f".{target.name}.restore")
            shutil.copy2(previous, restore_tmp)
            os.replace(restore_tmp, target)
        return True

    def recover(
        self,
        json_filename: str,
        md_filename: str,
    ) -> dict[str, Any] | None:
        """Recover from any orphaned transaction.

        Scans for leftover ``.pair_tmp_*`` staging directories and either
        completes or rolls back orphaned transactions.

        Returns recovery details if orphaned state was found, None otherwise.
        """
        orphans = sorted(self._output_dir.glob(".pair_tmp_*"))
        if not orphans:
            return None

        recovered = []
        for orphan_dir in orphans:
            tx_marker = orphan_dir / ".tx_active"
            json_stage = orphan_dir / json_filename
            md_stage = orphan_dir / md_filename
            json_target = self._output_dir / json_filename
            md_target = self._output_dir / md_filename

            if tx_marker.exists() and json_stage.exists() and md_stage.exists():
                # Transaction was interrupted mid-commit. Validate staged files.
                try:
                    if json_stage.stat().st_size == 0:
                        raise ValueError("empty JSON stage")
                    if md_stage.stat().st_size == 0:
                        raise ValueError("empty MD stage")
                    json.loads(json_stage.read_text(encoding="utf-8"))

                    # Staged files are valid — complete the transaction
                    json_bak = self._output_dir / f"{json_filename}.prev"
                    md_bak = self._output_dir / f"{md_filename}.prev"
                    for target, bak in [(json_target, json_bak), (md_target, md_bak)]:
                        if target.exists():
                            if bak.exists():
                                bak.unlink()
                            target.rename(bak)
                    shutil.move(str(json_stage), str(json_target))
                    shutil.move(str(md_stage), str(md_target))
                    tx_marker.unlink()
                    recovered.append({
                        "orphan": orphan_dir.name,
                        "action": "completed",
                        "reason": "valid staged files found",
                    })
                except Exception as e:
                    # Validation or completion failed. A staged move may have
                    # partially promoted, so restore the previous complete pair.
                    json_promoted = not json_stage.exists()
                    md_promoted = not md_stage.exists()
                    restored = self._restore_previous_pair(
                        json_filename, md_filename,
                        json_promoted=json_promoted,
                        md_promoted=md_promoted,
                    )
                    recovered.append({
                        "orphan": orphan_dir.name,
                        "action": "rolled_back",
                        "reason": f"staged files invalid: {e}",
                        "previous_pair_restored": restored,
                    })
            else:
                # No active tx marker or incomplete staging — rollback
                restored = self._restore_previous_pair(json_filename, md_filename)
                recovered.append({
                    "orphan": orphan_dir.name,
                    "action": "rolled_back",
                    "reason": "incomplete staging or missing tx marker",
                    "previous_pair_restored": restored,
                })

            # Clean up staging directory
            if tx_marker.exists():
                tx_marker.unlink()
            shutil.rmtree(str(orphan_dir), ignore_errors=True)

        return {"orphaned_transactions": len(orphans), "details": recovered} if recovered else None
