# 020 — Emergency Policy

## Purpose

Some situations cannot wait for a full MIP cycle:

- a critical security vulnerability is being actively exploited.
- a credential or key is leaked or compromised.
- an infrastructure endpoint is misbehaving in a way that harms Residents.
- an active exploit against the public surface is in progress.

This policy defines the minimum-viable emergency response.

## What Emergency Action May Do

A Maintainer acting under emergency policy may:

- pause a subsystem (e.g. stop accepting new submissions to a task).
- hide a dangerous endpoint from the public surface.
- disable a claim / economic path that is in flight.

A Maintainer may NOT, under emergency policy:

- bypass canon without a follow-up MIP.
- permanently delete a registry record.
- rewrite history.
- unilaterally move a MIP to `accepted` outside the normal flow.

## Required Logging

Every emergency action MUST be recorded with:

1. **Actor** — Resident ID of the Maintainer taking the action.
2. **Reason** — short rationale explaining the threat.
3. **Time** — exact ISO-8601 timestamp.
4. **Scope** — exactly what was paused, hidden, or disabled.

The record is stored in the registry as a `MipUpdated` audit event with
the reason explaining the emergency.

## Retrospective MIP

Within 7 days of an emergency action, the Maintainer who took the action
MUST either:

- open a new MIP describing the incident, the action taken, and the
  follow-up remediation, or
- attach a `MipImplemented` reference to an existing MIP that documents
  the same.

The retrospective MIP is the public record of what happened. Without it,
the emergency action is not a closed incident.

## Abuse Prevention

Emergency policy may not be used:

- to permanently bypass governance.
- to suppress a public decision record.
- to hide an operational bug from the audit trail.
- as a substitute for the normal MIP review process.

If an emergency action becomes a pattern, it is itself a governance
problem and must be addressed via a new MIP (category `governance` or
`security`).

## Sunset

There is no permanent emergency mode. The registry always returns to the
normal lifecycle after the action. Emergency actions are bounded in
duration by the retrospective MIP.
