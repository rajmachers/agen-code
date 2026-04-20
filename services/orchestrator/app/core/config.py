from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5-coder:1.5b"
    ollama_timeout_seconds: int = 20
    ollama_num_predict: int = 32
    ollama_temperature: float = 0.1
    ollama_max_chars: int = 300
    assessment_ollama_timeout_seconds: int = 5
    assessment_ollama_num_predict: int = 12
    assessment_ollama_max_chars: int = 120
    assessment_use_ollama: bool = False
    learning_ollama_timeout_seconds: int = 6
    learning_ollama_num_predict: int = 16
    learning_ollama_max_chars: int = 140
    runner_base_url: str = "http://localhost:8010"
    simulator_base_url: str = "http://localhost:8020"
    moodle_base_url: str = "http://localhost:8081"
    moodle_token: str = "replace-me"
    connector_publish_history_path: str = "/tmp/orchestrator_moodle_publish_history.jsonl"
    auth_enabled: bool = False
    keycloak_base_url: str = "http://localhost:8080"
    keycloak_realm: str = "master"
    keycloak_client_id: str = "orchestrator-api"
    keycloak_client_secret: str = "replace-me"
    keycloak_verify_ssl: bool = True
    auth_claim_tenant: str = "tenant_id"
    auth_claim_tenants: str = "tenant_ids"
    auth_claim_roles: str = "roles"
    auth_claim_super_admin_role: str = "super_admin"
    auth_header_tenant: str = "x-tenant-id"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
