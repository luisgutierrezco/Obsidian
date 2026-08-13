---
tags:
  - Servicios
  - Nextcloud
  - Docker
  - Infraestructura
area: Infraestructura
---

# INFORME FINAL — Nextcloud en NAS-OMV

> Despliegue de Nextcloud en contenedor Docker (Docker Compose) sobre el servidor NAS-OMV (`192.168.90.63`).

## Desplegado y operativo

**URL de acceso:** http://192.168.90.63:8080

| Servicio | Estado | Puerto |
|---|---|---|
| nextcloud-app (Nextcloud **34.0.2** + PHP 8.5) | Up | 8080→80 |
| nextcloud-db (MariaDB 10.6) | Up (healthy) | interno |
| nextcloud-redis (Redis alpine) | Up (healthy) | interno |

## Ruta del NAS mapeada en Nextcloud

- **Carpeta NAS:** `/srv/dev-disk-by-uuid-dd6d6b33-dcd2-4919-bddd-a3cdebd2473e/STORAGE_PRODUCTS/`
- **Montada en el contenedor:** `/mnt/nas` (lectura/escritura verificada)
- **Propietarios preservados:** Nextcloud/Apache corren como **`USER_PRODUCTS` (UID 1021, GID 100)** — los archivos que cree quedarán `1021:100` (verificado con archivo de prueba, borrado luego). Ningún archivo existente fue tocado.

## Credenciales MariaDB
Guardadas en `/opt/docker-stacks/nextcloud/.env` (chmod 600):

| Variable | Valor |
|---|---|
| Base de datos | `nextcloud` |
| Usuario | `nextcloud` |
| Password app | `jNsV9UHQBxKDvV25eml3RnuI` |
| Password root | `90rwAaUV0d7Se3HWiyTB1nXO` |
| Redis password | `hswZsEVln67v4eEF5pykGzYC` |

**Admin Nextcloud:** usuario `admin` / `W8zCGCd5sTWiDkpBNYMsYk0l`

## Activar "External Storage Support" (opcional)

1. Loguéate como admin → **Aplicaciones** (ícono de apps).
2. Busca **"External storage support"** → **Activar**.
3. **Configuración → Almacenamiento externo** → **Añadir almacenamiento**.
4. Tipo: **Almacenamiento local** → Ruta: `/mnt/nas` → activa para los usuarios/`admin` → **Guardar**.
5. (La carpeta ya está visible para el sistema; el plugin solo la expone en la interfaz de archivos.)

## Control de acceso: bloqueo de eliminación en BANCO_DE_IMAGENES

> Objetivo: los usuarios de los grupos **Cashea** (`casheaonline`) y **Web** (`website`) pueden ver/subir/editar en `/BANCO_DE_IMAGENES` (storage externo → NAS) pero **no pueden eliminar** archivos. `admin` conserva todos los permisos.

- **App:** File Access Control (`files_accesscontrol` **5.0.0**) — funciona como operación del Workflow Engine (no tiene página propia; vive en la sección **Configuración → Flujo**).
- **2 reglas creadas** en scope admin (tablas `oc_flow_operations` + `oc_flow_operations_scope`):

| ID | Regla | Grupo | Operación |
|---|---|---|---|
| 1 | Bloquear eliminar en BANCO_DE_IMAGENES (Cashea) | `Cashea` | `{"permissions":23}` |
| 2 | Bloquear eliminar en BANCO_DE_IMAGENES (Web) | `Web` | `{"permissions":23}` |

- **Checks por regla:** `UserGroupMembership` (`is` grupo) **+** `RequestURL` (`matches` `/BANCO_DE_IMAGENES/`).
- **`{"permissions":23}`** = `PERMISSION_ALL(31) − DELETE(8)`: permite leer/crear/actualizar pero **deniega eliminar** (se usa en lugar de `deny`, que bloquearía todo).
- **Prueba funcional (2026-08-13):** usuario temporal `test_probe` (grupo Cashea) — listar 207, crear 201, leer 200, **eliminar 403**, archivo intacto; **admin**: eliminar 204 ✓, archivo desaparece. Usuario de prueba eliminado después.
- Si se edita una regla desde la WebUI, el formulario guarda `deny` (bloquea todo); para el comportamiento "solo eliminar" hay que conservar `{"permissions":23}` (o recrear vía consola).

## Notas

- Docker (`/var/lib/docker`) **y containerd** reubicados al disco de datos (`.../docker/`) vía `daemon.json` + `config.toml` — no llenan `/`.
- El disco del sistema `/` está al **90%** (668M libres); Docker ya no crece ahí, pero conviene liberar espacio pronto.
- SMB/FTP/usuarios/permisos de OMV quedaron **intactos** (no se modificó configuración alguna de OMV).
- Gestiona el stack con: `cd /opt/docker-stacks/nextcloud && docker compose up -d / down / logs -f`.

## Historial de cambios

| Fecha | Versión | Cambio | Autor |
|---|---|---|---|
| 2026-08-13 | 1.0 | Despliegue de Nextcloud 34.0.2 (Docker Compose) en NAS-OMV | Luis Gutiérrez |
| 2026-08-13 | 1.1 | File Access Control: bloqueo de eliminación en BANCO_DE_IMAGENES para grupos Cashea y Web (verificado) | Luis Gutiérrez |

## Enlaces relacionados

- [[servidores/SRVNASOMV|SRVNASOMV]] — documentación del servidor NAS-OMV
- [[servidores/README|README]] — índice de servidores