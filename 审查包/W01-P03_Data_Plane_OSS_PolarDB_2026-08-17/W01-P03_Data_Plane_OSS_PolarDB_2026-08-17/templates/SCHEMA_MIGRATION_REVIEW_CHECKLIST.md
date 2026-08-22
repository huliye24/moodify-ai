# Schema Migration Review Checklist

## Engine
- [ ] Engine matches P02 decision
- [ ] Existing tables inspected
- [ ] No duplicate authority introduced

## Safety
- [ ] No DROP by default
- [ ] No destructive ALTER without explicit review
- [ ] Migration transaction behavior understood
- [ ] Rollback or forward-fix plan exists
- [ ] Backup prerequisite documented

## Identity
- [ ] Track ID stable
- [ ] Job ID stable
- [ ] Object ID stable
- [ ] Evidence ID stable
- [ ] hash indexed appropriately

## Relationships
- [ ] track → source
- [ ] job → track
- [ ] object → track
- [ ] produced object → job
- [ ] evidence → subject/claim

## Scope
- [ ] No queue semantics added
- [ ] No final state machine semantics added
- [ ] No large audio blob columns
