import pandas as pd
from modules.loader import preparar_datos

# =========================
# Constantes
# =========================
CLAVES = ["CODIGO PRODUCTO", "LOTE"]
CANTIDAD = "CANTIDAD"


# =========================
# Normalización de datos
# =========================
def normalizar(df):
    df = df.copy()

    # Código de producto: texto limpio
    df["CODIGO PRODUCTO"] = (
        df["CODIGO PRODUCTO"]
        .astype(str)
        .str.strip()
    )

    df["LOTE"] = (
        df["LOTE"]
        .astype(str)
        .str.replace(".0", "", regex=False)  
        .str.strip()
        .str.upper()                         
    )

    # Cantidad: numérica segura
    df[CANTIDAD] = (
        pd.to_numeric(df[CANTIDAD], errors="coerce")
        .fillna(0)
    )

    return df

# =========================
# Agrupación
# =========================
def agrupar(df):
    return (
        df
        .groupby(CLAVES, as_index=False)[CANTIDAD]
        .sum()
    )
    
def clasificar_inconsistencia(row):

    inicial = row["Inicial"]
    recep = row["Recepciones"]
    sal = row["Salidas"]
    final_calc = row["Final_Calculado"]
    final_sys = row["Final_Sistema"]
    diff = row["Diferencia"]

    # 1️⃣ Sin inconsistencia
    if diff == 0:
        return "Sin Inconsistencia"

    # 2️⃣ Recepción no registrada
    if (
        final_sys > inicial and
        recep == 0
    ):
        return "Inconsistencia de Recepción"

    # 3️⃣ Traslado / salida no registrada
    if (
        inicial > final_sys and
        sal == 0
    ):
        return "Inconsistencia de Traslado"

    # 4️⃣ Salidas mal aplicadas
    if (
        sal > 0 and
        final_sys != final_calc
    ):
        return "Inconsistencia en Salidas"

    # 5️⃣ Ajuste / diferencia de inventario
    return "Inconsistencia de Inventario"


def conciliar(inicial, traslados, recepciones, salidas, final_sistema):

    # ===============================
    # Limpiezas específicas
    # ===============================
    traslados, salidas, recepciones = preparar_datos(traslados, salidas, recepciones)

    # ===============================
    # Guardar nombres de productos
    # ===============================
    nombres = (
        inicial[["CODIGO PRODUCTO", "NOMBRE PRODUCTO"]]
        .drop_duplicates()
    )

    # ===============================
    # Normalizar (sin agrupar)
    # ===============================
    inicial = normalizar(inicial)
    traslados = normalizar(traslados)
    recepciones = normalizar(recepciones)
    final_sistema = normalizar(final_sistema)

    if salidas is not None and not salidas.empty:
        salidas = normalizar(salidas)
    else:
        salidas = pd.DataFrame(columns=["CODIGO PRODUCTO", "LOTE", "CANTIDAD"])


    # ===============================
    # Detectar lotes nuevos desde recepciones
    # ===============================
    nuevos = (
        recepciones[CLAVES]
        .drop_duplicates()
        .merge(
            inicial[CLAVES],
            on=CLAVES,
            how="left",
            indicator=True
        )
    )

    nuevos = nuevos[nuevos["_merge"] == "left_only"].drop(columns="_merge")

    if not nuevos.empty:
        nuevos[CANTIDAD] = 0
        inicial = pd.concat([inicial, nuevos], ignore_index=True)

    # ===============================
    # Unificar salidas (traslados + salidas bodega)
    # ===============================
    
    traslados["TIPO_SALIDA"] = "TRASLADO"

    frames_salidas = [traslados]

    if salidas is not None and not salidas.empty:
        salidas["TIPO_SALIDA"] = "SALIDA_BODEGA"
        frames_salidas.append(salidas)

    salidas_total = pd.concat(frames_salidas, ignore_index=True)



    salidas_total = pd.concat(
        [traslados, salidas],
        ignore_index=True
    )

    # ===============================
    # Agrupar
    # ===============================
    inicial = agrupar(inicial).rename(columns={CANTIDAD: "Inicial"})
    recepciones = agrupar(recepciones).rename(columns={CANTIDAD: "Recepciones"})
    salidas_total = agrupar(salidas_total).rename(columns={CANTIDAD: "Salidas"})
    final_sistema = agrupar(final_sistema).rename(columns={CANTIDAD: "Final_Sistema"})
    
    print("Inicial cols after group:", inicial.columns.tolist())

    # ===============================
    # Merge general
    # ===============================
    df = inicial.merge(recepciones, on=CLAVES, how="outer")
    df = df.merge(salidas_total, on=CLAVES, how="outer")
    df = df.merge(final_sistema, on=CLAVES, how="outer")

    # ===============================
    # Agregar nombre del producto
    # ===============================
    df = df.merge(nombres, on="CODIGO PRODUCTO", how="left")

    # ===============================
    # Reemplazar NaN por 0
    # ===============================
    df[["Inicial", "Recepciones", "Salidas", "Final_Sistema"]] = (
        df[["Inicial", "Recepciones", "Salidas", "Final_Sistema"]]
        .fillna(0)
    )

    # ===============================
    # Cálculos
    # ===============================
    df["Final_Calculado"] = df["Inicial"] + df["Recepciones"] - df["Salidas"]
    df["Diferencia"] = df["Final_Sistema"] - df["Final_Calculado"]

    # ===============================
    # Clasificación de inconsistencias
    # ===============================
    df["Tipo_Inconsistencia"] = df.apply(
        clasificar_inconsistencia,
        axis=1
    )

    # ===============================
    # Renombrar columnas
    # ===============================
    df = df.rename(columns={
        "CODIGO PRODUCTO": "Codigo_Articulo",
        "NOMBRE PRODUCTO": "Nombre_Producto",
        "LOTE": "Lote"
    })

    # ===============================
    # Orden final
    # ===============================
    columnas_orden = [
        "Codigo_Articulo",
        "Nombre_Producto",
        "Lote",
        "Tipo_Inconsistencia",
        "Inicial",
        "Recepciones",
        "Salidas",
        "Final_Calculado",
        "Final_Sistema",
        "Diferencia"
    ]

    return df[columnas_orden]
