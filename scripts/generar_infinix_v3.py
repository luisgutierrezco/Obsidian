#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script agrupacion OPTIMA para Infinix - Extrae la base del modelo automaticamente
sin dependencia de listas de colores
"""

import pandas as pd
import os
import re
import time
import subprocess
import xlwt
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = BASE_DIR

# Patrones que indican el FINAL del modelo (colores o especificaciones)
# Estos son los comunes en Infinix
PATRONES_FIN_MODELO = [
    r'\s+(SUNLIKE|IRIS|MEADOW|CLOUDLINE|MIST|TWILIGHT|NIGHT|POLARIS|SHADOW|SOUL|ENCHANTED|NEBULA|AURORA)\s+(ORANGE|GREEN|BLUE|GOLD|PURPLE|TITANIUM|SILVER|BLACK)',  # combinaciones
    r'\s+(TITANIUM|MIST|SHADOW|SLEEK|DEEP|STARLIGHT|MOONLIGHT|SUNSET|DAWN|DUSK|STEALTH|CHROME)\s+(SILVER|BLACK|BLUE|GREEN|TITANIUM|GREY|CYAN)',  # mas combinaciones
    r'\s+(POLARIS|SUNLIKE|IRIS|MEADOW|CLOUDLINE)\s+(RED|ORANGE|GOLD)',  # colores con prefijos
]

# Lista simple de palabras que indican inicio de COLOR/ESPECIFICACION al final
PALABRAS_FIN = [
    "SUNLIKE", "IRIS", "MEADOW", "CLOUDLINE", "MIST", "TWILIGHT", "NIGHT", "NIGHTFALL",
    "POLARIS", "SHADOW", "SLEEK", "DEEP", "STARLIGHT", "MOONLIGHT", "SUNSET", "DAWN", "DUSK",
    "STEALTH", "CHROME", "OCEAN", "STARRY", "FOREST", "SAPPHIRE", "ENCHANTED", "SOUL",
    "AMETHYST", "BURGUNDY", "GLACI", "AZURE", "ONYX", "PEARL", "CREAM", "BRONZE",
    "COPPER", "PLATINUM", "SAGE", "SAND", "PEACH", "LIME", "CORAL", "MARINE",
    "NAVY", "SKY", "CYAN", "FIZZ", "MIDNIGHT", "SOLAR", "TITANIUM", "TITANIUM GREY",
    "DUAL SIM", "ROSE GOLD", "SUNLIKE ORANGE", "MEADOW GREEN", "CLOUDLINE BLUE",
    "MIST TITANIUM", "SHADOW BLACK", "SLEEK BLACK", "DEEP OCEAN BLUE", "TWILIGHT GOLD"
]

def normalizar_texto(texto):
    if pd.isna(texto):
        return ""
    return str(texto).upper().strip()

def extraer_base_modelo(nombre):
    """
    Extrae la base del modelo.
    Elimina todo lo que venga DESPUES de GB (memoria).
    """
    if pd.isna(nombre):
        return ""
    
    n = normalizar_texto(nombre)
    
    # Eliminar codigos de tienda como (1049/1037), (1250), etc al final
    n = re.sub(r'\s*\(\d+/\d+\)\s*$', '', n)
    n = re.sub(r'\s*\(\d+\)\s*$', '', n)
    
    n = n.strip()
    if not n:
        return ""
    
    # Buscar donde esta GB - todo despues de GB es color
    idx = n.find("GB")
    if idx != -1:
        # Encontramos GB, devolver todo hasta GB + 2 (para incluir GB)
        base = n[:idx+2]
        return base.strip()
    
    # Si no tiene GB, eliminar los ultimos 2 terminos (colores)
    partes = n.split()
    if len(partes) >= 3:
        return normalizar_texto(" ".join(partes[:-2]))
    
    return n

def parse_numero(valor):
    if pd.isna(valor):
        return 0
    s = str(valor).strip().replace(".", "").replace(",", ".")
    try:
        return float(s)
    except:
        return 0

def detectar_columna(df, palabras_clave):
    for col in df.columns:
        col_norm = normalizar_texto(col)
        for kw in palabras_clave:
            if kw in col_norm:
                return col
    return None

def main():
    print("\n" + "="*50)
    print("PROCESANDO INFINIX (AGRUPACION OPTIMA v2)")
    print("="*50)
    
    subprocess.run(["taskkill", "/F", "/IM", "EXCEL.EXE"], capture_output=True)
    time.sleep(2)
    
    inv_path = os.path.join(BASE_DIR, "Inventario Infinix.xls")
    vent_path = os.path.join(BASE_DIR, "Ventas Infinix.xls")
    deli_path = os.path.join(BASE_DIR, "VENTAS DELIVERY.xls")
    
    if not os.path.exists(inv_path) or not os.path.exists(vent_path):
        print("ERROR: Archivos no encontrados")
        return
    
    # INVENTARIO
    print("\n--- INVENTARIO ---")
    inv_df = pd.read_excel(inv_path)
    
    nom_col = detectar_columna(inv_df, ["NOMBRE", "DESC", "DESCRIPCION"])
    dep_col = detectar_columna(inv_df, ["DEPARTAMENTO", "DEPT"])
    exi_col = detectar_columna(inv_df, ["EXISTENCIA", "STOCK"])
    
    print(f"Columnas: Nombre={nom_col}, Depto={dep_col}, Existencia={exi_col}")
    
    if dep_col and dep_col in inv_df.columns:
        inv_df = inv_df[inv_df[dep_col].astype(str).str.upper().str.strip() == "TELEFONO"]
    
    inv_df = inv_df.dropna(subset=[nom_col, exi_col])
    
    # Extraer base del modelo
    inv_df["modelo_base"] = inv_df[nom_col].apply(extraer_base_modelo)
    inv_df["modelo_original"] = inv_df[nom_col]
    inv_df["existencia_num"] = inv_df[exi_col].apply(parse_numero)
    inv_df = inv_df[inv_df["modelo_base"].str.contains("INFINIX", na=False)]
    
    # Agrupar
    stock = inv_df.groupby("modelo_base", as_index=False)["existencia_num"].sum()
    stock = stock.sort_values("existencia_num", ascending=False)
    
    print(f"Inventario: {len(stock)} modelos base")
    print("\nTop 3:")
    print(stock.head(3).to_string(index=False))
    
    # VENTAS
    print("\n--- VENTAS ---")
    vent_df = pd.read_excel(vent_path)
    
    mar_col = detectar_columna(vent_df, ["MARCA"])
    desc_col = detectar_columna(vent_df, ["DESC", "DESCRIPCION", "NOMBRE"])
    cant_col = detectar_columna(vent_df, ["CANTIDAD"])
    dep_col_v = detectar_columna(vent_df, ["DEPOSITO", "DEP"])
    
    print(f"Columnas: Marca={mar_col}, Desc={desc_col}, Cant={cant_col}")
    
    vent_df["marca_clean"] = vent_df[mar_col].astype(str).str.upper().str.strip()
    vent_df = vent_df[vent_df["marca_clean"] == "INFINIX"]
    
    if dep_col_v and dep_col_v in vent_df.columns:
        vent_df = vent_df[vent_df[dep_col_v].astype(str).str.upper().str.strip() != "DEP PRI D003"]
    
    vent_df = vent_df.dropna(subset=[desc_col, cant_col])
    
    # Extraer base
    vent_df["modelo_base"] = vent_df[desc_col].apply(extraer_base_modelo)
    vent_df["modelo_original"] = vent_df[desc_col]
    vent_df["cantidad_num"] = vent_df[cant_col].apply(parse_numero)
    
    ventas_combined = vent_df[["modelo_base", "modelo_original", "cantidad_num"]].copy()
    
    # Combinar con DELIVERY
    if os.path.exists(deli_path):
        deli_df = pd.read_excel(deli_path)
        d_desc = detectar_columna(deli_df, ["DESC", "DESCRIPCION", "NOMBRE"])
        d_cant = detectar_columna(deli_df, ["CANTIDAD"])
        
        if d_desc and d_cant:
            deli_df = deli_df[deli_df[d_desc].astype(str).str.upper().str.contains("INFINIX", na=False)]
            deli_df = deli_df.dropna(subset=[d_desc, d_cant])
            deli_df["modelo_base"] = deli_df[d_desc].apply(extraer_base_modelo)
            deli_df["modelo_original"] = deli_df[d_desc]
            deli_df["cantidad_num"] = deli_df[d_cant].apply(parse_numero)
            ventas_combined = pd.concat([ventas_combined, deli_df[["modelo_base", "modelo_original", "cantidad_num"]]], ignore_index=True)
    
    ventas = ventas_combined.groupby("modelo_base", as_index=False)["cantidad_num"].sum()
    ventas = ventas.sort_values("cantidad_num", ascending=False)
    
    print(f"Ventas: {len(ventas)} modelos base")
    print("\nTop 3:")
    print(ventas.head(3).to_string(index=False))
    
    # GUARDAR
    fecha = datetime.now().strftime("%d-%m-%Y")
    
    # Inventario
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Inventario')
    ws.col(0).width = 50 * 256
    ws.col(1).width = 12 * 256
    ws.write(0, 0, 'Modelo')
    ws.write(0, 1, 'Stock')
    for i, (_, row) in enumerate(stock.iterrows(), start=1):
        ws.write(i, 0, row['modelo_base'])
        ws.write(i, 1, row['existencia_num'])
    inv_out = os.path.join(OUTPUT_DIR, f"Inventario Infinix {fecha}.xls")
    wb.save(inv_out)
    
    # Ventas
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Ventas')
    ws.col(0).width = 50 * 256
    ws.col(1).width = 12 * 256
    ws.write(0, 0, 'Modelo')
    ws.write(0, 1, 'Total')
    for i, (_, row) in enumerate(ventas.iterrows(), start=1):
        ws.write(i, 0, row['modelo_base'])
        ws.write(i, 1, int(row['cantidad_num']))
    vent_out = os.path.join(OUTPUT_DIR, f"Ventas Infinix {fecha}.xls")
    wb.save(vent_out)
    
    print("\n" + "="*50)
    print("PROCESO COMPLETADO")
    print("="*50)
    print(f"Archivos:")
    print(f"  - {inv_out}")
    print(f"  - {vent_out}")

if __name__ == "__main__":
    main()