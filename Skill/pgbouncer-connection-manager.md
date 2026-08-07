---
name: pgbouncer-connection-manager
description: Gestiona conexiones de PgBouncer en servidor 192.168.91.131 (ver conexiones por IP, matar sesiones, ajustar MAX_PER_IP, pg_hba.conf)
tags:
  - Agentes
  - Servidores
  - Red
  - Administracion
---

# PgBouncer Connection Manager

Skill para gestionar conexiones de PgBouncer en `192.168.91.131`.

## Conexión

Dos formas de ejecutar los comandos:

### Directa (recomendada)
```
PGPASSWORD="$PGBOUNCER_PASS" psql -h 192.168.91.131 -p 5432 -U postgres -d pgbouncer -tA -c "<QUERY>"
```

### Via SSH
```
sshpass -p "$PGBOUNCER_SSH_PASS" ssh -o StrictHostKeyChecking=no root@192.168.91.131 "<COMMAND>"
```

## Comandos

### 1. Ver conexiones por IP (ordenadas)
```
PGPASSWORD="$PGBOUNCER_PASS" psql -h 192.168.91.131 -p 5432 -U postgres -d pgbouncer -tA -F'|' -c "SHOW CLIENTS;" 2>/dev/null | awk -F'|' '{if($6 != "" && $6 != "127.0.0.1") print $6}' | sort | uniq -c | sort -rn
```

### 2. Ver IPs con más de N conexiones
Agregar al final: `| awk '{if($1 > N) print $2}'`

### 3. Matar conexiones de IP(s) específica(s)
```
PGPASSWORD="$PGBOUNCER_PASS"
for ip in IP1 IP2 IP3; do
  for id in $(psql -h 192.168.91.131 -p 5432 -U postgres -d pgbouncer -tA -c "SHOW CLIENTS;" 2>/dev/null | awk -F'|' -v ip="$ip" '{if($6 == ip) print $21}'); do
    echo "KILL_CLIENT $id" | psql -h 192.168.91.131 -p 5432 -U postgres -d pgbouncer 2>&1
  done
done
```

### 4. Matar IPs no whitelisted con >5 conexiones
```
PGPASSWORD="$PGBOUNCER_PASS"
for ip in $(psql -h 192.168.91.131 -p 5432 -U postgres -d pgbouncer -tA -F'|' -c "SHOW CLIENTS;" 2>/dev/null | awk -F'|' '{if($6 != "" && $6 != "127.0.0.1" && $6 != "192.168.91.55" && $6 != "192.168.91.158" && $6 != "192.168.91.210" && $6 != "192.168.90.151") print $6}' | sort | uniq -c | sort -rn | awk '{if($1 > 5) print $2}'); do
  for id in $(psql -h 192.168.91.131 -p 5432 -U postgres -d pgbouncer -tA -c "SHOW CLIENTS;" 2>/dev/null | awk -F'|' -v ip="$ip" '{if($6 == ip) print $21}'); do
    echo "KILL_CLIENT $id" | psql -h 192.168.91.131 -p 5432 -U postgres -d pgbouncer 2>&1
  done
done
```

### 5. Ver/Ajustar MAX_PER_IP
```
sshpass -p "$PGBOUNCER_SSH_PASS" ssh -o StrictHostKeyChecking=no root@192.168.91.131 "grep MAX_PER_IP /etc/pgbouncer/trim-by-ip.env"
sshpass -p "$PGBOUNCER_SSH_PASS" ssh -o StrictHostKeyChecking=no root@192.168.91.131 "sed -i 's/MAX_PER_IP=.*/MAX_PER_IP=15/' /etc/pgbouncer/trim-by-ip.env"
```

### 6. Ver/Ajustar whitelist
```
sshpass -p "$PGBOUNCER_SSH_PASS" ssh -o StrictHostKeyChecking=no root@192.168.91.131 "grep WHITELIST /etc/pgbouncer/trim-by-ip.env"
sshpass -p "$PGBOUNCER_SSH_PASS" ssh -o StrictHostKeyChecking=no root@192.168.91.131 "sed -i 's/WHITELIST=.*/WHITELIST=IP1,IP2,IP3/' /etc/pgbouncer/trim-by-ip.env"
```

### 7. Ver IPs permitidas en PostgreSQL (pg_hba.conf)
```
sshpass -p "$PGBOUNCER_SSH_PASS" ssh -o StrictHostKeyChecking=no root@192.168.91.131 "grep -vE '^(#|$)' /etc/postgresql/9.6/main/pg_hba.conf"
```

### 8. Agregar IP a pg_hba.conf
```
sshpass -p "$PGBOUNCER_SSH_PASS" ssh -o StrictHostKeyChecking=no root@192.168.91.131 "echo 'host cadm_j5004625301 postgres IP/32 md5' >> /etc/postgresql/9.6/main/pg_hba.conf && systemctl reload postgresql"
```

### 9. Listar bases de datos
```
PGPASSWORD="$PGPASS" psql -h 192.168.91.131 -p 5432 -U postgres -c '\l+'
```


## Enlaces relacionados

- [[AGENTESOPENCODE/README|Agentes-Indice]] - indice de agentes y skills
- [[servidores/README|Servidores]] - infraestructura conectada
- [[Soluciones/SolucionesChrystal/README|Soluciones Chrystal]]

