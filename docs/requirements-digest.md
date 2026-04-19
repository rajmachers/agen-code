# Requirements Digest and Recommendations

## Product goals

- Deliver coding practice and graded assessments in one workflow.
- Keep AI inference private and low latency with local model serving.
- Integrate deeply with Moodle for roster, grades, and adaptive learning paths.
- Provide educator controls for course generation, rubric tuning, and auditability.

## Functional requirements

- AI-generated learning modules:
  - concept roadmap
  - micro-lessons
  - objective-mapped quizzes
- Practice and assessment engine:
  - repo-based coding tasks
  - automated test execution
  - complexity/performance feedback
  - rubric-aligned preliminary grading
- Dynamic course generation in Moodle:
  - auto-create sections, activities, and question banks
  - adapt sequence based on learner signals
- Academic integrity:
  - plagiarism/anomaly analysis
  - proctoring signal ingestion
  - decision trails for faculty review

## Non-functional requirements

- Privacy-first: local model inference through Ollama.
- Reliable grading: deterministic test harness before AI commentary.
- Scalability: separate API/orchestrator from execution workers.
- Security: isolated execution for untrusted submissions.
- Explainability: store evidence for each score and flag.

## Recommendations

- Start with a single language lane (Python) and expand by runner adapters.
- Use hybrid scoring:
  - 70% deterministic tests/rubrics
  - 30% AI feedback for guidance and partial-credit suggestions
- Keep Moodle as system of record for enrollment and final grades.
- Store all attempts and AI prompts/responses for governance.
