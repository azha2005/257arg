$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$atlasAddress = 'http://127.0.0.1:8793/mapas/mapa2003escenarios/index.html'
try {
    $response = Invoke-WebRequest -Uri $atlasAddress -UseBasicParsing -TimeoutSec 2
    $ready = $response.StatusCode -eq 200 -and $response.Content.Contains('Atlas de escenarios 2003')
} catch { $ready = $false }
if (-not $ready) {
    $pythonPath = (Get-Command python).Source
    $serverArguments = @('-m','http.server','8793','--bind','127.0.0.1','--directory',('"' + $projectRoot + '"'))
    Start-Process -FilePath $pythonPath -ArgumentList $serverArguments -WindowStyle Hidden -RedirectStandardOutput (Join-Path $PSScriptRoot 'servidor.out.log') -RedirectStandardError (Join-Path $PSScriptRoot 'servidor.err.log')
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        try {
            $response = Invoke-WebRequest -Uri $atlasAddress -UseBasicParsing -TimeoutSec 1
            if ($response.StatusCode -eq 200 -and $response.Content.Contains('Atlas de escenarios 2003')) { $ready = $true; break }
        } catch { Start-Sleep -Milliseconds 200 }
    }
}
if (-not $ready) { throw 'No se pudo iniciar el servidor local de los atlas en el puerto 8793.' }
Start-Process $atlasAddress
