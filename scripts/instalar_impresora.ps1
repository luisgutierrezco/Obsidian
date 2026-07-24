$ippUrl = "http://192.168.92.21:631/printers/AUDITORIA_EPSON"
$nombre = "AUDITORIA EPSON"
$driver = "EPSON L3250 Series"

if (-not (Get-PrinterPort -Name $ippUrl -ErrorAction SilentlyContinue)) {
    Add-PrinterPort -Name $ippUrl
}
if (-not (Get-Printer -Name $nombre -ErrorAction SilentlyContinue)) {
    Add-Printer -Name $nombre -PortName $ippUrl -DriverName $driver
    Write-Host "Impresora '$nombre' agregada correctamente."
} else {
    Write-Host "La impresora '$nombre' ya existe."
}
