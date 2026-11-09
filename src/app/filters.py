"""Pure functions to clean and filter scraped job records (no network)."""

import math
import re
import unicodedata
from datetime import date, datetime
from typing import Any

INCLUDE_TITLE = re.compile(r"arquitet|projetista|desenhista|cadista", re.IGNORECASE)

# "Arquiteto" in the IT sense, sales roles and internships are noise for this profile.
EXCLUDE_TITLE = re.compile(
    r"software|sistema|solu[cç]|dados|data\b|cloud|\bti\b|\bia\b|\bai\b|devops|salesforce|"
    r"java|golang|python|aplica[cç]|integra[cç]|seguran[cç]a|redes|network|enterprise|"
    r"vendedor|vendas|estagi|est[aá]gio|trainee|aprendiz|"
    r"mecanic|eletric|ar condicionado|climatiza|ferramentaria|automac|industrial|"
    r"\bsap\b|cyber|negocio",
    re.IGNORECASE,
)

TRACKING_PARAMS = re.compile(r"[?&](utm_[^=&]+|ref|refId|trackingId|trk|source|gclid|fbclid)=[^&]*")


def strip_accents(text: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", text) if not unicodedata.combining(ch)
    )


def is_relevant_title(title: str | None) -> bool:
    if not title:
        return False
    plain = strip_accents(title)
    return bool(INCLUDE_TITLE.search(plain)) and not EXCLUDE_TITLE.search(plain)


def normalize_url(url: str | None) -> str | None:
    if not url:
        return None
    cleaned = TRACKING_PARAMS.sub("", url)
    if "?" not in cleaned and "&" in cleaned:
        cleaned = cleaned.replace("&", "?", 1)
    return cleaned.split("#", 1)[0].rstrip("/")


def clean_value(value: Any) -> Any:
    """Turn pandas/numpy leftovers into JSON-safe values."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if hasattr(value, "item"):  # numpy scalar
        return clean_value(value.item())
    if isinstance(value, str):
        return value.strip() or None
    return value


def dedup_key(job: dict[str, Any]) -> str:
    company = strip_accents(str(job.get("company") or "")).lower().strip()
    title = strip_accents(str(job.get("title") or "")).lower().strip()
    location = strip_accents(str(job.get("location") or "")).lower().strip()
    return f"{company}|{title}|{location}"


def dedupe(jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop repeats by URL or company+title+location; prefer records with a direct URL."""
    jobs = sorted(jobs, key=lambda j: j.get("job_url_direct") is None)
    seen_urls: set[str] = set()
    seen_keys: set[str] = set()
    result = []
    for job in jobs:
        url = job.get("job_url")
        key = dedup_key(job)
        if (url and url in seen_urls) or key in seen_keys:
            continue
        if url:
            seen_urls.add(url)
        seen_keys.add(key)
        result.append(job)
    return result
