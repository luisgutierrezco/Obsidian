---
tags:
  - Chrystal
  - FixBug
  - JasperReports
  - Reportes
  - Recompilacion
fecha: 2026-08-07
area: Reportes
app: Chrystal Ultra Plus
modulo: Impresion de facturas / Reportes
sistema: Windows
severidad: Alta
estado: Resuelto
version_afectada: JasperReports 6.2.0 (app) vs 6.2.1 (compilacion)
enlaces:
  - "[[Soluciones/SolucionesChrystal/README|README]]"
  - "[[Soluciones/SolucionesChrystal/_TAG|_TAG]]"
---

# Fix: Error "class not found when loading object from file" al abrir facturas

## Problema

Al abrir/visualizar la factura (u otros reportes) en **Chrystal Ultra Plus**, la app mostraba el error:

```
class not found when loading object from file
```

## Causa raiz

- La app Chrystal usa `jasperreports-6.2.0.jar` (confirmado leyendo el MANIFEST del jar en `C:\ChrystalUltraPlus2022\lib\`).
- Los archivos `.jasper` en `PROJECT\Reports` habian sido compilados con **Jaspersoft Studio / JR 6.2.1**.
- El formato serializado de los `.jasper` **no es compatible hacia atras**: la version 6.2.0 no puede deserializar un objeto compilado con 6.2.1.

## Diagnostico (como se confirmo)

1. **Version del jar de la app:** se leyo el `MANIFEST.MF` dentro de `jasperreports-6.2.0.jar` -> `Implementation-Version: 6.2.0`.
2. **Carpeta de reportes de la app:** en `C:\ChrystalUltraPlus2022\config.ini` el parametro `REPORTS=C:\ChrystalUltraPlus2022\Reports1`.
3. **Confirmacion del mismatch:** los `.jrxml` fuente fueron compilados con JR 6.2.1 (origen Jaspersoft Studio) -> mismatch con la app 6.2.0.

## Resolucion

Recompilar **todos** los `.jrxml` -> `.jasper` usando la **misma version de la libreria que usa la app** (`jasperreports-6.2.0.jar`).

### Requisitos

- Java 8 JRE disponible (version usada: 1.8.0_441). NO hay `javac` -> se usa el compilador **ECJ** incluido en `C:\ChrystalUltraPlus2022\lib\ecj-4.3.1.jar`.
- Classpath con los jars de `C:\ChrystalUltraPlus2022\lib` (incluye jasperreports-6.2.0.jar y sus dependencias).

### Comandos

1. **Compilar el helper** (sin lambdas, compatible Java 7 que es el maximo que soporta ECJ 4.3.1):

```
java -Xmx512m -cp "$cp" org.eclipse.jdt.internal.compiler.batch.Main -source 1.7 -target 1.7 -proc:none -d out CompileAll.java
```

> Nota: ECJ 4.3.1 solo soporta source/target hasta **1.7**; por eso el helper NO usa lambdas y se compila con `-source 1.7 -target 1.7`.

2. **Ejecutar la recompilacion de los 171 reportes:**

```
java -Xmx1024m -cp "$cp;out" CompileAll "C:\Users\segur\OneDrive\Desktop\PROJECT\Reports"
```

3. **Verificar que todos los `.jasper` son cargables** (simula lo que hace la app al deserializar):

```
java -Xmx1024m -cp "$cp;out" LoadCheck "C:\Users\segur\OneDrive\Desktop\PROJECT\Reports"
```

## Verificacion

| Comprobacion | Resultado |
|---|---|
| Compilacion `.jrxml` -> `.jasper` | **171/171 OK, 0 errores** |
| Carga/deserializacion con JR **6.2.0** | **171/171 OK** |
| Factura `REP_FMT_SALES_OPERATION_BILL.jasper` | Regenerado, carga OK |
| Estructura / texto / consultas | Intactos (solo se regenero el `.jasper`) |

Respaldo previo de los `.jasper` antiguos: `PROJECT\Reports\_Backup_Jasper_20260807\` (171 archivos).

## Aprendizajes / Reglas de oro

1. **Regla principal:** recompilar reportes SIEMPRE con la **misma version** de la libreria JasperReports que usa la app (revisar `config.ini` y el MANIFEST del jar).
2. La serializacion de `.jasper` NO es compatible entre versiones de JasperReports.
3. Si hay JRE pero no `javac`, usar el ECJ de la carpeta `lib` de la app con `-source 1.7 -target 1.7` (limita el codigo: sin lambdas).
4. SIEMPRE respaldar los `.jasper` actuales antes de sobrescribir.
5. La carpeta de reportes que usa la app puede diferir de la carpeta de desarrollo: leer `config.ini` (`REPORTS=...`).

## Archivos relacionados / herramientas

- `scripts/CompileAll.java` — helper para recompilar todos los `.jrxml` de una carpeta.
- `scripts/LoadCheck.java` — verifica que los `.jasper` son cargables con la version objetivo.
- `scripts/LEEME.txt` — instrucciones de uso.
- [[Soluciones/SolucionesChrystal/README|README]] — indice de soluciones Chrystal.
- [[Soluciones/SolucionesChrystal/_TAG|_TAG]] — glosario de etiquetas.

## Etiquetas

`#Chrystal` `#FixBug` `#JasperReports` `#Reportes` `#Recompilacion`
