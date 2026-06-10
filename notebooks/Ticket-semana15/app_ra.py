import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Configuración profesional de la página
st.set_page_config(
    page_title="Dashboard Retail - Canasta Básica", 
    layout="wide",
    page_icon="🛒"
)

# Estilos personalizados para mejorar la visualización corporativa
st.markdown("""
    <style>
    .main-title { font-size:2.4rem !important; font-weight: bold; color: #1e3a8a; }
    .subtitle { font-size:1.2rem !important; color: #475569; margin-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">📊 Cuadro de Mando Integral - Analítica de Retail</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Monitoreo y Posicionamiento de Precios Basado en Segmentación Inteligente (K-Means)</p>', unsafe_allow_html=True)
st.markdown("---")

# 2. Carga de datos optimizada (CSV generado en tu Storytelling)
@st.cache_data
def cargar_datos():
    df = pd.read_csv("datos_retail_dashboard.csv")
    # Mapeo de clústeres a nombres estratégicos del negocio
    cluster_nombres = {
        0: "Gama Económica (Clúster 0)",
        1: "Gama Media (Clúster 1)",
        2: "Gama Alta/Premium (Clúster 2)"
    }
    df['Segmento_Cluster'] = df['prediction'].map(cluster_nombres)
    return df

try:
    df = cargar_datos()
except FileNotFoundError:
    st.error("❌ No se encontró el archivo 'datos_retail_dashboard.csv'. Por favor, ejecuta por completo tu Jupyter Notebook para generarlo.")
    st.stop()

# 3. Estructura de Navegación por Niveles Organizacionales
tab_est, tab_tac, tab_op = st.tabs([
    "📈 Nivel Estratégico (Director General)", 
    "💼 Nivel Táctico (Gerente Comercial)", 
    "🏪 Nivel Operacional (Supervisor de Tienda)"
])

# ==========================================
# PESTAÑA 1: NIVEL ESTRATÉGICO
# ==========================================
with tab_est:
    st.header("🏢 Composición Macroeconómica del Portafolio")
    st.caption("Frecuencia: Mensual | Objetivo: Analizar la distribución del surtido por categorías y clústeres de IA.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric(label="Total SKUs Monitoreados en Canasta", value=len(df))
        
        # Resumen por clúster estratégico
        st.markdown("**Participación por Segmento de Precio (IA):**")
        resumen_cluster = df['Segmento_Cluster'].value_counts().reset_index()
        resumen_cluster.columns = ['Segmento', 'Cantidad SKUs']
        st.dataframe(resumen_cluster, hide_index=True, use_container_width=True)
        
        st.markdown("**Top 5 Marcas con Mayor Presencia:**")
        st.dataframe(df['marca'].value_counts().head(5).reset_index(name='SKUs'), use_container_width=True)

    with col2:
        # Gráfico de distribución de categorías para el Director General
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.set_theme(style="whitegrid")
        
        order_cat = df['categoria'].value_counts().index
        sns.countplot(
            y="categoria", 
            data=df, 
            order=order_cat, 
            palette="Blues_r", 
            hue="categoria", 
            legend=False, 
            ax=ax
        )
        
        ax.set_title("Distribución de Productos por Categoría de Alimento", fontsize=12, fontweight='bold', color='#1e3a8a')
        ax.set_xlabel("Cantidad de SKUs en Góndola", fontweight='bold')
        ax.set_ylabel("Categoría", fontweight='bold')
        sns.despine(left=True)
        st.pyplot(fig)

# ==========================================
# PESTAÑA 2: NIVEL TÁCTICO
# ==========================================
with tab_tac:
    st.header("🔍 Bandas de Competitividad en Gama Media")
    st.caption("Frecuencia: Semanal | Objetivo: Evaluar el posicionamiento de precios de las cadenas competidoras dentro del Clúster 1.")
    
    # Filtrar por Gama Media tal como se diseñó en el Storytelling
    df_gama_media = df[df['prediction'] == 1]
    
    # Filtro interactivo opcional por categoría para darle más dinamismo a la app
    categorias_disponibles = ["Todas las Categorías"] + list(df_gama_media['categoria'].unique())
    categoria_seleccionada = st.selectbox(
        "Filtrar Bandas de Competencia por Categoría:", 
        options=categorias_disponibles
    )
    
    if categoria_seleccionada != "Todas las Categorías":
        df_gama_media = df_gama_media[df_gama_media['categoria'] == categoria_seleccionada]
    
    # Procesar métricas por supermercado
    df_tac = df_gama_media.groupby('supermercado')['precio'].agg(
        Precio_Minimo='min',
        Precio_Promedio_Gama_Media='mean',
        Precio_Maximo='max'
    ).reset_index().sort_values(by='Precio_Promedio_Gama_Media')
    
    if not df_tac.empty:
        # Renderizado del gráfico idéntico al Jupyter Notebook
        fig, ax = plt.subplots(figsize=(10, 4.5))
        
        ax.vlines(
            x=df_tac['supermercado'], 
            ymin=df_tac['Precio_Minimo'], 
            ymax=df_tac['Precio_Maximo'], 
            colors='#cbd5e1', 
            linewidth=6, 
            label="Banda de Precios (Mín a Máx)"
        )
        ax.scatter(df_tac['supermercado'], df_tac['Precio_Promedio_Gama_Media'], color='#1e3a8a', s=160, zorder=3, label="Precio Promedio")
        ax.scatter(df_tac['supermercado'], df_tac['Precio_Minimo'], color='#10b981', marker='^', s=100, zorder=3, label="Mínimo")
        ax.scatter(df_tac['supermercado'], df_tac['Precio_Maximo'], color='#ef4444', marker='v', s=100, zorder=3, label="Máximo")
        
        ax.set_ylabel("Precio Unitario ($ CLP)", fontweight='bold')
        ax.set_xlabel("Cadena de Supermercado", fontweight='bold')
        ax.set_title(f"Bandas de Precios - Segmento Medio ({categoria_seleccionada})", fontsize=12, fontweight='bold', color='#1e3a8a')
        ax.legend(frameon=True, facecolor='white')
        sns.despine(left=True)
        st.pyplot(fig)
        
        # Tabla de soporte táctico
        st.markdown("**Matriz de Soporte para Negociación Comercial:**")
        st.dataframe(df_tac.style.format({
            'Precio_Minimo': '$ {:.0f}',
            'Precio_Promedio_Gama_Media': '$ {:.1f}',
            'Precio_Maximo': '$ {:.0f}'
        }), hide_index=True, use_container_width=True)
    else:
        st.info("No hay suficientes registros para esta combinación de filtros.")

# ==========================================
# PESTAÑA 3: NIVEL OPERACIONAL
# ==========================================
with tab_op:
    st.header("🚨 Control Operativo de Precios en Gama Económica")
    st.caption("Frecuencia: Diario | Objetivo: Detectar sobreprecios o anomalías en góndola sobre productos del Clúster 0.")
    
    # Slider interactivo para ajustar el umbral de desvío operativo
    umbral_desvio = st.slider(
        "Ajustar Límite de Tolerancia Operativa (+% respecto al promedio de categoría):", 
        min_value=5, 
        max_value=50, 
        value=15, # 15% por defecto igual que en el Storytelling
        step=1
    )
    
    # Filtrar el DataFrame base por el Clúster Económico (Clúster 0)
    df_op_base = df[df['prediction'] == 0]
    zona_peligro = df_op_base[df_op_base['dif_porcentual_promedio'] >= umbral_desvio]
    
    # Alertas interactivas dinámicas
    if len(zona_peligro) > 0:
        st.warning(f"⚠️ AUDITORÍA URGENTE: Se han detectado {len(zona_peligro)} productos de la gama económica superando el límite establecido de +{umbral_desvio}%.")
    else:
        st.success("✅ Operación bajo control. Ningún producto económico supera la tolerancia establecida.")
        
    # Renderizado del Mapa de Control de Dispersión
    fig, ax = plt.subplots(figsize=(10, 5))
    
    sns.scatterplot(
        x="precio",
        y="dif_porcentual_promedio",
        data=df_op_base,
        color="#94a3b8",
        alpha=0.6,
        s=60,
        label="Económico Estable",
        ax=ax
    )
    
    if not zona_peligro.empty:
        sns.scatterplot(
            x="precio",
            y="dif_porcentual_promedio",
            data=zona_peligro,
            color="#f43f5e",
            s=90,
            edgecolor="black",
            linewidth=1,
            zorder=4,
            label="⚠️ Alertas Fuera de Rango",
            ax=ax
        )
        
    ax.axhline(y=umbral_desvio, color='#f43f5e', linestyle='--', linewidth=2, label=f"Umbral de Alerta (+{umbral_desvio}%)")
    ax.set_title("Matriz de Control y Auditoría de Góndolas (Clúster 0)", fontsize=12, fontweight='bold', color='#1e3a8a')
    ax.set_xlabel("Precio Redondeado ($ CLP)", fontweight='bold')
    ax.set_ylabel("Desviación Respecto al Promedio de Categoría (%)", fontweight='bold')
    ax.legend(loc="upper right", frameon=True)
    sns.despine(left=True)
    st.pyplot(fig)
    
    # Listado estructurado para inspección del Supervisor
    if len(zona_peligro) > 0:
        st.subheader("📋 Lista de Productos para Verificación Inmediata en Sala:")
        columnas_visibles = ['nombre_producto', 'marca', 'supermercado', 'categoria', 'precio', 'precio_promedio_cat', 'dif_porcentual_promedio']
        
        st.dataframe(
            zona_peligro[columnas_visibles].sort_values(by='dif_porcentual_promedio', ascending=False),
            hide_index=True,
            use_container_width=True
        )