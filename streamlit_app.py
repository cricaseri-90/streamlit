import streamlit as st
import pandas as pd
import os

# Intentar importar librerías gráficas con manejo de errores para diagnóstico
try:
    import plotly.express as px
    import seaborn as sns
    import matplotlib.pyplot as plt
    import kagglehub
except ImportError as e:
    st.error(f"Falta una dependencia crítica: {e}. Por favor revisa tu archivo requirements.txt")
    st.stop()

# CONFIGURACIÓN PROFESIONAL
st.set_page_config(
    page_title="Data Analysis COVID-19 Perú | Cristian Serna",
    page_icon="🧬",
    layout="wide"
)

# CARGA DE DATOS CON CACHÉ
@st.cache_data(show_spinner=False)
def load_data():
    try:
        # Descarga desde Kaggle
        path = kagglehub.dataset_download("martinclark/peru-covid19-august-2020")
        
        # Listar archivos para encontrar el CSV correcto
        files = [f for f in os.listdir(path) if f.endswith('.csv')]
        if not files:
            st.error("No se encontró el archivo CSV en el dataset descargado.")
            return None
            
        full_path = os.path.join(path, files[0])
        df = pd.read_csv(full_path)
        
        # Preprocesamiento de fechas
        if 'FECHA_RESULTADO' in df.columns:
            df['FECHA_RESULTADO'] = pd.to_datetime(df['FECHA_RESULTADO'], errors='coerce')
        
        # Limpieza de nulos en columnas críticas
        if 'DEPARTAMENTO' in df.columns and 'METODODX' in df.columns:
            df = df.dropna(subset=['DEPARTAMENTO', 'METODODX'])
        
        return df
    except Exception as e:
        st.error(f"Error en la carga de datos: {str(e)}")
        return None

# ESTADO DE NAVEGACIÓN
if 'page' not in st.session_state:
    st.session_state.page = 'landing'

# Función para cambiar de página
def navigate_to(page_name):
    st.session_state.page = page_name

# --- VISTA 1: LANDING PAGE ---
if st.session_state.page == 'landing':
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.title("🧬 Análisis de Datos COVID-19 Perú")
        st.subheader("Proyecto Integrador - Talento TECH")
        st.write("""
        Plataforma profesional para la exploración de datos epidemiológicos. 
        Analice la distribución regional, los métodos de diagnóstico y las tendencias temporales 
        de la pandemia en agosto de 2020.
        
        **Analista:** Cristian Serna
        """)
        if st.button("Ingresar al Panel de Trabajo ➔", type="primary"):
            navigate_to('dashboard')
            st.rerun()

    with col2:
        # Lógica de imagen robusta
        image_path = "covid.png"
        fallback_url = "https://raw.githubusercontent.com/CristianSerna/assets/main/covid_viz.png"
        
        if os.path.exists(image_path):
            st.image(image_path, caption="Análisis Epidemiológico Perú", use_container_width=True)
        else:
            st.image(fallback_url, caption="Estructura SARS-CoV-2 (Enlace Externo)", use_container_width=True)

# --- VISTA 2: DASHBOARD ---
elif st.session_state.page == 'dashboard':
    st.sidebar.title("🛠️ Panel de Control")
    if st.sidebar.button("🏠 Volver al Inicio"):
        navigate_to('landing')
        st.rerun()

    with st.spinner("Cargando base de datos..."):
        df = load_data()
    
    if df is not None:
        # Filtros Sidebar
        regiones_disponibles = sorted(df['DEPARTAMENTO'].unique())
        regiones = st.sidebar.multiselect(
            "Seleccionar Departamentos:",
            options=regiones_disponibles,
            default=regiones_disponibles[:6]
        )
        
        if not regiones:
            st.warning("Por favor, selecciona al menos un departamento en el panel lateral.")
        else:
            df_filtered = df[df['DEPARTAMENTO'].isin(regiones)]

            # Organización por pestañas
            tab1, tab2, tab3 = st.tabs(["📊 Visualización Seaborn", "📈 Interactivos Plotly", "📄 Documentación"])

            with tab1:
                st.write("#### Distribución Regional (Análisis Estático con Seaborn)")
                if not df_filtered.empty:
                    fig1, ax1 = plt.subplots(figsize=(10, 6))
                    sns.countplot(
                        data=df_filtered, 
                        y='DEPARTAMENTO', 
                        palette='viridis', 
                        order=df_filtered['DEPARTAMENTO'].value_counts().index, 
                        ax=ax1
                    )
                    ax1.set_title("Cantidad de Casos por Región")
                    st.pyplot(fig1)
                    plt.close(fig1) # Cerrar figura para liberar memoria
                
                with st.expander("ℹ️ Ayuda del Gráfico"):
                    st.info("Este gráfico de barras permite comparar la carga de casos entre departamentos de forma clara y profesional.")

                st.divider()
                st.write("#### Densidad Temporal de Contagios")
                if 'FECHA_RESULTADO' in df_filtered.columns:
                    fig2, ax2 = plt.subplots(figsize=(10, 4))
                    df_temp = df_filtered.copy()
                    df_temp['Day'] = df_temp['FECHA_RESULTADO'].dt.dayofyear
                    sns.kdeplot(data=df_temp, x='Day', hue='DEPARTAMENTO', fill=True, palette='crest', ax=ax2)
                    ax2.set_title("Curva de Densidad de Casos")
                    st.pyplot(fig2)
                    plt.close(fig2)
                
                with st.expander("ℹ️ Ayuda del Gráfico"):
                    st.info("La curva de densidad (KDE) muestra cuándo se concentró el mayor volumen de casos según el día del año.")

            with tab2:
                st.write("#### Proporción por Método de Diagnóstico")
                fig_pie = px.pie(
                    df_filtered, 
                    names='METODODX', 
                    hole=0.4, 
                    color_discrete_sequence=px.colors.qualitative.Safe,
                    title="Distribución de Pruebas Realizadas"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                with st.expander("ℹ️ Ayuda del Gráfico"):
                    st.info("Visualización interactiva que permite ver el porcentaje de uso de cada tipo de prueba diagnóstica.")

            with tab3:
                st.markdown(f"""
                ### Detalle Técnico
                **Analista:** Cristian Serna  
                **Librerías principales:** Streamlit, Seaborn, Plotly, Pandas.  
                **Dataset:** Peru COVID-19 August 2020 (Kaggle).
                
                #### Proceso de Datos:
                Se realizó un preprocesamiento para estandarizar las fechas y eliminar registros incompletos 
                que pudieran sesgar el análisis geográfico.
                """)
                st.metric("Total de casos filtrados", f"{len(df_filtered):,}")

    else:
        st.error("No se pudo establecer la conexión con los datos. Verifica tu conexión a internet.")

st.sidebar.markdown("---")
st.sidebar.caption("Desarrollado por Cristian Serna | Talento TECH")
