import { useEffect, useMemo, useState } from "react";

import MonacoWorkspace from "./components/MonacoWorkspace";
import {
  configureConnector,
  createScenario,
  createScenarioFromTemplate,
  deleteConnector,
  evaluateSubmission,
  generateModule,
  getConnector,
  getScenarioReport,
  getScenarioStatus,
  listConnectors,
  listSimulatorTemplates,
  pauseScenario,
  purgeScenario,
  replayScenario,
  resumeScenario,
  runScenario,
} from "./api/client";

const starterCode = `def two_sum(nums, target):\n    seen = {}\n    for idx, value in enumerate(nums):\n        diff = target - value\n        if diff in seen:\n            return [seen[diff], idx]\n        seen[value] = idx\n    return []\n`;

const starterScenario = {
  scenarioId: "demo_ui_001",
  scenarioType: "quick_demo",
  seed: 12345,
  tenantConfig: { tenantId: "tenant-acme", connectorType: "moodle" },
  courseConfig: { courseCount: 2, pedagogyProfile: "foundational" },
  batchConfig: {
    batchCount: 1,
    modeMix: { practice: 0.8, interview: 0.1, exam: 0.1 },
  },
  population: { candidates: 40, instructors: 2, evaluators: 2 },
  timeline: { mode: "accelerated", durationDays: 14 },
  governance: { simulationSource: "simulator_service", purgeOnComplete: false },
};

const starterConnector = {
  tenantId: "tenant-acme",
  connectorType: "moodle",
  contractVersion: "v1.0",
  endpoints: {
    launchResolve: "https://moodle.example.com/local/codingengine/launch",
    outcomePush: "https://moodle.example.com/local/codingengine/outcomes",
    health: "https://moodle.example.com/local/codingengine/health",
    capabilities: "https://moodle.example.com/local/codingengine/capabilities",
  },
  auth: {
    method: "oauth2",
    clientId: "acme-platform-client",
    secretRef: "vault://tenant-acme/moodle/client-secret",
    tokenUrl: "https://moodle.example.com/oauth2/token",
  },
  mappings: {
    roles: {
      instructor: "editingteacher",
      candidate: "student",
      evaluator: "teacher",
    },
    course: "courseid",
    module: "cmid",
    activity: "instanceid",
  },
  capabilities: {
    launch: true,
    rosterSync: true,
    competencySync: true,
    resultRelease: true,
  },
  retryPolicy: { maxAttempts: 5, backoffSeconds: 10 },
};

export default function App() {
  const [activeTab, setActiveTab] = useState("simulator");
  const [topic, setTopic] = useState("arrays and hash maps");
  const [code, setCode] = useState(starterCode);
  const [moduleData, setModuleData] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const [templates, setTemplates] = useState([]);
  const [templateId, setTemplateId] = useState("quick_demo");
  const [tenantId, setTenantId] = useState("tenant-acme");
  const [scenarioId, setScenarioId] = useState("demo_ui_001");
  const [connectorType, setConnectorType] = useState("moodle");
  const [scenarioJson, setScenarioJson] = useState(JSON.stringify(starterScenario, null, 2));
  const [connectorJson, setConnectorJson] = useState(JSON.stringify(starterConnector, null, 2));
  const [connectorsState, setConnectorsState] = useState(null);
  const [scenarioState, setScenarioState] = useState(null);
  const [reportState, setReportState] = useState(null);
  const [lastAction, setLastAction] = useState("No simulation actions run yet.");
  const [simBusy, setSimBusy] = useState(false);

  useEffect(() => {
    loadTemplates();
  }, []);

  const parsedScenario = useMemo(() => {
    try {
      return JSON.parse(scenarioJson);
    } catch {
      return null;
    }
  }, [scenarioJson]);

  const parsedConnector = useMemo(() => {
    try {
      return JSON.parse(connectorJson);
    } catch {
      return null;
    }
  }, [connectorJson]);

  async function withSimAction(name, action) {
    setSimBusy(true);
    try {
      const response = await action();
      setLastAction(`${name}: success`);
      return response;
    } catch (err) {
      setLastAction(`${name}: ${err.message}`);
      return null;
    } finally {
      setSimBusy(false);
    }
  }

  async function loadTemplates() {
    const response = await withSimAction("Load templates", () => listSimulatorTemplates());
    if (response?.items) {
      setTemplates(response.items);
      if (response.items.length && !response.items.some((x) => x.templateId === templateId)) {
        setTemplateId(response.items[0].templateId);
      }
    }
  }

  async function runCreateFromTemplate() {
    const response = await withSimAction("Create scenario from template", () =>
      createScenarioFromTemplate(templateId, {
        tenant_id: tenantId,
        scenario_id: scenarioId,
        connector_type: connectorType,
      }),
    );
    if (response?.scenarioId) {
      setScenarioId(response.scenarioId);
    }
  }

  async function runCreateCustomScenario() {
    if (!parsedScenario) {
      setLastAction("Create custom scenario: invalid JSON");
      return;
    }
    const response = await withSimAction("Create custom scenario", () => createScenario(parsedScenario));
    if (response?.scenarioId) {
      setScenarioId(response.scenarioId);
    }
  }

  async function runScenarioAction(actionName, fn) {
    if (!scenarioId) {
      setLastAction(`${actionName}: set a scenario id first`);
      return;
    }
    const response = await withSimAction(actionName, () => fn(scenarioId));
    if (!response) {
      return;
    }
    if (response.report) {
      setReportState(response.report);
    }
    if (response.status || response.scenarioId) {
      setScenarioState((prev) => ({ ...prev, ...response }));
    }
  }

  async function runGetStatus() {
    await runScenarioAction("Get scenario status", async (id) => {
      const response = await getScenarioStatus(id);
      setScenarioState(response);
      return response;
    });
  }

  async function runGetReport() {
    await runScenarioAction("Get scenario report", async (id) => {
      const response = await getScenarioReport(id);
      setReportState(response);
      return response;
    });
  }

  async function runConfigureConnector() {
    if (!parsedConnector) {
      setLastAction("Configure connector: invalid JSON");
      return;
    }
    await withSimAction("Configure connector", () => configureConnector(parsedConnector));
  }

  async function runListConnectors() {
    const response = await withSimAction("List connectors", () => listConnectors());
    if (response) {
      setConnectorsState(response);
    }
  }

  async function runGetConnector() {
    if (!tenantId) {
      setLastAction("Get connector: set tenant id first");
      return;
    }
    const response = await withSimAction("Get connector", () => getConnector(tenantId));
    if (response) {
      setConnectorsState(response);
    }
  }

  async function runDeleteConnector() {
    if (!tenantId) {
      setLastAction("Delete connector: set tenant id first");
      return;
    }
    await withSimAction("Delete connector", () => deleteConnector(tenantId));
  }

  function resetScenarioSample() {
    const next = { ...starterScenario, scenarioId };
    setScenarioJson(JSON.stringify(next, null, 2));
    setLastAction("Scenario sample payload loaded");
  }

  function resetConnectorSample() {
    const next = { ...starterConnector, tenantId, connectorType };
    setConnectorJson(JSON.stringify(next, null, 2));
    setLastAction("Connector sample payload loaded");
  }

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

      <section className="panel tabs">
        <button
          className={activeTab === "simulator" ? "tab active" : "tab"}
          onClick={() => setActiveTab("simulator")}
        >
          Simulator Test Console
        </button>
        <button
          className={activeTab === "learning" ? "tab active" : "tab"}
          onClick={() => setActiveTab("learning")}
        >
          Learning + Assessment
        </button>
      </section>

      {activeTab === "learning" && (
        <>
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
        </>
      )}

      {activeTab === "simulator" && (
        <section className="simulator-layout">
          <article className="panel step-card">
            <h2>Step 1: Set Test Context</h2>
            <p className="note">Pick IDs once. All guided actions below use these values.</p>
            <div className="field-grid">
              <label>
                Tenant ID
                <input value={tenantId} onChange={(event) => setTenantId(event.target.value)} />
              </label>
              <label>
                Scenario ID
                <input value={scenarioId} onChange={(event) => setScenarioId(event.target.value)} />
              </label>
              <label>
                Connector Type
                <input value={connectorType} onChange={(event) => setConnectorType(event.target.value)} />
              </label>
            </div>
          </article>

          <article className="panel step-card">
            <h2>Step 2: Create Scenario (Template Click Path)</h2>
            <p className="note">Recommended quick start for smoke testing.</p>
            <div className="inline-actions">
              <button disabled={simBusy} onClick={loadTemplates}>Load Templates</button>
              <select value={templateId} onChange={(event) => setTemplateId(event.target.value)}>
                {templates.map((item) => (
                  <option key={item.templateId} value={item.templateId}>
                    {item.templateId}
                  </option>
                ))}
              </select>
              <button disabled={simBusy || !templateId} onClick={runCreateFromTemplate}>Create from Template</button>
            </div>
          </article>

          <article className="panel step-card">
            <h2>Step 3: Optional Custom Scenario (Sample Data Autofill)</h2>
            <p className="note">Use this when you want custom population, timeline, or mode mix.</p>
            <div className="inline-actions">
              <button onClick={resetScenarioSample}>Load Sample Scenario JSON</button>
              <button disabled={simBusy} onClick={runCreateCustomScenario}>Create Custom Scenario</button>
            </div>
            <textarea
              className="json-box"
              value={scenarioJson}
              onChange={(event) => setScenarioJson(event.target.value)}
            />
          </article>

          <article className="panel step-card">
            <h2>Step 4: Execute Scenario</h2>
            <p className="note">Run first, then status/report. Replay helps deterministic regression checks.</p>
            <div className="inline-actions wrap">
              <button disabled={simBusy} onClick={() => runScenarioAction("Run scenario", runScenario)}>Run</button>
              <button disabled={simBusy} onClick={runGetStatus}>Status</button>
              <button disabled={simBusy} onClick={runGetReport}>Report</button>
              <button disabled={simBusy} onClick={() => runScenarioAction("Replay scenario", replayScenario)}>Replay</button>
              <button disabled={simBusy} onClick={() => runScenarioAction("Pause scenario", pauseScenario)}>Pause</button>
              <button disabled={simBusy} onClick={() => runScenarioAction("Resume scenario", resumeScenario)}>Resume</button>
            </div>
          </article>

          <article className="panel step-card">
            <h2>Step 5: Connector Sample Data and Lifecycle</h2>
            <p className="note">Use this section before LMS integration to validate connector config handling.</p>
            <div className="inline-actions wrap">
              <button onClick={resetConnectorSample}>Load Sample Connector JSON</button>
              <button disabled={simBusy} onClick={runConfigureConnector}>Configure</button>
              <button disabled={simBusy} onClick={runListConnectors}>List</button>
              <button disabled={simBusy} onClick={runGetConnector}>Get by Tenant</button>
              <button disabled={simBusy} onClick={runDeleteConnector}>Delete by Tenant</button>
            </div>
            <textarea
              className="json-box"
              value={connectorJson}
              onChange={(event) => setConnectorJson(event.target.value)}
            />
          </article>

          <article className="panel step-card danger">
            <h2>Step 6: Cleanup</h2>
            <p className="note">After each test cycle, purge scenario data to keep the environment clean.</p>
            <div className="inline-actions">
              <button
                disabled={simBusy || !scenarioId}
                onClick={() => runScenarioAction("Purge scenario", purgeScenario)}
              >
                Purge Scenario
              </button>
            </div>
          </article>

          <section className="grid">
            <article className="panel output">
              <h3>Action Log</h3>
              <p>{lastAction}</p>
            </article>
            <article className="panel output">
              <h3>Scenario Status</h3>
              <pre>{scenarioState ? JSON.stringify(scenarioState, null, 2) : "No status fetched yet."}</pre>
            </article>
            <article className="panel output">
              <h3>Scenario Report</h3>
              <pre>{reportState ? JSON.stringify(reportState, null, 2) : "No report fetched yet."}</pre>
            </article>
            <article className="panel output">
              <h3>Connector Result</h3>
              <pre>{connectorsState ? JSON.stringify(connectorsState, null, 2) : "No connector action yet."}</pre>
            </article>
          </section>
        </section>
      )}
    </div>
  );
}
