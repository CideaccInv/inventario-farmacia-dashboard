import streamlit as st
import base64

def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def upload_section():
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
            width: 64px;
            opacity: 0.9;
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

    # =========================
    # SALIDAS DE BODEGA (CONDICIONAL)
    # =========================
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
            key="salidas_bodega"
        )

    st.markdown("---")

    # =========================
    # ESTADO DE CARGA
    # =========================
    st.markdown("### 🧾 Estado de carga")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.success("✔ Inicial") if inicial else st.warning("❌ Inicial")
    with c2:
        st.success("✔ Traslados") if traslados else st.warning("❌ Traslados")
    with c3:
        st.success("✔ Recepciones") if recepciones else st.warning("❌ Recepciones")
    with c4:
        st.success("✔ Final") if final else st.warning("❌ Final")
    with c5:
        if hubo_salidas:
            st.success("✔ Salidas") if salidas else st.warning("❌ Salidas")
        else:
            st.info("➖ No aplica")

    return inicial, traslados, recepciones, salidas, final
