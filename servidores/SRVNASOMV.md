---
tags:
  - Servidores
  - Red
  - Backup
  - Administracion
area: Infraestructura
---

# Documentación del Servidor NAS-OMV

## 1. Datos Generales

| Campo | Valor |
|---|---|
| **Hostname** | `NAS-OMV` |
| **SO** | Debian 12 (Bookworm) |
| **OMV** | OpenMediaVault 7.7.5 |
| **Tipo de máquina** | Máquina Virtual (VirtualBox) — discos VBOX HARDDISK |
| **IP** | `192.168.90.63/24` |
| **Gateway** | `192.168.90.1` |
| **DNS** | `127.0.0.53` (systemd-resolved → resuelve a 8.8.8.8, 8.8.4.4) |
| **Interfaz de red** | `enp0s3` |
| **Zona horaria** | `America/Caracas` |
| **Host** | Servidor NAS en VirtualBox con OpenMediaVault |

---

## 2. Especificaciones técnicas

### 2.1 Hardware virtual

| Componente | Detalle |
|---|---|
| **CPU** | 1 núcleo (VM) |
| **RAM** | ~1 GB |
| **Disco OS** | `/dev/sdb` — 8 GB VBOX HARDDISK |
| **Disco datos** | `/dev/sda` — 128 GB VBOX HARDDISK |
| **Swap** | 975 MB en `/dev/sdb5` |

### 2.2 Particiones

```
Disco OS (/dev/sdb - 8 GB):
  /dev/sdb1  7 GB  ext4   /          (raíz del sistema)
  /dev/sdb5  975M  swap   [SWAP]

Disco datos (/dev/sda - 128 GB):
  /dev/sda1  128 GB  ext4   /srv/dev-disk-by-uuid-dd6d6b33-dcd2-4919-bddd-a3cdebd2473e
```

### 2.3 Uso de disco

| Montura | Tamaño | Usado | Disponible | Uso |
|---|---|---|---|---|
| `/` | 6.9 GB | 4.8 GB | 1.7 GB | **75%** ⚠️ |
| `/srv/dev-disk-by-uuid-...` | 126 GB | 25 GB | 101 GB | 20% |

### 2.4 Sistema de archivos

```
UUID=eb20c13f-1a06-46cf-b6e7-d72386d2a100 /       ext4  errors=remount-ro  0 1
UUID=065a5f7f-294a-402d-b09f-3e78b7cdf8ca none    swap  sw                  0 0
/dev/disk/by-uuid/dd6d6b33-dcd2-4919-bddd-a3cdebd2473e  /srv/dev-disk-by-uuid-dd6d6b33-dcd2-4919-bddd-a3cdebd2473e  ext4  defaults,nofail,user_xattr,usrquota,grpquota,acl  0 2
```

---

## 3. Red

### 3.1 Configuración de red

| Campo | Valor |
|---|---|
| **Interfaz** | `enp0s3` |
| **Método** | **DHCP** (no estática) |
| **IP** | `192.168.90.63/24` |
| **Gateway** | `192.168.90.1` |
| **DNS** | systemd-resolved (`127.0.0.53`) |
| **MTU** | 1500 |

### 3.2 Puertos abiertos

| Puerto | Servicio | Propósito | Dirección |
|---|---|---|---|
| **22** | SSH | Acceso remoto | `0.0.0.0:22` |
| **21** | ProFTPD | FTP | `*:21` |
| **80** | nginx | Web UI de OMV | `0.0.0.0:80` |
| **139** | Samba (smbd) | NetBIOS/SMB | `0.0.0.0:139` |
| **445** | Samba (smbd) | SMB/CIFS | `0.0.0.0:445` |
| **5353** | avahi-daemon | mDNS (descubrimiento) | `0.0.0.0:5353` (UDP) |
| **3702** | python3 | WSD (Web Services Discovery) | `192.168.90.63:3702` (UDP) |

### 3.3 Red multi-VLAN

El NAS recibe conexiones desde múltiples VLANs:
- `192.168.89.x` — VLAN de Auditoría / Laptop (ej: `192.168.89.99`)
- `192.168.90.x` — VLAN local del NAS (misma subred)
- `192.168.92.x` — VLAN del Servidor de Impresión (`192.168.92.21`)
- `192.168.88.x` — Otra VLAN (configurada en SANE)

---

## 4. Servicios

### 4.1 Web UI — OpenMediaVault (nginx)

- **URL:** `http://192.168.90.63`
- **Puerto:** 80
- **SSL/TLS:** ❌ No configurado
- **Root:** `/var/www/openmediavault`
- **PHP:** 8.2 (PHP-FPM)
- **Tamaño máximo de subida:** 25 MB
- **Config:** `/etc/nginx/sites-available/openmediavault-webgui`

### 4.2 SMB/CIFS (Samba)

- **Servicio:** `smbd`
- **Puertos:** 139 (NetBIOS), 445 (SMB directo)
- **NetBIOS:** Deshabilitado (`disable netbios = Yes`)
- **mDNS:** Deshabilitado (`multicast dns register = No`)
- **WINS:** Habilitado (`wins support = Yes`)
- **Log:** `/var/log/samba/log.%m`
- **Config:** `/etc/samba/smb.conf` (generado por OMV)

#### 4.2.1 Configuración global de SMB

```ini
[global]
disable netbios = Yes
disable spoolss = Yes
dns proxy = No
load printers = No
wins support = Yes
fruit:nfs_aces = no
fruit:copyfile = yes
fruit:aapl = yes
idmap config * : backend = tdb
create mask = 0777
directory mask = 0777
use sendfile = Yes
```

### 4.3 FTP (ProFTPD)

- **Servicio:** `proftpd`
- **Puerto:** 21
- **Tipo:** Standalone
- **Autenticación:** PAM (usuarios del sistema Linux/OMV)
- **SSL/TLS:** ❌ No configurado
- **Root virtual:** Los usuarios ven su home como raíz
- **Límites:** Max 5 clientes simultáneos, Max 5 intentos de login
- **Timeout:** 1200s idle, 600s no transferencia
- **Config:** `/etc/proftpd/proftpd.conf`

#### Configuración especial FTP — VRoot

ProFTPD usa `mod_vroot` para mapear rutas virtuales:

```
VRootAlias "/srv/dev-disk-by-uuid-dd6d6b33-dcd2-4919-bddd-a3cdebd2473e/DEPARTAMENTO_DE_AUDITORIA/" "/DEPARTAMENTO_DE_AUDITORIA"
```

Esto permite que los usuarios autorizados accedan vía FTP a `192.168.90.63/DEPARTAMENTO_DE_AUDITORIA/`.

**Restricciones de directorio FTP:**

```conf
<Directory /DEPARTAMENTO_DE_AUDITORIA>
  Umask 000 000
  <Limit ALL>
    AllowUser OR Admin, AUDT_1
    DenyAll
  </Limit>
  <Limit READ DIRS>
    AllowUser OR Admin, AUDT_1
    DenyAll
  </Limit>
</Directory>
```

Solo los usuarios `Admin` y `AUDT_1` pueden acceder por FTP al directorio de auditoría.

### 4.4 SSH

- **Puerto:** 22
- **Autenticación:** Password (por defecto en OMV)
- **Usuarios del sistema pueden acceder**

---

## 5. Usuarios del sistema

### 5.1 Usuarios OMV/Samba

| Usuario | UID | Grupo primario | Descripción |
|---|---|---|---|
| `Admin` | 1001 | users | Administrador del NAS |
| `AUDT_1` | 1013 | users | Auditoría principal |
| `AUDT_MAYOR` | 1015 | users | Auditoría al mayor |
| `ALMACEN` | 1020 | users | Almacén |
| `RRHH` | 1019 | users | Recursos Humanos |
| `DELIVERY` | 1014 | users | Delivery/Entregas |
| `SAMBILCANDELARIA` | 1016 | users | Tienda Sambil Candelaria |
| `VIPENVIOS` | 1017 | users | Envíos VIP |
| `B407` | 1012 | users | Bodega 407 |
| `L111` | 1008 | users | Local 111 |
| `L160` | 1009 | users | Local 160 |
| `L210` | 1007 | users | Local 210 |
| `L227` | 1000 | users | Local 227 |
| `L229` | 1002 | users | Local 229 |
| `L230` | 1003 | users | Local 230 |
| `L231` | 1004 | users | Local 231 |
| `L246` | 1006 | users | Local 246 |
| `L250` | 1005 | users | Local 250 |
| `L251` | 1018 | users | Local 251 |
| `L337` | 1010 | users | Local 337 |
| `L429` | 1011 | users | Local 429 |

Todos los usuarios pertenecen al grupo `users` (GID 100).

### 5.2 Convención de nombres

| Prefijo | Significado | Ejemplos |
|---|---|---|
| **L + número** | Local / Tienda física | L111, L227, L246 |
| **B + número** | Bodega | B407 |
| **AB + número** | Almacén | AB06, AB71, AB77 |
| **AUDT\_** | Auditoría | AUDT_1, AUDT_MAYOR |
| **VIP\_** | Envíos/Personal VIP | VIPENVIOS |

### 5.3 Grupos

| Grupo | Miembros | Propósito |
|---|---|---|
| **TIENDASCITYMARKET** (GID 1000) | L229, L230, L231, L250, L246, L210, L111, L160, L337, L429, B407, L227, DELIVERY, L251 | Agrupa todos los locales para acceso a carpetas compartidas como LISTAS y PERSONAL_VIP |
| **users** (GID 100) | Todos los usuarios OMV | Grupo primario de todos los usuarios |

---

## 6. Estructura de carpetas compartidas

### 6.1 Árbol completo

```
/srv/dev-disk-by-uuid-dd6d6b33-dcd2-4919-bddd-a3cdebd2473e/
│
├── 📁 L227/               → Carpeta privada Local 227
├── 📁 L229/               → Carpeta privada Local 229
├── 📁 L230/               → Carpeta privada Local 230
├── 📁 L231/               → Carpeta privada Local 231
├── 📁 L250/               → Carpeta privada Local 250
├── 📁 L246/               → Carpeta privada Local 246
├── 📁 L210/               → Carpeta privada Local 210
├── 📁 L111/               → Carpeta privada Local 111
├── 📁 L160/               → Carpeta privada Local 160
├── 📁 L337/               → Carpeta privada Local 337
├── 📁 L429/               → Carpeta privada Local 429
├── 📁 L251/               → Carpeta privada Local 251
│
├── 📁 B407/               → Carpeta privada Bodega 407
├── 📁 AB06/               → Carpeta privada Almacén 06
├── 📁 AB71/               → Carpeta privada Almacén 71
├── 📁 AB77/               → Carpeta privada Almacén 77
│
├── 📁 MARCAS227/          → Marcas/Productos Local 227
├── 📁 MARCAS229/          → Marcas/Productos Local 229
├── 📁 MARCAS230/          → Marcas/Productos Local 230
├── 📁 MARCAS231/          → Marcas/Productos Local 231
├── 📁 MARCAS250/          → Marcas/Productos Local 250
├── 📁 MARCAS246/          → Marcas/Productos Local 246
├── 📁 MARCAS210/          → Marcas/Productos Local 210
├── 📁 MARCAS111/          → Marcas/Productos Local 111
├── 📁 MARCAS160/          → Marcas/Productos Local 160
├── 📁 MARCAS337/          → Marcas/Productos Local 337
├── 📁 MARCAS251/          → Marcas/Productos Local 251
├── 📁 MARCASB407/         → Marcas/Productos Bodega 407
├── 📁 MARCASAB06/         → Marcas/Productos Almacén 06
├── 📁 MARCASAB71/         → Marcas/Productos Almacén 71
├── 📁 MARCASAB77/         → Marcas/Productos Almacén 77 (apunta a MARCAS/)
│
├── 📁 DEPARTAMENTO_DE_AUDITORIA/   → Auditoría (23 GB)
├── 📁 AUDT_MAYOR/                  → Ventas al mayor (128 MB)
├── 📁 RRHH/                        → Recursos Humanos (2.6 GB)
├── 📁 DELIVERY/                    → Delivery/Entregas
├── 📁 LISTAS/                      → Documentos compartidos (776 KB)
├── 📁 PERSONAL_VIP/               → Datos personal VIP
├── 📁 Reports/                     → Reportes Crystal Reports
├── 📁 STORAGE/                     → Almacenamiento general
├── 📁 ENVIOS_VIP/                 → Envíos VIP
├── 📁 MARCAS/                     → Marcas generales (SAMBILCANDELARIA)
├── 📁 MARCAS L210/                → (con espacio, posible error de nombre)
├── 📁 MASCAS229/                  → (posible typo de MARCAS229)
├── 📁 RESPALDO_ACCESORIOS/        → Respaldo accesorios
├── 📁 ftp/                        → Raíz FTP
│
└── 📁 lost+found/                 → Sistema de archivos ext4
```

### 6.2 Carpetas privadas por tienda/local

Cada local (Lxxx) tiene **2 carpetas**:

| Carpeta | Acceso | Permisos |
|---|---|---|
| `Lxxx/` | Dueño del local + Admin + AUDT_1 | Lectura/Escritura |
| `MARCASxxx/` | Dueño del local + Admin + AUDT_1 + RRHH | Lectura/Escritura |

Ejemplo para Local 227:
```
L227/      → Accede: L227(7), Admin(7), AUDT_1(7)
MARCAS227/ → Accede: L227(7), Admin(7), AUDT_1(7), RRHH(7)
```

### 6.3 Carpetas compartidas

| Carpeta | Quién accede | Permisos |
|---|---|---|
| **LISTAS** | Todos los locales (lectura) + Admin, AUDT_1, L251 (escritura) | Documentos compartidos: amonestaciones, cierres de caja, solicitudes |
| **PERSONAL_VIP** | Todos los locales (lectura) + Admin, AUDT_1, AUDT_MAYOR (escritura) | Listado general de personal |
| **DEPARTAMENTO_DE_AUDITORIA** | Admin, AUDT_1 | Auditoría completa (~23 GB) |
| **AUDT_MAYOR** | Admin, AUDT_1, AUDT_MAYOR | Ventas al mayor y envíos Zoom |
| **RRHH** | Admin, AUDT_1, RRHH | Facturación mensual y cortes semanales |
| **DELIVERY** | Admin, AUDT_1, DELIVERY | Entregas (vacía actualmente) |
| **Reports** | Admin (escritura), AUDT_1, DELIVERY, ALMACEN (lectura) | Reportes Crystal Reports |
| **STORAGE** | Admin + grupo TIENDASCITYMARKET | Almacenamiento general |
| **ENVIOS_VIP** | — | Envíos VIP (vacía) |

### 6.4 Estructura interna de DEPARTAMENTO_DE_AUDITORIA

La carpeta más grande (23 GB) con la siguiente organización:

```
DEPARTAMENTO_DE_AUDITORIA/
├── 👤 1-FRANCHESCA GARCIA/     → Trabajos asignados
├── 👤 2-DANIEL GONZALEZ/        → Trabajos asignados
├── 👤 3-LUIS GUTIERREZ/         → Trabajos asignados
├── 👤 4-HAIDY/                  → Trabajos asignados
├── 📁 2024/                     → Documentos año 2024
├── 📁 2025/                     → Documentos año 2025
├── 📁 2026/                     → Documentos año 2026
│   ├── ARQUEO/
│   ├── AUTORIZACIONES/
│   ├── CIERRE CASHEA/
│   ├── CIERRE SAMBIL/
│   ├── CUENTAS POR COBRAR/
│   ├── INCENTIVOS/
│   ├── INGRESO Y EGRESO/
│   ├── PAPELERIA/
│   ├── RELACION CIERRE Y APERTURA (2025)/
│   ├── RELACION DE PUNTOS/
│   └── TRANSACCIONES 2026/
├── 📁 ADMINISTRACION/
├── 📁 ARQUEOS/
├── 📁 CANDELARIA/
├── 📁 CONTROL DE MATERIAL POP TECNO/
├── 📁 FACTURAS/
├── 📁 FORMATOS/
├── 📁 LISTADO PERSONAL ADMINISTRATIVO/
├── 📁 LOGOS/
├── 📁 ORGANIZADORES/
├── 📁 REUNION DE CAJEROS/
├── 📁 SISTEMA/
│   ├── ChrystalUltraPlus2022/
│   ├── Reports/
│   └── Accesos directos (.lnk) a cada local
├── 📁 TIENDAS/
│   └── Formularios por tienda (apertura/cierre, equipos, papelería)
└── 📁 ZOOM/
```

### 6.5 Estructura interna de RRHH

```
RRHH/
├── 📁 CORTES SEMANALES/
├── 📁 FACTURA JUNIO/          → 130 archivos
├── 📁 FACTURA MARZO/
├── 📁 FACTURAS ABRIL/         → 138 archivos
├── 📁 FACTURAS ENERO/
├── 📁 FACTURAS FEBRERO/
├── 📁 FACTURAS MAYO/          → 137 archivos
├── 📁 FACTURAS SAMSUNG DICIEMBRE/
├── 📁 PRODUCTOS/
└── 📄 VENTAS MARCA rrhhr [MES].xlsm
```

### 6.6 Carpetas con papelera de reciclaje SMB

Las siguientes carpetas tienen `vfs objects = recycle` (papelera de reciclaje al eliminar archivos vía SMB):
- `L429/`
- `DEPARTAMENTO_DE_AUDITORIA/`
- `Reports/`

La papelera se guarda en `.recycle/[usuario]/` dentro de cada carpeta.

---

## 7. Permisos SMB por carpeta (detalle)

### 7.1 Carpetas privadas de tiendas (ejemplo: L227)

```ini
[L227]
valid users = L227 Admin AUDT_1
write list = L227 Admin AUDT_1
invalid users = L246 VIPENVIOS
path = /srv/.../L227/
```

### 7.2 Carpetas de Marcas (ejemplo: MARCAS227)

```ini
[MARCAS227]
valid users = L227 Admin AUDT_1 RRHH
write list = L227 Admin AUDT_1 RRHH
invalid users = L229 L230 L231 L250 L246 L210 L111 L160 L337 L429 B407 DELIVERY AUDT_MAYOR L251
```

### 7.3 Carpetas de Almacén (ejemplo: AB06)

```ini
[AB06]
valid users = Admin AUDT_1 SAMBILCANDELARIA
write list = Admin AUDT_1 SAMBILCANDELARIA
invalid users = L227 L229 L230 L231 L250 L246 L210 L111 L160 L337 L429 B407 AUDT_MAYOR VIPENVIOS @TIENDASCITYMARKET
```

### 7.4 LISTAS (carpeta colaborativa)

```ini
[LISTAS]
valid users = L227 Admin L229 L230 L231 L250 L246 L210 L111 L160 L337 L429 B407 AUDT_1 DELIVERY SAMBILCANDELARIA L251 @TIENDASCITYMARKET
write list = Admin AUDT_1 L251
read list = L227 L229 L230 L231 L250 L246 L210 L111 L160 L337 L429 B407 DELIVERY SAMBILCANDELARIA @TIENDASCITYMARKET
invalid users = AUDT_MAYOR VIPENVIOS
```

---

## 8. Cuadro resumen de permisos

| Carpeta | Admin | AUDT_1 | AUDT_M | RRHH | Local dueño | Otros locales | DELIVERY | SAMBIL | VIPENV | ALMACEN |
|---|---|---|---|---|---|---|---|---|---|---|
| **Lxxx/** | RW | RW | — | — | RW | — | — | — | — | — |
| **MARCASxxx/** | RW | RW | — | RW | RW | — | — | — | — | — |
| **LISTAS** | RW | RW | — | — | RW* | R | R | R | — | — |
| **PERSONAL_VIP** | RW | RW | RW | — | R | R | R | R | — | — |
| **DEPTO_AUDITORIA** | RW | RW | — | — | — | — | — | — | — | — |
| **AUDT_MAYOR** | RW | RW | RW | — | — | — | — | — | — | — |
| **RRHH** | RW | RW | — | RW | — | — | — | — | — | — |
| **DELIVERY** | RW | RW | — | — | — | — | RW | — | — | — |
| **Reports** | RW | R | — | — | — | — | R | — | — | R |
| **ABxx/** | RW | RW | — | — | — | — | — | RW | — | — |
| **STORAGE** | RW | — | — | — | RW* | — | — | — | — | — |

> *L251 tiene permisos de escritura en LISTAS*
> *L227 tiene permisos de escritura en STORAGE*
> *RW = Lectura+Escritura, R = Solo lectura, — = Sin acceso*

---

## 9. Plugins OMV instalados

| Plugin | Versión | Estado | Descripción |
|---|---|---|---|
| `openmediavault-ftp` | 7.0.1-1 | Activo | Servidor FTP (ProFTPD) |
| `openmediavault-usbbackup` | 7.1.2-1 | Instalado | Backup automático a USB |

No hay configuraciones de backup USB visibles (no hay archivos en `/etc/openmediavault/usbbackup.d/`).

### Plugins disponibles que NO están instalados

| Plugin | Posible utilidad |
|---|---|
| `openmediavault-remotemount` | Montar carpetas remotas (NFS, SMB) |
| `openmediavault-rsync` | Copias de seguridad programadas |
| `openmediavault-snapraid` | Protección contra errores de disco |
| `openmediavault-backup` | Backup de la configuración OMV |
| `openmediavault-diskstats` | Estadísticas de disco |
| `openmediavault-luksencryption` | Cifrado de discos |
| `openmediavault-tftp` | Servidor TFTP |
| `openmediavault-wireguard` | VPN |

---

## 10. Configuraciones adicionales del sistema

### 10.1 Actualizaciones automáticas

Activadas (`unattendedupgrade = 1`) — el sistema instala actualizaciones de seguridad automáticamente.

### 10.2 Monitoreo de rendimiento

Activado (`perfstats: enable = 1`) — OMV recolecta estadísticas de rendimiento.

### 10.3 Administración de energía

| Opción | Valor |
|---|---|
| CPU Frequency Scaling | Activado |
| Botón de encendido | No hace nada |
| Modo de suspensión | Apagado |

### 10.4 Notificaciones

Solo está activada la notificación de eventos de procesos (`monitprocevents`).  
El correo electrónico **no está configurado** (`email: enable = 0`), por lo que las notificaciones no se envían externamente.

---

## 11. Acceso desde la red

### 11.1 Cómo acceder al NAS

| Método | Dirección | Credenciales |
|---|---|---|
| **Web UI** | `http://192.168.90.63` | Usuarios OMV |
| **SMB** | `\\192.168.90.63\carpeta` o `\\NAS-OMV\carpeta` | Usuarios OMV |
| **FTP** | `ftp://192.168.90.63` | Usuarios OMV (solo Admin y AUDT_1) |
| **SSH** | `ssh root@192.168.90.63` | Password root |

### 11.2 Conexiones activas típicas

El NAS recibe conexiones desde:
- `192.168.89.x` — VLAN de auditoría
- `192.168.90.x` — VLAN local
- `192.168.92.x` — VLAN del servidor de impresión
- `192.168.88.x` — Otra VLAN

---

## 12. Observaciones y recomendaciones

### ⚠️ Problemas identificados

| # | Problema | Riesgo | Solución recomendada |
|---|---|---|---|
| 1 | **IP por DHCP** | Si el NAS se reinicia, la IP puede cambiar y perderías acceso desde otras VLANs | Configurar **IP estática** en OMV → Red → Interfaz |
| 2 | **Disco OS casi lleno** (75%) | Podría causar problemas de rendimiento o impedir actualizaciones | Revisar `/var/log/` y `/tmp/`, o ampliar disco en VirtualBox |
| 3 | **Sin SSL/TLS** en Web UI ni FTP | Las contraseñas viajan en texto plano por la red | Configurar HTTPS (Let's Encrypt o certificado autofirmado) |
| 4 | **Sin backup** configurado | No hay copias de seguridad de los 25 GB de datos críticos | Configurar `openmediavault-rsync` o backup USB |
| 5 | **Sin notificaciones por correo** | No hay alertas si algo falla | Configurar servidor SMTP en OMV |
| 6 | **20 usuarios OMV activos** | Muchas cuentas humanas que rotan, difícil de mantener | Revisar periódicamente cuentas inactivas |
| 7 | **FTP sin cifrar** | Contraseñas visibles en la red | Usar SFTP (SSH) en lugar de FTP, o configurar FTPS |

### ✅ Buenas prácticas activas

- Actualizaciones automáticas de seguridad habilitadas
- Monitoreo de rendimiento activo
- Papelera de reciclaje SMB en carpetas críticas (auditoría, reports, L429)
- Usuarios con permisos granulares (mínimo privilegio)

---

## 13. Comandos útiles (servidor)

| Acción | Comando |
|---|---|
| Ver estado de OMV | `omv-release` |
| Ver uso de disco | `df -h` |
| Ver SMB sessions activas | `smbstatus` |
| Ver servicios activos | `systemctl list-units --type=service --state=running` |
| Configurar OMV (consola) | `omv-firstaid` |
| Ver configuración OMV | `omv-confdbadm read "conf.system..."` |
| Monitorear logs SMB | `tail -f /var/log/samba/log.*` |
| Monitorear logs FTP | `tail -f /var/log/proftpd/proftpd.log` |
| Ver puertos en escucha | `ss -tlnp` |
| Ver discos | `lsblk` |
| Ver SMART del disco | `smartctl -a /dev/sda` |

---

## 14. Backup automático a Google Drive

### 14.1 Configuración

| Campo | Valor |
|---|---|
| **Herramienta** | `rclone` v1.60.1 |
| **Destino** | Google Drive — carpeta `Backup_NAS/` |
| **Frecuencia** | Diario a las 3:00 AM |
| **Formato** | `tar.gz` (comprimido) |
| **Ubicación temporal** | `/srv/dev-disk-by-uuid-.../backups/` |
| **Script** | `/usr/local/bin/backup-nas.sh` |

### 14.2 Flujo del backup

```
1. tar czf → comprime /srv/.../ en /srv/.../backups/backup-nas-YYYYMMDD_HHMM.tar.gz
   (excluye la propia carpeta backups/)
2. gzip -t  → verifica que el comprimido NO está corrupto
3. stat     → obtiene tamaño local
4. rclone copy → sube a Google Drive
5. rclone size → verifica que el archivo en cloud tiene el MISMO tamaño
6. rm -f    → elimina el comprimido local
7. rclone delete → elimina backups anteriores en Google Drive (solo mantiene 1)
```

### 14.3 Verificaciones de seguridad

- ❌ Si la **compresión falla** → aborta, no sube nada
- ❌ Si el archivo **está corrupto** → aborta, lo borra local, no sube
- ❌ Si la **subida falla** → aborta, no borra nada (el backup queda local)
- ❌ Si el **tamaño en cloud no coincide** → aborta, no borra el anterior

### 14.4 Logs

Los logs del backup se guardan en:
```
/srv/dev-disk-by-uuid-.../backups/backup.log
```

### 14.5 Espacio estimado

| Recurso | Tamaño |
|---|---|
| Backup comprimido | ~18-20 GB |
| Disco datos disponible | 101 GB ✅ |
| Google Drive requerido | ~20 GB |

### 14.6 Comandos útiles

| Acción | Comando |
|---|---|
| Ejecutar backup manual | `/usr/local/bin/backup-nas.sh` |
| Ver crontab | `crontab -l` |
| Ver config rclone | `cat /root/.config/rclone/rclone.conf` |
| Listar backups en cloud | `rclone ls gdrive:Backup_NAS/` |
| Ver logs de backup | `cat /srv/dev-disk-by-uuid-.../backups/backup.log` |

---

## 15. Historial de cambios

| Fecha | Versión | Cambio | Autor |
|---|---|---|---|
| 2026-07-11 | 1.0 | Documentación inicial | Luis Gutiérrez |
| 2026-07-11 | 1.1 | Sección de backup a Google Drive agregada | Luis Gutiérrez |
| 2026-07-11 | 1.1 | IP cambiada de DHCP a estática (192.168.90.63/24) | Luis Gutiérrez |
