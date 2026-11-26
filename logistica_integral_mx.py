import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import LoginError
import os
import json
from datetime import date
from urllib.parse import quote

from db import (
    consultar,
    cargar_credenciales,
    crear_usuario,
    asegurar_usuarios_demo,
    describir_conexion,
    cookie_key,
    id_usuario,
    conductor_de_usuario,
    lista_unidades,
    lista_conductores,
    paradas_de_unidad,
    df_conductores,
    df_rutas,
    df_combustible,
    guardar_registro_conductor,
    guardar_ruta,
    guardar_combustible,
    parametro,
    actualizar_parametro,
)

# ==========================================
# --- ÍCONOS SVG (reemplazan a los emojis) ---
# ==========================================
ICONOS = {
    "camion": '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>',
    "panel": '<path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
    "portapapeles": '<rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M12 11h4"/><path d="M12 16h4"/><path d="M8 11h.01"/><path d="M8 16h.01"/>',
    "hoja": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
    "config": '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/>',
    "combustible": '<line x1="3" x2="15" y1="22" y2="22"/><line x1="4" x2="14" y1="9" y2="9"/><path d="M14 22V4a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v18"/><path d="M14 13h2a2 2 0 0 1 2 2v2a2 2 0 0 0 2 2a2 2 0 0 0 2-2V9.83a2 2 0 0 0-.59-1.42L18 5"/>',
    "paquete": '<path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>',
    "ruta": '<circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/><circle cx="18" cy="5" r="3"/>',
    "usuario": '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "buscar": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "mapa": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "candado": '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "usuario_mas": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M19 8v6"/><path d="M22 11h-6"/>',
}


def svg_html(nombre, size=20, color="currentColor"):
    """SVG en línea para usar dentro de HTML/markdown."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round" '
        f'style="vertical-align:-0.15em;flex-shrink:0">{ICONOS[nombre]}</svg>'
    )


def encabezado(nombre, texto, nivel=3):
    """Encabezado con ícono SVG (reemplaza st.title / st.subheader / '### ' con emoji)."""
    tamanos = {1: 36, 2: 30, 3: 24, 4: 20}
    st.markdown(
        f'<h{nivel} style="display:flex;align-items:center;gap:0.5rem;margin:0;padding:0.5rem 0">'
        f'{svg_html(nombre, tamanos.get(nivel, 20))}<span>{texto}</span></h{nivel}>',
        unsafe_allow_html=True,
    )


def _svg_data_uri(nombre):
    s = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        'stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'{ICONOS[nombre]}</svg>'
    )
    return "data:image/svg+xml;utf8," + quote(s, safe="")


def inyectar_iconos(selector, nombres):
    """
    Pone un ícono SVG (como máscara, hereda el color del texto) antes de cada elemento
    que coincida con `selector`, en orden. Sirve para tabs y radios, cuyas etiquetas no aceptan HTML.
    """
    reglas = (
        f"{selector}::before {{ content: ''; display: inline-block; flex-shrink: 0; "
        "width: 1.15em; height: 1.15em; margin-right: 10px; align-self: center; "
        "background-color: currentColor; "
        "-webkit-mask-repeat: no-repeat; mask-repeat: no-repeat; "
        "-webkit-mask-position: center; mask-position: center; "
        "-webkit-mask-size: contain; mask-size: contain; }\n"
    )
    for i, nombre in enumerate(nombres, start=1):
        uri = _svg_data_uri(nombre)
        reglas += (
            f"{selector}:nth-of-type({i})::before "
            f'{{ -webkit-mask-image: url("{uri}"); mask-image: url("{uri}"); }}\n'
        )
    st.markdown(f"<style>{reglas}</style>", unsafe_allow_html=True)


SELECTOR_TABS = 'div[role="tablist"] > button[data-baseweb="tab"]'
SELECTOR_MENU = '[data-testid="stSidebar"] div[role="radiogroup"] > label'

# --- Favicon SVG (page_icon acepta una ruta a archivo) ---
FAVICON = "favicon_logistica.svg"
if not os.path.exists(FAVICON):
    with open(FAVICON, "w", encoding="utf-8") as f:
        f.write(svg_html("camion", 64, "#007AFF"))

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Logística Integral MX - Huella y Rutas",
    page_icon=FAVICON,
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

LOGO_FILENAME = "LogisticaIntegralLogo.jpeg"

# --- USUARIOS DESDE MYSQL ---
try:
    asegurar_usuarios_demo()
    credentials = cargar_credenciales()
except Exception as e:
    st.error(
        "No se pudo conectar con la base de datos. Revisa que MySQL esté encendido, que hayas importado "
        "database/esquema_logistica.sql y los datos de .streamlit/secrets.toml."
    )
    st.code(str(e))
    try:
        st.caption(describir_conexion())
    except Exception as e2:
        st.caption(f"No se pudo leer secrets.toml: {e2}")
    st.stop()


def render_mapa_leaflet(puntos: list, altura: int = 440):
    puntos_json = json.dumps(puntos)
    lat_centro = puntos[0]["lat"] if puntos else 32.6278
    lon_centro = puntos[0]["lon"] if puntos else -115.4545

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
    encabezado("panel", "Panel General - Logística Integral MX")
    st.caption("Monitoreo operativo de flota (3 VANs), consumo de diésel y huella de carbono.")

    df_cond = df_conductores()
    df_comb = df_combustible()
    df_ru = df_rutas()
    factor = parametro("factor_co2_diesel", 2.68)

    total_litros = float(df_cond["Diesel_Usado_L"].sum()) if not df_cond.empty else 0.0
    total_co2 = total_litros * factor
    total_gasto = float(df_comb["Costo_Combustible"].sum()) if not df_comb.empty else 0.0
    total_entregas = int(df_cond["Paquetes_Entregados"].sum()) if not df_cond.empty else 0
    total_fallidas = int(df_cond["Entregas_Fallidas"].sum()) if not df_cond.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Diésel Consumido", f"{total_litros:,.1f} L")
    col2.metric("Huella CO₂ Estimada", f"{total_co2:,.1f} kg CO₂")
    col3.metric("Gasto en Diésel", f"${total_gasto:,.2f} MXN")
    col4.metric("Paquetes Entregados", f"{total_entregas}", f"{total_fallidas} fallidas", delta_color="inverse")

    st.divider()

    c_izq, c_der = st.columns(2)
    with c_izq:
        encabezado("combustible", "Emisiones de CO₂ por Unidad (kg)", nivel=4)
        if not df_cond.empty:
            co2_van = df_cond.groupby("Camioneta")["Diesel_Usado_L"].sum() * factor
            st.bar_chart(co2_van)
    with c_der:
        encabezado("paquete", "Entregas vs. Fallidas por Conductor", nivel=4)
        if not df_cond.empty:
            ent_cond = df_cond.groupby("Conductor")[["Paquetes_Entregados", "Entregas_Fallidas"]].sum()
            st.bar_chart(ent_cond)

    st.divider()
    encabezado("ruta", "Desviación de Rutas (Estimado vs. Real)", nivel=4)
    if not df_ru.empty:
        df_vista = df_ru.copy()
        df_vista["Desviacion_Km"] = df_vista["Distancia_Real_Km"] - df_vista["Distancia_Estimada_Km"]
        st.dataframe(df_vista, use_container_width=True)
    else:
        st.info("Todavía no hay rutas registradas.")


def modulo_captura_formatos(username, user_role):
    encabezado("portapapeles", "Captura de Formatos Operativos")
    st.write("Registra la información diaria para alimentar el cálculo de rutas, costos y emisiones.")

    unidades = lista_unidades()
    ids_unidad = dict(zip(unidades["codigo"], unidades["id_unidad"]))
    opciones_van = list(unidades["codigo"])
    id_usr = id_usuario(username)

    inyectar_iconos(SELECTOR_TABS, ["usuario", "ruta", "combustible"])
    tab1, tab2, tab3 = st.tabs([
        "Formato 1: Registro Diario del Conductor",
        "Formato 2: Registro de Rutas de Entrega",
        "Formato 3: Combustible y Mantenimiento"
    ])

    # --- FORMATO 1: CONDUCTOR ---
    with tab1:
        st.markdown("#### Responsable: Conductor de la camioneta")
        conductores = lista_conductores()
        ids_conductor = dict(zip(conductores["etiqueta"], conductores["id_conductor"]))
        propio = conductor_de_usuario(username) if user_role == "Conductor" else None
        opciones_cond = [propio["etiqueta"]] if propio is not None else list(conductores["etiqueta"])

        with st.form("form_f1", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            fecha_f1 = c1.date_input("Fecha", value=date.today(), key="f1_fecha")
            conductor_f1 = c2.selectbox("Nombre o clave del conductor", opciones_cond, key="f1_cond")
            van_f1 = c3.selectbox("Número de camioneta", opciones_van, key="f1_van")

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
                    guardar_registro_conductor(
                        fecha_f1, int(ids_conductor[conductor_f1]), int(ids_unidad[van_f1]),
                        km_ini, km_fin, diesel_f1, int(entregados), int(fallidas), tiempo_f1,
                        incidencias_f1.strip() or "Sin incidencias", id_usr)
                    st.success("Formato 1 guardado correctamente.")

    # --- FORMATO 2: RUTAS ---
    with tab2:
        st.markdown("#### Responsable: Personal administrativo")
        with st.form("form_f2", clear_on_submit=True):
            c1, c2 = st.columns(2)
            fecha_f2 = c1.date_input("Fecha", value=date.today(), key="f2_fecha")
            van_f2 = c2.selectbox("Número de camioneta", opciones_van, key="f2_van")

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
                guardar_ruta(
                    fecha_f2, int(ids_unidad[van_f2]), salida_f2.strip() or "CEDIS Central",
                    destinos_f2.strip() or "No especificados", dist_est, dist_real, int(paradas),
                    tiempo_est, tiempo_real, obs_f2.strip() or "Sin observaciones", id_usr)
                st.success("Formato 2 guardado correctamente.")

    # --- FORMATO 3: COMBUSTIBLE Y MANTENIMIENTO ---
    with tab3:
        st.markdown("#### Responsables: Conductor y personal administrativo")
        with st.form("form_f3", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            fecha_f3 = c1.date_input("Fecha", value=date.today(), key="f3_fecha")
            van_f3 = c2.selectbox("Número de camioneta", opciones_van, key="f3_van")
            km_uni = c3.number_input("Kilometraje de la unidad (km)", min_value=0.0, step=1.0, value=45120.0)

            c4, c5 = st.columns(2)
            litros_cargados = c4.number_input("Litros de diésel cargados (L)", min_value=0.0, step=0.5, value=40.0)
            costo_comb = c5.number_input("Costo del combustible ($)", min_value=0.0, step=10.0, value=960.0)

            mant_f3 = st.text_input("Mantenimiento realizado", placeholder="Ej. Cambio de aceite, llantas, frenos o Ninguno")
            obs_f3 = st.text_area("Observaciones sobre la unidad", placeholder="Ruidos, testigos encendidos, rendimiento, etc.")
            submitted_f3 = st.form_submit_button("Guardar Formato 3")

            if submitted_f3:
                guardar_combustible(
                    fecha_f3, int(ids_unidad[van_f3]), litros_cargados, costo_comb, km_uni,
                    mant_f3.strip() or "Ninguno", obs_f3.strip() or "Sin observaciones", id_usr)
                st.success("Formato 3 guardado correctamente.")


def modulo_co2_y_costos():
    encabezado("hoja", "Cálculo de Huella de Carbono y Control de Combustible")
    df_cond = df_conductores()
    df_comb = df_combustible()
    factor = parametro("factor_co2_diesel", 2.68)
    precio_param = parametro("precio_litro_diesel", 26.99)

    c1, c2 = st.columns(2)
    with c1:
        encabezado("combustible", "Simulador de Emisiones por Jornada", nivel=4)
        litros_sim = st.slider("Litros de diésel consumidos:", 1.0, 120.0, 25.0, step=0.5)
        precio_litro = st.number_input("Precio promedio por litro de diésel ($):", min_value=1.0, value=precio_param)
        co2_sim = litros_sim * factor
        costo_sim = litros_sim * precio_litro
        st.metric("Emisión Estimada", f"{co2_sim:.2f} kg CO₂")
        st.metric("Costo Estimado", f"${costo_sim:,.2f}")

    with c2:
        encabezado("camion", "Rendimiento Histórico por Camioneta", nivel=4)
        if not df_cond.empty:
            resumen = df_cond.groupby("Camioneta").agg(
                Km_Totales=("Km_Recorridos", "sum"),
                Diesel_L=("Diesel_Usado_L", "sum"),
                Entregas=("Paquetes_Entregados", "sum"),
                Fallidas=("Entregas_Fallidas", "sum")
            ).reset_index()
            resumen["Rendimiento_Km_L"] = (
                resumen["Km_Totales"] / resumen["Diesel_L"].where(resumen["Diesel_L"] != 0)
            ).round(2)
            resumen["CO2_kg"] = (resumen["Diesel_L"] * factor).round(2)
            st.dataframe(resumen, use_container_width=True)
        else:
            st.info("Todavía no hay registros de conductores.")

    st.divider()
    encabezado("portapapeles", "Bitácora de Combustible y Mantenimiento (Formato 3)", nivel=4)
    st.dataframe(df_comb, use_container_width=True)


def modulo_optimizacion_rutas():
    encabezado("camion", "Optimización de Rutas y Oportunidades de Mejora")
    df_ru = df_rutas()
    df_cond = df_conductores()
    umbral = parametro("umbral_km_extra", 5.0)
    co2_km = parametro("co2_kg_por_km_extra", 0.22)

    if not df_ru.empty:
        df_analisis = df_ru.copy()
        df_analisis["Km_Extra"] = df_analisis["Distancia_Real_Km"] - df_analisis["Distancia_Estimada_Km"]
        df_analisis["CO2_Extra_Est_kg"] = (df_analisis["Km_Extra"].clip(lower=0) * co2_km).round(2)

        encabezado("buscar", "Detección de Recorridos Excesivos", nivel=4)
        st.dataframe(df_analisis[[
            "Fecha", "Camioneta", "Punto_Salida", "Destinos",
            "Distancia_Estimada_Km", "Distancia_Real_Km", "Km_Extra",
            "Num_Paradas", "CO2_Extra_Est_kg", "Observaciones"
        ]], use_container_width=True)

        excesos = df_analisis[df_analisis["Km_Extra"] > umbral]
        if not excesos.empty:
            for _, fila in excesos.iterrows():
                st.warning(
                    f"**{fila['Camioneta']} ({fila['Fecha']})** recorrió **{fila['Km_Extra']:.1f} km** por encima de lo estimado en *{fila['Destinos']}*. "
                    f"Revisar secuencia de {int(fila['Num_Paradas'])} paradas y evitar retornos."
                )
        else:
            st.success("Todas las rutas están dentro del margen esperado de kilometraje.")
    else:
        st.info("Todavía no hay rutas registradas.")

    st.divider()
    encabezado("mapa", "Visualización de Ruta de Distribución", nivel=4)

    codigos = list(lista_unidades()["codigo"])
    van_sel = st.selectbox("Selecciona unidad para visualizar su ruta:", codigos, key="mapa_van_sel")
    puntos = paradas_de_unidad(van_sel)
    if puntos:
        render_mapa_leaflet(puntos, altura=440)
    else:
        st.info("Esta unidad todavía no tiene paradas registradas para el mapa.")

    if not df_cond.empty:
        st.divider()
        encabezado("portapapeles", "Bitácora de Conductores (Formato 1)", nivel=4)
        st.dataframe(df_cond, use_container_width=True)


def modulo_configuracion(username):
    encabezado("config", "Configuración del Sistema")
    st.text_input("Empresa", value="Logística Integral MX", disabled=True)
    st.text_input("Flota registrada", value="3 Camionetas tipo VAN | 4 Conductores | 2 Administrativos", disabled=True)

    encabezado("hoja", "Parámetros de cálculo", nivel=4)
    factor = parametro("factor_co2_diesel", 2.68)
    precio = parametro("precio_litro_diesel", 26.99)
    nuevo_factor = st.number_input("Factor de emisión de diésel (kg CO₂ / L)", min_value=0.0,
                                   value=factor, step=0.01, format="%.4f")
    nuevo_precio = st.number_input("Precio del diésel ($ / L)", min_value=0.0,
                                   value=precio, step=0.01, format="%.2f")
    if st.button("Guardar parámetros"):
        uid = id_usuario(username)
        actualizar_parametro("factor_co2_diesel", float(nuevo_factor), uid)
        actualizar_parametro("precio_litro_diesel", float(nuevo_precio), uid)
        st.success("Parámetros guardados.")

    st.divider()
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
    cookie_key(),
    cookie_expiry_days=30
)

# Una cookie de sesión de un usuario que ya no existe se ignora (borrarla desde aquí
# provoca recargas en bucle).
_get_cookie_original = authenticator.cookie_controller.get_cookie
def _get_cookie_valida():
    token = _get_cookie_original()
    if token and token.get("username") not in credentials["usernames"]:
        return None
    return token
authenticator.cookie_controller.get_cookie = _get_cookie_valida

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
                st.info(f"Coloca tu logo aquí con el nombre: {LOGO_FILENAME}")

        st.markdown("<h1 style='text-align: center; color: #FFFFFF;'>Logística Integral MX</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #8B949E;'>Control de Rutas y Huella de Carbono</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6E7681;'>Paquetería en Línea · Eficiencia de Diésel · Trazabilidad Operativa</p>", unsafe_allow_html=True)

    with col_der:
        st.markdown("### Acceso al Sistema")
        inyectar_iconos(SELECTOR_TABS, ["candado", "usuario_mas"])
        tab_login, tab_registro = st.tabs(["Ingresar", "Registrarse"])

        with tab_login:
            try:
                authenticator.login(location="main")
            except LoginError as e:
                st.warning(f"No se pudo iniciar sesión: {e}")
            if authentication_status is False:
                st.error("Usuario o contraseña incorrectos")
            elif authentication_status is None:
                st.warning("Ingresa tus credenciales")

        with tab_registro:
            # El registro público solo crea cuentas de conductor; los roles administrativo y
            # administrador se asignan directamente en la tabla usuarios.
            with st.form("registro_form"):
                nuevo_nombre = st.text_input("Nombre Completo:")
                nuevo_usuario = st.text_input("Usuario:")
                nueva_password = st.text_input("Contraseña:", type="password")
                btn_registro = st.form_submit_button("Crear Cuenta")

                if btn_registro:
                    usuario = nuevo_usuario.strip().lower()
                    if not nuevo_nombre or not usuario or not nueva_password:
                        st.error("Llena todos los campos.")
                    elif usuario in credentials["usernames"]:
                        st.error("Usuario ya en uso.")
                    else:
                        crear_usuario(usuario, nuevo_nombre, nueva_password, "conductor")
                        st.success(f"¡Cuenta creada para {nuevo_nombre}! Ya puedes ingresar.")

elif authentication_status:
    name = st.session_state.get("name")
    username = st.session_state.get("username")
    user_role = credentials["usernames"].get(username, {}).get("role", "Administrativo")

    # Cada opción es (texto, ícono SVG)
    opciones_menu = [("Panel General", "panel"), ("Captura de Formatos", "portapapeles")]
    if user_role != "Conductor":
        opciones_menu.append(("CO₂ y Combustible", "hoja"))
    opciones_menu.append(("Rutas y Mejoras", "camion"))
    if user_role == "Administrador":
        opciones_menu.append(("Configuración", "config"))
    etiquetas_menu = [texto for texto, _ in opciones_menu]

    with st.sidebar:
        if os.path.exists(LOGO_FILENAME):
            st.image(LOGO_FILENAME, use_container_width=True)
        else:
            st.warning("Logo no encontrado")

        st.title("Menú Principal")
        st.write(f"Bienvenido, **{name}**")
        st.write(f"Rol: **{user_role}**")
        st.divider()
        opcion = st.radio("Selecciona un módulo:", etiquetas_menu, label_visibility="collapsed")
        st.divider()
        authenticator.logout("Cerrar Sesión", location="sidebar")

    # Íconos del menú lateral (en el mismo orden que las opciones)
    inyectar_iconos(SELECTOR_MENU, [icono for _, icono in opciones_menu])

    encabezado("camion", "Logística Integral MX", nivel=1)
    st.subheader(f"Operación, Combustible y Huella de Carbono ({user_role})")
    st.divider()

    if opcion == "Panel General":
        modulo_panel_general()
    elif opcion == "Captura de Formatos":
        modulo_captura_formatos(username, user_role)
    elif opcion == "CO₂ y Combustible":
        modulo_co2_y_costos()
    elif opcion == "Rutas y Mejoras":
        modulo_optimizacion_rutas()
    elif opcion == "Configuración":
        modulo_configuracion(username)
