import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import kagglehub
import os

# CONFIGURACIÓN PROFESIONAL DE LA PÁGINA
st.set_page_config(
    page_title="COVID-19 Perú | Cristian Serna",
    page_icon="🧬",
    layout="wide"
)

# CARGA DE DATOS OPTIMIZADA
@st.cache_data
def load_data():
    try:
        path = kagglehub.dataset_download("martinclark/peru-covid19-august-2020")
        files = [f for f in os.listdir(path) if f.endswith('.csv')]
        full_path = os.path.join(path, files[0])
        df = pd.read_csv(full_path)
        if 'FECHA_RESULTADO' in df.columns:
            df['FECHA_RESULTADO'] = pd.to_datetime(df['FECHA_RESULTADO'], errors='coerce')
        df = df.dropna(subset=['DEPARTAMENTO', 'METODODX'])
        return df
    except Exception as e:
        st.error(f"Error al conectar con Kaggle: {e}")
        return None

# NAVEGACIÓN ENTRE LANDING Y DASHBOARD
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'landing'

# --- VISTA 1: LANDING PAGE ---
if st.session_state.current_page == 'landing':
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.title("🧬 Análisis Epidemiológico COVID-19 Perú")
        st.subheader("Proyecto Integrador - Talento TECH")
        st.write("""
        Bienvenido a la plataforma de análisis de datos. Este sistema permite explorar 
        el impacto del COVID-19 en el territorio peruano mediante el uso de herramientas 
        avanzadas de Data Science.
        
        **¿Qué encontrarás aquí?**
        - Distribución geográfica de casos.
        - Análisis de métodos de diagnóstico.
        - Tendencias temporales con densidad estadística.
        
        **Analista:** Cristian Serna
        """)
        if st.button("Ingresar al Panel de Trabajo ➔", type="primary"):
            st.session_state.current_page = 'dashboard'
            st.rerun()

    with col2:
        # Imagen representativa del dataset
        st.image("https://raw.githubusercontent.com/CristianSerna/assets/main/covid_viz.png", 
                 caption="Visualización de la estructura viral SARS-CoV-2", 
                 use_container_width=True)

# --- VISTA 2: DASHBOARD ---
elif st.session_state.current_page == 'dashboard':
    st.sidebar.title("🛠️ Panel de Control")
    if st.sidebar.button("🏠 Volver al Inicio"):
        st.session_state.current_page = 'landing'
        st.rerun()

    df = load_data()
    
    if df is not None:
        # Filtros en el sidebar
        regiones = st.sidebar.multiselect(
            "Selecciona Departamentos:",
            options=sorted(df['DEPARTAMENTO'].unique()),
            default=sorted(df['DEPARTAMENTO'].unique())[:6]
        )
        
        df_filtered = df[df['DEPARTAMENTO'].isin(regiones)]

        # Tabs de organización
        tab_viz, tab_data, tab_info = st.tabs(["📈 Gráficos", "📋 Datos", "📄 Documentación"])

        with tab_viz:
            col_a, col_b = st.columns(2)

            with col_a:
                st.write("#### 📊 Casos por Departamento (Seaborn)")
                fig, ax = plt.subplots()
                sns.countplot(data=df_filtered, y='DEPARTAMENTO', palette='magma', ax=ax)
                st.pyplot(fig)
                st.info("💡 **Ayuda:** Este gráfico muestra el volumen total de contagios por región seleccionada.")

            with col_b:
                st.write("#### 🧪 Proporción de Métodos DX")
                fig_pie = px.pie(df_filtered, names='METODODX', hole=0.3, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_pie, use_container_width=True)
                st.info("💡 **Ayuda:** Compara el uso de Pruebas Rápidas vs Moleculares.")

            st.divider()
            st.write("#### 📉 Curva de Densidad Temporal (Análisis Avanzado)")
            fig_kde, ax_kde = plt.subplots(figsize=(10, 4))
            df_filtered['Day'] = df_filtered['FECHA_RESULTADO'].dt.dayofyear
            sns.kdeplot(data=df_filtered, x='Day', hue='DEPARTAMENTO', fill=True, ax=ax_kde)
            st.pyplot(fig_kde)

        with tab_data:
            st.subheader("Muestra del Dataset Filtrado")
            st.dataframe(df_filtered.head(50), use_container_width=True)

        with tab_info:
            st.markdown("""
            ### Metodología de Análisis
            - **Fuente:** Dataset de Martin Clark en Kaggle (Agosto 2020).
            - **Herramientas:** Python, Streamlit, Seaborn para estadística y Plotly para interacción.
            - **Limpieza:** Se eliminaron valores nulos en departamentos y se normalizaron las fechas.
            """)
