#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Genera reporte de ventas por tienda (mes abril) con cantidades y porcentajes
Excluye DEP PRI D003, limpia descripciones (corta despues de patron de memoria)
Formato: un solo .xls, una sola hoja, tiendas separadas por bloques
"""

import pandas as pd
import os
import re
import unicodedata
import xlwt
from datetime import datetime

BASE_DIR = r"C:\Users\segur\OneDrive\Desktop\reportes marcas\Reporte Infinix"
ORIGEN = os.path.join(BASE_DIR, "ventas por tienda mes abril.xls")

# Tiendas a EXCLUIR
EXCLUIR = {"DEP PRI D003"}

# Solo esta marca
FILTRO_MARCA = "INFINIX"

def normalizar_texto(t):
    return ''.join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').upper()

def extraer_base(desc):
    if pd.isna(desc):
        return ""
    d = str(desc).upper().strip()
    d = d.replace("GREENTEXTURA", "TEXTURA").replace("GREEN TEXTURA", "TEXTURA").replace("NIGTH", "NIGHT")
    d = re.sub(r'\s*\(MAYOR\)\s*', '', d)
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

def escribir_bloque(ws, row, tienda, datos, col_label, es_porcentaje):
    """Escribe bloque de una tienda, retorna siguiente fila disponible"""
    style_tienda = xlwt.easyxf('font: bold on; font: height 280;')
    style_header = xlwt.easyxf('font: bold on; borders: bottom thin;')
    style_total = xlwt.easyxf('font: bold on; borders: top thin;')
    style_entero = xlwt.easyxf(num_format_str='#,##0')
    style_pct = xlwt.easyxf(num_format_str='0.00')
    
    ws.write(row, 0, tienda, style_tienda)
    row += 1
    ws.write(row, 0, 'Modelo', style_header)
    ws.write(row, 1, col_label, style_header)
    row += 1
    
    total = 0
    for _, r in datos.iterrows():
        ws.write(row, 0, r['modelo'])
        if es_porcentaje:
            ws.write(row, 1, r['pct'], style_pct)
        else:
            ws.write(row, 1, int(r['cant']), style_entero)
            total += int(r['cant'])
        row += 1
    
    if es_porcentaje:
        ws.write(row, 0, 'Total', style_total)
        ws.write(row, 1, 100.00, style_pct)
    else:
        ws.write(row, 0, 'Total', style_total)
        ws.write(row, 1, total, style_entero)
    row += 2  # dejar fila en blanco
    return row

def main():
    print("="*50)
    print("VENTAS POR TIENDA - ABRIL 2026")
    print("="*50)
    
    if not os.path.exists(ORIGEN):
        print("ERROR: No se encuentra", ORIGEN)
        return
    
    df = pd.read_excel(ORIGEN)
    
    # Identificar columnas
    cols_norm = {c: normalizar_texto(c) for c in df.columns}
    dep_col = next(c for c in df.columns if 'DEPOSITO' in cols_norm[c] or 'DEP' in cols_norm[c])
    desc_col = next(c for c in df.columns if 'DESCRIPCION' in cols_norm[c] or 'NOMBRE' in cols_norm[c])
    cant_col = next(c for c in df.columns if 'CANTIDAD' in cols_norm[c] or 'CANT' in cols_norm[c])
    
    print("Columnas: Dep={}, Desc={}, Cant={}".format(dep_col, desc_col, cant_col))
    
    # Limpiar
    df = df.dropna(subset=[desc_col])
    df['tienda'] = df[dep_col].astype(str).str.strip()
    df['modelo'] = df[desc_col].apply(extraer_base)
    df['cant'] = pd.to_numeric(df[cant_col], errors='coerce').fillna(0)
    
    # Filtrar solo INFINIX
    mar_col = next((c for c in df.columns if 'MARCA' in normalizar_texto(c)), None)
    if mar_col:
        antes = len(df)
        df = df[df[mar_col].astype(str).str.upper().str.strip() == FILTRO_MARCA]
        print("Filtro {}: {} -> {} filas".format(FILTRO_MARCA, antes, len(df)))
    
    # Excluir tiendas
    tiendas_excluir = {normalizar_texto(t) for t in EXCLUIR}
    df = df[~df['tienda'].apply(lambda x: normalizar_texto(x) in tiendas_excluir)]
    
    # Agrupar por tienda + modelo
    grouped = df.groupby(['tienda', 'modelo'], as_index=False)['cant'].sum()
    
    # Obtener lista de tiendas ordenadas
    tiendas = sorted(grouped['tienda'].unique())
    print("Tiendas a procesar:", len(tiendas))
    
    # Generar ambos archivos
    for es_porcentaje, sufijo, col_label in [
        (False, "Cantidades", "Cant"),
        (True, "Porcentajes", "%"),
    ]:
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Ventas por Tienda')
        ws.col(0).width = 55 * 256
        ws.col(1).width = 14 * 256
        
        row = 0
        for tienda in tiendas:
            datos = grouped[grouped['tienda'] == tienda].sort_values('cant', ascending=False)
            if es_porcentaje:
                total_tienda = datos['cant'].sum()
                datos = datos.copy()
                datos['pct'] = (datos['cant'] / total_tienda * 100) if total_tienda > 0 else 0.0
            
            row = escribir_bloque(ws, row, tienda, datos, col_label, es_porcentaje)
        
        nombre = "Reporte Infinix Tiendas Abril {}.xls".format(sufijo)
        ruta = os.path.join(BASE_DIR, nombre)
        wb.save(ruta)
        print("OK:", nombre)
    
    print("="*50)

if __name__ == "__main__":
    main()
