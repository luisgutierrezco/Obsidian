import pandas as pd
import os

BASE = r"C:\Users\segur\OneDrive\Desktop\Reporte Samsung"
INV = os.path.join(BASE, "INV SAMSUNG.xls")
VENT = os.path.join(BASE, "VENTAS SAMSUNG.xls")

print("=== INVENTARIO ===")
xls = pd.ExcelFile(INV)
for sheet in xls.sheet_names:
    df = xls.parse(sheet, nrows=0)
    print(f"Hoja: {sheet}")
    print(f"Columnas: {list(df.columns)}")
    df2 = xls.parse(sheet, nrows=3)
    print(f"Primeras filas:")
    print(df2.head())
    print()

print("=== VENTAS ===")
xls2 = pd.ExcelFile(VENT)
for sheet in xls2.sheet_names:
    df = xls2.parse(sheet, nrows=0)
    print(f"Hoja: {sheet}")
    print(f"Columnas: {list(df.columns)}")
    df2 = xls2.parse(sheet, nrows=3)
    print(f"Primeras filas:")
    print(df2.head())
    print()
