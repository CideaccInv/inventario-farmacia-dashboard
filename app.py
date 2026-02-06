import base64
import streamlit as st
from modules.loader import load_excel
from modules.conciliacion import conciliar
from modules.exporter import to_excel_download


def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()
    
st.set_page_config(page_title="Conciliación de Inventarios", layout="wide")
st.markdown("""
    <style>
    .column-title {
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        font-weight: 600;
        font-size: 1.6rem;
        margin-bottom: 1rem;
        width: 100%;
    }

    .column-subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 0.9rem;
        margin-bottom: 0.75rem;
    }

    /* Tarjetas normales */
    .card {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        border-left: 6px solid #c1121f;
    }

    .card h4 {
        margin: 0;
        font-size: 0.95rem;
        text-align: center;
        color: #343a40;
    }

    .card .count {
        font-size: 1.8rem;
        text-align: center;
        font-weight: 700;
        margin-top: 0.3rem;
    }

    /* Tarjeta TOTAL (roja) */
    .total-card {
        background-color: #c1121f;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 6px 16px rgba(0,0,0,0.12);
    }

    .total-card h4 {
        margin: 0;
        font-size: 0.95rem;
        text-align: center;
        color: #ffffff;
        opacity: 0.9;
    }

    .total-card .count {
        font-size: 2.2rem;
        text-align: center;
        font-weight: 800;
        margin-top: 0.3rem;
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)


icono = img_to_base64("assets/inventario.png")

st.markdown(
    f"""
    <style>
    .header-box {{
        background-color: #f8f9fa;
        border-left: 6px solid #c1121f;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    .header-text h1 {{
        margin: 0;
    }}

    .header-text p {{
        margin: 0.2rem 0 0;
        color: #6c757d;
    }}

    .header-icon img {{
        width: 120px;
        opacity: 0.9;
        margin-right: 20px; 
    }}
    </style>

    <div class="header-box">
        <div class="header-text">
            <h1>Conciliación de Inventario Farmacéutico</h1>
            <p>Control de traslados, salidas y recepciones</p>
        </div>
        <div class="header-icon">
            <img src="data:image/png;base64,{icono}">
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ======================
# UI – SECCIÓN DE CARGA
# ======================
def uploader_con_estado(label, icon, key, obligatorio=True):
    f_col, s_col = st.columns([4, 1], vertical_alignment="center")

    with f_col:
        archivo = st.file_uploader(
            f"{icon} {label}",
            type=["xlsx", "xls"],
            key=key
        )

    with s_col:
        if archivo:
            st.markdown("✅")
        else:
            if obligatorio:
                st.markdown("❌")
            else:
                st.markdown("➖")

    return archivo


def upload_section():

    col1, col2 = st.columns(2)

    # ======================
    # COLUMNA IZQUIERDA
    # ======================
    with col1:
        st.markdown(
            "<div class='column-title'>📦 Inventario inicial y final</div>",
            unsafe_allow_html=True
        )

        inicial = uploader_con_estado(
            "Inventario Inicial", "📘", "inicial"
        )
        final = uploader_con_estado(
            "Inventario Final", "📕", "final"
        )

    # ======================
    # COLUMNA DERECHA
    # ======================
    with col2:
        st.markdown(
            "<div class='column-title'>🔄 Recepciones y traslados</div>",
            unsafe_allow_html=True
        )

        recepciones = uploader_con_estado(
            "Recepciones (Entradas)", "📥", "recepciones"
        )
        traslados = uploader_con_estado(
            "Traslados (Salidas internas)", "📤", "traslados"
        )

    st.markdown("---")

    # ======================
    # SALIDAS DE BODEGA
    # ======================
    st.markdown("### 🚚 Salidas de bodega")
    hubo_salidas = st.checkbox("¿Hubo salidas de la bodega?", key="hubo_salidas")

    salidas = None
    if hubo_salidas:
        salidas = uploader_con_estado(
            "Salidas de bodega", "🚚", "salidas", obligatorio=False
        )

    return inicial, traslados, recepciones, salidas, final


# ======================
# EJECUCIÓN
# ======================
inicial_file, traslados_file, recepciones_file, salidas_file, final_file = upload_section()

archivos_ok = all([
    inicial_file,
    traslados_file,
    recepciones_file,
    final_file
])

# ======================
# CONCILIAR (UNA VEZ)
# ======================
if archivos_ok and st.button("🔍 Reconstruir y Conciliar Inventario"):
    salidas_df = load_excel(salidas_file, "salidas") if salidas_file else None

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

    resumen = (
        inconsistencias_base
        .groupby("Tipo_Inconsistencia")
        .size()
        .reset_index(name="Cantidad")
    )

    total_inc = len(inconsistencias_base)
    resumen["Porcentaje"] = (resumen["Cantidad"] / total_inc * 100).round(1)

    st.subheader("🚨 Distribución de inconsistencias")

    cols = st.columns(len(resumen) + 1)

    for col, row in zip(cols, resumen.itertuples()):
        with col:
            st.markdown(
                f"""
                <div class="card">
                    <div class="count">{row.Cantidad} ({row.Porcentaje}%)</div>
                    <h4>{row.Tipo_Inconsistencia}</h4>
                </div>
                """,
                unsafe_allow_html=True
            )

    with cols[-1]:
        st.markdown(
            f"""
            <div class="total-card">
                <div class="count">{total_inc}</div>
                <h4>Total inconsistencias</h4>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    tipos = ["Todas"] + resumen["Tipo_Inconsistencia"].tolist()
    filtro = st.selectbox("Filtrar inconsistencias", tipos)

    data = (
        inconsistencias_base
        if filtro == "Todas"
        else inconsistencias_base[inconsistencias_base["Tipo_Inconsistencia"] == filtro]
    )

    st.dataframe(data, use_container_width=True)

    st.download_button(
        "⬇️ Descargar inconsistencias",
        data=to_excel_download(data),
        file_name="inconsistencias.xlsx"
    )

else:
    st.info("📂 Cargue los archivos y ejecute la conciliación")
