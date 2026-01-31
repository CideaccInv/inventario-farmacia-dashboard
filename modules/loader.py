import pandas as pd
from io import StringIO

def preparar_datos(traslados,salidas,  recepciones):

    # Filtros de negocio
    traslados = traslados[traslados["BODEGA ORIGEN"] == "SERVICIO FARMACEUTICO SOTANO"]
    if salidas is not None and not salidas.empty:
        salidas = salidas[
            salidas["BODEGA ORIGEN"] == "SERVICIO FARMACEUTICO SOTANO"
        ]
    
    recepciones = recepciones[
        (recepciones["PROVEEDOR"] != "--------------")
    ]

    # Ahora sí limpiamos columnas
    columnas = ["CODIGO PRODUCTO", "LOTE", "CANTIDAD"]
    traslados = traslados[columnas]
    recepciones = recepciones[columnas]

    return traslados, salidas, recepciones


def load_excel(file, tipo):
    if file is None:
        return None

    # Leer SIEMPRE como texto
    try:
        file.seek(0)
        df_raw = pd.read_excel(
            file,
            header=None,
            dtype=str
        )
        print("Leído como Excel real")
    except Exception:
        file.seek(0)
        raw = file.read()
        text = raw.decode("latin-1", errors="ignore")
        df_raw = pd.read_html(StringIO(text), header=None)[0]
        df_raw = df_raw.astype(str)
        print("Leído como HTML disfrazado")

    # Buscar encabezado real
    header_row = None
    for i in range(len(df_raw)):
        fila = df_raw.iloc[i].astype(str).str.upper().tolist()
        if any("CODIGO" in c for c in fila) and any("LOTE" in c for c in fila):
            header_row = i
            break

    if header_row is None:
        raise ValueError("No se encontró la fila de encabezados")

    # Reconstruir
    df = df_raw.iloc[header_row + 1:].copy()
    df.columns = df_raw.iloc[header_row].astype(str).str.strip().str.upper()
    df = df.dropna(how="all")
    df = df.loc[:, ~df.columns.str.contains("UNNAMED")]

    # Normalización de columnas
    if tipo in ["inicial", "final"]:
        rename_map = {
            "CODIGO PRODUCTO": "CODIGO PRODUCTO",
            "CÓDIGO PRODUCTO": "CODIGO PRODUCTO",
            "PRODUCTO": "NOMBRE PRODUCTO",
            "DESCRIPCION": "NOMBRE PRODUCTO",
            "DESCRIPCIÓN": "NOMBRE PRODUCTO",
            "LOTE": "LOTE",
            "CANTIDAD": "CANTIDAD"
        }
    elif tipo in ["traslados", "salidas"]:
        rename_map = {
            "CODIGO ARTICULO": "CODIGO PRODUCTO",
            "CÓDIGO ARTICULO": "CODIGO PRODUCTO",
            "NOMBRE ARTICULO": "NOMBRE PRODUCTO",
            "LOTE": "LOTE",
            "CANTIDAD": "CANTIDAD"
        }
    elif tipo == "recepciones":
        rename_map = {
            "CODIGO ARTICULO": "CODIGO PRODUCTO",
            "CÓDIGO ARTICULO": "CODIGO PRODUCTO",
            "NOMBRE ARTICULO": "NOMBRE PRODUCTO",
            "DESCRIPCION": "NOMBRE PRODUCTO",
            "LOTE": "LOTE",
            "CANTIDAD RECIBIDA": "CANTIDAD"
        }
    else:
        raise ValueError("Tipo de archivo no reconocido")

    df = df.rename(columns=rename_map)

    print(f"Columnas {tipo}:", df.columns.tolist())

    # Limpieza fuerte
    df["CODIGO PRODUCTO"] = df["CODIGO PRODUCTO"].astype(str).str.strip()
    df["LOTE"] = df["LOTE"].astype(str).str.strip()

    # Eliminar basura tipo ".0"
    df["LOTE"] = df["LOTE"].str.replace(".0", "", regex=False)

    df["CANTIDAD"] = pd.to_numeric(df["CANTIDAD"], errors="coerce").fillna(0)

    return df





