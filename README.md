# job-feed

Coleta vagas públicas do LinkedIn, Glassdoor e Indeed (Brasil) com a biblioteca
[JobSpy](https://github.com/speedyapply/JobSpy) e grava `output/vagas.json`.
A skill **ai-headhunter** lê esse arquivo antes de cada rodada (08:00 e 16:00).

## Como roda
- **GitHub Actions** (`.github/workflows/feed.yml`): LinkedIn e Indeed, 05:10 e 12:40 (horário
  de Brasília) e sob demanda pelo botão *Run workflow*. Grava `output/vagas.json`.
- **PC (`scripts\run-local.ps1`):** Glassdoor, que bloqueia o GitHub (HTTP 403). Agende no
  Agendador de Tarefas do Windows às 05:10 e 12:40. Grava `output/vagas_local.json`.

## Setup local
```powershell
uv sync
copy .env.example .env   # opcional; os padrões já funcionam
uv run app
```

## Testes
```powershell
uv run ruff check . && uv run pytest
```

## Saída (`output/vagas.json`)
- `sites`: status por site (consultas ok/falhas, resultados brutos, erros).
- `jobs`: vagas já filtradas por título (exclui arquitetura de TI, vendas e estágio) e sem
  repetições. Campos: `site, title, company, location, is_remote, job_type, job_level,
  date_posted, job_url, job_url_direct, min_amount, max_amount, currency, interval, emails,
  description, search_term, search_mode`.

Regras de perfil (CLT, nível, região) ficam na skill, não aqui.
