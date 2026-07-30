# Reportes Crystal Ultra Plus - Diseño Minimalista

## Resumen de Cambios

Se rediseñaron 3 reportes principales (TRASLADO, CARGA, DESCARGA) con sus respectivos subreportes de detalle, pasando de un diseño con rectángulos/recuadros a un estilo **minimalista profesional (ahorro de tinta)**.

---

## Archivos Modificados

### Reportes Principales
| Archivo | Descripción |
|---------|-------------|
| `REP_FMT_INVENTORY_OPERATION_TRANSFER.jrxml` | Comprobante de Traslado |
| `REP_FMT_INVENTORY_OPERATION_LOAD.jrxml` | Comprobante de Carga |
| `REP_FMT_INVENTORY_OPERATION_DOWNLOAD.jrxml` | Comprobante de Descarga |

### Subreportes de Detalle
| Archivo | Descripción |
|---------|-------------|
| `REP_FMT_INVENTORY_OPERATION_DETAILS_TRANSFER.jrxml` | Detalle Traslado |
| `REP_FMT_INVENTORY_OPERATION_DETAILS_LOAD.jrxml` | Detalle Carga |
| `REP_FMT_INVENTORY_OPERATION_DETAILS_DOWNLOAD.jrxml` | Detalle Descarga |

---

## Estructura de Columnas (Subreportes)

### TRASLADO
| Columna | x | width |
|---------|---|-------|
| CODIGO | 0 | 65 |
| DESCRIPCION DEL PRODUCTO | 70 | 260 |
| CANT. | 335 | 55 |
| DEP. ORIGEN | 395 | 70 |
| DEP. DESTINO | 470 | 102 |

### CARGA y DESCARGA
| Columna | x | width |
|---------|---|-------|
| CODIGO | 0 | 65 |
| DESCRIPCION DEL PRODUCTO | 70 | 260 |
| CANT. | 335 | 55 |
| UNIDAD | 395 | 60 |
| DEPOSITO | 460 | 112 |

---

## Diseño Aplicado

### Encabezado (pageHeader)
- Empresa + RIF a la izquierda (SansSerif 14 bold / 8 bold #555)
- Línea separadora superior (1.25px)
- Título del documento a la derecha: "COMPROBANTE DE TRASLADO/CARGA/DESCARGA" (SansSerif 9 bold #444)
- N° de documento (SansSerif 14 bold)
- Datos: Usuario, Fecha Emisión, Motivo, Hora Registro (SansSerif 8)
- Línea separadora inferior (0.5px #888)

### Tabla de Detalle (columnHeader + detail)
- Líneas superior e inferior del encabezado (1.0px)
- Fuente SansSerif 8 bold para títulos, 8 normal para datos
- Cantidad centrada y en bold
- Código producto con isStretchWithOverflow para códigos largos
- Línea separadora de filas (#E0E0E0 0.5px)
- Seriales: se muestran solo si existen (printWhenExpression), fuente 7

### Pie de Página (pageFooter)
- Notas (isRemoveLineWhenBlank)
- Total Renglones + Total Cantidad a la derecha
- Línea separadora (0.75px)
- 4 firmas: Realizado | Verificado | Entregado | Recibido
- Líneas verticales separadoras (#888888)
- Línea inferior (0.75px)

---

## Cambios Técnicos

### Página
- Tamaño: **Letter** (612x792)
- columnWidth: **572** (555 anterior)
- Márgenes: top/bottom 15px

### Subreportes
- columnWidth: **572** (555 anterior)
- leftMargin/rightMargin: 0 (incrustado en el principal)

### Rutas de Subreportes
- Cambiado de `"//"` a `"/"` en las rutas de subreportes

---

## Cómo Compilar .jrxml a .jasper

### Requisitos
- Java 8 JRE instalado
- JasperReports 6.2.0+ (las libs están en `C:\ChrystalUltraPlus2022\lib\`)

### Método 1: Usando ECJ (Eclipse Compiler for Java) - SIN JDK

```bash
# 1. Crear archivo Java CompileReports.java
```

```java
import net.sf.jasperreports.engine.JasperCompileManager;

public class CompileReports {
    public static void main(String[] args) throws Exception {
        String base = "C:\\ChrystalUltraPlus2022\\Reports1\\";
        String[] names = {
            "REP_FMT_INVENTORY_OPERATION_TRANSFER",
            "REP_FMT_INVENTORY_OPERATION_DETAILS_TRANSFER",
            "REP_FMT_INVENTORY_OPERATION_LOAD",
            "REP_FMT_INVENTORY_OPERATION_DETAILS_LOAD",
            "REP_FMT_INVENTORY_OPERATION_DOWNLOAD",
            "REP_FMT_INVENTORY_OPERATION_DETAILS_DOWNLOAD"
        };
        for (String n : names) {
            String jrxml = base + n + ".jrxml";
            String jasper = base + n + ".jasper";
            System.out.println("Compilando: " + n);
            JasperCompileManager.compileReportToFile(jrxml, jasper);
            System.out.println("  -> OK: " + jasper);
        }
        System.out.println("Listo!");
    }
}
```

```powershell
# 2. Compilar el .java usando ECJ (sin JDK)
java -cp "C:\ChrystalUltraPlus2022\lib\ecj-4.3.1.jar" org.eclipse.jdt.internal.compiler.batch.Main CompileReports.java -cp "C:\ChrystalUltraPlus2022\lib\jasperreports-6.2.0.jar" -d . -source 1.7 -target 1.7

# 3. Ejecutar para compilar los .jrxml a .jasper
java -cp ".;C:\ChrystalUltraPlus2022\lib\*" CompileReports
```

### Método 2: Usando JasperSoft Studio (IDE)
1. Abrir cada `.jrxml` en JasperSoft Studio
2. Clic derecho > **Compile Report** (o Report > Compile Report)
3. El `.jasper` se genera en la misma carpeta

### Método 3: Con JDK instalado
```bash
javac -cp "C:\ChrystalUltraPlus2022\lib\jasperreports-6.2.0.jar" CompileReports.java
java -cp ".;C:\ChrystalUltraPlus2022\lib\*" CompileReports
```

---

## Notas Importantes
- La columna **DESCRIPCION DEL PRODUCTO** es la más ancha (260px) en todos los reportes
- Los códigos de producto largos se desbordan a la siguiente línea (`isStretchWithOverflow`)
- Los márgenes izquierdo/derecho del detalle calzan exactamente con el encabezado
- Los seriales se muestran en fuente pequeña (7) solo cuando existen
- Diseño optimizado para ahorro de tinta (líneas finas, sin rectángulos/recuadros)
