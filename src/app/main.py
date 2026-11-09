"""Ponto de entrada: `uv run app`. Gera output/vagas.json para a skill ai-headhunter."""

import json
import logging
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from app.config import settings
from app.filters import dedupe
from app.scraper import run
from app.validate import validate_jobs

log = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    jobs, status = run(settings)
    jobs = dedupe(jobs)
    validate_jobs(jobs)

    payload = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "hours_old": settings.hours_old,
        "sites": {site: asdict(st) for site, st in status.items()},
        "total_jobs": len(jobs),
        "jobs": jobs,
    }
    path = Path(settings.output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("wrote %d jobs to %s", len(jobs), path)
    for site, st in status.items():
        log.info(
            "%s: %d ok, %d failed, %d raw", site, st.ok_queries, st.failed_queries, st.raw_results
        )


if __name__ == "__main__":
    main()
