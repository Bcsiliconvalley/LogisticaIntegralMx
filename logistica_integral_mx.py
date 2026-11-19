import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
import os
import json
from datetime import date

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Logística Integral MX - Huella y Rutas",
    page_icon="🚚",
    layout="wide"
)

# --- CSS PERSONALIZADO (DARK MODE) ---
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    [data-testid="stSidebar"] {
        background-color: #161B22 !important;
        border-right: 1px solid #30363D;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
        display: none !important; width: 0 !important; margin: 0 !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        background-color: transparent;
        border-radius: 6px;
        padding: 10px 15px;
        margin-bottom: 2px;
        cursor: pointer;
        border-left: 4px solid transparent;
        width: 100%;
        transition: all 0.2s ease;
        color: #C9D1D9 !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background-color: rgba(255, 255, 255, 0.05);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
        background-color: rgba(0, 122, 255, 0.15) !important;
        border-left: 4px solid #007AFF !important;
        font-weight: bold;
        color: #FFFFFF !important;
    }
    div[data-baseweb="input"] input,
    div[data-baseweb="select"] > div,
    textarea {
        background-color: #0D1117 !important;
        color: #FAFAFA !important;
        border: 1px solid #30363D !important;
    }
    button[data-baseweb="tab"] {
        color: #8B949E !important;
        background-color: transparent !important;
    }
    button[aria-selected="true"] {
        color: #FFFFFF !important;
        border-bottom-color: #007AFF !important;
    }
</style>
""", unsafe_allow_html=True)

# --- CONSTANTES Y ARCHIVOS DE DATOS ---
LOGO_FILENAME = "LogisticaIntegralLogo.jpeg"
USERS_FILE = "users_logistica.json"

FILE_CONDUCTORES = "registro_conductores.csv"
FILE_RUTAS = "registro_rutas.csv"
FILE_COMBUSTIBLE = "registro_combustible.csv"

FACTOR_CO2_DIESEL = 2.68  # kg de CO2 estimados por litro de diésel quemado
UNIDADES_VAN = ["VAN-01", "VAN-02", "VAN-03"]
CONDUCTORES = ["COND-01 (Carlos M.)", "COND-02 (Luis R.)", "COND-03 (Jorge H.)", "COND-04 (Diego S.)"]


# --- INICIALIZACIÓN DE ARCHIVOS CSV ---
def inicializar_archivos():
    if not os.path.exists(FILE_CONDUCTORES):
        pd.DataFrame({
            "Fecha": ["2026-11-18", "2026-11-18", "2026-11-18"],
            "Conductor": ["COND-01 (Carlos M.)", "COND-02 (Luis R.)", "COND-03 (Jorge H.)"],
            "Camioneta": ["VAN-01", "VAN-02", "VAN-03"],
            "Km_Inicial": [45120.0, 38900.0, 51200.0],
            "Km_Final": [45245.0, 39040.0, 51310.0],
            "Km_Recorridos": [125.0, 140.0, 110.0],
            "Diesel_Usado_L": [18.5, 22.0, 15.0],
            "Paquetes_Entregados": [42, 38, 35],
            "Entregas_Fallidas": [3, 5, 2],
            "Tiempo_Recorrido_Hr": [6.5, 7.2, 5.8],
            "Incidencias": ["Tráfico pesado en av. principal", "Cliente ausente en 3 domicilios", "Sin incidencias"]
        }).to_csv(FILE_CONDUCTORES, index=False)

    if not os.path.exists(FILE_RUTAS):
        pd.DataFrame({
            "Fecha": ["2026-11-18", "2026-11-18", "2026-11-18"],
            "Camioneta": ["VAN-01", "VAN-02", "VAN-03"],
            "Punto_Salida": ["CEDIS Central", "CEDIS Central", "CEDIS Central"],
            "Destinos": ["Zona Norte / Centro", "Zona Poniente / Industrial", "Zona Sur / Residencial"],
            "Distancia_Estimada_Km": [110.0, 120.0, 100.0],
            "Distancia_Real_Km": [125.0, 140.0, 110.0],
            "Num_Paradas": [28, 32, 24],
            "Tiempo_Estimado_Hr": [5.5, 6.0, 5.0],
            "Tiempo_Real_Hr": [6.5, 7.2, 5.8],
            "Observaciones": ["Desvío por obra vial", "Ruta con retornos innecesarios", "Buen rendimiento general"]
        }).to_csv(FILE_RUTAS, index=False)

    if not os.path.exists(FILE_COMBUSTIBLE):
        pd.DataFrame({
            "Fecha": ["2026-11-18", "2026-11-18"],
            "Camioneta": ["VAN-01", "VAN-02"],
            "Diesel_Cargado_L": [45.0, 50.0],
            "Costo_Combustible": [1080.0, 1200.0],
            "Kilometraje_Unidad": [45245.0, 39040.0],
            "Mantenimiento": ["Revisión de presión de neumáticos", "Cambio de filtros de aire y diésel"],
            "Observaciones": ["Carga completa al cierre de turno", "Listo para jornada matutina"]
        }).to_csv(FILE_COMBUSTIBLE, index=False)

inicializar_archivos()

def cargar_csv(ruta):
    return pd.read_csv(ruta)

def guardar_csv(df, ruta):
    df.to_csv(ruta, index=False)

# --- MANEJO DE USUARIOS ---
def cargar_usuarios():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    default_credentials = {
        "usernames": {
            "admin": {
                "name": "Dirección Operativa",
                "password": stauth.Hasher.hash("123"),
                "email": "admin@logisticaintegralmx.com",
                "role": "Administrador"
            },
            "admin_staff": {
                "name": "Personal Administrativo",
                "password": stauth.Hasher.hash("456"),
                "email": "rutas@logisticaintegralmx.com",
                "role": "Administrativo"
            },
            "conductor1": {
                "name": "Carlos M. (COND-01)",
                "password": stauth.Hasher.hash("789"),
                "email": "cond1@logisticaintegralmx.com",
                "role": "Conductor"
            }
        }
    }
    with open(USERS_FILE, "w") as f:
        json.dump(default_credentials, f)
    return default_credentials

credentials = cargar_usuarios()


def render_mapa_leaflet(puntos: list, altura: int = 440):
    puntos_json = json.dumps(puntos)
    lat_centro = puntos[0]["lat"] if puntos else 19.4326
    lon_centro = puntos[0]["lon"] if puntos else -99.1332

    html_mapa = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            html, body, #map {{
                height: 100%;
                width: 100%;
                margin: 0;
                padding: 0;
                background-color: #0E1117;
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            var puntos = {puntos_json};
            var map = L.map('map').setView([{lat_centro}, {lon_centro}], 11);

            L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                maxZoom: 19,
                attribution: '&copy; OpenStreetMap contributors'
            }}).addTo(map);

            var coordsRuta = [];
            puntos.forEach(function(p, idx) {{
                var latlng = [p.lat, p.lon];
                coordsRuta.push(latlng);
                L.marker(latlng)
                    .addTo(map)
                    .bindPopup("<b>" + (idx + 1) + ". " + p.nombre + "</b><br>" + p.desc);
            }});

            if (coordsRuta.length > 1) {{
                coordsRuta.push(coordsRuta[0]);
                var polyline = L.polyline(coordsRuta, {{
                    color: '#007AFF',
                    weight: 4,
                    opacity: 0.9
                }}).addTo(map);
                map.fitBounds(polyline.getBounds(), {{ padding: [25, 25] }});
            }}
        </script>
    </body>
    </html>
    """
    st.components.v1.html(html_mapa, height=altura)


# ==========================================
# --- MÓDULOS DEL SISTEMA ---
# ==========================================

def modulo_panel_general():
    st.subheader("📊 Panel General - Logística Integral MX")
    st.caption("Monitoreo operativo de flota (3 VANs), consumo de diésel y huella de carbono.")

    df_cond = cargar_csv(FILE_CONDUCTORES)
    df_comb = cargar_csv(FILE_COMBUSTIBLE)
    df_rutas = cargar_csv(FILE_RUTAS)

    total_litros = df_cond["Diesel_Usado_L"].sum() if not df_cond.empty else 0.0
    total_co2 = total_litros * FACTOR_CO2_DIESEL
    total_gasto = df_comb["Costo_Combustible"].sum() if not df_comb.empty else 0.0
    total_entregas = df_cond["Paquetes_Entregados"].sum() if not df_cond.empty else 0
    total_fallidas = df_cond["Entregas_Fallidas"].sum() if not df_cond.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Diésel Consumido", f"{total_litros:,.1f} L")
    col2.metric("Huella CO₂ Estimada", f"{total_co2:,.1f} kg CO₂", delta="-8.5% meta", delta_color="normal")
    col3.metric("Gasto en Diésel", f"${total_gasto:,.2f} MXN")
    col4.metric("Paquetes Entregados", f"{int(total_entregas)}", f"{int(total_fallidas)} fallidas")

    st.divider()

    c_izq, c_der = st.columns(2)
    with c_izq:
        st.markdown("### ⛽ Emisiones de CO₂ por Unidad (kg)")
        if not df_cond.empty:
            co2_van = df_cond.groupby("Camioneta")["Diesel_Usado_L"].sum() * FACTOR_CO2_DIESEL
            st.bar_chart(co2_van)
    with c_der:
        st.markdown("### 📦 Entregas vs. Fallidas por Conductor")
        if not df_cond.empty:
            ent_cond = df_cond.groupby("Conductor")[["Paquetes_Entregados", "Entregas_Fallidas"]].sum()
            st.bar_chart(ent_cond)

    st.divider()
    st.markdown("### 🛣️ Desviación de Rutas (Estimado vs. Real)")
    if not df_rutas.empty:
        df_vista = df_rutas.copy()
        df_vista["Desviacion_Km"] = df_vista["Distancia_Real_Km"] - df_vista["Distancia_Estimada_Km"]
        st.dataframe(df_vista, use_container_width=True)


def modulo_captura_formatos():
    st.subheader("📝 Captura de Formatos Operativos")
    st.write("Registra la información diaria para alimentar el cálculo de rutas, costos y emisiones.")

    tab1, tab2, tab3 = st.tabs([
        "Formato 1: Registro Diario del Conductor",
        "Formato 2: Registro de Rutas de Entrega",
        "Formato 3: Combustible y Mantenimiento"
    ])

    # --- FORMATO 1: CONDUCTOR ---
    with tab1:
        st.markdown("#### Responsable: Conductor de la camioneta")
        with st.form("form_f1", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            fecha_f1 = c1.date_input("Fecha", value=date.today(), key="f1_fecha")
            conductor_f1 = c2.selectbox("Nombre o clave del conductor", CONDUCTORES, key="f1_cond")
            van_f1 = c3.selectbox("Número de camioneta", UNIDADES_VAN, key="f1_van")

            c4, c5, c6 = st.columns(3)
            km_ini = c4.number_input("Kilometraje inicial (km)", min_value=0.0, step=1.0, value=45000.0)
            km_fin = c5.number_input("Kilometraje final (km)", min_value=0.0, step=1.0, value=45120.0)
            diesel_f1 = c6.number_input("Litros de diésel utilizados (L)", min_value=0.0, step=0.5, value=18.0)

            c7, c8, c9 = st.columns(3)
            entregados = c7.number_input("Paquetes entregados", min_value=0, step=1, value=30)
            fallidas = c8.number_input("Entregas fallidas", min_value=0, step=1, value=2)
            tiempo_f1 = c9.number_input("Tiempo total del recorrido (horas)", min_value=0.1, step=0.1, value=6.0)

            incidencias_f1 = st.text_area("Incidencias durante la ruta", placeholder="Tráfico, cierres viales, dirección incorrecta, etc.")
            submitted_f1 = st.form_submit_button("Guardar Formato 1")

            if submitted_f1:
                if km_fin < km_ini:
                    st.error("El kilometraje final no puede ser menor al kilometraje inicial.")
                else:
                    df = cargar_csv(FILE_CONDUCTORES)
                    nuevo = pd.DataFrame([{
                        "Fecha": str(fecha_f1),
                        "Conductor": conductor_f1,
                        "Camioneta": van_f1,
                        "Km_Inicial": km_ini,
                        "Km_Final": km_fin,
                        "Km_Recorridos": round(km_fin - km_ini, 2),
                        "Diesel_Usado_L": diesel_f1,
                        "Paquetes_Entregados": entregados,
                        "Entregas_Fallidas": fallidas,
                        "Tiempo_Recorrido_Hr": tiempo_f1,
                        "Incidencias": incidencias_f1.strip() or "Sin incidencias"
                    }])
                    df = pd.concat([df, nuevo], ignore_index=True)
                    guardar_csv(df, FILE_CONDUCTORES)
                    st.success("Formato 1 guardado correctamente.")

    # --- FORMATO 2: RUTAS ---
    with tab2:
        st.markdown("#### Responsable: Personal administrativo")
        with st.form("form_f2", clear_on_submit=True):
            c1, c2 = st.columns(2)
            fecha_f2 = c1.date_input("Fecha", value=date.today(), key="f2_fecha")
            van_f2 = c2.selectbox("Número de camioneta", UNIDADES_VAN, key="f2_van")

            c3, c4 = st.columns(2)
            salida_f2 = c3.text_input("Punto de salida", value="CEDIS Central")
            destinos_f2 = c4.text_input("Destinos de entrega", placeholder="Ej. Colonia Centro, Zona Industrial, Parque Sur")

            c5, c6, c7 = st.columns(3)
            dist_est = c5.number_input("Distancia estimada de la ruta (km)", min_value=0.0, step=1.0, value=100.0)
            dist_real = c6.number_input("Distancia real recorrida (km)", min_value=0.0, step=1.0, value=115.0)
            paradas = c7.number_input("Número de paradas", min_value=1, step=1, value=25)

            c8, c9 = st.columns(2)
            tiempo_est = c8.number_input("Tiempo estimado de la ruta (horas)", min_value=0.1, step=0.1, value=5.0)
            tiempo_real = c9.number_input("Tiempo real de la ruta (horas)", min_value=0.1, step=0.1, value=6.2)

            obs_f2 = st.text_area("Observaciones", placeholder="Notas relevantes sobre tráfico, desvíos o zonas")
            submitted_f2 = st.form_submit_button("Guardar Formato 2")

            if submitted_f2:
                df = cargar_csv(FILE_RUTAS)
                nuevo = pd.DataFrame([{
                    "Fecha": str(fecha_f2),
                    "Camioneta": van_f2,
                    "Punto_Salida": salida_f2.strip(),
                    "Destinos": destinos_f2.strip() or "No especificados",
                    "Distancia_Estimada_Km": dist_est,
                    "Distancia_Real_Km": dist_real,
                    "Num_Paradas": paradas,
                    "Tiempo_Estimado_Hr": tiempo_est,
                    "Tiempo_Real_Hr": tiempo_real,
                    "Observaciones": obs_f2.strip() or "Sin observaciones"
                }])
                df = pd.concat([df, nuevo], ignore_index=True)
                guardar_csv(df, FILE_RUTAS)
                st.success("Formato 2 guardado correctamente.")

    # --- FORMATO 3: COMBUSTIBLE Y MANTENIMIENTO ---
    with tab3:
        st.markdown("#### Responsables: Conductor y personal administrativo")
        with st.form("form_f3", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            fecha_f3 = c1.date_input("Fecha", value=date.today(), key="f3_fecha")
            van_f3 = c2.selectbox("Número de camioneta", UNIDADES_VAN, key="f3_van")
            km_uni = c3.number_input("Kilometraje de la unidad (km)", min_value=0.0, step=1.0, value=45120.0)

            c4, c5 = st.columns(2)
            litros_cargados = c4.number_input("Litros de diésel cargados (L)", min_value=0.0, step=0.5, value=40.0)
            costo_comb = c5.number_input("Costo del combustible ($)", min_value=0.0, step=10.0, value=960.0)

            mant_f3 = st.text_input("Mantenimiento realizado", placeholder="Ej. Cambio de aceite, llantas, frenos o Ninguno")
            obs_f3 = st.text_area("Observaciones sobre la unidad", placeholder="Ruidos, testigos encendidos, rendimiento, etc.")
            submitted_f3 = st.form_submit_button("Guardar Formato 3")

            if submitted_f3:
                df = cargar_csv(FILE_COMBUSTIBLE)
                nuevo = pd.DataFrame([{
                    "Fecha": str(fecha_f3),
                    "Camioneta": van_f3,
                    "Diesel_Cargado_L": litros_cargados,
                    "Costo_Combustible": costo_comb,
                    "Kilometraje_Unidad": km_uni,
                    "Mantenimiento": mant_f3.strip() or "Ninguno",
                    "Observaciones": obs_f3.strip() or "Sin observaciones"
                }])
                df = pd.concat([df, nuevo], ignore_index=True)
                guardar_csv(df, FILE_COMBUSTIBLE)
                st.success("Formato 3 guardado correctamente.")


def modulo_co2_y_costos():
    st.subheader("🌿 Cálculo de Huella de Carbono y Control de Combustible")
    df_cond = cargar_csv(FILE_CONDUCTORES)
    df_comb = cargar_csv(FILE_COMBUSTIBLE)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Simulador de Emisiones por Jornada")
        litros_sim = st.slider("Litros de diésel consumidos:", 1.0, 120.0, 25.0, step=0.5)
        precio_litro = st.number_input("Precio promedio por litro de diésel ($):", min_value=1.0, value=24.0)
        co2_sim = litros_sim * FACTOR_CO2_DIESEL
        costo_sim = litros_sim * precio_litro
        st.metric("Emisión Estimada", f"{co2_sim:.2f} kg CO₂")
        st.metric("Costo Estimado", f"${costo_sim:,.2f}")

    with c2:
        st.markdown("### Rendimiento Histórico por Camioneta")
        if not df_cond.empty:
            resumen = df_cond.groupby("Camioneta").agg(
                Km_Totales=("Km_Recorridos", "sum"),
                Diesel_L=("Diesel_Usado_L", "sum"),
                Entregas=("Paquetes_Entregados", "sum"),
                Fallidas=("Entregas_Fallidas", "sum")
            ).reset_index()
            resumen["Rendimiento_Km_L"] = (resumen["Km_Totales"] / resumen["Diesel_L"].replace(0, pd.NA)).round(2)
            resumen["CO2_kg"] = (resumen["Diesel_L"] * FACTOR_CO2_DIESEL).round(2)
            st.dataframe(resumen, use_container_width=True)

    st.divider()
    st.markdown("### 📋 Bitácora de Combustible y Mantenimiento (Formato 3)")
    st.dataframe(df_comb, use_container_width=True)


def modulo_optimizacion_rutas():
    st.subheader("🚚 Optimización de Rutas y Oportunidades de Mejora")
    df_rutas = cargar_csv(FILE_RUTAS)
    df_cond = cargar_csv(FILE_CONDUCTORES)

    if not df_rutas.empty:
        df_analisis = df_rutas.copy()
        df_analisis["Km_Extra"] = df_analisis["Distancia_Real_Km"] - df_analisis["Distancia_Estimada_Km"]
        df_analisis["CO2_Extra_Est_kg"] = (df_analisis["Km_Extra"].clip(lower=0) * 0.22).round(2)

        st.markdown("### 🔍 Detección de Recorridos Excesivos")
        st.dataframe(df_analisis[[
            "Fecha", "Camioneta", "Punto_Salida", "Destinos",
            "Distancia_Estimada_Km", "Distancia_Real_Km", "Km_Extra",
            "Num_Paradas", "CO2_Extra_Est_kg", "Observaciones"
        ]], use_container_width=True)

        excesos = df_analisis[df_analisis["Km_Extra"] > 5]
        if not excesos.empty:
            for _, fila in excesos.iterrows():
                st.warning(
                    f"**{fila['Camioneta']} ({fila['Fecha']})** recorrió **{fila['Km_Extra']:.1f} km** por encima de lo estimado en *{fila['Destinos']}*. "
                    f"Revisar secuencia de {int(fila['Num_Paradas'])} paradas y evitar retornos."
                )
        else:
            st.success("Todas las rutas están dentro del margen esperado de kilometraje.")

    st.divider()
    st.markdown("### 🗺️ Visualización de Ruta de Distribución")

    van_sel = st.selectbox("Selecciona unidad para visualizar su ruta:", UNIDADES_VAN, key="mapa_van_sel")

    rutas_por_van = {
        "VAN-01": [
            {"nombre": "CEDIS Central", "lat": 19.4326, "lon": -99.1332, "desc": "Punto de salida"},
            {"nombre": "Zona Norte", "lat": 19.4900, "lon": -99.1400, "desc": "Parada 1 - Paquetería"},
            {"nombre": "Centro Histórico", "lat": 19.4360, "lon": -99.1310, "desc": "Parada 2 - Paquetería"},
        ],
        "VAN-02": [
            {"nombre": "CEDIS Central", "lat": 19.4326, "lon": -99.1332, "desc": "Punto de salida"},
            {"nombre": "Zona Poniente", "lat": 19.4200, "lon": -99.2100, "desc": "Parada 1 - Corredor Industrial"},
            {"nombre": "Polanco / Reforma", "lat": 19.4330, "lon": -99.1900, "desc": "Parada 2 - Paquetería"},
        ],
        "VAN-03": [
            {"nombre": "CEDIS Central", "lat": 19.4326, "lon": -99.1332, "desc": "Punto de salida"},
            {"nombre": "Zona Sur", "lat": 19.3500, "lon": -99.1600, "desc": "Parada 1 - Residencial"},
            {"nombre": "Coyoacán", "lat": 19.3467, "lon": -99.1618, "desc": "Parada 2 - Paquetería"},
        ],
    }

    render_mapa_leaflet(rutas_por_van[van_sel], altura=440)

    if not df_cond.empty:
        st.divider()
        st.markdown("### 📋 Bitácora de Conductores (Formato 1)")
        st.dataframe(df_cond, use_container_width=True)


def modulo_configuracion():
    st.subheader("⚙️ Configuración del Sistema")
    st.text_input("Empresa", value="Logística Integral MX", disabled=True)
    st.text_input("Flota registrada", value="3 Camionetas tipo VAN | 4 Conductores | 2 Administrativos", disabled=True)
    st.number_input("Factor de emisión de diésel (kg CO₂ / L)", value=FACTOR_CO2_DIESEL, disabled=True)
    st.toggle("Alertas por desviación de ruta > 10 km", value=True)
    st.toggle("Alertas por entregas fallidas elevadas", value=True)
    if st.button("Guardar Preferencias"):
        st.success("Preferencias actualizadas.")


# ==========================================
# --- 1. SISTEMA DE LOGIN Y REGISTRO ---
# ==========================================
authenticator = stauth.Authenticate(
    credentials,
    "logistica_integral_mx_dash",
    "logistica_auth_cookie",
    cookie_expiry_days=30
)
authentication_status = st.session_state.get("authentication_status")

if authentication_status is None or authentication_status is False:
    st.write("")
    st.write("")
    col_izq, col_der = st.columns([1.5, 1], gap="large")

    with col_izq:
        st.write("")
        _, centro_logo, _ = st.columns([1, 1.5, 1])
        with centro_logo:
            if os.path.exists(LOGO_FILENAME):
                st.image(LOGO_FILENAME, use_container_width=True)
            else:
                st.info(f"💡 Coloca tu logo aquí con el nombre: {LOGO_FILENAME}")

        st.markdown("<h1 style='text-align: center; color: #FFFFFF;'>Logística Integral MX</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #8B949E;'>Control de Rutas y Huella de Carbono</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6E7681;'>Paquetería en Línea · Eficiencia de Diésel · Trazabilidad Operativa</p>", unsafe_allow_html=True)

    with col_der:
        st.markdown("### Acceso al Sistema")
        tab_login, tab_registro = st.tabs(["🔐 Ingresar", "📝 Registrarse"])

        with tab_login:
            authenticator.login(location="main")
            if authentication_status is False:
                st.error("Usuario o contraseña incorrectos")
            elif authentication_status is None:
                st.warning("Ingresa tus credenciales")

        with tab_registro:
            with st.form("registro_form"):
                nuevo_nombre = st.text_input("Nombre Completo:")
                nuevo_usuario = st.text_input("Usuario:")
                nueva_password = st.text_input("Contraseña:", type="password")
                nuevo_rol = st.selectbox("Rol:", ["Conductor", "Administrativo", "Administrador"])
                btn_registro = st.form_submit_button("Crear Cuenta")

                if btn_registro:
                    if not nuevo_nombre or not nuevo_usuario or not nueva_password:
                        st.error("Llena todos los campos.")
                    elif nuevo_usuario in credentials["usernames"]:
                        st.error("Usuario ya en uso.")
                    else:
                        credentials["usernames"][nuevo_usuario] = {
                            "name": nuevo_nombre,
                            "password": stauth.Hasher.hash(nueva_password),
                            "email": "",
                            "role": nuevo_rol
                        }
                        with open(USERS_FILE, "w") as f:
                            json.dump(credentials, f)
                        st.success(f"¡Cuenta creada para {nuevo_nombre}!")

elif authentication_status:
    name = st.session_state.get("name")
    username = st.session_state.get("username")
    user_role = credentials["usernames"].get(username, {}).get("role", "Administrativo")

    with st.sidebar:
        if os.path.exists(LOGO_FILENAME):
            st.image(LOGO_FILENAME, use_container_width=True)
        else:
            st.warning("Logo no encontrado")

        st.title("Menú Principal")
        st.write(f"Bienvenido, **{name}**")
        st.write(f"Rol: **{user_role}**")
        st.divider()

        opciones_menu = ["📊 Panel General", "📝 Captura de Formatos"]

        if user_role != "Conductor":
            opciones_menu.append("🌿 CO₂ y Combustible")

        opciones_menu.append("🚚 Rutas y Mejoras")

        if user_role == "Administrador":
            opciones_menu.append("⚙️ Configuración")

        opcion = st.radio("Selecciona un módulo:", opciones_menu, label_visibility="collapsed")
        st.divider()
        authenticator.logout("Cerrar Sesión", location="sidebar")

    st.title("🚚 Logística Integral MX")
    st.subheader(f"Operación, Combustible y Huella de Carbono ({user_role})")
    st.divider()

    if opcion == "📊 Panel General":
        modulo_panel_general()
    elif opcion == "📝 Captura de Formatos":
        modulo_captura_formatos()
    elif opcion == "🌿 CO₂ y Combustible":
        modulo_co2_y_costos()
    elif opcion == "🚚 Rutas y Mejoras":
        modulo_optimizacion_rutas()
    elif opcion == "⚙️ Configuración":
        modulo_configuracion()
