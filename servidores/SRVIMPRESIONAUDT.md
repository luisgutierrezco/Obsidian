# Documentación del Servidor de Impresión

## 1. Datos del Servidor

| Campo | Valor |
|---|---|
| **Hostname** | `SERVERPRITNERAUDT` |
| **SO** | Debian 13 (Trixie) — Linux 6.12.73 |
| **IP estática** | `192.168.92.21/24` |
| **Gateway** | `192.168.92.1` |
| **DNS** | `8.8.8.8`, `8.8.4.4` |
| **Interfaz de red** | `enx00e04c360005` |
| **MAC** | `00:e0:4c:36:00:05` |

### Archivo de red (`/etc/network/interfaces`)

```ini
source /etc/network/interfaces.d/*

auto lo
iface lo inet loopback

allow-hotplug enx00e04c360167
iface enx00e04c360167 inet dhcp

auto enx00e04c360005
iface enx00e04c360005 inet static
    address 192.168.92.21/24
    gateway 192.168.92.1
    dns-nameservers 8.8.8.8 8.8.4.4
```

---

## 2. Impresión — CUPS

### Paquetes instalados

- `cups` 2.4.10
- `cups-browsed` 1.28.17
- `cups-filters` 1.28.17
- `ipp-usb` 0.9.23

### Cola de impresión

| Campo | Valor |
|---|---|
| **Nombre de cola** | `AUDITORIA_EPSON` |
| **Impresora** | EPSON L3250 Series |
| **Conexión** | USB (`usb://EPSON/L3250%20Series?serial=5841475A4630303464&interface=1`) |
| **URL IPP** | `http://192.168.92.21:631/printers/AUDITORIA_EPSON` |
| **Puerto** | `631` (abierto a toda la red `0.0.0.0:631`) |
| **Estado** | Activa, aceptando trabajos |

### Configuración destacada de CUPS (`/etc/cups/cupsd.conf`)

- `Port 631` — escucha en todas las interfaces
- `Browsing On` + `BrowseLocalProtocols dnssd` — publicación por DNS-SD
- `WebInterface Yes` — interfaz web habilitada en `http://192.168.92.21:631`
- **Acceso público** a `/printers` (sin autenticación)
- Autenticación requerida solo para `/admin`, `/admin/conf`, `/admin/log`

---

## 3. Escaneo — SANE

### Paquetes instalados

- `sane-utils` 1.3.1
- `libsane1` 1.3.1
- `sane-airscan` 0.99.35
- `epsonscan2` 6.7.87.0 (driver propietario Epson)
- `epsonscan2-non-free-plugin` 1.0.0.6

### Scanner detectado

```
device `epsonscan2:L3250 Series:5841475A4630303464:esci2:usb:ES022C:4490'
  is a EPSON L3250 Series:5841475A4630303464 flatbed scanner
```

**Nota:** Solo el backend `epsonscan2` funciona con este modelo. Los backends estándar `epson`, `epson2` y `epsonds` fallan con "Invalid argument".

### Daemon SANE — `saned`

| Campo | Valor |
|---|---|
| **Puerto** | `6566` (sanepord) |
| **Activación** | Socket systemd (`saned.socket`) |
| **Servicio** | `saned@.service` (socket-activated por conexión) |
| **Usuario** | `saned` (grupos: `saned`, `scanner`) |
| **Estado** | Activo (listening) |

### Control de acceso (`/etc/sane.d/saned.conf`)

```ini
192.168.88.0/24
192.168.89.99
```

Agregar más clientes editando este archivo y reiniciando el socket:

```bash
systemctl restart saned.socket
```

### Configuración de `epsonscan2` (`/etc/sane.d/epsonscan2.conf`)

```ini
[usb]
usb 0x04b8 0x118a
```

---

## 4. eSCL / IPP-USB (Alternativa para escaneo)

`ipp-usb` está **instalado pero inactivo**. Al activarlo, expone el escáner USB como dispositivo de red eSCL (AirScan), permitiendo que Windows lo descubra automáticamente sin SANE.

Para activarlo:

```bash
systemctl start ipp-usb
systemctl enable ipp-usb
```

Una vez activo, el escáner aparecerá en:
- **Windows 11:** Configuración → Bluetooth y dispositivos → Escáneres
- **NAPS2:** Se descubre automáticamente vía eSCL

---

## 5. Paso a paso — Agregar impresora desde Windows 11

### 5.1 Impresión vía IPP (recomendado)

1. Abrir **Configuración → Bluetooth y dispositivos → Impresoras y escáneres**
2. Click en **"Agregar impresora o escáner"**
3. Esperar que termine la búsqueda
4. Click en **"La impresora que quiero no está en la lista"**
5. Seleccionar **"Agregar una impresora mediante una dirección IP o nombre de host"** → Siguiente
6. Tipo de dispositivo: **"Dispositivo IPP"**
7. URL: `http://192.168.92.21:631/printers/AUDITORIA_EPSON`
8. Desmarcar **"Consultar la impresora y seleccionar el controlador automáticamente"**
9. Seleccionar fabricante **EPSON** y modelo **L3250 Series**
   - Si no aparece, descargar el driver desde [epson.com/support](https://epson.com/support)
10. Siguiente → Finalizar

### 5.2 Escaneo vía NAPS2 + SANE

1. Descargar e instalar [NAPS2](https://www.naps2.com/)
2. Abrir NAPS2 → **Perfil → Agregar**
3. Tipo: **SANE**
4. Host: `192.168.92.21`
5. Puerto: `6566`
6. Click en **"Detectar dispositivo"** (o ingresar manualmente):
   ```
   epsonscan2:L3250 Series:5841475A4630303464:esci2:usb:ES022C:4490
   ```
7. Guardar perfil
8. Seleccionar el perfil y escanear

### 5.3 Escaneo vía eSCL (alternativa, sin SANE)

**En el servidor (una vez):**

```bash
systemctl start ipp-usb
systemctl enable ipp-usb
```

**En Windows 11:**

- El escáner aparece automáticamente en **Configuración → Escáneres**
- En **NAPS2**: va a **Escáner → eSCL/WSD** y lo detecta solo

---

## 6. Script PowerShell — Instalación rápida en Windows

```powershell
# Ejecutar en PowerShell como ADMINISTRADOR
$ippUrl  = "http://192.168.92.21:631/printers/AUDITORIA_EPSON"
$nombre  = "AUDITORIA EPSON"
$driver  = "EPSON L3250 Series"

# Crear puerto IPP
if (-not (Get-PrinterPort -Name $ippUrl -ErrorAction SilentlyContinue)) {
    Add-PrinterPort -Name $ippUrl
}

# Agregar impresora
if (-not (Get-Printer -Name $nombre -ErrorAction SilentlyContinue)) {
    Add-Printer -Name $nombre -PortName $ippUrl -DriverName $driver
    Write-Host "Impresora '$nombre' agregada correctamente."
}
else {
    Write-Host "La impresora '$nombre' ya existe."
}
```

---

## 7. Comandos útiles (servidor)

| Acción | Comando |
|---|---|
| Ver colas de impresión | `lpstat -t` |
| Ver escáneres detectados | `scanimage -L` |
| Ver estado CUPS | `systemctl status cups` |
| Ver estado SANE | `systemctl status saned.socket` |
| Reiniciar socket SANE | `systemctl restart saned.socket` |
| Agregar IP a SANE | `echo "IP" >> /etc/sane.d/saned.conf` y reiniciar socket |
| Ver logs de CUPS | `journalctl -u cups -n 50 --no-pager` |
| Ver permisos USB | `ls -la /dev/bus/usb/$(lsusb \| grep -i epson \| awk '{print $2}' \| tr -d :)/$(lsusb \| grep -i epson \| awk '{print $4}' \| tr -d :)` |

---

## 8. Puertos de red

| Puerto | Servicio | Protocolo | Propósito |
|---|---|---|---|
| `631` | CUPS | IPP | Impresión por red |
| `6566` | SANE (saned) | SANE | Escaneo por red |
| `5353` | mDNS/DNS-SD | UDP | Descubrimiento de impresoras |
