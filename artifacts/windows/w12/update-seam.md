# Update Seam

`UpdateService` is disabled unless explicitly gated and does not download or execute anything. No unsafe updater was introduced. A future updater requires HTTPS plus a trusted manifest, artifact hash/signature verification, interrupted-download handling and rollback. `UPDATE_SEAM = SAFE_DISABLED`.
