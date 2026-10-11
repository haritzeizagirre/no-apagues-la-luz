# Diagnóstico de red y cortafuegos para el servidor del juego
Write-Output "=== Adaptadores e IPs ==="
Get-NetIPConfiguration | Where-Object { $null -ne $_.IPv4Address } | ForEach-Object {
    Write-Output ($_.InterfaceAlias + " | " + $_.IPv4Address.IPAddress + " | " + $_.NetProfile.Name + " (" + $_.NetProfile.NetworkCategory + ")")
}
Write-Output ""
Write-Output "=== Reglas de cortafuegos que mencionan python/8000 ==="
$rules = Get-NetFirewallRule -Enabled True -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -match "python|NAPL|8000" }
foreach ($r in $rules) {
    $app = ($r | Get-NetFirewallApplicationFilter -ErrorAction SilentlyContinue).Program
    $port = ($r | Get-NetFirewallPortFilter -ErrorAction SilentlyContinue).LocalPort
    Write-Output ($r.DisplayName + " | " + $r.Direction + " | " + $r.Action + " | prof:" + $r.Profile + " | app:" + $app + " | puerto:" + $port)
}
Write-Output "(fin reglas)"
