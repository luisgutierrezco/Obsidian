---
name: listas-vip
description: Generates product price listing PDFs for Chrystal Ultra Plus. Handles 4 report variants for DELIVERY and TIENDAS. Use ONLY for price list PDF generation - not for other report tasks.
mode: subagent
tags:
  - Agentes
  - Reportes
  - Chrystal
  - DesarrolloTech
---

# LISTAS_VIP — Generador de Listados de Precios

## Subcomandos disponibles

| Comando | Qué hace |
|---------|----------|
| `/listas-vip test` | Genera 1 PDF por reporte (4 total) para verificación rápida |
| `/listas-vip full` | Genera los 11 PDFs completos (DELIVERY + TIENDAS) |
| `/listas-vip delivery` | Genera solo los 8 PDFs de la carpeta DELIVERY |
| `/listas-vip tiendas` | Genera solo los 3 PDFs de la carpeta TIENDAS |

## Cómo ejecutar

Ejecuta el script PowerShell:

```
C:\Users\segur\OneDrive\Desktop\LISTAS_PRECIOS\AGENTE\generar_listas.ps1 -Mode <comando>
```

Ejemplos:
```
.\generar_listas.ps1 -Mode test
.\generar_listas.ps1 -Mode full
.\generar_listas.ps1 -Mode delivery
.\generar_listas.ps1 -Mode tiendas
```

El script compila automaticamente el Java si hay cambios y luego genera los PDFs.

## Archivos del proyecto

- **Script**: `C:\Users\segur\OneDrive\Desktop\LISTAS_PRECIOS\AGENTE\generar_listas.ps1`
- **Programa Java**: `C:\Users\segur\OneDrive\Desktop\LISTAS_PRECIOS\AGENTE\GenerateListadosPrecios.java`
- **Reportes .jrxml**: `C:\ChrystalUltraPlus2022\Reports1\`
- **PDFs generados**: `C:\Users\segur\OneDrive\Desktop\LISTAS_PRECIOS\DELIVERY\` y `TIENDAS\`

## Reportes utilizados (4)

| # | Archivo | Título | Precio que muestra |
|---|---------|--------|-------------------|
| 1 | `REP_FMT_LIST_PRODUCTS.jrxml` | Listado de Productos | `offer_price * aliquot` (con IVA) |
| 2 | `REP_FMT_LIST_PRODUCTS_2.jrxml` | Listado de Productos | `offer_price * aliquot` + `offer_price` + códigos F1/F3 |
| 3 | `REP_FMT_LIST_PRODUCTS_3.jrxml` | PRECIOS PARA TARJETAS INTERNACIONAL | `higher_price * 1.05` (recargo 5%) |
| 4 | `REP_FMT_LIST_PRODUCTS_4_CASHEA.jrxml` | LISTA DE PRECIO CASHEA | `maximum_price` (agrupado por categoría) |

## Mapeo de PDFs generados

### DELIVERY (8 PDFs) — Reportes 1 y 4

| Reporte | Depto | Nombre archivo |
|---------|-------|----------------|
| 1 | 12 | `Accesorios_DD-MM.pdf` |
| 1 | 11 | `Conectividad y Camaras_DD-MM.pdf` |
| 1 | 005 | `Televisores y Consolas_DD-MM.pdf` |
| 1 | 004 | `Laptops e Impresoras_DD-MM.pdf` |
| 1 | 01 | `Telefonia_DD-MM.pdf` |
| 1 | 08 | `Juegos_DD-MM.pdf` |
| 4 | 02 | `Catalogo Cashea Acc_DD-MM.pdf` |
| 4 | 006 | `Catalogo Cashea Telf_DD-MM.pdf` |

### TIENDAS (3 PDFs) — Reportes 2 y 3

| Reporte | Depto | Nombre archivo |
|---------|-------|----------------|
| 2 | 02 | `Catalogo Accesorios_DD-MM.pdf` |
| 2 | 006 | `Catalogo Telefonia_DD-MM.pdf` |
| 3 | Todos | `Tarjeta Internacional_DD-MM.pdf` |

## Parámetros fijos

- **Tiendas**: `P_INITIAL_STORE=00`, `P_FINAL_STORE=17`
- **Stock**: Solo productos con stock (`P_SHOW_WITH_STOCK=true`)
- **Moneda**: Bolivares (codigo `'02'` hardcoded en los reportes)
