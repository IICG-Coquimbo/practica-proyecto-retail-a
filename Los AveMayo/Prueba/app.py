import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="Dashboard Ejecutivo Supermercados",
    layout="wide"
)

st.title("🛒 Cuadro de Mando Integral - Supermercados")
st.markdown("---")

# =====================================================
# CARGA DE DATOS
# =====================================================

@st.cache_data
def cargar_datos():
    return pd.read_csv(
        "/home/jovyan/work/Los AveMayo/Prueba/datos_dashboard.csv"
    )

df = cargar_datos()

# =====================================================
# LIMPIEZA
# =====================================================

df["marca"] = (
    df["marca"]
    .astype(str)
    .str.upper()
    .str.strip()
)

df["supermercado"] = (
    df["supermercado"]
    .astype(str)
    .str.upper()
    .str.strip()
)

df["categoria"] = (
    df["categoria"]
    .astype(str)
    .str.upper()
    .str.strip()
)

df["precio"] = pd.to_numeric(
    df["precio"],
    errors="coerce"
)

df = df.dropna(subset=["precio"])

# =====================================================
# PESTAÑAS
# =====================================================

tab_est, tab_tac, tab_op = st.tabs(
    [
        "📈 Estratégico",
        "📊 Táctico",
        "⚙️ Operacional"
    ]
)
# =====================================================
# NIVEL ESTRATÉGICO
# =====================================================

with tab_est:

    st.header("📈 Índice de Competitividad por Cadena")

    st.caption(
        "Comparación del precio promedio entre supermercados."
    )

    precio_promedio = (
        df.groupby("supermercado")["precio"]
        .mean()
        .reset_index()
        .sort_values("precio")
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Supermercado Más Competitivo",
            precio_promedio.iloc[0]["supermercado"]
        )

        st.metric(
            "Precio Promedio Más Bajo",
            f"${precio_promedio.iloc[0]['precio']:,.0f}"
        )

        st.metric(
            "Total Productos",
            len(df)
        )

    with col2:

        fig, ax = plt.subplots(figsize=(10, 5))

        sns.barplot(
            data=precio_promedio,
            x="precio",
            y="supermercado",
            ax=ax
        )

        ax.set_title(
            "Precio Promedio por Supermercado"
        )

        ax.set_xlabel("Precio Promedio")
        ax.set_ylabel("Supermercado")

        st.pyplot(fig)

    st.dataframe(
        precio_promedio,
        use_container_width=True
    )
# =====================================================
# NIVEL TÁCTICO
# =====================================================

with tab_tac:

    st.header("📊 Brecha de Precios por Supermercado")

    st.caption(
        "Comparación de dispersión y comportamiento de precios."
    )

    supermercados = sorted(
        df["supermercado"].unique()
    )

    seleccionados = st.multiselect(
        "Seleccionar supermercados",
        supermercados,
        default=supermercados
    )

    df_filtrado = df[
        df["supermercado"].isin(seleccionados)
    ]

    fig, ax = plt.subplots(figsize=(12, 6))

    sns.boxplot(
        data=df_filtrado,
        x="precio",
        y="supermercado",
        ax=ax
    )

    ax.set_title(
        "Brecha de Precios por Supermercado"
    )

    ax.set_xlabel("Precio")
    ax.set_ylabel("Supermercado")

    st.pyplot(fig)

    resumen = (
        df_filtrado
        .groupby("supermercado")["precio"]
        .agg(["min", "mean", "max"])
        .round(0)
        .reset_index()
    )

    resumen.columns = [
        "Supermercado",
        "Precio Mínimo",
        "Precio Promedio",
        "Precio Máximo"
    ]

    st.dataframe(
        resumen,
        use_container_width=True
    )
# =====================================================
# NIVEL OPERACIONAL
# =====================================================

with tab_op:

    st.header("⚙️ Alerta de Productos Fuera de Rango")

    st.caption(
        "Detección de precios anómalos utilizando clusters."
    )

    cluster = st.selectbox(
        "Seleccionar Cluster",
        sorted(df["prediction"].unique())
    )

    df_cluster = df[
        df["prediction"] == cluster
    ].copy()

    promedio = df_cluster["precio"].mean()

    desviacion = df_cluster["precio"].std()

    limite_superior = promedio + (
        2 * desviacion
    )

    alertas = df_cluster[
        df_cluster["precio"] > limite_superior
    ]

    st.metric(
        "Productos con Alerta",
        len(alertas)
    )

    if len(alertas) > 0:

        ranking = (
            alertas
            .groupby("supermercado")
            .size()
            .reset_index(name="Alertas")
            .sort_values(
                "Alertas",
                ascending=False
            )
        )

        fig, ax = plt.subplots(figsize=(10, 5))

        sns.barplot(
            data=ranking,
            x="Alertas",
            y="supermercado",
            ax=ax
        )

        ax.set_title(
            "Ranking de Alertas por Supermercado"
        )

        st.pyplot(fig)

        st.subheader(
            "Productos Detectados"
        )

        st.dataframe(
            alertas[
                [
                    "marca",
                    "supermercado",
                    "categoria",
                    "precio",
                    "prediction"
                ]
            ],
            use_container_width=True
        )

    else:

        st.success(
            "No se detectaron productos fuera de rango en este cluster."
        )
st.markdown("---")

st.info(
    f"""
    Registros analizados: {len(df):,}
    | Marcas: {df['marca'].nunique()}
    | Categorías: {df['categoria'].nunique()}
    | Supermercados: {df['supermercado'].nunique()}
    """
)