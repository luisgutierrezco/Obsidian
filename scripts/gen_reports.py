import pandas as pd
import os
import re

BASE = r"C:\Users\segur\OneDrive\Desktop\Reporte Samsung"
INV = os.path.join(BASE, "INV SAMSUNG.xls")
VENT = os.path.join(BASE, "VENTAS SAMSUNG.xls")

# Colores Samsung a eliminar (según contexto)
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
    # Correcciones de errores comunes
    n = n.replace("SAMUSNG", "SAMSUNG")
    n = n.replace("TWLIGHT", "TWILIGHT")
    # Quitar colores
    for c in colors_samsung:
        n = n.replace(c, "")
    # Quitar código tienda: ( 123 )
    n = re.sub(r'\(\s*\d+\s*\)', '', n)
    # Quitar espacios dobles
    n = " ".join(n.split())
    # Corregir duplicados SAMSUNG SAMSUNG
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
print("Leyendo inventario...")
xls_inv = pd.ExcelFile(INV)
inv_df = xls_inv.parse(xls_inv.sheet_names[0])
print(f"Columnas inventario: {list(inv_df.columns)}")

# Mapear columnas (estructura real: Código, Nombre, Departamento, Existencia)
inv_df = inv_df.rename(columns={
    inv_df.columns[0]: 'codigo',
    inv_df.columns[1]: 'nombre',
    inv_df.columns[2]: 'departamento',
    inv_df.columns[3]: 'existencia'
})

# Limpiar inventario
inv_df['codigo'] = inv_df['codigo'].astype(str).str.upper().str.strip()
inv_df['nombre_limpio'] = inv_df['nombre'].apply(limpiar_nombre)
inv_df['existencia_num'] = inv_df['existencia'].apply(parse_numero)

# Filtrar solo SAMSUNG
inv_df = inv_df[inv_df['nombre_limpio'].str.contains('SAMSUNG', na=False)]
print(f"Productos Samsung en inventario: {len(inv_df)}")

# Agrupar stock por modelo limpio
stock = inv_df.groupby('nombre_limpio', as_index=False)['existencia_num'].sum()
stock = stock.sort_values('existencia_num', ascending=False)

print("\nTOP 3 STOCK SAMSUNG:")
for i, row in stock.head(3).iterrows():
    print(f"{i+1}. {row['nombre_limpio']} - {row['existencia_num']:.0f}")

print("\n" + "="*50 + "\n")

# Leer Ventas
print("Leyendo ventas...")
xls_vent = pd.ExcelFile(VENT)
vent_df = xls_vent.parse(xls_vent.sheet_names[0])
print(f"Columnas ventas: {list(vent_df.columns)}")

# Mapear columnas (estructura real: Deposito, Código, Marca, Descripción, Cantidad)
vent_df = vent_df.rename(columns={
    vent_df.columns[0]: 'deposito',
    vent_df.columns[1]: 'codigo',
    vent_df.columns[2]: 'marca',
    vent_df.columns[3]: 'descripcion',
    vent_df.columns[4]: 'cantidad'
})

# Limpiar ventas
vent_df['marca'] = vent_df['marca'].astype(str).str.upper().str.strip()
vent_df = vent_df[vent_df['marca'] == 'SAMSUNG']
vent_df['descripcion_limpio'] = vent_df['descripcion'].apply(limpiar_nombre)
vent_df['cantidad_num'] = vent_df['cantidad'].apply(parse_numero)

print(f"Ventas Samsung: {len(vent_df)}")

# Agrupar ventas por modelo
ventas = vent_df.groupby('descripcion_limpio', as_index=False)['cantidad_num'].sum()
ventas = ventas.sort_values('cantidad_num', ascending=False)

print("\nTOP 3 VENTAS SAMSUNG:")
for i, row in ventas.head(3).iterrows():
    print(f"{i+1}. {row['descripcion_limpio']} - {row['cantidad_num']:.0f}")
