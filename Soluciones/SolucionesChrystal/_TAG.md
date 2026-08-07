---
tags:
  - Documentacion
  - Chrystal
  - Servidores
tema: Taxonomia global de etiquetas del vault
---

# Glosario global de etiquetas del repo

Este archivo define la **taxonomia oficial** de etiquetas de todo el vault. Su proposito es que Obsidian **conecte automaticamente** notas relacionadas via backlinks y que se mantenga una convencion consistente.

> Regla: toda nota/script/skill DEBE usar estas etiquetas y seguir estas convenciones.

## Etiquetas por dominio

| Etiqueta | Que indica | Notas/folders donde aplica |
|----------|-----------|-----------------------------|
| `#Chrystal` | Sistema **Chrystal Ultra Plus** (POS, reportes, config) | `Soluciones/SolucionesChrystal`, reportes |
| `#Servidores` | Infraestructura / servidores Linux/Windows | `servidores/` |
| `#Red` | Red, VLANs, router, MikroTik, habilitaciones | `servidores/`, router RB5009 |
| `#Impresion` | Impresoras, escaneres, CUPS, IPP | `servidores/SRVIMPRESIONAUDT` |
| `#Backup` | Copias de seguridad, rclone, cloud | `servidores/SRVNASOMV` |
| `#DesarrolloTech` | Programacion, scripts, automatizacion, codigo | `scripts/`, `reportesnuevos/` |
| `#Reportes` | Generacion/recompilacion de reportes | `Soluciones/SolucionesChrystal`, `reportesnuevos/` |
| `#Agentes` | Agentes y skills de opencode | `AGENTESOPENCODE/`, `Skill/`, `.opencode/agent/` |
| `#Web` | Pagina web de tiendas | `Pagina Web.md` |
| `#Administracion` | Admin de usuarios, permisos, tiendas, auditoria | `servidores/SRVNASOMV`, notas de tiendas |
| `#JasperReports` | Reportes Jasper / recompilacion | `Soluciones/SolucionesChrystal` |

## Etiquetas de estado (solo para soluciones)

| Etiqueta | Uso |
|----------|-----|
| `#FixBug` | Es una solucion a un bug/error |
| `#Resuelto` / `#EnProgreso` / `#Pendiente` | Estado de una solucion o investigacion |

## Etiquetas de la taxonomia (forma de uso)

- **Una nota puede llevar varias etiquetas de dominio** si aplica a varios temas.
- Combina una de dominio + estado en las soluciones.
- Las carpetas agrupan por area; las etiquetas + `[[wikilinks]]` conectan entre areas.

## Como conectan las notas

1. **Frontmatter `tags:`** — el bloque YAML de cada nota. Obsidian indexa y crea backlinks.
2. **`[[wikilinks]]`** — enlaces manuales entre notas (ej. `[[SRVNASOMV]]`). Conectan la nota a su area y a notas relacionadas.
3. **Carpertas + README (MOC)** — punto de entrada por area.

## Al crear una nota nueva

1. Pon frontmatter con `tags` de dominio (tabla de arriba) + `fecha`, `area`, `estado` si es solucion.
2. Enlaza con `[[wikilinks]]` a la nota de su area y al indice correspondiente.
3. Anade una fila en el README/MOC del area.
4. Commit y push.

## Enlaces
- [[Soluciones/SolucionesChrystal/README|README]] — indice de soluciones Chrystal.
- [[2026-08-07_recompilar_reports_jasper_620]] — ejemplo de solucion con etiquetas de dominio + FixBug.