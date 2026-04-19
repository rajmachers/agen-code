# API Payload Examples

## 1) Connector Configuration

Request:
```json
{
  "tenantId": "tenant-acme",
  "connectorType": "moodle",
  "contractVersion": "v1.0",
  "endpoints": {
    "launchResolve": "https://moodle.example.com/local/codingengine/launch",
    "outcomePush": "https://moodle.example.com/local/codingengine/outcomes",
    "health": "https://moodle.example.com/local/codingengine/health",
    "capabilities": "https://moodle.example.com/local/codingengine/capabilities"
  },
  "auth": {
    "method": "oauth2",
    "clientId": "acme-platform-client",
    "secretRef": "vault://tenant-acme/moodle/client-secret",
    "tokenUrl": "https://moodle.example.com/oauth2/token"
  },
  "mappings": {
    "roles": {
      "instructor": "editingteacher",
      "candidate": "student",
      "evaluator": "teacher"
    },
    "course": "courseid",
    "module": "cmid",
    "activity": "instanceid"
  },
  "capabilities": {
    "launch": true,
    "rosterSync": true,
    "competencySync": true,
    "resultRelease": true
  },
  "retryPolicy": {
    "maxAttempts": 5,
    "backoffSeconds": 10
  }
}
```

## 2) Zero-Shot Authoring

Request:
```json
{
  "tenantId": "tenant-acme",
  "sourceUrl": "https://github.com/acme-org/python-foundations",
  "pedagogyProfile": "foundational",
  "trackName": "Python Foundations Track",
  "targetModes": ["practice", "exam"],
  "competencyTargets": ["Data Structures", "Control Flow", "Debugging"]
}
```

Response:
```json
{
  "trackId": "trk_9f2a11",
  "status": "generated",
  "modules": 8,
  "assessments": 12,
  "competencyDraft": ["Data Structures", "Control Flow", "Debugging"]
}
```

## 3) Realtime Intervention

Request:
```json
{
  "tenantId": "tenant-acme",
  "attemptId": "att_7719",
  "mode": "practice",
  "language": "python",
  "cursorContext": {
    "file": "solution.py",
    "line": 42,
    "snippet": "for i in range(len(nums))"
  },
  "intent": "optimize_loop",
  "hintBudgetRemaining": 3
}
```

Response:
```json
{
  "requestId": "req_31c8",
  "latencyMs": 864,
  "severity": "medium",
  "message": "Possible O(n^2) pattern detected. Consider a hash map for lookups.",
  "explainWhy": "Nested scans can degrade performance on large inputs.",
  "actions": ["show_example", "ignore_once"]
}
```

## 4) Submission Result (Binary-Plus)

Response:
```json
{
  "submissionId": "sub_1201",
  "overallScore": 84,
  "baselineScore": 76,
  "insightScore": 92,
  "skillsMastered": ["Hash Maps", "Edge Case Handling"],
  "skillsNeedingSupport": ["Complexity Analysis"],
  "integrityFlags": [],
  "evidenceRefs": [
    "test:T17",
    "code:solution.py#L35",
    "dialogue:evt_901"
  ]
}
```

## 5) LMS Outcome Push

Request:
```json
{
  "tenantId": "tenant-acme",
  "submissionId": "sub_1201",
  "lmsContext": {
    "courseId": "C-440",
    "activityId": "A-903"
  },
  "outcome": {
    "overallScore": 84,
    "baselineScore": 76,
    "insightScore": 92,
    "skillsMastered": ["Hash Maps", "Edge Case Handling"],
    "skillsNeedingSupport": ["Complexity Analysis"],
    "evidenceRefs": ["test:T17", "code:solution.py#L35"]
  },
  "idempotencyKey": "idem_outcome_sub_1201"
}
```

## 6) Simulator Scenario Create

Request:
```json
{
  "scenarioId": "demo_acme_w1",
  "scenarioType": "quick_demo",
  "seed": 12345,
  "tenantConfig": {
    "tenantId": "tenant-acme",
    "connectorType": "moodle"
  },
  "courseConfig": {
    "courseCount": 2,
    "pedagogyProfile": "foundational",
    "sourceUrls": ["https://github.com/acme-org/python-foundations"]
  },
  "batchConfig": {
    "batchCount": 1,
    "modeMix": {"practice": 0.8, "interview": 0.1, "exam": 0.1}
  },
  "population": {
    "candidates": 40,
    "instructors": 2,
    "evaluators": 2
  },
  "timeline": {
    "mode": "accelerated",
    "durationDays": 14
  },
  "governance": {
    "simulationSource": "simulator_service",
    "purgeOnComplete": false
  }
}
```
