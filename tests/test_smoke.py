from app.config import Settings
from app.filters import dedupe, is_relevant_title, normalize_url
from app.scraper import Query, build_queries, query_params


def test_relevant_titles() -> None:
    assert is_relevant_title("Analista de Arquitetura")
    assert is_relevant_title("Arquiteta Júnior")
    assert is_relevant_title("Projetista de Arquitetura")
    assert not is_relevant_title("Arquiteto de Software Sênior")
    assert not is_relevant_title("Arquiteto(a) de Soluções de IA")
    assert not is_relevant_title("Arquiteto Vendedor")
    assert not is_relevant_title("Estágio em Arquitetura")
    assert not is_relevant_title(None)


def test_normalize_url_drops_tracking() -> None:
    url = "https://www.linkedin.com/jobs/view/123/?refId=abc&trackingId=x#top"
    assert normalize_url(url) == "https://www.linkedin.com/jobs/view/123"
    assert (
        normalize_url("https://x.gupy.io/jobs/9?utm_source=a&id=1")
        == "https://x.gupy.io/jobs/9?id=1"
    )


def test_dedupe_prefers_direct_url() -> None:
    base = {"company": "X", "title": "Arquiteta", "location": "BH"}
    jobs = [
        {"job_url": "a", "job_url_direct": None, **base},
        {"job_url": "b", "job_url_direct": "https://x.com/1", **base},
    ]
    result = dedupe(jobs)
    assert len(result) == 1
    assert result[0]["job_url_direct"] == "https://x.com/1"


def test_queries_respect_indeed_limit() -> None:
    s = Settings(sites=["indeed", "linkedin"], search_terms=["arquiteta"])
    queries = build_queries(s)
    assert len(queries) == 4
    indeed_remote = query_params(Query("indeed", "arquiteta", "remote"), s)
    assert "is_remote" not in indeed_remote
    assert indeed_remote["search_term"].endswith("home office")
    linkedin_remote = query_params(Query("linkedin", "arquiteta", "remote"), s)
    assert linkedin_remote["is_remote"] is True
    assert "linkedin_fetch_description" in linkedin_remote
