# job-feed

> Segue os padrões de `C:\VituDev\CLAUDE.md`. Aqui ficam só as particularidades deste projeto.

## Objetivo
Coletar vagas públicas do LinkedIn, Glassdoor e Indeed (Brasil) via JobSpy e gravar `output/vagas.json`, que a skill ai-headhunter (Claude) lê antes de cada rodada.

## Comandos
- Instalar/atualizar dependências: `uv sync`
- Rodar: `uv run app`
- Testes: `uv run pytest`
- Lint/format: `uv run ruff check . --fix && uv run ruff format .`

## Estrutura
- `src/app/main.py` — ponto de entrada
- `src/app/config.py` — configuração via `.env`
- `src/app/scraper.py` — consultas por site/termo, falha isolada por consulta
- `src/app/filters.py` — filtro de título, normalização de URL, deduplicação
- `.github/workflows/feed.yml` — agendamento 07:30 e 15:30 (BRT)
- `scripts/run-local.ps1` — plano B no PC
- `tests/` — testes

## Integrações e segredos
- JobSpy (sem login, sem chaves). Nenhum segredo necessário.

## Decisões e restrições
- Só busca pública, nunca login em conta pessoal.
- Filtros de perfil (CLT, senioridade, região) ficam na skill; aqui só ruído óbvio de título.
- Indeed: só um de hours_old / is_remote por consulta, por isso a busca remota usa o termo "home office".
- Se o Actions for bloqueado, usar o plano B (`scripts/run-local.ps1`).
