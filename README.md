# Logística Integral MX — Control de Rutas y Huella de Carbono

Aplicación web desarrollada en **Python** con **Streamlit** para optimizar las rutas de distribución, controlar el consumo de diésel y estimar la huella de carbono operativa de **Logística Integral MX** (3 camionetas tipo VAN, 4 conductores y 2 personas de personal administrativo).

Los datos se guardan en una base **MySQL/MariaDB** (`logistica_integral`).

---

## Requisitos
- Python 3.11 o superior
- MySQL 5.7+ o MariaDB 10.2+ (por ejemplo MAMP o XAMPP)

## Instalación
1. **Base de datos.** En phpMyAdmin, sin seleccionar ninguna base, ve a *Importar* y carga en este orden:
   1. `database/esquema_logistica.sql` — crea la base `logistica_integral` con sus tablas y vistas (si ya existía, la borra)
   2. `database/datos_demo_logistica.sql` — datos de ejemplo (opcional)
2. **Configuración.** Copia `.streamlit/secrets.toml.ejemplo` como `.streamlit/secrets.toml` y ajusta el usuario y la contraseña de tu MySQL (MAMP usa `root`). Cambia también `cookie_key` por una cadena aleatoria:
   ```
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
3. **Dependencias:**
   ```
   pip install -r requirements.txt
   ```

## Iniciar el proyecto
Ejecuta el siguiente comando dentro de la carpeta del proyecto:
```
python -m streamlit run logistica_integral_mx.py
```

## Usuarios de prueba
Si la tabla `usuarios` está vacía, la app crea estas cuentas al abrirse:

| Usuario | Contraseña | Rol |
|---|---|---|
| admin | 123 | Administrador |
| admin_staff | 456 | Administrativo |
| conductor1 | 789 | Conductor (ligado a COND-01) |

**Cambia o elimina estas cuentas antes de usar la app con datos reales.** Las contraseñas se guardan cifradas (bcrypt).

### ¿Cómo probar el registro?
En la pantalla de inicio de sesión, ve a la pestaña **Registrarse**. El registro público crea cuentas con rol **Conductor**; los roles Administrativo y Administrador se asignan directamente en la tabla `usuarios`.
El menú lateral se adapta al rol: el Conductor no ve CO₂ y Combustible ni Configuración, y solo puede registrar sus propios datos en el Formato 1.

## Estructura
```
logistica_integral_mx.py    Interfaz (Streamlit)
db.py                       Conexión y consultas a MySQL
database/                   Esquema y datos de ejemplo
.streamlit/secrets.toml     Configuración local (no se sube a GitHub)
```

## Notas
- Los formatos 1, 2 y 3 se guardan en las tablas `registros_conductor`, `rutas_entrega` y `cargas_combustible`.
- El factor de CO₂ del diésel y el precio del litro se editan desde Configuración (solo Administrador).
- Antes los datos vivían en `users_logistica.json` y en archivos `.csv`; ya no se usan.
