import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Configuración de la página web
st.set_page_config(
    page_title="Dashboard Ejecutivo Retail Alimenticio", 
    layout="wide",
    page_icon="🛒"
)

st.title("📊 Cuadro de Mando Integral - Analítica de la Canasta Básica Chilena")
st.markdown("### Monitoreo Estratégico, Táctico y Operacional de Precios de Retail")
st.markdown("---")

# 2. Carga de datos optimizada
@st.cache_data
def cargar_datos():
    # Cargamos el archivo CSV exportado en la Semana 15
    return pd.read_csv("datos_retail_dashboard.csv")

df = cargar_datos()

# 3. Creación de las Pestañas (Tabs) por Nivel Organizacional
tab_est, tab_tac, tab_op = st.tabs([
    "📈 Nivel Estratégico (Director General)", 
    "💼 Nivel Táctico (Gerente Comercial)", 
    "🏪 Nivel Operacional (Supervisor de Tienda)"
])

# ==========================================
# PESTAÑA 1: NIVEL ESTRATÉGICO
# ==========================================
with tab_est:
    st.header("🏢 Concentración del Portafolio por Marca")
    st.caption("Frecuencia: Mensual | Objetivo: Evaluar la presencia y peso de las marcas líderes en góndola")
    
    # Procesamiento rápido en Pandas
    total_sku = len(df)
    df_est_completo = df['marca'].value_counts().reset_index()
    df_est_completo.columns = ['marca', 'Cantidad_SKUs']
    df_est_completo['Participacion'] = (df_est_completo['Cantidad_SKUs'] / total_sku) * 100
    
    # Tomamos las top 15 para la gráfica del Director General
    df_est_top15 = df_est_completo.head(15)
    
    # Diseño en columnas de Streamlit (Métricas clave arriba)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(label="Total SKUs en Canasta Básica", value=total_sku)
        st.metric(
            label="Marca Alimenticia Líder", 
            value=df_est_completo['marca'].iloc[0], 
            delta=f"{df_est_completo['Participacion'].iloc[0]:.1f}% del catálogo"
        )
        st.markdown("**Tabla General de Posicionamiento:**")
        st.dataframe(df_est_completo, hide_index=True, use_container_width=True)
        
    with col2:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(
            x="Participacion", 
            y="marca", 
            data=df_est_top15, 
            hue="marca", 
            palette="viridis", 
            legend=False, 
            ax=ax
        )
        sns.despine(left=True, bottom=False)
        ax.set_xlabel("Participación en Góndola (%)", fontweight='bold')
        ax.set_ylabel("Marca de Alimento", fontweight='bold')
        ax.set_title("Top 15 Marcas con Mayor Surtido", fontsize=12, fontweight='bold')
        st.pyplot(fig)

# ==========================================
# PESTAÑA 2: NIVEL TÁCTICO
# ==========================================
with tab_tac:
    st.header("🔍 Bandas de Competitividad y Volatilidad de Precios")
    st.caption("Frecuencia: Semanal | Objetivo: Diseñar estrategias de precios competitivos frente al mercado")
    
    # Filtro interactivo en tiempo real por Marca
    # Por defecto seleccionamos las top 5 para que el gráfico empiece limpio
    marcas_defecto = list(df_est_completo['marca'].head(5))
    marcas_seleccionadas = st.multiselect(
        "Filtrar Marcas Alimenticias para Análisis de Competencia:", 
        options=df['marca'].unique(), 
        default=marcas_defecto
    )
    
    if marcas_seleccionadas:
        df_filtrado = df[df['marca'].isin(marcas_seleccionadas)]
        
        # Corregido: Usamos la columna 'precio' en lugar de 'precio_kg'
        df_tac = df_filtrado.groupby('marca')['precio'].agg(['min', 'mean', 'max']).reset_index().sort_values(by='mean')
        
        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.vlines(x=df_tac['marca'], ymin=df_tac['min'], ymax=df_tac['max'], colors='#B0BEC5', alpha=0.7, linewidth=3)
        ax.scatter(df_tac['marca'], df_tac['mean'], color='#1A237E', s=120, zorder=3, label="Precio Promedio")
        ax.scatter(df_tac['marca'], df_tac['min'], color='#2E7D32', marker='^', s=80, zorder=3, label="Precio Mínimo")
        ax.scatter(df_tac['marca'], df_tac['max'], color='#C62828', marker='v', s=80, zorder=3, label="Precio Máximo")
        
        ax.set_ylabel("Precio del Producto ($ CLP)", fontweight='bold')
        ax.set_xlabel("Marcas Analizadas", fontweight='bold')
        plt.xticks(rotation=25, ha='right')
        ax.legend(facecolor='#f8f9fa')
        sns.despine(left=True)
        st.pyplot(fig)
    else:
        st.info("Por favor, selecciona al menos una marca para visualizar el análisis táctico.")

# ==========================================
# PESTAÑA 3: NIVEL OPERACIONAL
# ==========================================
with tab_op:
    st.header("🚨 Matriz de Alertas de Desviación de Precios en Góndola")
    st.caption("Frecuencia: Diario / Tiempo Real | Objetivo: Detectar anomalías operacionales o errores de etiquetado")
    
    # Control interactivo para el Supervisor (Slider para mover el umbral de desvío en vivo)
    umbral_desvio = st.slider(
        "Ajustar Umbral Crítico de Variación Porcentual (%):", 
        min_value=20, 
        max_value=100, 
        value=50, 
        step=5
    )
    
    df_op = df.copy()
    # Corregido: Filtramos usando las desviaciones porcentuales de la categoría reales
    zona_peligro = df_op[
        (df_op['dif_porcentual_promedio'] >= umbral_desvio) | 
        (df_op['dif_porcentual_promedio'] <= -umbral_desvio)
    ]
    
    if len(zona_peligro) > 0:
        st.warning(f"Se han detectado {len(zona_peligro)} SKUs con desvíos de precios extremos (+/- {umbral_desvio}%) que requieren auditoría en tienda.")
    else:
        st.success("No se registran anomalías operacionales críticas para el umbral seleccionado.")
        
    fig, ax = plt.subplots(figsize=(10, 5))
    # Eje X: precio, Eje Y: diferencia respecto al promedio
    ax.scatter(df_op["precio"], df_op["dif_porcentual_promedio"], alpha=0.4, s=50, color="#78909C", label="Rango Estable")
    ax.scatter(zona_peligro["precio"], zona_peligro["dif_porcentual_promedio"], color="#D32F2F", s=90, edgecolor="black", zorder=4, label="Productos Desviados")
    
    # Líneas límites basadas en el slider
    ax.axhline(y=umbral_desvio, color='#C62828', linestyle='--', alpha=0.6)
    ax.axhline(y=-umbral_desvio, color='#C62828', linestyle='--', alpha=0.6)
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    ax.set_xlabel("Precio del Producto ($ CLP)", fontweight='bold')
    ax.set_ylabel("Desviación respecto al Promedio Cat. (%)", fontweight='bold')
    ax.legend(loc="upper right")
    sns.despine(left=True)
    st.pyplot(fig)
    
    if len(zona_peligro) > 0:
        st.subheader("📋 Lista de Productos para Auditoría Inmediata:")
        # Corregido: Ajustadas las columnas reales agregando supermercado
        columnas_visibles = ['nombre_producto', 'marca', 'supermercado', 'precio', 'precio_promedio_cat', 'dif_porcentual_promedio']
        st.dataframe(zona_peligro[columnas_visibles].sort_values(by='dif_porcentual_promedio', ascending=False), hide_index=True)