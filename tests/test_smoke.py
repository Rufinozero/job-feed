from app.config import Settings
from app.filters import dedupe, is_relevant_title, normalize_url
from app.scraper import Query, build_queries, is_rate_limited, query_params


def test_relevant_titles() -> None:
    assert is_relevant_title("Analista de Arquitetura")
    assert is_relevant_title("Arquiteta Júnior")
    assert is_relevant_title("Projetista de Arquitetura")
    assert not is_relevant_title("Arquiteto de Software Sênior")
    assert not is_relevant_title("Arquiteto(a) de Soluções de IA")
    assert not is_relevant_title("Arquiteto Vendedor")
    assert not is_relevant_title("Estágio em Arquitetura")
    assert not is_relevant_title("Projetista Mecânico Júnior")
    assert not is_relevant_title("Projetista de Instalações Elétricas Pleno")
    assert not is_relevant_title("Arquiteto SAP")
    assert not is_relevant_title("Arquiteto de Negócios | Mineração")
    assert is_relevant_title("Desenhista Projetista")
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


def test_rate_limit_detection() -> None:
    assert is_rate_limited(["response status code 429 (blocked: use a proxy)"])
    assert not is_rate_limited(["response status code 403 (blocked: use a proxy)"])


def test_classify_links() -> None:
    from app.validate import classify

    url = "https://x.gupy.io/jobs/123"
    assert classify(200, url, "<h1>Arquiteta</h1>", url) == "Validada"
    assert classify(200, url, "Esta vaga não está mais disponível", url) == "Encerrada"
    assert classify(404, url, "", url) == "Encerrada"
    assert classify(403, url, "", url) == "Não validada"
    assert classify(200, "https://x.gupy.io", "home", url) == "Não validada"


def test_translation_bundle_is_not_a_closure() -> None:
    from app.validate import classify

    url = "https://x.gupy.io/job/abc"
    body = '{"closedapplications":"inscrições encerradas","apply":"candidatar"} <h1>Arquiteta</h1>'
    assert classify(200, url, body, url) == "Validada"


def test_status_field_closed() -> None:
    from app.validate import classify

    url = "https://x.gupy.io/job/abc"
    assert classify(200, url, '{"status":"closed"}', url) == "Encerrada"
    assert classify(200, url, '{"status":"published"}', url) == "Validada"
