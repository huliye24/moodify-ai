# Status Refresh Policy

Status refresh is not implemented because there is no public status endpoint or preparation ID. The unblock implementation should use bounded polling: immediate refresh, then stepped/exponential intervals with jitter, maximum attempts/time, foreground-aware scheduling and terminal stop on READY/FAILED/CANCELLED. Unknown backend values map to UNKNOWN. Restart refreshes persisted active IDs and never creates a request.
