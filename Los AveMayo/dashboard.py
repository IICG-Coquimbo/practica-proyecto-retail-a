import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================================
# CONFIGURACIÓN
# =====================================================
st.set_page_config(page_title="Dashboard Retail | Isidora Matus", layout="wide")

st.title("📊 Cuadro de Mando Integral - Analítica de Supermercados")
st.markdown("---")

# =====================================================
# CARGA Y LIMPIEZA
# =====================================================
@st.cache_data
def cargar_datos():
    # Usamos el nombre exacto que detectamos en tu carpeta
    return pd.read_csv("datos_retail_dashboard.csv")

df = cargar_datos()

# Limpieza original
df["marca"] = df["marca"].astype(str).str.upper().str.strip()
df["supermercado"] = df["supermercado"].astype(str).str.upper().str.strip()
df["categoria"] = df["categoria"].astype(str).str.upper().str.strip()
df["precio"] = pd.to_numeric(df["precio"], errors="coerce")

# Homologación Categorías
df["categoria_limpia"] = df["categoria"]
df.loc[df["categoria"].isin(["ACEITES","ADEREZOS Y CONDIMENTOS","ARROZ","ARROZ, LEGUMBRES Y SEMILLAS","AZUCARES","CONSERVAS","CONSERVAS Y ENLATADOS","DESPENSA","DESPENSA GENERAL","PASTAS","PASTAS FIDEOS Y SALSAS","SALSAS","LEGUMBRES","HARINAS","HARINAS LEVADURAS Y GRASAS"]), "categoria_limpia"] = "DESPENSA Y ABARROTES"
df.loc[df["categoria"].isin(["LACTEOS","LACTEOS Y CONGELADOS","LACTEOS, HUEVOS Y REFRIGERADOS","LACTEOS/FIAMBRERIA","LECHE EN POLVO","LECHES LIQUIDAS Y CREMAS","MANTEQUILLAS Y MARGARINAS","QUESOS","YOGHURT Y POSTRES","HUEVOS"]), "categoria_limpia"] = "LACTEOS Y FRESCOS"
df.loc[df["categoria"].isin(["AVES","CARNICERIA","CERDO","FIAMBRERIA","FIAMBRERIA EMBUTIDOS Y QUESOS","FIAMBRERIA Y EMBUTIDOS","PESCADOS Y MARISCOS"]), "categoria_limpia"] = "CARNES Y FIAMBRERIA"
df.loc[df["categoria"].isin(["AGUA CON GAS","AGUA SIN GAS","BEBIDAS","BEBIDAS JUGOS Y AGUAS","BEBIDAS LACTEAS Y VEGETALES"]), "categoria_limpia"] = "BEBIDAS Y AGUAS"
df.loc[df["categoria"].isin(["ASEO","LIMPIEZA"]), "categoria_limpia"] = "LIMPIEZA Y ASEO"

# =====================================================
# PESTAÑAS
# =====================================================
tab_est, tab_tac, tab_op = st.tabs(["🚀 Nivel Estratégico", "📈 Nivel Táctico", "⚠️ Nivel Operacional"])

# --- NIVEL ESTRATÉGICO ---
with tab_est:
    st.header("Análisis Estratégico de Surtido y Precios")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Distribución del Surtido")
        data_surtido = df.groupby(["supermercado", "categoria_limpia"]).size().reset_index(name="count")
        fig1 = px.bar(data_surtido, x="supermercado", y="count", color="categoria_limpia", barmode="group", template="plotly_dark")
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        st.subheader("2. Dispersión de Precios")
        fig2 = px.box(df, x="precio", y="categoria_limpia", color="categoria_limpia", orientation='h', template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

# --- NIVEL TÁCTICO ---
with tab_tac:
    st.header("Benchmarking Táctico de Precios")
    col3, col4 = st.columns(2)
    
    # Datos tácticos
    df_tactico = df.groupby('supermercado')['precio'].agg(['min', 'mean', 'max']).reset_index()
    
    with col3:
        st.subheader("3. Bandas de Precios (Min/Max)")
        fig3 = px.scatter(df_tactico, x="supermercado", y="mean", error_y=df_tactico['max']-df_tactico['mean'], error_y_minus=df_tactico['mean']-df_tactico['min'], template="plotly_dark")
        st.plotly_chart(fig3, use_container_width=True)
        
    with col4:
        st.subheader("4. Boxplot Comparativo")
        fig4 = px.box(df, x="precio", y="supermercado", color="supermercado", orientation='h', template="plotly_dark")
        st.plotly_chart(fig4, use_container_width=True)

# =====================================================
# NIVEL OPERACIONAL (ACTUALIZADO: Visión Total)
# =====================================================
with tab_op:
    st.header("Matriz de Alertas Críticas - Visión Total")
    
    # 1. Calculamos las anomalías sobre el dataframe completo (df)
    promedio = df["precio"].mean()
    desviacion = df["precio"].std()
    limite = promedio + (2 * desviacion) # Umbral estadístico para detectar outliers
    
    # Filtramos las alertas de todo el dataset
    alertas = df[df["precio"] > limite].copy()

    st.metric("Total Productos Fuera de Rango", len(alertas))

    if len(alertas) > 0:
        col5, col6 = st.columns(2)
        
        with col5:
            st.subheader("Matriz de Dispersión")
            # Gráfico de todos los productos (puntos grises) y los alertados (rojos)
            fig5 = px.scatter(df, x="precio", y=df.index, template="plotly_dark", 
                             title="Anomalías vs Normalidad")
            fig5.add_trace(px.scatter(alertas, x="precio", y=alertas.index).data[0])
            fig5.update_traces(marker=dict(color='red'), selector=dict(name='trace 1'))
            st.plotly_chart(fig5, use_container_width=True)

        with col6:
            st.subheader("Ranking por Supermercado")
            # Ranking consolidado
            rank = alertas.groupby("supermercado").size().reset_index(name="count").sort_values("count", ascending=False)
            fig6 = px.bar(rank, x="count", y="supermercado", orientation='h', color="count", 
                          template="plotly_dark", text="count")
            st.plotly_chart(fig6, use_container_width=True)

        st.subheader("Detalle de Productos Críticos")
        st.dataframe(alertas[["marca", "supermercado", "categoria", "precio"]], use_container_width=True)
        
    else:
        st.success("¡Excelente! No se detectaron anomalías en el sistema.")