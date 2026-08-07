---
tags:
  - Documentacion
  - Chrystal
tema: Taxonomia de etiquetas
---

# Glosario de etiquetas del vault

Este archivo define la taxonomia de etiquetas usada en este vault (especialmente en `Soluciones/SolucionesChrystal`). Sirve para mantener **consistencia** y que Obsidian **conecte automaticamente** notas relacionadas via backlinks.

> Regla: toda solucion nueva DEBE usar las etiquetas de aca y seguir estas convenciones.

## Etiquetas principales

| Etiqueta | Que indica | Cuando usarla |
|----------|-----------|---------------|
| `#Chrystal` | Toca cualquier parte del sistema **Chrystal Ultra Plus** | Todas las soluciones de esta carpeta |
| `#FixBug` | Es una solucion a un bug/error | Toda nota de solucion/resolucion |
| `#JasperReports` | Relacionado a reportes Jasper | Recompilacion, formatos, diseno de reportes |
| `#Reportes` | Reportes en general | Cualquier nota de reportes |
| `#Recompilacion` | Se recompilaron recursos (`.jrxml`->`.jasper`) | Compilacion de reportes |
| `#Windows` | Aplica a equipos SO Windows | Kamando/ejecucion de app |
| `#Red` / `#Servidor` / `#Router` | Infraestructura | Config de red, servidores, MikroTik |
| `#Skill` | Es un Skill/agente documentado en el vault | Notas de agentes y skills |

## Etiquetas de estado

| Etiqueta | Uso |
|----------|-----|
| `#Resuelto` | Solucion aplicada y verificada |
| `#EnProgreso` | Investigacion en curso, aun sin resolucion |
| `#Pendiente` | Detectado pero no resuelto |
| `#Mediano` / `#Abierto` | (opcional) temas abiertos de mejora |

## Como se conectan las notas

1. **Frontmatter `tags:`** — en el bloque YAML de cada nota. Obsidian los indexa y crea backlinks en la vista de "Tags".
2. **`[[wikilinks]]`** — enlaces manuales entre notas (ej. `[[2026-08-07_recompilar_reports_jasper_620]]`). Conectan la solucion al README, al glosario y a otras notas relacionadas.
3. **Carpetas** — `Soluciones/SolucionesChrystal/{main}README.md` es el punto de entrada (MOC).

## Al crear una nota nueva

1. Crea el archivo en `Soluciones/SolucionesChrystal/` con nombre `AAAA-MM-DD_asunto_breve.md`.
2. Pon el frontmatter con `tags` (usa las de arriba), `fecha`, `area`, `app`, `estado`.
3. Enlaza con `[[README]]` en los `enlaces` del frontmatter o en el cuerpo.
4. Anade una fila en `README.md` (MOC).
5. Commit y push.

## Etiquetas de la nota actual

`#Chrystal` `#FixBug` `#JasperReports` `#Reportes` `#Recompilacion`

## Enlaces

- [[README]] — indice de soluciones Chrystal.
- [[2026-08-07_recompilar_reports_jasper_620]] — ejemplo de nota resuelta.