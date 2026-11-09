"""Runs JobSpy per site and query, isolating failures so one blocked site does not stop the rest."""

import logging
from dataclasses import dataclass, field
from typing import Any

from app.config import Settings
from app.filters import clean_value, is_relevant_title, normalize_url

log = logging.getLogger(__name__)

FIELDS = [
    "site",
    "title",
    "company",
    "location",
    "is_remote",
    "job_type",
    "job_level",
    "date_posted",
    "job_url",
    "job_url_direct",
    "min_amount",
    "max_amount",
    "currency",
    "interval",
    "emails",
    "description",
]


@dataclass(frozen=True)
class Query:
    site: str
    term: str
    mode: str  # "hybrid" or "remote"


@dataclass
class SiteStatus:
    ok_queries: int = 0
    failed_queries: int = 0
    raw_results: int = 0
    errors: list[str] = field(default_factory=list)


def build_queries(settings: Settings) -> list[Query]:
    return [
        Query(site=site, term=term, mode=mode)
        for site in settings.sites
        for term in settings.search_terms
        for mode in ("hybrid", "remote")
    ]


def query_params(query: Query, settings: Settings) -> dict[str, Any]:
    params: dict[str, Any] = {
        "site_name": [query.site],
        "search_term": query.term,
        "results_wanted": settings.results_per_query,
        "country_indeed": settings.country,
        "description_format": "markdown",
        "verbose": 0,
    }
    if query.mode == "hybrid":
        params |= {
            "location": settings.hybrid_location,
            "distance": settings.hybrid_distance_miles,
            "hours_old": settings.hours_old,
        }
    elif query.site == "indeed":
        # Indeed accepts only one of hours_old / is_remote, so search the keyword instead.
        params |= {
            "location": settings.remote_location,
            "search_term": f"{query.term} home office",
            "hours_old": settings.hours_old,
        }
    else:
        params |= {
            "location": settings.remote_location,
            "is_remote": True,
            "hours_old": settings.hours_old,
        }
    if query.site == "linkedin":
        params["linkedin_fetch_description"] = settings.linkedin_fetch_description
    return params


def to_records(frame: Any, query: Query) -> list[dict[str, Any]]:
    records = []
    for row in frame.to_dict(orient="records"):
        job = {name: clean_value(row.get(name)) for name in FIELDS}
        if not is_relevant_title(job["title"]):
            continue
        job["job_url"] = normalize_url(job["job_url"])
        job["job_url_direct"] = normalize_url(job["job_url_direct"])
        job["search_term"] = query.term
        job["search_mode"] = query.mode
        records.append(job)
    return records


def run(settings: Settings) -> tuple[list[dict[str, Any]], dict[str, SiteStatus]]:
    from jobspy import scrape_jobs  # imported lazily so tests run without network deps

    jobs: list[dict[str, Any]] = []
    status = {site: SiteStatus() for site in settings.sites}
    for query in build_queries(settings):
        st = status[query.site]
        try:
            frame = scrape_jobs(**query_params(query, settings))
        except Exception as exc:  # noqa: BLE001 - any site failure must not stop the run
            st.failed_queries += 1
            message = f"{query.term} ({query.mode}): {type(exc).__name__}: {exc}"[:300]
            st.errors.append(message)
            log.warning("%s failed: %s", query.site, message)
            continue
        st.ok_queries += 1
        st.raw_results += len(frame)
        jobs.extend(to_records(frame, query))
        log.info("%s | %s | %s -> %d raw", query.site, query.mode, query.term, len(frame))
    return jobs, status
