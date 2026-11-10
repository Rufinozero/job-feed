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
- `src/app/validate.py` — abre cada link no runner e marca Validada / Encerrada / Não validada
- `.github/workflows/feed.yml` — agendamento 05:10 e 12:40 (BRT); skill roda 08:41 e 17:41
- `scripts/run-local.ps1` — plano B no PC
- `tests/` — testes

## Integrações e segredos
- JobSpy (sem login, sem chaves). Nenhum segredo necessário.

## Decisões e restrições
- Só busca pública, nunca login em conta pessoal.
- Filtros de perfil (CLT, senioridade, região) ficam na skill; aqui só ruído óbvio de título.
- Indeed: só um de hours_old / is_remote por consulta, por isso a busca remota usa o termo "home office".
- Glassdoor devolve HTTP 403 no GitHub Actions; roda no PC via `scripts/run-local.ps1`
  (saída `output/vagas_local.json`). A skill lê os dois arquivos.
- JobSpy às vezes só loga o erro (não lança exceção); `_ErrorCollector` captura isso no status.
- A validação dos links é feita aqui (runner tem internet livre); a skill não consegue abrir URLs vindas de arquivo.
- LinkedIn: pausa de 12 s + 0–6 s aleatórios entre consultas; em HTTP 429, novas tentativas após 90 s e 180 s.
