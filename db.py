"""
Acceso a MySQL/MariaDB (base logistica_integral) para el dashboard de Logística Integral MX.

Configuración (en este orden de prioridad):
  1) .streamlit/secrets.toml junto a este archivo -> [mysql] y [auth] cookie_key
  2) st.secrets (Streamlit Cloud: Settings -> Secrets)
  3) variables de entorno DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
"""
import os
import secrets as pysecrets
import tomllib
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

ROLES_VISIBLES = {"administrador": "Administrador", "administrativo": "Administrativo", "conductor": "Conductor"}


# ---------------------------------------------------------------------
# Configuración y conexión
# ---------------------------------------------------------------------
def _leer_toml():
    ruta = Path(__file__).resolve().parent / ".streamlit" / "secrets.toml"
    if not ruta.exists():
        return None
    datos = ruta.read_bytes()
    if datos.startswith(b"\xef\xbb\xbf"):  # BOM que agregan algunos editores de Windows
        datos = datos[3:]
    return tomllib.loads(datos.decode("utf-8"))


def _config_con_fuente():
    datos = _leer_toml()
    if datos and datos.get("mysql"):
        return dict(datos["mysql"]), "archivo .streamlit/secrets.toml"
    try:
        return dict(st.secrets["mysql"]), "st.secrets"
    except Exception:
        pass
    return {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": os.getenv("DB_PORT", "3306"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "logistica_integral"),
    }, "valores por defecto (no se encontró configuración)"


def describir_conexion():
    c, fuente = _config_con_fuente()
    return (f"Configuración leída de: {fuente} · host={c.get('host')} · puerto={c.get('port')} · "
            f"usuario={c.get('user')} · contraseña={'sí' if c.get('password') else 'NO'} · "
            f"base={c.get('database')}")


@st.cache_resource
def get_engine():
    c, _ = _config_con_fuente()
    url = URL.create(
        "mysql+pymysql",
        username=c.get("user", "root"),
        password=c.get("password", ""),
        host=c.get("host", "127.0.0.1"),
        port=int(c.get("port", 3306)),
        database=c.get("database", "logistica_integral"),
        query={"charset": "utf8mb4"},
    )
    return create_engine(url, pool_pre_ping=True, pool_recycle=3600)


def consultar(sql, params=None) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})


def ejecutar(sql, params=None):
    with get_engine().begin() as conn:
        return conn.execute(text(sql), params or {})


@st.cache_resource
def _clave_aleatoria():
    return pysecrets.token_hex(32)


def cookie_key():
    """Clave de la cookie de sesión: [auth] cookie_key, o una aleatoria por arranque."""
    clave = None
    datos = _leer_toml()
    if datos:
        clave = (datos.get("auth") or {}).get("cookie_key")
    if not clave:
        try:
            clave = st.secrets["auth"]["cookie_key"]
        except Exception:
            clave = None
    return clave or _clave_aleatoria()


# ---------------------------------------------------------------------
# Usuarios
# ---------------------------------------------------------------------
def cargar_credenciales():
    df = consultar("SELECT usuario, nombre, email, password_hash, rol FROM usuarios WHERE activo = TRUE")
    return {"usernames": {
        f["usuario"]: {
            "name": f["nombre"],
            "password": f["password_hash"],
            "email": f["email"] or "",
            "role": ROLES_VISIBLES[f["rol"]],
        }
        for _, f in df.iterrows()
    }}


def crear_usuario(usuario, nombre, password_plano, rol="conductor", email=None):
    ejecutar(
        "INSERT INTO usuarios (usuario, nombre, email, password_hash, rol) "
        "VALUES (:u, :n, :e, :h, :r)",
        {"u": usuario.strip().lower(), "n": nombre, "e": email or None,
         "h": stauth.Hasher.hash(password_plano), "r": rol},
    )


def asegurar_usuarios_demo():
    """Si no hay usuarios, crea tres cuentas de prueba (y liga al conductor demo)."""
    if int(consultar("SELECT COUNT(*) AS n FROM usuarios").iloc[0]["n"]) > 0:
        return
    crear_usuario("admin", "Dirección Operativa", "123", "administrador", "admin@logisticaintegralmx.com")
    crear_usuario("admin_staff", "Personal Administrativo", "456", "administrativo", "rutas@logisticaintegralmx.com")
    crear_usuario("conductor1", "Carlos M. (COND-01)", "789", "conductor", "cond1@logisticaintegralmx.com")
    ejecutar("UPDATE conductores SET id_usuario = (SELECT id_usuario FROM usuarios WHERE usuario = 'conductor1') "
             "WHERE clave = 'COND-01'")


def id_usuario(usuario):
    df = consultar("SELECT id_usuario FROM usuarios WHERE usuario = :u", {"u": usuario})
    return None if df.empty else int(df.iloc[0]["id_usuario"])


def conductor_de_usuario(usuario):
    """Conductor ligado a la cuenta (o None)."""
    df = consultar(
        "SELECT c.id_conductor, CONCAT(c.clave, ' (', c.nombre, ')') AS etiqueta "
        "FROM conductores c JOIN usuarios u ON u.id_usuario = c.id_usuario WHERE u.usuario = :u",
        {"u": usuario},
    )
    return None if df.empty else df.iloc[0]


# ---------------------------------------------------------------------
# Catálogos
# ---------------------------------------------------------------------
def lista_unidades():
    return consultar("SELECT id_unidad, codigo FROM unidades WHERE activa = TRUE ORDER BY codigo")


def lista_conductores():
    return consultar("SELECT id_conductor, CONCAT(clave, ' (', nombre, ')') AS etiqueta "
                     "FROM conductores WHERE activo = TRUE ORDER BY clave")


def paradas_de_unidad(codigo):
    df = consultar(
        "SELECT p.nombre, p.latitud AS lat, p.longitud AS lon, p.descripcion AS `desc` "
        "FROM paradas_ruta p JOIN unidades u ON u.id_unidad = p.id_unidad "
        "WHERE u.codigo = :c ORDER BY p.orden", {"c": codigo})
    return [{"nombre": f["nombre"], "lat": float(f["lat"]), "lon": float(f["lon"]), "desc": f["desc"] or ""}
            for _, f in df.iterrows()]


# ---------------------------------------------------------------------
# Datos de los tres formatos (mismos nombres de columna que usaban los CSV)
# ---------------------------------------------------------------------
def df_conductores():
    df = consultar("""
        SELECT r.fecha AS Fecha, CONCAT(c.clave, ' (', c.nombre, ')') AS Conductor, u.codigo AS Camioneta,
               r.km_inicial AS Km_Inicial, r.km_final AS Km_Final, r.km_recorridos AS Km_Recorridos,
               r.diesel_usado_l AS Diesel_Usado_L, r.paquetes_entregados AS Paquetes_Entregados,
               r.entregas_fallidas AS Entregas_Fallidas, r.tiempo_hr AS Tiempo_Recorrido_Hr,
               r.incidencias AS Incidencias
        FROM registros_conductor r
        JOIN conductores c ON c.id_conductor = r.id_conductor
        JOIN unidades u ON u.id_unidad = r.id_unidad
        ORDER BY r.fecha DESC, r.id_registro DESC""")
    df["Fecha"] = df["Fecha"].astype(str)
    return df


def df_rutas():
    df = consultar("""
        SELECT r.fecha AS Fecha, u.codigo AS Camioneta, r.punto_salida AS Punto_Salida, r.destinos AS Destinos,
               r.dist_estimada_km AS Distancia_Estimada_Km, r.dist_real_km AS Distancia_Real_Km,
               r.num_paradas AS Num_Paradas, r.tiempo_est_hr AS Tiempo_Estimado_Hr,
               r.tiempo_real_hr AS Tiempo_Real_Hr, r.observaciones AS Observaciones
        FROM rutas_entrega r JOIN unidades u ON u.id_unidad = r.id_unidad
        ORDER BY r.fecha DESC, r.id_ruta DESC""")
    df["Fecha"] = df["Fecha"].astype(str)
    return df


def df_combustible():
    df = consultar("""
        SELECT c.fecha AS Fecha, u.codigo AS Camioneta, c.litros_cargados AS Diesel_Cargado_L,
               c.costo_mxn AS Costo_Combustible, c.km_unidad AS Kilometraje_Unidad,
               c.mantenimiento AS Mantenimiento, c.observaciones AS Observaciones
        FROM cargas_combustible c JOIN unidades u ON u.id_unidad = c.id_unidad
        ORDER BY c.fecha DESC, c.id_carga DESC""")
    df["Fecha"] = df["Fecha"].astype(str)
    return df


def guardar_registro_conductor(fecha, id_conductor, id_unidad, km_ini, km_fin, diesel,
                               entregados, fallidas, tiempo_hr, incidencias, id_usr):
    ejecutar("""
        INSERT INTO registros_conductor
          (fecha, id_conductor, id_unidad, km_inicial, km_final, diesel_usado_l,
           paquetes_entregados, entregas_fallidas, tiempo_hr, incidencias, registrado_por)
        VALUES (:f, :c, :u, :ki, :kf, :d, :e, :x, :t, :i, :r)""",
        {"f": fecha, "c": id_conductor, "u": id_unidad, "ki": km_ini, "kf": km_fin, "d": diesel,
         "e": entregados, "x": fallidas, "t": tiempo_hr, "i": incidencias, "r": id_usr})


def guardar_ruta(fecha, id_unidad, salida, destinos, dist_est, dist_real, paradas,
                 t_est, t_real, observaciones, id_usr):
    ejecutar("""
        INSERT INTO rutas_entrega
          (fecha, id_unidad, punto_salida, destinos, dist_estimada_km, dist_real_km,
           num_paradas, tiempo_est_hr, tiempo_real_hr, observaciones, registrado_por)
        VALUES (:f, :u, :s, :d, :de, :dr, :p, :te, :tr, :o, :r)""",
        {"f": fecha, "u": id_unidad, "s": salida, "d": destinos, "de": dist_est, "dr": dist_real,
         "p": paradas, "te": t_est, "tr": t_real, "o": observaciones, "r": id_usr})


def guardar_combustible(fecha, id_unidad, litros, costo, km_unidad, mantenimiento, observaciones, id_usr):
    ejecutar("""
        INSERT INTO cargas_combustible
          (fecha, id_unidad, litros_cargados, costo_mxn, km_unidad, mantenimiento, observaciones, registrado_por)
        VALUES (:f, :u, :l, :c, :k, :m, :o, :r)""",
        {"f": fecha, "u": id_unidad, "l": litros, "c": costo, "k": km_unidad,
         "m": mantenimiento, "o": observaciones, "r": id_usr})


# ---------------------------------------------------------------------
# Parámetros
# ---------------------------------------------------------------------
def parametro(clave, por_defecto):
    df = consultar("SELECT valor FROM parametros WHERE clave = :c", {"c": clave})
    return por_defecto if df.empty else float(df.iloc[0]["valor"])


def actualizar_parametro(clave, valor, id_usr):
    ejecutar("UPDATE parametros SET valor = :v, actualizado_por = :u WHERE clave = :c",
             {"v": valor, "u": id_usr, "c": clave})
