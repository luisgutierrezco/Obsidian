# Servidor Privado RustDesk

## Información General

- **Hostname:** rustdesk-vip
- **SO:** Debian 6.1 (x86_64)
- **IP:** 192.168.90.104
- **Red:** 192.168.90.0/24 (interfaz enp0s3, DHCP)
- **Virtualización:** Docker con `network_mode: host`
- **Versión RustDesk Server:** latest (imagen Docker `rustdesk/rustdesk-server`)

---

## Arquitectura del Servicio

RustDesk usa dos componentes que corren como contenedores Docker:

### hbbs (Rendezvous / ID Server)
- **Función:** Servidor de registro y coordinación. Los clientes se conectan aquí para anunciar su presencia, obtener IDs y coordinar el establecimiento de conexiones P2P.
- **Comando:** `hbbs -r 192.168.90.104:21117 -k _`
  - `-r`: Dirección del relay server que se le envía a los clientes.
  - `-k _`: Deshabilita la clave de verificación forzada (la clave real se usa igual).
- **Puertos:**
  - `21115` TCP — Prueba de tipo NAT
  - `21116` TCP/UDP — Registro de IDs y coordinación (principal)
  - `21118` TCP — Prueba de relay

### hbbr (Relay Server)
- **Función:** Servidor de retransmisión. Cuando dos clientes no pueden establecer una conexión directa P2P (por NAT restrictivo, firewalls, etc.), el tráfico se reenvía a través de este relay.
- **Comando:** `hbbr` (sin parámetros)
- **Puertos:**
  - `21117` TCP — Relay de datos (principal)
  - `21119` TCP — Prueba de relay

### Almacenamiento
- **Ruta local:** `/opt/rustdesk-server/data/`
- **Montado en:** `/root` dentro del contenedor
- **Archivos:**
  - `id_ed25519` — Clave privada del servidor (88 bytes)
  - `id_ed25519.pub` — Clave pública (44 bytes)
  - `db_v2.sqlite3` — Base de datos SQLite con usuarios registrados y sesiones

---

## Docker Compose

Archivo: `/opt/rustdesk-server/docker-compose.yml`

```yaml
version: '3'

services:
  hbbs:
    container_name: hbbs
    image: rustdesk/rustdesk-server:latest
    command: hbbs -r 192.168.90.104:21117 -k _
    volumes:
      - ./data:/root
    network_mode: host
    restart: unless-stopped

  hbbr:
    container_name: hbbr
    image: rustdesk/rustdesk-server:latest
    command: hbbr
    volumes:
      - ./data:/root
    network_mode: host
    restart: unless-stopped
```

### Explicación de opciones

| Opción | Explicación |
|---|---|
| `network_mode: host` | Los contenedores usan la red del host directamente. No hay aislamiento de puertos, lo que permite que hbbs/hbbr escuchen en las interfaces reales del servidor. |
| `restart: unless-stopped` | Los contenedores se reinician automáticamente al arrancar el sistema o si fallan, a menos que se detengan explícitamente. |
| `volumes: ./data:/root` | Persiste la configuración (claves, base de datos) fuera del contenedor para que sobrevivan a recreaciones del contenedor. |
| `-k _` | Bandera opcional que desactiva la verificación obligatoria de clave en el servidor. La clave pública sigue siendo necesaria del lado del cliente. |

---

## Clave Pública

```
7tA7P4vZoHwx9dx4SNZjC3t1PxxS+AZui4VfuUWclGA=
```

Esta clave se genera automáticamente la primera vez que arranca hbbs. Es única para este servidor. Cada cliente debe tener esta clave configurada para conectarse.

---

## Puertos a Abrir en el Firewall

Si hay un firewall entre los clientes y este servidor, se deben abrir:

| Puerto | Protocolo | Servicio | Motivo |
|---|---|---|---|
| 21115 | TCP | hbbs | Prueba de tipo NAT |
| 21116 | TCP | hbbs | Conexión de registro de IDs |
| 21116 | UDP | hbbs | Conexión de registro de IDs |
| 21117 | TCP | hbbr | Tráfico de relay cuando no hay P2P directo |
| 21118 | TCP | hbbs | Prueba de relay |
| 21119 | TCP | hbbr | Prueba de relay |

---

## Cómo Funciona RustDesk

1. **Registro:** El cliente Windows se conecta al ID Server (192.168.90.104:21116) y se registra con un ID único generado localmente.
2. **Coordinación:** Cuando otro cliente quiere conectarse, consulta al ID Server para obtener la dirección del cliente destino.
3. **Conexión directa (P2P):** Si ambos clientes pueden alcanzarse directamente (NAT favorable), el tráfico viaja directamente entre ellos sin pasar por el relay.
4. **Conexión por relay:** Si no es posible P2P (NAT simétrico, firewalls), el tráfico se reenvía a través del Relay Server (192.168.90.104:21117).
5. **Cifrado:** Todo el tráfico está cifrado de extremo a extremo usando la clave pública del servidor. Ni siquiera el relay puede descifrar los datos.

---

## Configuración en el Cliente

En la aplicación de RustDesk (Windows, Linux, Android, macOS):

| Campo | Valor |
|---|---|
| **ID Server** | `192.168.90.104` |
| **Relay Server** | `192.168.90.104` |
| **Key** | `7tA7P4vZoHwx9dx4SNZjC3t1PxxS+AZui4VfuUWclGA=` |

---

## Comandos Útiles

```bash
# Ver estado de los contenedores
docker ps | grep hbb

# Ver logs del ID server
docker logs hbbs

# Ver logs del relay server
docker logs hbbr

# Reiniciar servicios
docker restart hbbs hbbr

# Ver la clave pública
cat /opt/rustdesk-server/data/id_ed25519.pub

# Acceder al contenedor
docker exec -it hbbs /bin/sh
```
