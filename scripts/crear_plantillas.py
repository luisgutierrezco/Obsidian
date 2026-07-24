#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Genera plantillas en blanco (.xls) para exportar datos del sistema"""
import xlwt
import os

BASE = r"C:\Users\segur\OneDrive\Desktop\reportes marcas"

plantillas = [
    # (ruta, nombre_archivo, [columnas...])
    (os.path.join(BASE, "Reporte Samsung"), "Plantilla Inventario Samsung.xls",
     ["Código", "Nombre", "Departamento", "Unidad", "Costo Calculado", "Existencia", "Precio Máximo", "Moneda"]),
    (os.path.join(BASE, "Reporte Samsung"), "Plantilla Ventas Samsung.xls",
     ["Deposito", "Código", "Marca", "Descripción", "Cantidad", "Cant. Actual"]),
    (os.path.join(BASE, "Reporte Infinix"), "Plantilla Inventario Infinix.xls",
     ["Código", "Nombre", "Departamento", "Existencia"]),
    (os.path.join(BASE, "Reporte Infinix"), "Plantilla Ventas Infinix.xls",
     ["Deposito", "Código", "Marca", "Descripción", "Cantidad"]),
    (os.path.join(BASE, "Reporte Infinix"), "Plantilla Ventas Delivery.xls",
     ["Código", "Descripción", "Cantidad"]),
    (os.path.join(BASE, "Reporte Infinix"), "Plantilla Ventas Mayor.xls",
     ["Código", "Descripción", "Cantidad"]),
]

for ruta, nombre, columnas in plantillas:
    os.makedirs(ruta, exist_ok=True)
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Plantilla')
    for i, col in enumerate(columnas):
        ws.col(i).width = max(20 * 256, len(col) * 2 * 256)
        ws.write(0, i, col)
    archivo = os.path.join(ruta, nombre)
    wb.save(archivo)
    print(f"  OK: {archivo}")

print("\nTodas las plantillas creadas.")
