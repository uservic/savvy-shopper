from pathlib import Path
from typing import Any
import yaml
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://savvy:savvy_pass@db:5432/savvy_db"
    ollama_base_url: str = "http://docker.internal"
    ollama_model: str = "qwen2.5:14b"
    domains_dir: Path = Path("configs/domains")

    class Config:
        env_file = ".env"


settings = Settings()


def load_domain_config(domain_name: str = "smartphones") -> dict[str, Any]:
    """Загружает YAML-профиль домена с поддержкой наследования (ADR-002)."""
    target_path = settings.domains_dir / f"{domain_name}.yaml"
    if not target_path.exists():
        raise FileNotFoundError(f"Конфигурация домена не найдена: {target_path}")

    with open(target_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if "extends" in config:
        base_path = settings.domains_dir / config["extends"]
        with open(base_path, "r", encoding="utf-8") as f:
            base_config = yaml.safe_load(f)
        merged = {**base_config, **config}
        merged.pop("extends", None)
        return merged

    return config
