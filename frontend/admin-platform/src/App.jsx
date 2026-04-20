import { useState } from "react";
import {
  createTenant,
  getAuthMe,
  getTenantMetering,
  getTenantUsers,
  impersonateTenant,
  listTenants,
  upsertTenantUserRoles,
} from "./api";

export default function App() {
  const [token, setToken] = useState("");
  const [tenantId, setTenantId] = useState("tenant-acme");
  const [tenantName, setTenantName] = useState("Acme Org");
  const [userId, setUserId] = useState("teacher-1");
  const [rolesCsv, setRolesCsv] = useState("tenant_admin,teacher");
  const [auth, setAuth] = useState(null);
  const [tenants, setTenants] = useState(null);
  const [users, setUsers] = useState(null);
  const [metering, setMetering] = useState(null);
  const [impersonation, setImpersonation] = useState(null);
  const [message, setMessage] = useState("Ready");

  async function withAction(label, action) {
    try {
      const result = await action();
      setMessage(`${label}: success`);
      return result;
    } catch (error) {
      setMessage(`${label}: ${error.message}`);
      return null;
    }
  }

  return (
    <div className="page">
      <header>
        <h1>Admin Platform App</h1>
        <p>Super admin, tenant admin and integration governance.</p>
      </header>

      <section className="panel controls">
        <input
          value={token}
          onChange={(event) => setToken(event.target.value)}
          placeholder="Bearer token (optional while AUTH_ENABLED=false)"
        />
        <button onClick={() => withAction("Auth /me", async () => setAuth(await getAuthMe(token)))}>
          Load My Identity
        </button>
      </section>

      <section className="panel controls">
        <input value={tenantId} onChange={(event) => setTenantId(event.target.value)} placeholder="Tenant ID" />
        <input value={tenantName} onChange={(event) => setTenantName(event.target.value)} placeholder="Tenant name" />
        <button
          onClick={() =>
            withAction("Create tenant", async () =>
              createTenant(
                {
                  tenant_id: tenantId,
                  name: tenantName,
                  quotas: {
                    context_generations_daily: 200,
                    evidence_sessions_daily: 1000,
                    handover_daily: 1000,
                  },
                },
                token,
              ),
            )
          }
        >
          Create Tenant
        </button>
        <button onClick={() => withAction("List tenants", async () => setTenants(await listTenants(token)))}>
          List Tenants
        </button>
      </section>

      <section className="panel controls">
        <input value={userId} onChange={(event) => setUserId(event.target.value)} placeholder="User ID" />
        <input
          value={rolesCsv}
          onChange={(event) => setRolesCsv(event.target.value)}
          placeholder="Roles CSV"
        />
        <button
          onClick={() =>
            withAction("Upsert roles", async () =>
              upsertTenantUserRoles(
                tenantId,
                userId,
                rolesCsv.split(",").map((x) => x.trim()).filter(Boolean),
                token,
              ),
            )
          }
        >
          Upsert Tenant User Roles
        </button>
        <button onClick={() => withAction("List users", async () => setUsers(await getTenantUsers(tenantId, token)))}>
          List Tenant Users
        </button>
        <button onClick={() => withAction("Metering", async () => setMetering(await getTenantMetering(tenantId, token)))}>
          Get Metering
        </button>
      </section>

      <section className="panel controls">
        <button
          onClick={() =>
            withAction("Impersonate", async () =>
              setImpersonation(
                await impersonateTenant(
                  {
                    tenant_id: tenantId,
                    assumed_roles: ["tenant_admin"],
                  },
                  token,
                ),
              ),
            )
          }
        >
          Impersonated Tenant View
        </button>
      </section>

      <section className="grid">
        <article className="panel"><h3>Status</h3><p>{message}</p></article>
        <article className="panel"><h3>Identity</h3><pre>{auth ? JSON.stringify(auth, null, 2) : "-"}</pre></article>
        <article className="panel"><h3>Tenants</h3><pre>{tenants ? JSON.stringify(tenants, null, 2) : "-"}</pre></article>
        <article className="panel"><h3>Users</h3><pre>{users ? JSON.stringify(users, null, 2) : "-"}</pre></article>
        <article className="panel"><h3>Metering</h3><pre>{metering ? JSON.stringify(metering, null, 2) : "-"}</pre></article>
        <article className="panel"><h3>Impersonation</h3><pre>{impersonation ? JSON.stringify(impersonation, null, 2) : "-"}</pre></article>
      </section>
    </div>
  );
}
