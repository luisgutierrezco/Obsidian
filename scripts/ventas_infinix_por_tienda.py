#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reporte de Ventas Infinix por Tienda
Fuente: Plantilla Ventas Infinix.xls
Excluye: DEP PRI D003 (no incluye Delivery ni Ventas Mayor)
Filtro: solo Marca = INFINIX
Salida: un solo .xls con todas las tiendas en una hoja
"""

import pandas as pd
import os
import re
import unicodedata
import xlwt
from datetime import datetime

BASE_DIR = r"C:\Users\segur\OneDrive\Desktop\reportes marcas\Reporte Infinix"
ORIGEN = os.path.join(BASE_DIR, "Plantilla Ventas Infinix.xls")
EXCLUIR_DEP = {"DEP PRI D003"}
FILTRO_MARCA = "INFINIX"

def normalizar_texto(t):
    return ''.join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').upper()

def extraer_base(desc):
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

def main():
    print("="*50)
    print("VENTAS INFINIX POR TIENDA")
    print("="*50)
    
    if not os.path.exists(ORIGEN):
        print("ERROR: No se encuentra", ORIGEN)
        return
    
    df = pd.read_excel(ORIGEN)
    print("Filas total:", len(df))
    
    cols_norm = {c: normalizar_texto(c) for c in df.columns}
    dep_col = next(c for c in df.columns if 'DEPOSITO' in cols_norm[c] or 'DEP' in cols_norm[c])
    desc_col = next(c for c in df.columns if 'DESCRIPCION' in cols_norm[c] or 'NOMBRE' in cols_norm[c])
    cant_col = next(c for c in df.columns if 'CANTIDAD' in cols_norm[c] or 'CANT' in cols_norm[c])
    mar_col = next(c for c in df.columns if 'MARCA' in cols_norm[c])
    
    df = df.dropna(subset=[desc_col])
    df['tienda'] = df[dep_col].astype(str).str.strip()
    df['marca'] = df[mar_col].astype(str).str.upper().str.strip()
    df['modelo'] = df[desc_col].apply(extraer_base)
    df['cant'] = pd.to_numeric(df[cant_col], errors='coerce').fillna(0)
    
    # Filtrar solo INFINIX
    antes = len(df)
    df = df[df['marca'] == FILTRO_MARCA]
    print("Filtro INFINIX:", antes, "->", len(df))
    
    # Excluir DEP PRI D003
    dep_excluir = {normalizar_texto(t) for t in EXCLUIR_DEP}
    df = df[~df['tienda'].apply(lambda x: normalizar_texto(x) in dep_excluir)]
    print("Excluyendo dep003 ->", len(df))
    
    # Agrupar por tienda + modelo
    grouped = df.groupby(['tienda', 'modelo'], as_index=False)['cant'].sum()
    tiendas = sorted(grouped['tienda'].unique())
    print("Tiendas:", len(tiendas))
    
    # Generar .xls
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Ventas Infinix por Tienda')
    ws.col(0).width = 55 * 256
    ws.col(1).width = 14 * 256
    
    style_tienda = xlwt.easyxf('font: bold on; font: height 280;')
    style_header = xlwt.easyxf('font: bold on; borders: bottom thin;')
    style_total = xlwt.easyxf('font: bold on; borders: top thin;')
    style_entero = xlwt.easyxf(num_format_str='#,##0')
    
    row = 0
    for tienda in tiendas:
        datos = grouped[grouped['tienda'] == tienda].sort_values('cant', ascending=False)
        
        ws.write(row, 0, tienda, style_tienda)
        row += 1
        ws.write(row, 0, 'Modelo', style_header)
        ws.write(row, 1, 'Cant', style_header)
        row += 1
        
        total = 0
        for _, r in datos.iterrows():
            ws.write(row, 0, r['modelo'])
            ws.write(row, 1, int(r['cant']), style_entero)
            total += int(r['cant'])
            row += 1
        
        ws.write(row, 0, 'Total', style_total)
        ws.write(row, 1, total, style_entero)
        row += 2
    
    fecha = datetime.now().strftime("%d-%m-%Y")
    nombre = "Reporte Infinix Ventas por Tienda {}.xls".format(fecha)
    ruta = os.path.join(BASE_DIR, nombre)
    wb.save(ruta)
    print("\nOK:", nombre)
    print("="*50)

if __name__ == "__main__":
    main()
