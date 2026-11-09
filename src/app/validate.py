"""Checks each job link from the runner (open internet) so the skill can trust the result."""

import logging
import time
from typing import Any

from app.filters import strip_accents

log = logging.getLogger(__name__)

CLOSED_MARKERS = [
    "vaga encerrada",
    "vaga nao esta mais disponivel",
    "esta vaga nao esta mais disponivel",
    "inscricoes encerradas",
    "inscricoes estao encerradas",
    "processo finalizado",
    "vaga expirada",
    "no longer accepting applications",
    "this job is no longer available",
    "job has expired",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
}


def classify(status_code: int | None, final_url: str | None, body: str, requested: str) -> str:
    """Return 'Validada', 'Encerrada' or 'Não validada'."""
    if status_code is None or status_code >= 400:
        return "Encerrada" if status_code in (404, 410) else "Não validada"
    text = strip_accents(body).lower()
    if any(marker in text for marker in CLOSED_MARKERS):
        return "Encerrada"
    if final_url and final_url.rstrip("/").count("/") <= 2 and requested.count("/") > 3:
        return "Não validada"  # redirected to a home page
    return "Validada"


def closed_evidence(body: str) -> str | None:
    """Short excerpt around the closure marker, to audit false positives."""
    text = strip_accents(body).lower()
    for marker in CLOSED_MARKERS:
        pos = text.find(marker)
        if pos >= 0:
            return text[max(0, pos - 120) : pos + 80].replace("\n", " ")
    return None


def check_url(session: Any, url: str) -> dict[str, Any]:
    try:
        resp = session.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
        body = resp.text[:400_000]
        result = classify(resp.status_code, resp.url, body, url)
        detail: dict[str, Any] = {
            "url": url,
            "status_code": resp.status_code,
            "final_url": resp.url,
            "result": result,
        }
        if result == "Encerrada":
            detail["evidence"] = closed_evidence(body)
        return detail
    except Exception as exc:  # noqa: BLE001 - network errors become "Não validada"
        return {
            "url": url,
            "status_code": None,
            "final_url": None,
            "result": "Não validada",
            "error": f"{type(exc).__name__}: {exc}"[:200],
        }


def validate_jobs(jobs: list[dict[str, Any]], delay_seconds: float = 1.5) -> None:
    """Annotate jobs in place with `validation` and `validation_detail`."""
    import requests

    session = requests.Session()
    for job in jobs:
        direct, listing = job.get("job_url_direct"), job.get("job_url")
        detail = check_url(session, direct) if direct else None
        if listing and (not detail or detail["result"] == "Não validada"):
            detail = check_url(session, listing)
        job["validation"] = detail["result"] if detail else "Não validada"
        job["validated_url"] = detail["url"] if detail and detail["result"] == "Validada" else None
        job["validation_detail"] = detail
        time.sleep(delay_seconds)
    counts: dict[str, int] = {}
    for job in jobs:
        counts[job["validation"]] = counts.get(job["validation"], 0) + 1
    log.info("validation: %s", counts)
