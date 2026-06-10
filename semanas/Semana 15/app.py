import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Configuración avanzada de la página web
st.set_page_config(
    page_title="Dashboard Integral - Retail Alimenticio", 
    layout="wide",
    page_icon="🛒"
)

# Estilos personalizados para mejorar el impacto visual ejecutivo
st.markdown("""
    <style>
    .main-title { font-size:36px !important; font-weight: bold; color: #1E3A8A; }
    .sub-title { font-size:18px !important; color: #555555; margin-bottom: 20px; }
    hr { margin-top: 10px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">📊 Cuadro de Mando Integral - Canasta Básica Chilena</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Monitoreo Analítico y Despliegue de Decisiones de Portafolio, Competencia y Operaciones</p>', unsafe_allow_html=True)
st.markdown("---")

# 2. Carga de datos optimizada (Utiliza tu CSV unificado)
@st.cache_data
def cargar_datos():
    # El archivo conserva el nombre estandarizado de tu ecosistema de datos
    df_data = pd.read_csv("datos_retail_dashboard.csv")
    # Limpieza o parseo de seguridad en caso de strings vacíos
    df_data['marca'] = df_data['marca'].fillna('S/M').replace('', 'S/M')
    return df_data

try:
    df = cargar_datos()
except FileNotFoundError:
    st.error("❌ No se encontró el archivo 'datos_retail_dashboard.csv'. Por favor, verifica que el archivo exportado esté en la misma carpeta que este script.")
    st.stop()

# 3. Estructuración de Pestañas Corporativas
tab_est, tab_tac, tab_op = st.tabs([
    "📈 Nivel Estratégico (Director General)", 
    "💼 Nivel Táctico (Gerente Comercial)", 
    "🏪 Nivel Operacional (Supervisor de Tienda)"
])

# ==========================================
# PESTAÑA 1: NIVEL ESTRATÉGICO
# ==========================================
with tab_est:
    st.header("🏢 Mix de Portafolio y Diferenciación por Cadena")
    st.caption("Frecuencia: Mensual | Objetivo: Analizar la participación de catálogo y la exclusividad de marcas entre competidores.")
    
    # Selector interactivo para cambiar la cadena de supermercados dinámicamente
    cadenas_disponibles = sorted(df['supermercado'].unique())
    cadena_seleccionada = st.selectbox("Seleccione la Cadena de Retail a Evaluar:", options=cadenas_disponibles)
    
    # Procesamiento dinámico del KPI de Surtido por Cadena
    df_cadena = df[df['supermercado'] == cadena_seleccionada]
    total_sku_cadena = len(df_cadena)
    
    df_est_kpi = df_cadena['marca'].value_counts().reset_index()
    df_est_kpi.columns = ['marca', 'Cantidad_SKUs']
    df_est_kpi['Participacion_Surtido_Porcentaje'] = (df_est_kpi['Cantidad_SKUs'] / total_sku_cadena) * 100
    
    # Top 10 para la gráfica multi-cadena limpia
    df_est_top10 = df_est_kpi.head(10)
    
    # Layout en columnas
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Métricas de Estructura")
        st.metric(label=f"Total SKUs en {cadena_seleccionada}", value=f"{total_sku_cadena:,}")
        st.metric(
            label="Marca Dominante en Góndola", 
            value=df_est_kpi['marca'].iloc[0], 
            delta=f"{df_est_kpi['Participacion_Surtido_Porcentaje'].iloc[0]:.2f}% del Mix"
        )
        st.markdown("**Surtido General por Marca:**")
        st.dataframe(df_est_kpi, hide_index=True, use_container_width=True)
        
    with col2:
        # Replicamos el gráfico del Storytelling adaptado a Streamlit
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.set_theme(style="whitegrid")
        
        # Filtramos el dataset global por las mejores marcas para ver la comparativa de hue
        df_multi_plot = df[df['marca'].isin(df_est_top10['marca'])]
        df_group_plot = df_multi_plot.groupby(['supermercado', 'marca']).size().reset_index(name='Cantidad')
        
        # Calcular participación interna para el gráfico agrupado
        totals = df_group_plot.groupby('supermercado')['Cantidad'].transform('sum')
        df_group_plot['Participacion_Surtido_Porcentaje'] = (df_group_plot['Cantidad'] / totals) * 100
        
        sns.barplot(
            x="Participacion_Surtido_Porcentaje",
            y="marca",
            hue="supermercado",
            data=df_group_plot,
            palette="muted",
            ax=ax
        )
        
        # Anotaciones
        for p in ax.patches:
            width = p.get_width()
            if width > 0.5:
                ax.annotate(f"{width:.1f}%", (width + 0.2, p.get_y() + p.get_height() / 2),
                            va="center", ha="left", fontsize=8, fontweight="bold", color="#34495e")
        
        ax.set_xlabel("Participación dentro del Supermercado (%)", fontweight='bold')
        ax.set_ylabel("Marcas Clave", fontweight='bold')
        ax.set_title(f"Comparativa de Surtido: Top Marcas vs Competencia", fontsize=11, fontweight='bold')
        ax.legend(title="Cadenas")
        sns.despine(left=True, bottom=True)
        st.pyplot(fig)

# ==========================================
# PESTAÑA 2: NIVEL TÁCTICO
# ==========================================
with tab_tac:
    st.header("🔍 Matriz de Posicionamiento Competitivo y Premiumización")
    st.caption("Frecuencia: Semanal | Objetivo: Auditar la desviación porcentual de precios frente al benchmark de la categoría.")
    
    # Selector de Categoría para no mezclar productos inconsistentes
    categorias = sorted(df['categoria'].unique()) if 'categoria' in df.columns else []
    
    if categorias:
        categoria_sel = st.selectbox("Seleccione Categoría de Alimentos para Análisis de Precios:", options=categorias)
        df_cat = df[df['categoria'] == categoria_sel]
    else:
        df_cat = df
        st.warning("No se detectó columna 'categoria', visualizando datos globales.")

    # Filtro dinámico de marcas basado en la categoría seleccionada
    marcas_en_cat = df_cat['marca'].unique()
    marcas_def_tac = list(marcas_en_cat[:8]) # Tomar las primeras por defecto
    
    marcas_tac = st.multiselect(
        "Filtrar Marcas Competidoras:", 
        options=marcas_en_cat, 
        default=marcas_def_tac
    )
    
    if marcas_tac:
        df_tac_filtrado = df_cat[df_cat['marca'].isin(marcas_tac)]
        
        # Agrupamos por el nuevo KPI Táctico: Promedio del Índice de Premiumización
        kpi_tactico = df_tac_filtrado.groupby('marca')['dif_porcentual_promedio'].mean().reset_index()
        kpi_tactico.columns = ['marca', 'Indice_Premium_Porcentaje']
        kpi_tactico = kpi_tactico.sort_values(by='Indice_Premium_Porcentaje', ascending=False)
        
        col_t1, col_t2 = st.columns([1, 2])
        with col_t1:
            st.markdown("**Índice de Posicionamiento por Marca:**")
            st.caption("Valores positivos implican precios sobre el promedio de la categoría (Premium). Valores negativos indican estrategias Low Cost.")
            st.dataframe(
                kpi_tactico.style.format({'Indice_Premium_Porcentaje': '{:.2f}%'}),
                hide_index=True, use_container_width=True
            )
            
        with col_t2:
            # Gráfico Divergente Adaptado
            fig, ax = plt.subplots(figsize=(9, 5))
            colors_cond = ['#2ecc71' if x >= 0 else '#e74c3c' for x in kpi_tactico['Indice_Premium_Porcentaje']]
            
            sns.barplot(
                x="Indice_Premium_Porcentaje",
                y="marca",
                data=kpi_tactico,
                palette=colors_cond,
                hue="marca",
                legend=False,
                ax=ax
            )
            
            ax.axvline(0, color='#2c3e50', linestyle='--', linewidth=1.5, alpha=0.8)
            ax.set_xlabel("Índice de Posicionamiento (% vs Promedio Categoría)", fontweight='bold')
            ax.set_ylabel("Marcas Evaluadas", fontweight='bold')
            ax.set_title("Divergencia de Posicionamiento Estratégico de Precios", fontsize=11, fontweight='bold')
            sns.despine(left=True, bottom=True)
            st.pyplot(fig)
    else:
        st.info("Seleccione al menos una marca para construir la matriz de posicionamiento.")

# ==========================================
# PESTAÑA 3: NIVEL OPERACIONAL
# ==========================================
with tab_op:
    st.header("🚨 Matriz de Alertas de Precio Mínimo Crítico (Riesgo de Quiebre)")
    st.caption("Frecuencia: Diario | Objetivo: Levantar alertas rápidas de reposición por fuga de margen o peligro de quiebres de stock (Stockout).")
    
    # Slider operacional invertido para buscar riesgos críticos (Precios sumamente bajos)
    umbral_quiebre = st.slider(
        "Ajustar Umbral Crítico Inferior de Desviación (%):", 
        min_value=-80, 
        max_value=-10, 
        value=-40, 
        step=5
    )
    
    # Filtrado operacional direccional (Menores o iguales al umbral negativo)
    df_alertas_op = df[df['dif_porcentual_promedio'] <= umbral_quiebre]
    
    if len(df_alertas_op) > 0:
        st.error(f"⚠️ ATENCIÓN SUPERVISOR: Se detectaron {len(df_alertas_op)} SKUs críticamente por debajo del precio promedio de mercado. Alto riesgo de quiebre o error en góndola.")
    else:
        st.success("✅ Operación Estable: No se registran riesgos de quiebre crítico para el umbral seleccionado.")
        
    # Gráfico de Dispersión Operacional enfocado en el extremo inferior
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.scatter(df["precio"], df["dif_porcentual_promedio"], alpha=0.3, s=40, color="darkgray", label="Rango Comercial Normal")
    
    if len(df_alertas_op) > 0:
        ax.scatter(df_alertas_op["precio"], df_alertas_op["dif_porcentual_promedio"], color="crimson", s=70, edgecolor="black", zorder=5, label="Alertas de Quiebre / Margen Mínimo")
        
    ax.axhline(y=umbral_quiebre, color='red', linestyle='--', alpha=0.8, linewidth=1.5)
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    ax.set_xlabel("Precio Actual del Producto ($ CLP)", fontweight='bold')
    ax.set_ylabel("Desviación respecto al Promedio (%)", fontweight='bold')
    ax.set_title("Monitoreo Operacional de Productos Outliers de Bajo Precio", fontsize=11, fontweight='bold')
    ax.legend(loc="upper right")
    sns.despine(left=True)
    st.pyplot(fig)
    
    # Tabla operativa de acción inmediata para el Supervisor
    if len(df_alertas_op) > 0:
        st.subheader("📋 Plan de Ruta: Productos para Auditoría Física Inmediata")
        columnas_operacionales = ['nombre_producto', 'marca', 'supermercado', 'precio', 'precio_promedio_cat', 'dif_porcentual_promedio']
        
        # Mostrar tabla ordenada con los casos más riesgosos (más negativos) al principio
        st.dataframe(
            df_alertas_op[columnas_operacionales].sort_values(by='dif_porcentual_promedio', ascending=True), 
            hide_index=True, 
            use_container_width=True
        )