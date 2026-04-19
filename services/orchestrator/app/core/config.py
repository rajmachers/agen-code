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

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
