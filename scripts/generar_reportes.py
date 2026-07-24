#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script unificado para generar reportes de marca (Samsung/Infinix)
Uso: python generar_reportes.py [--marca samsung|infinix]
"""

import pandas as pd
import os
import re
import time
import subprocess
import argparse
import shutil
from datetime import datetime
import unicodedata

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = BASE_DIR
TARGET_DIR = None  # Se setea desde --dir si se proporciona

COLORS = {
    'samsung': [
        "TITANIUM BLACK","TITANIUM GRAY","TITANIUM WHITESILVER","TITANIUM SILVERBLUE",
        "COBALT VIOLET","SKY BLUE","AWESOME ICYBLUE","AWESOME LILAC","AWESOME NAVY",
        "AWESOME GRAY","AWESOME CHARCOAL","AWESOME WHITE","AWESOME GRAYGREEN","AWESOME LAVENDER",
        "LIGHT VIOLET","LIGHT GREEN","LIGHT BLUE","MINT GREEN","JETBLACK","WHITE",
        "MIDNIGHT BLACK","OCEAN CYAN","STARRY PURPLE","DUAL SIM",
        "GRAY","BLACK","GREEN","BLUE","VIOLET","PINK","SILVER","NAVY","CHARCOAL","LAVENDER",
        "ICYBLUE","LILAC","GRAYGREEN","SKY",
        "GRAPHITE","LEVENDER","OLIVE","FIZZ","MIDNIGHT","SOLAR",
        "JUNGLE","TWLIGHT","RACING","CORAL","MISTY","TIDES",
        "JETC","GLACI","AZURE","ONYX","PEARL","CREAM","AMETHYST","BURGUNDY"
    ],
    'infinix': [
        "SHADOW BLACK","MIST TITANIUM","CLOUDLINE BLUE","NEON RED","MOCO CYBER GREEN",
        "SOUL EYE PURPLE","TITANIUM SILVER","SLEEK BLACK","DEEP OCEAN BLUE","TWILIGHT GOLD",
        "ROSE GOLD","SHADOW BLUE","SUNLIKE ORANGE","MEADOW GREEN","IRIS BLUE",
        "ENCHANTED PURPLE","POLARIS TITANIUM","NIGHTFALL PURPLE","SAPPHIRE BLUE",
        "FOREST GREEN","OCEAN CYAN","STARRY PURPLE","DUAL SIM",
        "GRAY","BLACK","GREEN","BLUE","VIOLET","PINK","SILVER",
        "RED","PURPLE","GOLD","ORANGE","NAVY","CHARCOAL","LAVENDER","CHAMPAGNE","CYAN",
        "FIZZ","MIDNIGHT","TITANIUM GREY","SOLAR","JUNGLE BREATH","TWLIGHT",
        "RACING GREY","CORAL TIDES","MISTY","TITANIUM"
    ]
}

def normalize_text(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

def limpiar_nombre(nombre, marca=None):
    if pd.isna(nombre):
        return ""
    n = str(nombre).upper().strip()
    n = n.replace("SAMUSNG", "SAMSUNG")
    n = n.replace("TWLIGHT", "TWILIGHT")
    n = n.replace("GREEN TEXTURA", "TEXTURA")
    n = n.replace("GREENTEXTURA", "TEXTURA")
    n = n.replace("NIGTH", "NIGHT")
    # Cortar despues del patron de memoria (numero/numero[GB])
    m = re.search(r'\b\d+/\d+GB\b', n)
    if m:
        n = n[:m.end()].strip()
    else:
        m = re.search(r'\b\d+/\d+\b', n)
        if m:
            n = n[:m.end()].strip()
            if not n.endswith("GB"):
                n += "GB"
    # Fallback: usar lista de colores solo si no se encontro patron
    if marca:
        for c in COLORS.get(marca.lower(), []):
            n = n.replace(c, "")
    n = re.sub(r'\(\s*[\d/]+\s*\)', '', n)
    n = " ".join(n.split())
    n = n.replace("SAMSUNG SAMSUNG", "SAMSUNG").replace("INFINIX INFINIX", "INFINIX")
    return n.strip()


def guardar_xls(data, nombre_base, nombre_plantilla, col_modelo, col_valor, titulo_col, output_dir, generar_plantilla=True):
    """Guarda .xls con fecha. Si generar_plantilla=True, tambien copia como plantilla (sobrescribe)."""
    import xlwt
    fecha = datetime.now().strftime("%d-%m-%Y")
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet(nombre_base)
    ws.col(0).width = 50 * 256
    ws.col(1).width = 12 * 256
    ws.write(0, 0, 'Modelo')
    ws.write(0, 1, titulo_col)
    for i, (_, row) in enumerate(data.iterrows(), start=1):
        ws.write(i, 0, row[col_modelo])
        ws.write(i, 1, row[col_valor])
    archivo_fecha = os.path.join(output_dir, "{} {}.xls".format(nombre_base, fecha))
    wb.save(archivo_fecha)
    print(f"  -> Guardado: {os.path.basename(archivo_fecha)}")
    archivo_plantilla = None
    if generar_plantilla:
        archivo_plantilla = os.path.join(output_dir, "{}.xls".format(nombre_plantilla))
        shutil.copy2(archivo_fecha, archivo_plantilla)
        print(f"  -> Plantilla: {os.path.basename(archivo_plantilla)}")
    return archivo_fecha, archivo_plantilla


def parse_numero(valor):
    if pd.isna(valor):
        return 0
    s = str(valor).strip()
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except:
        return 0

def detectar_columna(df, palabras_clave):
    for col in df.columns:
        col_norm = normalize_text(str(col)).upper()
        for kw in palabras_clave:
            if kw in col_norm:
                return col
    return None

def procesar_samsung(ventas_only=False, generar_plantilla=True):
    print("\n" + "="*50)
    print("PROCESANDO SAMSUNG")
    print("="*50)
    
    inv_path = None
    if not ventas_only:
        inv_path_candidates = [
            ("Plantilla Inventario Samsung.xls", ["CODIGO", "COD"], ["NOMBRE", "DESCRIPCION"], ["EXISTENCIA", "STOCK"]),
            ("Inventario Samsung.xls", ["CODIGO", "COD"], ["NOMBRE", "DESCRIPCION"], ["EXISTENCIA", "STOCK"]),
            ("INV SAMSUNG.xls", ["CODIGO", "COD"], ["NOMBRE", "DESCRIPCION"], ["EXISTENCIA", "STOCK"])
        ]
        for fname, cod_kw, nom_kw, exi_kw in inv_path_candidates:
            full = os.path.join(BASE_DIR, fname)
            if not os.path.exists(full):
                continue
            try:
                test_df = pd.read_excel(full)
                if len(test_df) == 0:
                    continue
                c = detectar_columna(test_df, cod_kw)
                n = detectar_columna(test_df, nom_kw)
                e = detectar_columna(test_df, exi_kw)
                if all([c, n, e]):
                    inv_path = full
                    break
            except:
                continue
    
    vent_path_candidates = [
        ("Plantilla Ventas Samsung.xls", ["CODIGO", "COD"], ["MARCA"], ["DESCRIPCION", "NOMBRE"], ["CANTIDAD"]),
        ("VENTAS SAMSUNG.xls", ["CODIGO", "COD"], ["MARCA"], ["DESCRIPCION", "NOMBRE"], ["CANTIDAD"]),
        ("Ventas Samsung.xls", ["CODIGO", "COD"], ["MARCA"], ["DESCRIPCION", "NOMBRE"], ["CANTIDAD"]),
    ]
    vent_path = None
    for fname, cod_kw, mar_kw, desc_kw, cant_kw in vent_path_candidates:
        full = os.path.join(BASE_DIR, fname)
        if not os.path.exists(full):
            continue
        try:
            test_df = pd.read_excel(full)
            if len(test_df) == 0:
                continue
            c = detectar_columna(test_df, cod_kw)
            m = detectar_columna(test_df, mar_kw)
            d = detectar_columna(test_df, desc_kw) or None
            ca = detectar_columna(test_df, cant_kw)
            if all([c, m, ca]):
                vent_path = full
                break
        except:
            continue
    
    if not vent_path:
        print("ERROR: No se encontró archivo de ventas Samsung")
        return
    
    if not ventas_only and not inv_path:
        print("ERROR: No se encontró archivo de inventario Samsung")
        return
    
    # Leer Inventario
    if not ventas_only:
        print("Archivo inventario: {}".format(os.path.basename(inv_path)))
        xls = pd.ExcelFile(inv_path)
        inv_df = xls.parse(xls.sheet_names[0])
        
        cod_col = detectar_columna(inv_df, ["CODIGO", "COD"])
        nom_col = detectar_columna(inv_df, ["NOMBRE", "DESCRIPCION"])
        exi_col = detectar_columna(inv_df, ["EXISTENCIA", "STOCK"])
        
        print("Columnas detectadas - Codigo: {}, Nombre: {}, Existencia: {}".format(cod_col, nom_col, exi_col))
        
        if not all([cod_col, nom_col, exi_col]):
            print("ERROR: No se encontraron columnas de inventario")
            return
        
        inv_df = inv_df[[cod_col, nom_col, exi_col]]
        inv_df.columns = ["codigo", "nombre", "existencia"]
        inv_df["nombre_limpio"] = inv_df["nombre"].apply(lambda x: limpiar_nombre(x, "samsung"))
        inv_df["existencia_num"] = inv_df["existencia"].apply(parse_numero)
        inv_df = inv_df[inv_df["nombre_limpio"].str.contains("SAMSUNG", na=False)]
        
        stock = inv_df.groupby("nombre_limpio", as_index=False)["existencia_num"].sum()
        stock = stock.sort_values("existencia_num", ascending=False)
    
    # Leer Ventas
    xls = pd.ExcelFile(vent_path)
    vent_df = xls.parse(xls.sheet_names[0])
    
    cod_col = detectar_columna(vent_df, ["CODIGO", "COD"])
    mar_col = detectar_columna(vent_df, ["MARCA"])
    desc_col = detectar_columna(vent_df, ["DESCRIPCION", "NOMBRE"])
    cant_col = detectar_columna(vent_df, ["CANTIDAD"])
    
    print("Columnas detectadas - Codigo: {}, Marca: {}, Desc: {}, Cant: {}".format(cod_col, mar_col, desc_col, cant_col))
    
    if not all([cod_col, mar_col, cant_col]):
        print("ERROR: No se encontraron columnas de ventas")
        return
    
    cols_needed = [cod_col, mar_col]
    if desc_col:
        cols_needed.append(desc_col)
    cols_needed.append(cant_col)
    vent_df = vent_df[cols_needed]
    vent_df.columns = ["codigo", "marca", "descripcion", "cantidad"][:len(cols_needed)]
    
    vent_df["marca"] = vent_df["marca"].astype(str).str.upper().str.strip()
    vent_df = vent_df[vent_df["marca"] == "SAMSUNG"]
    vent_df["descripcion_limpio"] = vent_df["descripcion"].apply(lambda x: limpiar_nombre(x, "samsung"))
    vent_df["cantidad_num"] = vent_df["cantidad"].apply(parse_numero)
    
    ventas = vent_df.groupby("descripcion_limpio", as_index=False)["cantidad_num"].sum()
    ventas = ventas.sort_values("cantidad_num", ascending=False)
    
    # Guardar .xls
    vent_out_fecha, vent_out_plant = guardar_xls(ventas, "Ventas Samsung", "Reporte Ventas Samsung", 'descripcion_limpio', 'cantidad_num', 'Total', OUTPUT_DIR, generar_plantilla=generar_plantilla)
    
    print("OK Ventas: {} modelos".format(len(ventas)))
    print("OK Archivos Samsung guardados:")
    print("  - {} (fecha)".format(vent_out_fecha))
    if vent_out_plant:
        print("  - {} (plantilla)".format(vent_out_plant))
    
    if not ventas_only:
        inv_out_fecha, inv_out_plant = guardar_xls(stock, "Inventario Samsung", "Reporte Inventario Samsung", 'nombre_limpio', 'existencia_num', 'Stock', OUTPUT_DIR, generar_plantilla=generar_plantilla)
        print("OK Inventario: {} modelos".format(len(stock)))
        print("  - {} (fecha)".format(inv_out_fecha))
        if inv_out_plant:
            print("  - {} (plantilla)".format(inv_out_plant))

def procesar_infinix(generar_plantilla=True):
    print("\n" + "="*50)
    print("PROCESANDO INFINIX")
    print("="*50)
    
    inv_path_candidates = [
        ("Plantilla Inventario Infinix.xls", ["CODIGO", "COD"], ["NOMBRE", "DESCRIPCION"], ["EXISTENCIA", "STOCK"]),
        ("Inventario Infinix.xls", ["CODIGO", "COD"], ["NOMBRE", "DESCRIPCION"], ["EXISTENCIA", "STOCK"]),
    ]
    inv_path = None
    for fname, cod_kw, nom_kw, exi_kw in inv_path_candidates:
        full = os.path.join(BASE_DIR, fname)
        if not os.path.exists(full):
            continue
        try:
            test_df = pd.read_excel(full)
            if len(test_df) == 0:
                continue
            c = detectar_columna(test_df, cod_kw)
            n = detectar_columna(test_df, nom_kw)
            e = detectar_columna(test_df, exi_kw)
            if all([c, n, e]):
                inv_path = full
                break
        except:
            continue
    
    vent_path_candidates = [
        ("Plantilla Ventas Infinix.xls", ["CODIGO", "COD"], ["MARCA"], ["CANTIDAD"]),
        ("Ventas Infinix.xls", ["CODIGO", "COD"], ["MARCA"], ["CANTIDAD"]),
    ]
    vent_path = None
    for fname, cod_kw, mar_kw, cant_kw in vent_path_candidates:
        full = os.path.join(BASE_DIR, fname)
        if not os.path.exists(full):
            continue
        try:
            test_df = pd.read_excel(full)
            if len(test_df) == 0:
                continue
            c = detectar_columna(test_df, cod_kw)
            m = detectar_columna(test_df, mar_kw)
            ca = detectar_columna(test_df, cant_kw)
            if all([c, m, ca]):
                vent_path = full
                break
        except:
            continue
    
    deli_path_candidates = [
        ("Plantilla Ventas Delivery.xls", ["DESCRIPCION", "NOMBRE"], ["CANTIDAD"]),
        ("VENTAS DELIVERY.xls", ["DESCRIPCION", "NOMBRE"], ["CANTIDAD"]),
    ]
    deli_path = None
    for fname, desc_kw, cant_kw in deli_path_candidates:
        full = os.path.join(BASE_DIR, fname)
        if not os.path.exists(full):
            continue
        try:
            test_df = pd.read_excel(full)
            if len(test_df) == 0:
                continue
            d = detectar_columna(test_df, desc_kw)
            ca = detectar_columna(test_df, cant_kw)
            if all([d, ca]):
                deli_path = full
                break
        except:
            continue
    
    if not inv_path:
        print("ERROR: Falta archivo de inventario Infinix")
        return
    
    # Leer Inventario
    xls = pd.ExcelFile(inv_path)
    inv_df = xls.parse(xls.sheet_names[0])
    
    cod_col = detectar_columna(inv_df, ["CODIGO", "COD"])
    nom_col = detectar_columna(inv_df, ["NOMBRE", "DESCRIPCION"])
    dep_col = detectar_columna(inv_df, ["DEPARTAMENTO", "DEPT"])
    exi_col = detectar_columna(inv_df, ["EXISTENCIA", "STOCK"])
    
    if not all([cod_col, nom_col, exi_col]):
        print("ERROR: No se encontraron columnas de inventario")
        return
    
    cols_needed = [cod_col, nom_col, exi_col]
    if dep_col:
        cols_needed.append(dep_col)
    inv_df = inv_df[cols_needed]
    inv_df.columns = ["codigo", "nombre", "existencia", "departamento"][:len(cols_needed)]
    
    inv_df["nombre_limpio"] = inv_df["nombre"].apply(lambda x: limpiar_nombre(x, "infinix"))
    inv_df["existencia_num"] = inv_df["existencia"].apply(parse_numero)
    
    if "departamento" in inv_df.columns:
        inv_df = inv_df[inv_df["departamento"].astype(str).str.upper().str.strip() == "TELEFONO"]
    
    inv_df = inv_df[inv_df["nombre_limpio"].str.contains("INFINIX", na=False)]
    stock = inv_df.groupby("nombre_limpio", as_index=False)["existencia_num"].sum()
    stock = stock.sort_values("existencia_num", ascending=False)
    
    # Leer Ventas
    if not os.path.exists(vent_path):
        print("ERROR: Falta archivo de ventas Infinix")
        return
    
    xls = pd.ExcelFile(vent_path)
    vent_df = xls.parse(xls.sheet_names[0])
    
    cod_col = detectar_columna(vent_df, ["CODIGO", "COD"])
    mar_col = detectar_columna(vent_df, ["MARCA"])
    desc_col = detectar_columna(vent_df, ["DESCRIPCION", "NOMBRE"])
    cant_col = detectar_columna(vent_df, ["CANTIDAD"])
    dep_col = detectar_columna(vent_df, ["DEP", "DEPOSITO"])
    
    if not all([cod_col, mar_col, cant_col]):
        print("ERROR: No se encontraron columnas de ventas")
        return
    
    cols_needed = [cod_col, mar_col, desc_col, cant_col]
    if dep_col:
        cols_needed.append(dep_col)
    vent_df = vent_df[cols_needed]
    vent_df.columns = ["codigo", "marca", "descripcion", "cantidad", "deposito"][:len(cols_needed)]
    
    vent_df["marca"] = vent_df["marca"].astype(str).str.upper().str.strip()
    vent_df = vent_df[vent_df["marca"] == "INFINIX"]
    
    if "deposito" in vent_df.columns:
        vent_df = vent_df[vent_df["deposito"].astype(str).str.upper().str.strip() != "DEP PRI D003"]
    
    vent_df["descripcion_limpio"] = vent_df["descripcion"].apply(lambda x: limpiar_nombre(x, "infinix"))
    vent_df["cantidad_num"] = vent_df["cantidad"].apply(parse_numero)
    
    # Combinar con Delivery
    if deli_path:
        xls = pd.ExcelFile(deli_path)
        deli_df = xls.parse(xls.sheet_names[0])
        
        cod_col = detectar_columna(deli_df, ["CODIGO", "COD"])
        desc_col = detectar_columna(deli_df, ["DESCRIPCION", "NOMBRE"])
        cant_col = detectar_columna(deli_df, ["CANTIDAD"])
        
        if all([cod_col, desc_col, cant_col]):
            deli_df = deli_df[[cod_col, desc_col, cant_col]]
            deli_df.columns = ["codigo", "descripcion", "cantidad"]
            deli_df = deli_df[deli_df["descripcion"].astype(str).str.upper().str.contains("INFINIX", na=False)]
            deli_df["descripcion_limpio"] = deli_df["descripcion"].apply(lambda x: limpiar_nombre(x, "infinix"))
            deli_df["cantidad_num"] = deli_df["cantidad"].apply(parse_numero)
            vent_df = pd.concat([vent_df, deli_df], ignore_index=True)
    
    ventas = vent_df.groupby("descripcion_limpio", as_index=False)["cantidad_num"].sum()
    ventas = ventas.sort_values("cantidad_num", ascending=False)
    
    # Guardar .xls
    inv_out_fecha, inv_out_plant = guardar_xls(stock, "Inventario Infinix", "Reporte Inventario Infinix", 'nombre_limpio', 'existencia_num', 'Stock', OUTPUT_DIR, generar_plantilla=generar_plantilla)
    vent_out_fecha, vent_out_plant = guardar_xls(ventas, "Ventas Infinix", "Reporte Ventas Infinix", 'descripcion_limpio', 'cantidad_num', 'Total', OUTPUT_DIR, generar_plantilla=generar_plantilla)
    
    print("OK Inventario: {} modelos".format(len(stock)))
    print("OK Ventas: {} modelos".format(len(ventas)))
    print("OK Archivos Infinix guardados:")
    print("  - {} (fecha)".format(inv_out_fecha))
    if inv_out_plant:
        print("  - {} (plantilla)".format(inv_out_plant))
    print("  - {} (fecha)".format(vent_out_fecha))
    if vent_out_plant:
        print("  - {} (plantilla)".format(vent_out_plant))

def procesar_honor(generar_plantilla=True):
    print("\n" + "="*50)
    print("PROCESANDO HONOR")
    print("="*50)
    
    DIR_BASE = r"C:\Users\segur\OneDrive\Desktop\reportes marcas"
    DIR_SALIDA = os.path.join(DIR_BASE, "Reporte HONOR")
    os.makedirs(DIR_SALIDA, exist_ok=True)
    
    honor_path = os.path.join(DIR_BASE, "honor.xls")
    deli_path = os.path.join(DIR_BASE, "ventas honor delivery.xls")
    
    if not os.path.exists(honor_path):
        print("ERROR: No se encuentra honor.xls")
        return
    
    # Leer Ventas HONOR
    xls = pd.ExcelFile(honor_path)
    vent_df = xls.parse(xls.sheet_names[0])
    
    cod_col = detectar_columna(vent_df, ["CODIGO", "COD"])
    mar_col = detectar_columna(vent_df, ["MARCA"])
    desc_col = detectar_columna(vent_df, ["DESCRIPCION", "NOMBRE"])
    cant_col = detectar_columna(vent_df, ["CANTIDAD"])
    dep_col = detectar_columna(vent_df, ["DEP", "DEPOSITO"])
    
    if not all([cod_col, mar_col, cant_col]):
        print("ERROR: Columnas de ventas no encontradas en honor.xls")
        return
    
    cols_needed = [cod_col, mar_col, desc_col, cant_col]
    if dep_col:
        cols_needed.append(dep_col)
    vent_df = vent_df[cols_needed]
    vent_df.columns = ["codigo", "marca", "descripcion", "cantidad", "deposito"][:len(cols_needed)]
    
    vent_df["marca"] = vent_df["marca"].astype(str).str.upper().str.strip()
    vent_df = vent_df[vent_df["marca"] == "HONOR"]
    vent_df = vent_df.dropna(subset=["descripcion"])
    
    if "deposito" in vent_df.columns:
        vent_df = vent_df[vent_df["deposito"].astype(str).str.upper().str.strip() != "DEP PRI D003"]
    
    vent_df["descripcion_limpio"] = vent_df["descripcion"].apply(lambda x: limpiar_nombre(x, "honor"))
    vent_df["cantidad_num"] = vent_df["cantidad"].apply(parse_numero)
    
    # Combinar con Delivery
    if os.path.exists(deli_path):
        xls = pd.ExcelFile(deli_path)
        deli_df = xls.parse(xls.sheet_names[0])
        
        cod_col = detectar_columna(deli_df, ["CODIGO", "COD"])
        desc_col = detectar_columna(deli_df, ["DESCRIPCION", "NOMBRE"])
        cant_col = detectar_columna(deli_df, ["CANTIDAD"])
        
        if all([cod_col, desc_col, cant_col]):
            deli_df = deli_df[[cod_col, desc_col, cant_col]]
            deli_df.columns = ["codigo", "descripcion", "cantidad"]
            deli_df = deli_df.dropna(subset=["descripcion"])
            deli_df["descripcion_limpio"] = deli_df["descripcion"].apply(lambda x: limpiar_nombre(x, "honor"))
            deli_df["cantidad_num"] = deli_df["cantidad"].apply(parse_numero)
            vent_df = pd.concat([vent_df, deli_df], ignore_index=True)
    
    ventas = vent_df.groupby("descripcion_limpio", as_index=False)["cantidad_num"].sum()
    ventas = ventas.sort_values("cantidad_num", ascending=False)
    
    # Guardar .xls
    vent_out_fecha, vent_out_plant = guardar_xls(ventas, "Ventas HONOR", "Reporte Ventas HONOR", 'descripcion_limpio', 'cantidad_num', 'Total', DIR_SALIDA, generar_plantilla=generar_plantilla)
    
    print("OK Ventas: {} modelos".format(len(ventas)))
    print("OK Archivos HONOR guardados:")
    print("  - {} (fecha)".format(vent_out_fecha))
    if vent_out_plant:
        print("  - {} (plantilla)".format(vent_out_plant))

def main():
    parser = argparse.ArgumentParser(description='Generar reportes de marca')
    parser.add_argument('--marca', choices=['samsung', 'infinix', 'honor'], help='Marca a procesar (por defecto: todas)')
    parser.add_argument('--dir', help='Directorio donde buscar los archivos fuente (por defecto: misma carpeta del script)')
    parser.add_argument('--ventas-only', action='store_true', help='Solo procesar ventas (saltar inventario)')
    parser.add_argument('--no-template', action='store_true', help='No generar archivos plantilla (solo historico fechado)')
    args = parser.parse_args()
    
    global BASE_DIR, OUTPUT_DIR
    if args.dir:
        BASE_DIR = os.path.abspath(args.dir)
        OUTPUT_DIR = BASE_DIR
    
    generar_plantilla = not args.no_template
    
    subprocess.run(["taskkill", "/F", "/IM", "EXCEL.EXE"], capture_output=True)
    time.sleep(2)
    
    if args.marca == 'samsung' or args.marca is None:
        procesar_samsung(ventas_only=args.ventas_only, generar_plantilla=generar_plantilla)
    
    if args.marca == 'infinix' or args.marca is None:
        procesar_infinix(generar_plantilla=generar_plantilla)
    
    if args.marca == 'honor' or args.marca is None:
        procesar_honor(generar_plantilla=generar_plantilla)
    
    print("\n" + "="*50)
    print("PROCESO COMPLETADO")
    print("="*50)

if __name__ == "__main__":
    main()
