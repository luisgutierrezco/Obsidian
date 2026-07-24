import pandas as pd
import os
import re
import xlwt
from datetime import datetime

BASE_DIR = r"C:\Users\segur\OneDrive\Desktop\reportes marcas\Reporte Infinix"
OUTPUT_DIR = BASE_DIR

def normalizar_texto(texto):
    if pd.isna(texto):
        return ""
    return str(texto).upper().strip()

def extraer_base_descripcion(desc):
    """
    Extrae la base de la descripción hasta el GB.
    Ej: "TELEFONO INFINIX HOT 60 PRO 8/256GB SLEEK BLACK (1049)" 
    -> "TELEFONO INFINIX HOT 60 PRO 8/256GB"
    """
    if pd.isna(desc):
        return ""
    d = normalizar_texto(desc)
    # Eliminar códigos de tienda como (1049/1037), (1250), etc al final
    d = re.sub(r'\s*\(\d+/\d+\)\s*$', '', d)
    d = re.sub(r'\s*\(\d+\)\s*$', '', d)
    d = d.strip()
    # Buscar donde termina GB
    idx = d.find("GB")
    if idx != -1:
        # Devolver hasta el final de GB (incluyendo GB)
        return d[:idx+2].strip()
    # Si no tiene GB, devolver tal cual
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
    print("Procesando VENTAS HOT 60 PRO Y 60 PRO PLUS.xls")
    file_path = os.path.join(BASE_DIR, "VENTAS HOT 60 PRO Y 60 PRO PLUS.xls")
    if not os.path.exists(file_path):
        print("ERROR: Archivo no encontrado")
        return
    df = pd.read_excel(file_path)
    print(f"Filas leídas: {len(df)}")
    print("Columnas:", df.columns.tolist())
    
    # Encontrar la columna de descripción (por posición o nombre aproximado)
    desc_col = None
    cant_col = None
    for col in df.columns:
        col_up = str(col).upper()
        if 'DESC' in col_up:
            desc_col = col
        if 'CANTIDAD' in col_up or 'CANT.' in col_up:
            cant_col = col
    
    if desc_col is None or cant_col is None:
        print("ERROR: No se encontraron columnas necesarias")
        print("Columnas disponibles:", df.columns.tolist())
        return
    
    print(f"Usando columnas: Descripción={desc_col}, Cantidad={cant_col}")
    
    # Filtrar solo las dos variantes requeridas
    mask = df[desc_col].str.contains('HOT 60 PRO 8/256GB', na=False) | \
           df[desc_col].str.contains('HOT 60 PRO PLUS 8/256GB', na=False)
    df_filtrado = df[[desc_col, cant_col]].copy()
    df_filtrado.columns = ['Descripcion', 'Cantidad']
    df_filtrado = df_filtrado[mask].copy()
    print(f"Filas después de filtrar: {len(df_filtrado)}")
    
    if len(df_filtrado) == 0:
        print("No se encontraron las variantes requeridas")
        return
    
    # Extraer base descripción
    df_filtrado['descripcion_base'] = df_filtrado['Descripcion'].apply(extraer_base_descripcion)
    
    # Agrupar por base descripción
    agrupado = df_filtrado.groupby('descripcion_base', as_index=False)['Cantidad'].sum()
    agrupado = agrupado.sort_values('Cantidad', ascending=False)
    
    print("Resultados agrupados:")
    print(agrupado.to_string(index=False))
    
    # Guardar como .xls
    fecha = datetime.now().strftime("%d-%m-%Y")
    output_file = os.path.join(OUTPUT_DIR, f"HOT_60_PRO_RESUMEN_{fecha}.xls")
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Resumen')
    ws.col(0).width = 50 * 256
    ws.col(1).width = 12 * 256
    ws.write(0, 0, 'Modelo')
    ws.write(0, 1, 'Total')
    for i, (_, row) in enumerate(agrupado.iterrows(), start=1):
        ws.write(i, 0, row['descripcion_base'])
        ws.write(i, 1, int(row['Cantidad']))
    wb.save(output_file)
    
    print(f"\nArchivo guardado: {output_file}")
    print("Filas totales:", len(agrupado))

if __name__ == "__main__":
    main()