#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Genera reporte limpio de Ventas al Mayor
Busca primero Plantilla Ventas Mayor.xls, luego ventas al mayor.xls
"""

import pandas as pd
import os
import re
import shutil
import xlwt
import unicodedata
from datetime import datetime

BASE_DIR = r"C:\Users\segur\OneDrive\Desktop\reportes marcas\Reporte Infinix"
OUTPUT_DIR = BASE_DIR

SOURCE_CANDIDATES = ["Plantilla Ventas Mayor.xls", "ventas al mayor.xls"]

def normalizar_texto(t):
    return ''.join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').upper()

def detectar_col(df, palabras):
    for col in df.columns:
        for kw in palabras:
            if kw in normalizar_texto(col):
                return col
    return None

def extraer_base_modelo(desc):
    if pd.isna(desc):
        return ""
    d = str(desc).upper().strip()
    d = d.replace("GREENTEXTURA", "TEXTURA").replace("GREEN TEXTURA", "TEXTURA").replace("NIGTH", "NIGHT")
    m = re.search(r'\b\d+/\d+GB\b', d)
    if m:
        return d[:m.end()].strip()
    m = re.search(r'\b(\d+/\d+)\b', d)
    if m:
        base = d[:m.end()].strip()
        if not base.endswith("GB"):
            base += "GB"
        return base
    return d.strip()

def parse_numero(valor):
    if pd.isna(valor):
        return 0
    s = str(valor).strip().replace(".", "").replace(",", ".")
    try:
        return float(s)
    except:
        return 0

def main():
    print("="*50)
    print("VENTAS AL MAYOR - REPORTE LIMPIO")
    print("="*50)
    
    # Buscar archivo fuente
    archivo = None
    for fname in SOURCE_CANDIDATES:
        full = os.path.join(BASE_DIR, fname)
        if os.path.exists(full):
            try:
                test_df = pd.read_excel(full)
                d = detectar_col(test_df, ["DESCRIPCION", "NOMBRE"])
                c = detectar_col(test_df, ["CANTIDAD", "CANT"])
                if d and c and len(test_df) > 0:
                    archivo = full
                    break
            except:
                continue
    
    if not archivo:
        print("ERROR: No se encontró archivo de Ventas al Mayor")
        return
    
    print("Fuente:", os.path.basename(archivo))
    
    df = pd.read_excel(archivo)
    desc_col = detectar_col(df, ["DESCRIPCION", "NOMBRE"])
    cant_col = detectar_col(df, ["CANTIDAD", "CANT"])
    
    print("Filas:", len(df), "| Desc:", desc_col, "| Cant:", cant_col)
    
    if not desc_col or not cant_col:
        print("ERROR: Columnas no encontradas")
        return
    
    # Eliminar fila total (NaN en descripcion)
    df = df.dropna(subset=[desc_col])
    print("Registros sin total:", len(df))
    
    # Extraer modelo base
    df["modelo_base"] = df[desc_col].apply(extraer_base_modelo)
    df["cantidad_num"] = df[cant_col].apply(parse_numero)
    
    # Agrupar y sumar
    resultado = df.groupby("modelo_base", as_index=False)["cantidad_num"].sum()
    resultado = resultado.sort_values("cantidad_num", ascending=False)
    
    print("\nModelos resultantes:", len(resultado))
    print(resultado.to_string(index=False))
    
    # Guardar
    fecha = datetime.now().strftime("%d-%m-%Y")
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('VentasMayor')
    ws.col(0).width = 50 * 256
    ws.col(1).width = 12 * 256
    ws.write(0, 0, 'Modelo')
    ws.write(0, 1, 'Total')
    for i, (_, row) in enumerate(resultado.iterrows(), start=1):
        ws.write(i, 0, row['modelo_base'])
        ws.write(i, 1, int(row['cantidad_num']))
    
    archivo_fecha = os.path.join(OUTPUT_DIR, "Ventas Mayor {}.xls".format(fecha))
    wb.save(archivo_fecha)
    archivo_plantilla = os.path.join(OUTPUT_DIR, "Reporte Ventas Mayor.xls")
    shutil.copy2(archivo_fecha, archivo_plantilla)
    
    print("\nArchivos guardados:")
    print("  -", archivo_fecha)
    print("  -", archivo_plantilla)
    print("="*50)

if __name__ == "__main__":
    main()
