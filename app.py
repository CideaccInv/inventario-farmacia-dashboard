import streamlit as st
from modules.loader import load_excel
from modules.conciliacion import conciliar
from modules.exporter import to_excel_download

# ======================
# CONFIGURACIÓN GENERAL
# ======================
st.set_page_config(
    page_title="Conciliación de Inventarios",
    layout="wide"
)

# ======================
# UI – SECCIÓN DE CARGA
# ======================
def upload_section():
    st.markdown(
        """
        <h1 style='text-align: center;'>📊 Dashboard de Conciliación de Inventarios</h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <p style="color:#6c757d; text-align:center;">
        Cargue los <b>archivos obligatorios</b> para reconstruir y conciliar el inventario
        por <b>código y lote</b>.
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📦 Inventario Base")
        inicial = st.file_uploader(
            "📘 Inventario Inicial",
            type=["xlsx", "xls"],
            key="inicial"
        )
        traslados = st.file_uploader(
            "📤 Traslados (Salidas internas)",
            type=["xlsx", "xls"],
            key="traslados"
        )

    with col2:
        st.markdown("### 🔄 Movimientos y Cierre")
        recepciones = st.file_uploader(
            "📥 Recepciones (Entradas)",
            type=["xlsx", "xls"],
            key="recepciones"
        )
        final = st.file_uploader(
            "📊 Inventario Final (Sistema)",
            type=["xlsx", "xls"],
            key="final"
        )

    st.markdown("---")

    st.markdown("### 🚚 Salidas de bodega")
    hubo_salidas = st.checkbox(
        "¿Hubo salidas de la bodega?",
        key="hubo_salidas"
    )

    salidas = None
    if hubo_salidas:
        salidas = st.file_uploader(
            "📦 Archivo de salidas de bodega",
            type=["xlsx", "xls"],
            key="salidas"
        )

    st.markdown("---")

    # ======================
    # ESTADO DE CARGA (FIX)
    # ======================
    st.markdown("### 🧾 Estado de carga")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.success("✔ Inicial") if inicial is not None else st.warning("❌ Inicial")

    with c2:
        st.success("✔ Traslados") if traslados is not None else st.warning("❌ Traslados")

    with c3:
        st.success("✔ Recepciones") if recepciones is not None else st.warning("❌ Recepciones")

    with c4:
        st.success("✔ Final") if final is not None else st.warning("❌ Final")

    with c5:
        if hubo_salidas:
            st.success("✔ Salidas") if salidas is not None else st.warning("❌ Salidas")
        else:
            st.info("➖ No aplica")

    return inicial, traslados, recepciones, salidas, final

# ======================
# EJECUCIÓN
# ======================
inicial_file, traslados_file, recepciones_file, salidas_file, final_file = upload_section()

archivos_ok = all([
    inicial_file is not None,
    traslados_file is not None,
    recepciones_file is not None,
    final_file is not None
])

# ======================
# CONCILIAR (UNA VEZ)
# ======================
if archivos_ok and st.button("🔍 Reconstruir y Conciliar Inventario"):

    salidas_df = (
        load_excel(salidas_file, "salidas")
        if salidas_file is not None
        else None
    )

    st.session_state["df_conciliado"] = conciliar(
        load_excel(inicial_file, "inicial"),
        load_excel(traslados_file, "traslados"),
        load_excel(recepciones_file, "recepciones"),
        salidas_df,
        load_excel(final_file, "final")
    )

    st.session_state["tipo_filtro"] = "Todas"

# ======================
# RESULTADOS
# ======================
if "df_conciliado" in st.session_state:

    df = st.session_state["df_conciliado"]

    inconsistencias_base = df[df["Diferencia"] != 0].copy()

    inconsistencias_base["Tipo_Inconsistencia"] = (
        inconsistencias_base["Tipo_Inconsistencia"]
        .fillna("Otra Inconsistencia")
        .astype(str)
        .str.strip()
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🚨 Inconsistencias", len(inconsistencias_base))
    with col2:
        st.metric("📦 Registros", len(df))
    with col3:
        pct = round(len(inconsistencias_base) / len(df) * 100, 2)
        st.metric("📊 % con diferencia", f"{pct}%")

    st.subheader("🚨 Inconsistencias detectadas")

    tipos = ["Todas"] + sorted(inconsistencias_base["Tipo_Inconsistencia"].unique())

    st.session_state["tipo_filtro"] = st.selectbox(
        "Filtrar por tipo de inconsistencia",
        tipos,
        index=tipos.index(st.session_state.get("tipo_filtro", "Todas"))
    )

    if st.session_state["tipo_filtro"] != "Todas":
        inconsistencias = inconsistencias_base[
            inconsistencias_base["Tipo_Inconsistencia"]
            == st.session_state["tipo_filtro"]
        ]
    else:
        inconsistencias = inconsistencias_base

    st.dataframe(inconsistencias, use_container_width=True)

    st.download_button(
        "⬇️ Descargar inconsistencias",
        data=to_excel_download(inconsistencias),
        file_name="inconsistencias.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if st.button("♻️ Reiniciar conciliación"):
        st.session_state.clear()
        st.experimental_rerun()

else:
    st.info("📂 Cargue los 4 archivos y ejecute la conciliación")
