import pandas as pd
import re
import xlwt
from datetime import datetime

# Leer archivos
sistema1 = pd.read_excel('PRECIOS DEL SISTEMA.xls')
sistema2 = pd.read_excel('PRECIOS DEL SISTEMA 2.xls')
nuevos = pd.read_excel('PRECIOS NUEVOS.xlsx')

# Limpiar modelo de PRECIOS NUEVOS
def limpiar_modelo(modelo):
    if pd.isna(modelo):
        return ''
    m = str(modelo).upper()
    m = re.sub(r'\(.*\)', '', m).strip()
    return m

nuevos['MODELO_BUSCAR'] = nuevos['MODELO'].apply(limpiar_modelo)

# Función para encontrar coincidencias
def encontrar_matches(sistema_df, nuevos_df):
    matches = []
    for _, row_nuevo in nuevos_df.iterrows():
        modelo_buscar = row_nuevo['MODELO_BUSCAR']
        for _, row_sis in sistema_df.iterrows():
            nombre_sis = str(row_sis['Nombre']).upper()
            if modelo_buscar in nombre_sis:
                diferencia = row_nuevo['PRECIO'] - row_sis['Costo']
                matches.append({
                    'Codigo': row_sis['Código'],
                    'Nombre_Sistema': row_sis['Nombre'],
                    'Modelo_Nuevo': row_nuevo['MODELO'],
                    'Costo_Sistema': round(row_sis['Costo'], 2),
                    'Precio_Nuevo': round(row_nuevo['PRECIO'], 2),
                    'Diferencia': round(diferencia, 2)
                })
                break
    df_matches = pd.DataFrame(matches)
    if not df_matches.empty:
        df_matches = df_matches.drop_duplicates(subset=['Codigo'])
    return df_matches

# Obtener matches de ambos sistemas
matches_s1 = encontrar_matches(sistema1, nuevos)
matches_s2 = encontrar_matches(sistema2, nuevos)

# Crear archivo XLS
wb = xlwt.Workbook(encoding='utf-8')
fecha = datetime.now().strftime("%d-%m-%Y")
output_path = "Comparacion Precios {}.xls".format(fecha)

# Estilo para encabezados
header_style = xlwt.easyxf('font: bold on;')

# Hoja para Sistema 1 (PRECIOS DEL SISTEMA.xls)
if not matches_s1.empty:
    ws1 = wb.add_sheet('Matches Sistema 1')
    headers = ['Codigo', 'Nombre_Sistema', 'Modelo_Nuevo', 'Costo_Sistema', 'Precio_Nuevo', 'Diferencia']
    for col, header in enumerate(headers):
        ws1.write(0, col, header, header_style)
        # Anchos de columna
        if col == 0:
            ws1.col(col).width = 15 * 256
        elif col == 1:
            ws1.col(col).width = 50 * 256
        elif col == 2:
            ws1.col(col).width = 20 * 256
        else:
            ws1.col(col).width = 12 * 256
    # Escribir datos
    for row_idx, (_, row) in enumerate(matches_s1.iterrows(), start=1):
        ws1.write(row_idx, 0, row['Codigo'])
        ws1.write(row_idx, 1, row['Nombre_Sistema'])
        ws1.write(row_idx, 2, row['Modelo_Nuevo'])
        ws1.write(row_idx, 3, row['Costo_Sistema'])
        ws1.write(row_idx, 4, row['Precio_Nuevo'])
        ws1.write(row_idx, 5, row['Diferencia'])

# Hoja para Sistema 2 (PRECIOS DEL SISTEMA 2.xls)
if not matches_s2.empty:
    ws2 = wb.add_sheet('Matches Sistema 2')
    headers = ['Codigo', 'Nombre_Sistema', 'Modelo_Nuevo', 'Costo_Sistema', 'Precio_Nuevo', 'Diferencia']
    for col, header in enumerate(headers):
        ws2.write(0, col, header, header_style)
        if col == 0:
            ws2.col(col).width = 15 * 256
        elif col == 1:
            ws2.col(col).width = 50 * 256
        elif col == 2:
            ws2.col(col).width = 20 * 256
        else:
            ws2.col(col).width = 12 * 256
    for row_idx, (_, row) in enumerate(matches_s2.iterrows(), start=1):
        ws2.write(row_idx, 0, row['Codigo'])
        ws2.write(row_idx, 1, row['Nombre_Sistema'])
        ws2.write(row_idx, 2, row['Modelo_Nuevo'])
        ws2.write(row_idx, 3, row['Costo_Sistema'])
        ws2.write(row_idx, 4, row['Precio_Nuevo'])
        ws2.write(row_idx, 5, row['Diferencia'])

# Guardar archivo
wb.save(output_path)
print("Archivo guardado: {}".format(output_path))
print("Matches Sistema 1: {} productos".format(len(matches_s1)))
print("Matches Sistema 2: {} productos".format(len(matches_s2)))
