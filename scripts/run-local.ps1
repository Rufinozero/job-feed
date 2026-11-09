<#
.SYNOPSIS
  Plano B: roda a coleta no PC (Agendador de Tarefas) e envia output/vagas.json ao GitHub.
  Use se o GitHub Actions for bloqueado pelo LinkedIn/Glassdoor.
.EXAMPLE
  .\scripts\run-local.ps1
#>
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
git pull --rebase
uv run app
git add output/vagas.json
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "chore(data): update vagas.json (local)"
    git push
}
