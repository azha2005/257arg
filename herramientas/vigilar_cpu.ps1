# Mantiene los procesos de Python en 4 hilos (afinidad 0x0F) y prioridad minima; si LibreHardwareMonitor
# tiene el servidor web en el 8085, anota la temperatura de la CPU (Tctl/Tdie) en vigilar_cpu.log.
# Uso: powershell -File herramientas/vigilar_cpu.ps1 [-Mascara 0x0F] [-Segundos 20]
param([int]$Mascara = 0x0F, [int]$Segundos = 20)
$log = Join-Path $PSScriptRoot "vigilar_cpu.log"
function Temp {
  try {
    $j = Invoke-RestMethod -Uri http://localhost:8085/data.json -TimeoutSec 3
    $t = @(); $stack = @($j)
    while ($stack.Count) { $n = $stack[0]; $stack = $stack[1..($stack.Count)] | Where-Object { $_ }
      if ($n.Text -match 'Tctl|Tdie' -and $n.Value) { $t += $n.Value }
      if ($n.Children) { $stack += $n.Children } }
    return ($t -join ' | ')
  } catch { return 'sin LHM' }
}
while ($true) {
  $n = 0
  foreach ($p in Get-Process python3.11 -ErrorAction SilentlyContinue) {
    try { if ([int64]$p.ProcessorAffinity -ne $Mascara) { $p.ProcessorAffinity = [IntPtr]$Mascara }; $p.PriorityClass = 'Idle'; $n++ } catch {}
  }
  $cpu = [math]::Round((Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples.CookedValue, 1)
  "$(Get-Date -Format 'HH:mm:ss')  python=$n  cpu=$cpu%  temp=$(Temp)" | Out-File $log -Append -Encoding utf8
  Start-Sleep $Segundos
}
