# Muat XML dari monitors.xml
[xml]$xml = Get-Content "$PSScriptRoot\monitors.xml"

# Cari monitor yang bukan primary
$externalMonitor = $xml.monitors_list.item | Where-Object { $_.primary -eq "No" }

# Jika ditemukan, ambil angka dari nama monitor (contoh: \\.\DISPLAY2 → 2)
if ($externalMonitor -ne $null) {
    $monitorNumber = $externalMonitor.name -replace '[^\d]', ''
    Write-Output $monitorNumber
} else {
    Write-Output ""
}
