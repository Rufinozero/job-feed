"""Configuração carregada do ambiente / arquivo .env."""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _list(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "dev")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    sites: list[str] = field(default_factory=lambda: _list("SITES", "linkedin,glassdoor,indeed"))
    search_terms: list[str] = field(
        default_factory=lambda: _list(
            "SEARCH_TERMS",
            "analista de arquitetura,arquiteta,arquiteto,projetista de arquitetura,"
            "assistente de arquitetura,cadista,desenhista",
        )
    )
    hybrid_location: str = os.getenv("HYBRID_LOCATION", "Belo Horizonte, MG")
    # JobSpy uses miles; 30 mi ~ 48 km, enough to cover the Belo Horizonte metro area.
    hybrid_distance_miles: int = int(os.getenv("HYBRID_DISTANCE_MILES", "30"))
    remote_location: str = os.getenv("REMOTE_LOCATION", "Brasil")
    country: str = os.getenv("COUNTRY", "Brazil")
    hours_old: int = int(os.getenv("HOURS_OLD", "168"))
    results_per_query: int = int(os.getenv("RESULTS_PER_QUERY", "15"))
    linkedin_fetch_description: bool = os.getenv("LINKEDIN_FETCH_DESCRIPTION", "true") == "true"
    output_path: str = os.getenv("OUTPUT_PATH", "output/vagas.json")


settings = Settings()
