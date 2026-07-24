#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script simple: solo Ventas Infinix.xls, sin excluir dep003 ni combinar delivery
"""

import pandas as pd
import os
import re
import shutil
import xlwt
from datetime import datetime
import unicodedata

BASE_DIR = r"C:\Users\segur\OneDrive\Desktop\reportes marcas\Reporte Infinix"
OUTPUT_DIR = BASE_DIR

def normalizar_texto(texto):
    if pd.isna(texto):
        return ""
    t = str(texto).upper().strip()
    return unicodedata.normalize('NFKD', t).encode('ASCII', 'ignore').decode('ASCII')

def extraer_base(desc):
    if pd.isna(desc):
        return ""
    d = normalizar_texto(desc)
    d = re.sub(r'\s*\(\d+/\d+\)\s*$', '', d)
    d = re.sub(r'\s*\(\d+\)\s*$', '', d)
    idx = d.find("GB")
    if idx != -1:
        return d[:idx+2].strip()
    return d.strip()

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
    print("VENTAS INFINIX - SIMPLE")
    print("="*50)
    
    archivo = os.path.join(BASE_DIR, "Ventas Infinix.xls")
    if not os.path.exists(archivo):
        print("ERROR: No se encuentra Ventas Infinix.xls")
        return
    
    df = pd.read_excel(archivo)
    print(f"Registros leidos: {len(df)}")
    
    mar_col = detectar_columna(df, ["MARCA"])
    desc_col = detectar_columna(df, ["DESCRIPCION", "DESC", "NOMBRE"])
    cant_col = detectar_columna(df, ["CANTIDAD"])
    
    print(f"Columnas: Marca={mar_col}, Desc={desc_col}, Cant={cant_col}")
    
    if not all([mar_col, desc_col, cant_col]):
        print("ERROR: Columnas requeridas no encontradas")
        return
    
    df["marca_clean"] = df[mar_col].astype(str).str.upper().str.strip()
    df = df[df["marca_clean"] == "INFINIX"]
    print(f"Filtrado INFINIX: {len(df)} registros")
    
    df["modelo_base"] = df[desc_col].apply(extraer_base)
    df["cantidad_num"] = df[cant_col].apply(parse_numero)
    
    resultado = df.groupby("modelo_base", as_index=False)["cantidad_num"].sum()
    resultado = resultado.sort_values("cantidad_num", ascending=False)
    
    print(f"\nModelos resultantes: {len(resultado)}")
    print("\nTop 3:")
    print(resultado.head(3).to_string(index=False))
    
    fecha = datetime.now().strftime("%d-%m-%Y")
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Ventas')
    ws.col(0).width = 50 * 256
    ws.col(1).width = 12 * 256
    ws.write(0, 0, 'Modelo')
    ws.write(0, 1, 'Total')
    for i, (_, row) in enumerate(resultado.iterrows(), start=1):
        ws.write(i, 0, row['modelo_base'])
        ws.write(i, 1, int(row['cantidad_num']))
    
    archivo_fecha = os.path.join(OUTPUT_DIR, f"Ventas Infinix Simple {fecha}.xls")
    wb.save(archivo_fecha)
    
    archivo_plantilla = os.path.join(OUTPUT_DIR, "Reporte Ventas Infinix Simple.xls")
    shutil.copy2(archivo_fecha, archivo_plantilla)
    
    print(f"\nArchivos guardados:")
    print(f"  - {archivo_fecha} (fecha)")
    print(f"  - {archivo_plantilla} (plantilla)")
    print("="*50)

if __name__ == "__main__":
    main()