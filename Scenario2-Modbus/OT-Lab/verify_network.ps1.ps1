Write-Host "=== NETWORK VERIFICATION SCRIPT ===" -ForegroundColor Green

$tests = @(
    @{Name="Attacker→Suricata"; Cmd="docker exec attacker ping -c 1 -W 1 192.168.20.10 2>&1"},
    @{Name="Suricata→PLC"; Cmd="docker exec suricata ping -c 1 -W 1 192.168.30.2 2>&1"},
    @{Name="PLC→Suricata"; Cmd="docker exec plc ping -c 1 -W 1 192.168.30.10 2>&1"},
    @{Name="Attacker→PLC (routed)"; Cmd="docker exec attacker ping -c 1 -W 1 192.168.30.2 2>&1"}
)

foreach ($test in $tests) {
    Write-Host "$($test.Name): " -NoNewline
    $result = Invoke-Expression $test.Cmd
    if ($result -match "64 bytes|1 received|open") {
        Write-Host "✓ OK" -ForegroundColor Green
    } else {
        Write-Host "✗ FAIL" -ForegroundColor Red
        Write-Host $result -ForegroundColor Gray
    }
}

Write-Host "`nRoute check (Attacker default):" -NoNewline
$route = docker exec attacker ip route | findstr default
if ($route -match "via 192.168.20.10") {
    Write-Host " ✓ Correct (via 20.10)" -ForegroundColor Green
} else {
    Write-Host " ✗ Wrong route: $route" -ForegroundColor Red
}