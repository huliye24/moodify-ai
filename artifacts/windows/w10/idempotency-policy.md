# Idempotency Policy

No request is issued, so duplicate cloud tasks cannot be created by W10. After backend unblocking, UI trigger policy is MANUAL and the client must reject a second request while the same Track/source revision has an active preparation. A server idempotency key is mandatory for network retry; recommended input is stable Track ID plus server/content source revision. Restart may refresh an existing ID but never resubmit automatically.
