$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (!(Test-Path -LiteralPath $python)) { throw 'Ambiente Python ausente. Consulte README.md para preparar o projeto.' }
Push-Location -LiteralPath $PSScriptRoot
try {
    & $python -m core.launch
    if ($LASTEXITCODE -ne 0) { throw 'Não foi possível iniciar o Agente Zero. Consulte a mensagem e os logs locais.' }
} finally { Pop-Location }
