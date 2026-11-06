$ErrorActionPreference = 'Stop'
try {
    [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
    if (-not [Console]::IsOutputRedirected) {
        $Host.UI.RawUI.WindowTitle = 'Atlas electorales'
        $Host.UI.RawUI.BackgroundColor = 'Black'
        $Host.UI.RawUI.ForegroundColor = 'Gray'
        [Console]::ResetColor()
    }
    $node = Get-Command node -ErrorAction Stop
    & $node.Source (Join-Path $PSScriptRoot 'atlas.mjs') @args
    if ($LASTEXITCODE -ne 0) { Read-Host 'El visor termino con un error. Enter para cerrar' }
    exit $LASTEXITCODE
} catch {
    Write-Host $_.Exception.Message
    Read-Host 'Enter para cerrar'
    exit 1
}
