# W01-P02 Acceptance Checklist

## Gates

- [ ] P00 Reality Gate passed
- [ ] P01 Canon Gate passed

## Node roles

- [ ] every observed node has one primary role
- [ ] secondary roles explicit
- [ ] forbidden roles explicit
- [ ] concurrency boundary explicit
- [ ] failure domain explicit
- [ ] recovery owner explicit

## Architecture

- [ ] Control Plane explicit
- [ ] Compute Plane explicit
- [ ] Data Plane boundary explicit
- [ ] Delivery Plane explicit
- [ ] no second Job authority
- [ ] DB and object storage roles separated
- [ ] client has no long-term cloud credentials

## Network/security

- [ ] network matrix complete
- [ ] public/private edges explicit
- [ ] secret ownership complete
- [ ] no secret values recorded

## Capacity/failure

- [ ] capacity contract complete
- [ ] unsupported claims marked UNKNOWN
- [ ] failure domain matrix complete
- [ ] revisit triggers documented

## Scope integrity

- [ ] no deployment
- [ ] no server mutation
- [ ] no DB mutation
- [ ] no OSS mutation
- [ ] no worker/API/Android mutation
- [ ] no heavy infra added

## Handoff

- [ ] target topology produced
- [ ] architecture decision register complete
- [ ] P03 handoff complete
- [ ] stop after P02
