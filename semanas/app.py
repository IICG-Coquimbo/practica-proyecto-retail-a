import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# CONFIGURACIÓN GENERAL DEL PANEL
# ==========================================
st.set_page_config(page_title="Dashboard Retail Ejecutivo", layout="wide")
st.title("📊 Cuadro de Mando Integral - Analítica Retail")
st.markdown("---")

# Carga automática del dataset exportado desde Spark
@st.cache_data
def cargar_datos():
    return pd.read_csv("datos_retail_dashboard.csv")

df = cargar_datos()

# Creación de pestañas por rol de negocio
tab_est, tab_tac, tab_op = st.tabs([
    "Nivel Estratégico (CEO)", 
    "Nivel Táctico (Gerente de Categoría)", 
    "Nivel Operacional (Supervisor de Tienda)"
])

# ==========================================
# 📊 PESTAÑA 1: NIVEL ESTRATÉGICO (GRÁFICO DE DONA)
# ==========================================
with tab_est:
    st.header("Concentración de Cartera y Portafolio en Góndola")
    st.caption("Objetivo: Mapear la participación del catálogo para detectar dependencias críticas de proveedores.")
    
    total_sku = len(df)
    df_est = df['marca_limpia'].value_counts().reset_index()
    df_est.columns = ['marca_limpia', 'Cantidad_SKUs']
    df_est['Participacion'] = (df_est['Cantidad_SKUs'] / total_sku) * 100
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Indicadores Clave")
        st.metric(label="Total SKUs Monitoreados", value=total_sku)
        st.metric(label="Proveedor Monopólico", value=df_est['marca_limpia'].iloc[0], delta=f"{df_est['Participacion'].iloc[0]:.1f}% del total")
        st.dataframe(df_est, hide_index=True)
        
    with col2:
        # Gráfico de Dona profesional
        fig, ax = plt.subplots(figsize=(6, 6))
        colors = sns.color_palette("Blues_r", len(df_est))
        
        ax.pie(
            df_est["Participacion"], 
            labels=df_est["marca_limpia"], 
            autopct='%1.1f%%', 
            startangle=90, 
            colors=colors,
            textprops={'fontsize': 10, 'weight': 'bold'}
        )
        # Dibujamos el círculo del centro para transformarlo en dona
        circulo_centro = plt.Circle((0,0), 0.70, fc='white')
        ax.add_artist(circulo_centro)
        plt.tight_layout()
        st.pyplot(fig)


# ==========================================
# 📈 PESTAÑA 2: NIVEL TÁCTICO (BOXPLOT DE PRECIOS)
# ==========================================
with tab_tac:
    st.header("Matriz de Volatilidad y Bandas de Competitividad de Precios")
    st.caption("Objetivo: Analizar la dispersión y estrategias de precios de los competidores líderes.")
    
    marcas_filtro = st.multiselect("Seleccionar marcas para auditar:", options=df['marca_limpia'].unique(), default=df['marca_limpia'].unique())
    df_filtrado = df[df['marca_limpia'].isin(marcas_filtro)]
    
    if len(df_filtrado) > 0:
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.set_theme(style="whitegrid")
        
        # Ordenamos las marcas automáticamente de menor a mayor precio mediano
        orden_marcas = df_filtrado.groupby("marca_limpia")["precio"].median().sort_values().index
        
        sns.boxplot(
            x="precio",
            y="marca_limpia",
            data=df_filtrado,
            order=orden_marcas,
            hue="marca_limpia",
            palette="Spectral",
            legend=False,
            ax=ax
        )
        ax.set_xlabel("Rango de Precios del Producto ($)", fontweight='bold')
        ax.set_ylabel("Marcas Líderes", fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.error("Por favor, selecciona al menos una marca para graficar.")


# ==========================================
# 🚨 PESTAÑA 3: NIVEL OPERACIONAL (BARRAS DE RETIRO)
# ==========================================
with tab_op:
    st.header("Plan de Acción Diario: Alertas Críticas para Retiro de Stock")
    st.caption("Objetivo: Identificar de forma inmediata cuántas unidades deben ser retiradas de góndola por baja reputación.")
    
    # Control dinámico interactivo para el Supervisor
    umbral_rating = st.slider("Ajustar tolerancia crítica de Rating (Filtro Rojo):", min_value=2.0, max_value=4.0, value=3.5, step=0.1)
    
    df_op = df.copy()
    # Filtro operativo de crisis
    zona_peligro = df_op[(df_op['rating'] < umbral_rating) & (df_op['opiniones'] > 10)]
    
    st.error(f"🚨 ACCIÓN REQUERIDA: Se detectaron {len(zona_peligro)} variedades de productos en Estado Crítico.")
    
    if len(zona_peligro) > 0:
        # Agrupamos por marca para contar las alertas
        reporte_alertas = zona_peligro['marca_limpia'].value_counts().reset_index()
        reporte_alertas.columns = ['marca_limpia', 'cantidad_alertas']
        
        fig, ax = plt.subplots(figsize=(10, 4.5))
        sns.barplot(
            x="cantidad_alertas",
            y="marca_limpia",
            data=reporte_alertas,
            hue="marca_limpia",
            palette="Reds_r",
            legend=False,
            ax=ax
        )
        
        # Colocamos las etiquetas numéricas en las barras de forma limpia
        for p in ax.patches:
            width = p.get_width()
            ax.annotate(
                f' {int(width)} u.',
                (width, p.get_y() + p.get_height() / 2),
                va='center', ha='left', fontsize=10, fontweight='bold', color='darkred'
            )
            
        ax.set_xlabel("Cantidad de SKU con Alerta Roja", fontweight='bold')
        ax.set_ylabel("Marcas Afectadas", fontweight='bold')
        ax.set_xlim(0, reporte_alertas["cantidad_alertas"].max() + 2)
        plt.tight_layout()
        st.pyplot(fig)
        
        st.subheader("📋 Lista de Tareas para Reponedores (Retiro Inmediato):")
        st.dataframe(zona_peligro[['marca_limpia', 'precio', 'rating', 'opiniones']], hide_index=True)
    else:
        st.success("✅ No hay alertas críticas registradas con los parámetros actuales. Góndola limpia.")