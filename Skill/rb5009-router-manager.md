---glpat-HJpiFu6cs9SiKTNcqOlOw2M6MQpvOjEKdTpvNnlzNw8.01.170xlxclm
name: rb5009-router-manager
description: Gestiona y diagnostica el router MikroTik RB5009 (192.168.3.1, VLANs, firewall, tráfico)
---

# RB5009 Router Manager

Skill para gestionar el router MikroTik RB5009UG+S+ en `$RB5009_HOST`.

Conexión SSH: `sshpass -p "$RB5009_PASS" ssh -o StrictHostKeyChecking=no -p $RB5009_PORT $RB5009_USER@$RB5009_HOST`

## Hardware

| Item | Valor |
|------|-------|
| Modelo | RB5009UG+S+ |
| Serial | HH80AFPHC53 |
| RouterOS | 7.15.3 |
| CPU | ARM 64bit |
| Puertos | 1x SFP+ (unused), 8x Gigabit RJ45 |

## Topología de Red

### Interfaces

| Interfaz | Subred | Propósito |
|----------|--------|-----------|
| ether1_wan | 190.6.31.61/24 (gw 190.6.31.1) | WAN (Internet) |
| ether2_LAN | 192.168.2.0/24 | Libre |
| ether3_WIFI | 192.168.3.0/24 | Admin |
| ether4 | PVID 10 | VLAN 10 - WIFI |
| ether5 | PVID 20 | VLAN 20 - SRV |
| ether6 | PVID 30 | VLAN 30 - REDVIP1 |
| ether7 | PVID 40 | VLAN 40 - REDVIP2 |
| ether8 | PVID 50 | VLAN 50 - CCTV |

### VLANs (bridge-vip, vlan-filtering=yes)

| VLAN         | Subred          | Interface | Notas           |
| ------------ | --------------- | --------- | --------------- |
| 10 (WIFI)    | 192.168.88.0/24 | ether4    | WiFi clients    |
| 20 (SRV)     | 192.168.91.0/24 | ether5    | Proxmox en .248 |
| 30 (REDVIP1) | 192.168.89.0/24 | ether6    |                 |
| 40 (REDVIP2) | 192.168.90.0/24 | ether7    | Tráfico alto    |
| 50 (CCTV)    | 192.168.92.0/24 | ether8    | Cámaras         |

## Firewall

### Reglas Forward activas (6 reglas VLAN20↔VLAN30/40/50)

| # | src | dst | action | hits |
|---|-----|-----|--------|------|
| 1 | vlan20-SRV | vlan30-redvip1 | accept | ~3 pkts |
| 2 | vlan30-redvip1 | vlan20-SRV | accept | ~659 pkts |
| 3 | vlan20-SRV | vlan40-redvip2 | accept | ~3 pkts |
| 4 | vlan40-redvip2 | vlan20-SRV | accept | ~525 pkts |
| 5 | vlan20-SRV | vlan50-cctv | accept | ~4 pkts |
| 6 | vlan50-cctv | vlan20-SRV | accept | ~89 pkts |

### Otras reglas

- **#8**: drop input desde WAN (ether1_wan)
- **#9**: drop-invalid (deshabilitada)

### Faltantes
- VLAN10 (WIFI) ↔ cualquier VLAN
- ether2_LAN ↔ cualquier VLAN
- ether3_WIFI ↔ cualquier VLAN

## DHCP

- 204 leases activos
- 6 pools huérfanos por limpiar
- Interfaz: bridge-vip

## Problemas Conocidos

1. **Ping asimétrico a Proxmox**: 192.168.91.248 responde desde el router pero NO desde VLAN30/40/50. Proxmox sí puede ping a workstations. Sospecha: nftables, kernel filter, o vmbr0 bridge binding.
2. **ARP duplicado**: 192.168.91.248 aparece en vlan20-SRV (correcto) y vlan30-redvip1 (fallido).
3. **Puertos gestión cerrados desde ethernet**: SSH (3678), WinBox (8291), HTTP (80) no responden desde la red local. Solo accesible desde VLAN20/50 o consola física.
4. **Top tráfico**: ALMAYOR5 (192.168.90.18, MAC 00:E0:4C:36:02:5F) ~1,338 conexiones a 172.172.255.216:443 y 172.172.255.217:443.

## Comandos de Diagnóstico Rápido

### Conexiones
```bash
sshpass -p "$RB5009_PASS" ssh -o StrictHostKeyChecking=no -p $RB5009_PORT $RB5009_USER@$RB5009_HOST /ip firewall connection print count-only
sshpass -p "$RB5009_PASS" ssh -o StrictHostKeyChecking=no -p $RB5009_PORT $RB5009_USER@$RB5009_HOST /ip firewall connection print where dst-address=172.172.255.216
```

### Tráfico en tiempo real (5s)
```bash
sshpass -p "$RB5009_PASS" ssh -o StrictHostKeyChecking=no -p $RB5009_PORT $RB5009_USER@$RB5009_HOST /interface monitor-traffic ether1_wan once
```

### ARP
```bash
sshpass -p "$RB5009_PASS" ssh -o StrictHostKeyChecking=no -p $RB5009_PORT $RB5009_USER@$RB5009_HOST /ip arp print where address=192.168.91.248
```

### Firewall hits
```bash
sshpass -p "$RB5009_PASS" ssh -o StrictHostKeyChecking=no -p $RB5009_PORT $RB5009_USER@$RB5009_HOST /ip firewall filter print stats
```

### Backup configuración
```bash
sshpass -p "$RB5009_PASS" ssh -o StrictHostKeyChecking=no -p $RB5009_PORT $RB5009_USER@$RB5009_HOST /system backup save name=config-$(date +%Y%m%d).backup
```

### Top 10 IPs por conexiones
```bash
sshpass -p "$RB5009_PASS" ssh -o StrictHostKeyChecking=no -p $RB5009_PORT $RB5009_USER@$RB5009_HOST /ip firewall connection print | grep "src-address=" | sed 's/.*src-address=//' | sed 's/ .*//' | sort | uniq -c | sort -rn | head -10
```

### Monitoreo ancho de banda por VLAN
```bash
for vlan in vlan10-wifi vlan20-SRV vlan30-redvip1 vlan40-redvip2 vlan50-cctv; do
  echo "=== $vlan ==="
  sshpass -p "$RB5009_PASS" ssh -o StrictHostKeyChecking=no -p $RB5009_PORT $RB5009_USER@$RB5009_HOST /interface monitor-traffic $vlan once
done
```

## Tareas Pendientes

- [ ] Diagnosticar Proxmox: `nft list ruleset`, `tcpdump -i vmbr0 icmp`, `ip route show`, `sysctl net.ipv4.icmp_echo_ignore_all`
- [ ] Re-testear ping desde workstation a 192.168.91.248
- [ ] Limpiar 6 pools DHCP huérfanos
- [ ] Limpiar 4 direcciones IP deshabilitadas
- [ ] Agregar reglas forward para VLAN10, ether2_LAN, ether3_WIFI
- [ ] Habilitar regla #9 drop-invalid
- [ ] Restringir SSH a 192.168.3.0/24
- [ ] Crear usuario no-admin para SSH
- [ ] Habilitar traffic-flow o contadores de firewall para monitoreo por IP
