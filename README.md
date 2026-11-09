# job-feed

Coleta vagas públicas do LinkedIn, Glassdoor e Indeed (Brasil) com a biblioteca
[JobSpy](https://github.com/speedyapply/JobSpy) e grava `output/vagas.json`.
A skill **ai-headhunter** lê esse arquivo antes de cada rodada (08:00 e 16:00).

## Como roda
- **GitHub Actions** (`.github/workflows/feed.yml`): 07:30 e 15:30 (horário de Brasília) e
  sob demanda pelo botão *Run workflow*. O resultado é commitado em `output/vagas.json`.
- **Plano B (PC):** se o Actions for bloqueado, agende `scripts\run-local.ps1` no
  Agendador de Tarefas do Windows nos mesmos horários.

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
