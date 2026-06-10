import os
import sys
import subprocess
import streamlit as st
import pandas as pd

# --- TRUCO INYECTOR DE DEPENDENCIAS EN EL CONTENEDOR ---
try:
    import plotly
    import plotly.express as px
    import plotly.graph_objects as go
except ModuleNotFoundError:
    st_message = "Instalando Plotly dinámicamente en el contenedor... por favor espera."
    print(st_message)
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly"])
    import plotly
    import plotly.express as px
    import plotly.graph_objects as go

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================
st.set_page_config(
    page_title="Dashboard Ejecutivo Supermercados",
    layout="wide"
)

st.title("🛒 Cuadro de Mando Integral - Analítica de Supermercados")
st.markdown("### Análisis de Canasta Básica, Surtido Comercial y Stock — **Grupo Losavemayo**")
st.markdown("---")

# =====================================================
# CARGA DE DATOS (Usando tu ruta exacta de la Semana 15)
# =====================================================
@st.cache_data
def cargar_datos():
    return pd.read_csv(
        "/home/jovyan/work/semanas/Semana 15/datos_supermercado_dashboard.csv"
    )

df = cargar_datos()

# =====================================================
# LIMPIEZA Y ESTANDARIZACIÓN EN PANDAS
# =====================================================
df["marca"] = df["marca"].astype(str).str.upper().str.strip()
df["supermercado"] = df["supermercado"].astype(str).str.upper().str.strip()
df["categoria"] = df["categoria"].astype(str).str.upper().str.strip()
df["precio"] = pd.to_numeric(df["precio"], errors="coerce")

# Eliminar posibles nulos en columnas clave para los gráficos
df = df.dropna(subset=["precio", "supermercado"])

# =====================================================
# HOMOLOGACIÓN DE MACRO-CATEGORÍAS (Estratégico)
# =====================================================
df["categoria_limpia"] = df["categoria"]

df.loc[df["categoria"].isin([
    "ACEITES","ADEREZOS Y CONDIMENTOS","ARROZ","ARROZ, LEGUMBRES Y SEMILLAS",
    "AZUCARES","CONSERVAS","CONSERVAS Y ENLATADOS","DESPENSA","DESPENSA GENERAL",
    "PASTAS","PASTAS FIDEOS Y SALSAS","SALSAS","LEGUMBRES","HARINAS","HARINAS LEVADURAS Y GRASAS"
]), "categoria_limpia"] = "DESPENSA Y ABARROTES"

df.loc[df["categoria"].isin([
    "LACTEOS","LACTEOS Y CONGELADOS","LACTEOS, HUEVOS Y REFRIGERADOS","LACTEOS/FIAMBRERIA",
    "LECHE EN POLVO","LECHES LIQUIDAS Y CREMAS","MANTEQUILLAS Y MARGARINAS","QUESOS","YOGHURT Y POSTRES","HUEVOS"
]), "categoria_limpia"] = "LACTEOS Y FRESCOS"

df.loc[df["categoria"].isin([
    "AVES","CARNICERIA","CERDO","FIAMBRERIA","FIAMBRERIA EMBUTIDOS Y QUESOS","FIAMBRERIA Y EMBUTIDOS","PESCADOS Y MARISCOS"
]), "categoria_limpia"] = "CARNES Y FIAMBRERIA"

df.loc[df["categoria"].isin([
    "AGUA CON GAS","AGUA SIN GAS","BEBIDAS","BEBIDAS JUGOS Y AGUAS","BEBIDAS LACTEAS Y VEGETALES"
]), "categoria_limpia"] = "BEBIDAS Y AGUAS"

df.loc[df["categoria"].isin(["ASEO","LIMPIEZA"]), "categoria_limpia"] = "LIMPIEZA Y ASEO"

# =====================================================
# PESTAÑAS (Estratégico, Táctico, Operacional)
# =====================================================
tab_est, tab_tac, tab_op = st.tabs([
    "📈 Nivel Estratégico",
    "📊 Nivel Táctico",
    "🏪 Nivel Operacional"
])

# =====================================================
# 1. NIVEL ESTRATÉGICO
# =====================================================
with tab_est:
    st.header("📈 Estructura del Portafolio y Surtido Homologado")
    st.caption("Frecuencia: Mensual | Objetivo: Analizar el posicionamiento comercial e inflacionario por cadena.")
    
    # KPIs en Tarjetas
    col_m1, col_m2 = st.columns(2)
    col_m1.metric("Total Productos en Catálogo", f"{len(df):,}")
    col_m2.metric("Marcas Proveedoras Únicas", len(df["marca"].unique()))
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Concentración de Catálogo por Marca (Top 15 líderes)")
        df_marcas = df["marca"].value_counts().reset_index(name="cantidad").head(15)
        df_marcas["porcentaje"] = ((df_marcas["cantidad"] / len(df)) * 100).round(2)
        
        fig_marcas = px.bar(
            df_marcas,
            x="porcentaje",
            y="marca",
            orientation="h",
            text="porcentaje",
            labels={"porcentaje": "% de Participación", "marca": "Marca"},
            color="porcentaje",
            color_continuous_scale="blues"
        )
        fig_marcas.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, height=450)
        fig_marcas.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        st.plotly_chart(fig_marcas, use_container_width=True)

    with col2:
        st.subheader("Distribución Homologada del Surtido Comercial")
        resumen = df.groupby(["supermercado", "categoria_limpia"]).size().reset_index(name="cantidad")
        
        fig_surtido = px.bar(
            resumen,
            x="supermercado",
            y="cantidad",
            color="categoria_limpia",
            barmode="group",
            labels={"cantidad": "Cantidad de Productos", "supermercado": "Supermercado", "categoria_limpia": "Macro-Categoría"},
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        fig_surtido.update_layout(height=450, legend_title_text='Macro-Categorías')
        st.plotly_chart(fig_surtido, use_container_width=True)

    st.subheader("📋 Matriz de Surtido Estratégico (Datos Consolidados)")
    st.dataframe(resumen, use_container_width=True)

# =====================================================
# 2. NIVEL TÁCTICO
# =====================================================
with tab_tac:
    st.header("📊 Benchmarking Competitivo de Precios")
    st.caption("Frecuencia: Semanal | Objetivo: Evaluar la competitividad de bandas de precios e índices de elasticidad.")

    supermercados = sorted(df["supermercado"].unique())
    seleccionados = st.multiselect(
        "Filtrar Establecimientos Comerciales",
        supermercados,
        default=supermercados
    )

    df_filtrado = df[df["supermercado"].isin(seleccionados)]

    st.subheader("1. Distribución Dinámica de Bandas de Precios")
    fig_box = px.box(
        df_filtrado,
        x="precio",
        y="supermercado",
        color="supermercado",
        labels={"precio": "Rango de Precios ($)", "supermercado": "Establecimiento"},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_box.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")
    st.subheader("2. Bandas de Competitividad por Proveedores Líderes (Top 10)")
    
    # Filtrar marcas líderes
    top_10_marcas = df_filtrado["marca"].value_counts().head(10).index.tolist()
    df_bandas = df_filtrado[df_filtrado["marca"].isin(top_10_marcas)].groupby("marca")["precio"].agg(["min","mean","max"]).reset_index()
    df_bandas = df_bandas.sort_values(by="mean")
    
    # Construcción de gráfico de rango dinámico
    fig_bandas = go.Figure()
    for idx, row in df_bandas.iterrows():
        fig_bandas.add_trace(go.Scatter(
            x=[row['marca'], row['marca']],
            y=[row['min'], row['max']],
            mode='lines',
            line=dict(color='gray', width=3),
            showlegend=False
        ))
    fig_bandas.add_trace(go.Scatter(x=df_bandas['marca'], y=df_bandas['min'], mode='markers', name='Precio Mínimo', marker=dict(color='green', symbol='triangle-up', size=10)))
    fig_bandas.add_trace(go.Scatter(x=df_bandas['marca'], y=df_bandas['mean'], mode='markers', name='Precio Promedio', marker=dict(color='navy', size=12)))
    fig_bandas.add_trace(go.Scatter(x=df_bandas['marca'], y=df_bandas['max'], mode='markers', name='Precio Maximó', marker=dict(color='red', symbol='triangle-down', size=10)))
    
    fig_bandas.update_layout(xaxis_title="Marcas en Góndola", yaxis_title="Precio Registrado ($)", height=450)
    st.plotly_chart(fig_bandas, use_container_width=True)

    st.subheader("📋 Resumen Estadístico Táctico")
    resumen_tactico = df_filtrado.groupby("supermercado")["precio"].agg(["min","mean","max"]).round(0)
    st.dataframe(resumen_tactico, use_container_width=True)

# =====================================================
# 3. NIVEL OPERACIONAL
# =====================================================
with tab_op:
    st.header("🏪 Gestión Operativa de Góndola y Alertas Críticas")
    st.caption("Frecuencia: Diaria | Enfoque: Detección instantánea de anomalías de precios, quiebres de stock o errores de etiquetado.")

    cluster = st.selectbox(
        "Filtrar por Clúster Asignado (Modelo de Segmentación KMeans)",
        sorted(df["prediction"].unique())
    )

    df_cluster = df[df["prediction"] == cluster].copy()

    # Cálculo matemático de las alertas operacionales
    promedio = df_cluster["precio"].mean()
    desviacion = df_cluster["precio"].std()
    limite_superior = promedio + (2 * desviacion)

    df_cluster["Estado"] = "NORMAL"
    df_cluster.loc[df_cluster["precio"] > limite_superior, "Estado"] = "ALERTA"

    alertas = df_cluster[df_cluster["Estado"] == "ALERTA"]
    ranking = alertas.groupby("supermercado").size().reset_index(name="count").sort_values("count", ascending=False)

    # Métricas Operativas Rápidas
    col_o1, col_o2 = st.columns(2)
    col_o1.metric("Alertas de Desviación Crítica", f"{len(alertas)} SKUs", delta=f"{len(alertas)} Incidentes", delta_color="inverse")
    col_o2.metric("Precio Promedio Esperado en Clúster", f"${round(promedio, 0)}")

    st.markdown("---")

    if len(ranking) > 0:
        col_g1, col_g2 = st.columns([3, 2])
        
        with col_g1:
            st.subheader("Matriz de Dispersión: Detección de Desvíos Críticos")
            fig_scatter = px.scatter(
                df_cluster,
                x="marca",
                y="precio",
                color="Estado",
                color_discrete_map={"NORMAL": "darkgray", "ALERTA": "crimson"},
                hover_data=["supermercado", "categoria"],
                labels={"marca": "Marca del Producto", "precio": "Precio ($)"}
            )
            fig_scatter.add_hline(y=limite_superior, line_dash="dash", line_color="red", annotation_text="Umbral Operativo (Media + 2 Desv.)")
            fig_scatter.update_layout(height=450, xaxis={'showticklabels': False})
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        with col_g2:
            st.subheader("Ranking Operativo por Establecimiento")
            # SOLUCIÓN DEL ERROR: Se cambió 'autumn' por la paleta oficial de Plotly 'sunset'
            fig_ranking = px.bar(
                ranking,
                x="count",
                y="supermercado",
                orientation='h',
                color="count",
                color_continuous_scale="sunset",
                labels={"count": "Productos Fuera de Rango", "supermercado": "Supermercado"}
            )
            fig_ranking.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, height=450)
            st.plotly_chart(fig_ranking, use_container_width=True)

        st.subheader("🔍 Monitor de Auditoría (Acción Inmediata para Supervisor)")
        st.dataframe(
            alertas[["marca", "supermercado", "categoria", "precio", "prediction"]].sort_values(by="precio", ascending=False),
            use_container_width=True
        )
    else:
        st.success("✅ Excelente: No se detectaron anomalías operacionales de precios en este clúster hoy.")

st.markdown("---")
st.info(f"Dashboard cargado correctamente. Registros de retail analizados en tiempo real: {len(df)}")