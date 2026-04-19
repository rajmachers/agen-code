import { useState } from "react";

import MonacoWorkspace from "./components/MonacoWorkspace";
import { evaluateSubmission, generateModule } from "./api/client";

const starterCode = `def two_sum(nums, target):\n    seen = {}\n    for idx, value in enumerate(nums):\n        diff = target - value\n        if diff in seen:\n            return [seen[diff], idx]\n        seen[value] = idx\n    return []\n`;

export default function App() {
  const [topic, setTopic] = useState("arrays and hash maps");
  const [code, setCode] = useState(starterCode);
  const [moduleData, setModuleData] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleGenerate() {
    setLoading(true);
    try {
      const data = await generateModule(topic);
      setModuleData(data);
    } catch (err) {
      setModuleData({ summary: err.message, roadmap: [], quiz: [] });
    } finally {
      setLoading(false);
    }
  }

  async function handleEvaluate() {
    setLoading(true);
    try {
      const data = await evaluateSubmission({
        assignment_id: "array-001",
        learner_id: "demo-learner",
        language: "python",
        repo_url: "https://example.com/demo-repo.git",
        commit_hash: String(code.length),
        tests_path: "tests",
      });
      setResult(data);
    } catch (err) {
      setResult({ ai_feedback: err.message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <header>
        <h1>CodeLab Assessment Studio</h1>
        <p>Monaco + Ollama + Moodle orchestration MVP</p>
      </header>

      <section className="panel controls">
        <input
          value={topic}
          onChange={(event) => setTopic(event.target.value)}
          placeholder="Enter concept (e.g. dynamic programming)"
        />
        <button onClick={handleGenerate} disabled={loading}>Generate Learning Module</button>
        <button onClick={handleEvaluate} disabled={loading}>Run Assessment</button>
      </section>

      <MonacoWorkspace code={code} onCodeChange={setCode} />

      <section className="grid">
        <article className="panel">
          <h2>Learning Output</h2>
          <p>{moduleData?.summary || "Generate a module to view roadmap and quiz."}</p>
          <ul>
            {(moduleData?.roadmap || []).map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ul>
        </article>

        <article className="panel">
          <h2>Assessment Feedback</h2>
          <p>Score: {result?.score ?? "-"}</p>
          <p>Pass rate: {result?.test_pass_rate ?? "-"}</p>
          <p>Execution (ms): {result?.execution_ms ?? "-"}</p>
          <p>Memory (MB): {result?.memory_mb ?? "-"}</p>
          <p>{result?.ai_feedback || "Run assessment to receive AI feedback."}</p>
        </article>
      </section>
    </div>
  );
}
