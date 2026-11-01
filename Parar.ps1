$ErrorActionPreference = 'Stop'
$stateFile = Join-Path $env:LOCALAPPDATA 'AgentZero\run-state.json'
if (!(Test-Path -LiteralPath $stateFile)) { Write-Output 'Nenhum arranque registado.'; exit 0 }
$state = Get-Content -Raw -LiteralPath $stateFile | ConvertFrom-Json
$project = [IO.Path]::GetFullPath($PSScriptRoot)
if ([IO.Path]::GetFullPath($state.project) -ne $project) { throw 'O registo pertence a outro projeto; nenhum processo foi alterado.' }
$expectedPython = Join-Path $project '.venv\Scripts\python.exe'
foreach ($serviceId in $state.pids) {
    $service = Get-CimInstance Win32_Process -Filter "ProcessId = $([int]$serviceId)"
    if (!$service) { continue }
    if ($service.ExecutablePath -ne $expectedPython -or $service.CommandLine -notmatch '-m (uvicorn core\.main:app|streamlit run web/app\.py)') {
        throw "O processo $serviceId não corresponde ao serviço esperado; foi preservado."
    }
    Stop-Process -Id ([int]$serviceId) -Force
}
Remove-Item -LiteralPath $stateFile
Write-Output 'Serviços locais do Agente Zero parados.'
