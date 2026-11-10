<#
.SYNOPSIS
  Roda no PC a coleta dos sites que bloqueiam o GitHub Actions (padrão: Glassdoor)
  e envia output/vagas_local.json ao GitHub. Agende no Agendador de Tarefas às 05:10 e 12:40.
.EXAMPLE
  .\scripts\run-local.ps1
  .\scripts\run-local.ps1 -Sites "linkedin,glassdoor,indeed"
#>
param([string]$Sites = "glassdoor")

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
git pull --rebase
$env:SITES = $Sites
$env:OUTPUT_PATH = "output/vagas_local.json"
uv run app
git add output/vagas_local.json
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "chore(data): update vagas_local.json"
    git push
}
