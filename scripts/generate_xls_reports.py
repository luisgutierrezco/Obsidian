import pandas as pd
import os
import re
import time
import subprocess
from datetime import datetime

BASE = r"C:\Users\segur\OneDrive\Desktop\Reporte Samsung"
INV = os.path.join(BASE, "INV SAMSUNG.xls")
VENT = os.path.join(BASE, "VENTAS SAMSUNG.xls")

# Matar Excel antes de empezar
subprocess.run(["taskkill", "/F", "/IM", "EXCEL.EXE"], capture_output=True)
time.sleep(2)

# Fecha para nombres de archivo
fecha = datetime.now().strftime("%d-%m-%Y")
inv_out = os.path.join(BASE, f"Inventario Samsung {fecha}.xls")
vent_out = os.path.join(BASE, f"Ventas Samsung {fecha}.xls")

# Colores Samsung a eliminar
colors_samsung = [
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
]

def limpiar_nombre(nombre):
    if pd.isna(nombre):
        return ""
    n = str(nombre).upper().strip()
    n = n.replace("SAMUSNG", "SAMSUNG")
    n = n.replace("TWLIGHT", "TWILIGHT")
    for c in colors_samsung:
        n = n.replace(c, "")
    n = re.sub(r'\(\s*\d+\s*\)', '', n)
    n = " ".join(n.split())
    n = n.replace("SAMSUNG SAMSUNG", "SAMSUNG")
    return n.strip()

def parse_numero(valor):
    if pd.isna(valor):
        return 0
    s = str(valor).strip()
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except:
        return 0

# Leer Inventario
print("Procesando inventario...")
xls_inv = pd.ExcelFile(INV)
inv_df = xls_inv.parse(xls_inv.sheet_names[0])
inv_df = inv_df.rename(columns={
    inv_df.columns[0]: 'codigo',
    inv_df.columns[1]: 'nombre',
    inv_df.columns[2]: 'departamento',
    inv_df.columns[3]: 'existencia'
})

inv_df['nombre_limpio'] = inv_df['nombre'].apply(limpiar_nombre)
inv_df['existencia_num'] = inv_df['existencia'].apply(parse_numero)
inv_df = inv_df[inv_df['nombre_limpio'].str.contains('SAMSUNG', na=False)]

stock = inv_df.groupby('nombre_limpio', as_index=False)['existencia_num'].sum()
stock = stock.sort_values('existencia_num', ascending=False)

# Leer Ventas
print("Procesando ventas...")
xls_vent = pd.ExcelFile(VENT)
vent_df = xls_vent.parse(xls_vent.sheet_names[0])
vent_df = vent_df.rename(columns={
    vent_df.columns[0]: 'deposito',
    vent_df.columns[1]: 'codigo',
    vent_df.columns[2]: 'marca',
    vent_df.columns[3]: 'descripcion',
    vent_df.columns[4]: 'cantidad'
})

vent_df['marca'] = vent_df['marca'].astype(str).str.upper().str.strip()
vent_df = vent_df[vent_df['marca'] == 'SAMSUNG']
vent_df['descripcion_limpio'] = vent_df['descripcion'].apply(limpiar_nombre)
vent_df['cantidad_num'] = vent_df['cantidad'].apply(parse_numero)

ventas = vent_df.groupby('descripcion_limpio', as_index=False)['cantidad_num'].sum()
ventas = ventas.sort_values('cantidad_num', ascending=False)

# Generar archivos .xls con xlwt
import xlwt

# Inventario
print(f"Generando {inv_out}...")
wb_inv = xlwt.Workbook(encoding='utf-8')
ws_inv = wb_inv.add_sheet('Inventario')

# Configurar anchos de columna
ws_inv.col(0).width = 50 * 256  # Columna A (Modelo): 50
ws_inv.col(1).width = 12 * 256  # Columna B (Stock): 12

# Escribir datos
ws_inv.write(0, 0, 'Modelo')
ws_inv.write(0, 1, 'Stock')

for i, (_, row) in enumerate(stock.iterrows(), start=1):
    ws_inv.write(i, 0, row['nombre_limpio'])
    ws_inv.write(i, 1, row['existencia_num'])

wb_inv.save(inv_out)
print(f"Guardado: {inv_out}")

# Ventas
print(f"Generando {vent_out}...")
wb_vent = xlwt.Workbook(encoding='utf-8')
ws_vent = wb_vent.add_sheet('Ventas')

# Configurar anchos de columna
ws_vent.col(0).width = 50 * 256  # Columna A (Modelo): 50
ws_vent.col(1).width = 12 * 256  # Columna B (Total): 12

# Escribir datos
ws_vent.write(0, 0, 'Modelo')
ws_vent.write(0, 1, 'Total')

for i, (_, row) in enumerate(ventas.iterrows(), start=1):
    ws_vent.write(i, 0, row['descripcion_limpio'])
    ws_vent.write(i, 1, row['cantidad_num'])

wb_vent.save(vent_out)
print(f"Guardado: {vent_out}")

print("\nReportes completados:")
print(f"- {inv_out}")
print(f"- {vent_out}")
print(f"\nInventario: {len(stock)} modelos")
print(f"Ventas: {len(ventas)} modelos")
