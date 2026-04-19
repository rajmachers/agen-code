# Ops SLA and Incident Playbook

## 1) SLA Targets

## Real-Time Intervention
- p50 latency: < 2.0 seconds
- p95 latency: <= 4.0 seconds
- error rate: < 1.0 percent over 15-minute window

## Connector Sync
- outcome sync success: >= 99.0 percent
- retry success for transient failures: >= 99.5 percent

## Security Guards
- claim guard violation acceptance: 0
- cross-tenant leakage incidents: 0

## 2) Incident Severity

- Sev1: SLA breach impacting active assessments or any data isolation risk
- Sev2: sustained degradation with workaround available
- Sev3: localized issue with limited tenant impact

## 3) Runbooks

## Latency Breach (Sev1/Sev2)
1. Confirm dashboard breach on p50 or p95.
2. Activate fast-path fallback prompt template.
3. Route deep reasoning calls to async tier.
4. Scale intervention workers.
5. Validate recovery over 3 rolling windows.

## Claim Guard Breach (Sev1)
1. Freeze release pipeline immediately.
2. Block affected endpoint route.
3. Rotate access tokens and inspect audit trails.
4. Run cross-tenant negative test suite.
5. Resume only after security sign-off.

## Connector Sync Degradation (Sev2)
1. Check connector health and dependency status.
2. Enable retry backoff profile.
3. Queue unsent outcome payloads for replay.
4. Verify idempotent reprocessing.

## 4) Alert Rules

- Latency p50 >= 2.0s for 5 minutes
- Latency p95 >= 4.0s for 3 minutes
- Claim guard rejection anomaly spike > baseline
- Connector sync failures > 1 percent in 10 minutes

## 5) Incident Roles

- Incident Commander: SRE lead
- Technical Owner (latency): ML lead
- Technical Owner (claims): Security lead
- Technical Owner (sync): Integrations lead
- Communications: Product lead

## 6) Post-Incident Requirements

- RCA completed within 48 hours
- Corrective action tickets created and prioritized
- Regression tests added for failure mode
- SLA trend reviewed in weekly ops meeting
