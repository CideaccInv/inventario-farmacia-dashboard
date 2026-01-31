import streamlit as st

def upload_section():
    st.markdown(
        """
        <h1 style='text-align: center;'>
            📊 Dashboard de Conciliación de Inventarios
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <p style="color: #6c757d; text-align: center;">
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
