Markdown
# 🚚 Logística Integral MX — Control de Rutas y Huella de Carbono

Aplicación web desarrollada en **Python** con **Streamlit** para optimizar las rutas de distribución, controlar el consumo de diésel y estimar la huella de carbono operativa de **Logística Integral MX** (3 camionetas tipo VAN, 4 conductores y 2 personas de personal administrativo).

---

## ⚙️ Instalación

Instala las dependencias necesarias desde el archivo `requirements.txt` incluido en el proyecto:

```bash
pip install -r requirements.txt

▶️ Iniciar el Proyecto
Ejecuta el siguiente comando dentro de la carpeta del proyecto:
Bash
streamlit run logistica_integral_mx.py
⚠️ Nota Importante para el Equipo: Archivo users_logistica.json y Datos .csv
Este proyecto utiliza el archivo users_logistica.json como base de datos local para gestionar el inicio de sesión, las contraseñas encriptadas y los roles (Administrador, Administrativo, Conductor), además de archivos .csv (registro_conductores.csv, registro_rutas.csv y registro_combustible.csv) para almacenar los formatos capturados.
Credenciales de prueba (por defecto):
Administrador: Usuario: admin | Contraseña: 123
Administrativo: Usuario: admin_staff | Contraseña: 456
Conductor: Usuario: conductor1 | Contraseña: 789
¿Cómo probar el registro?
En la pantalla de inicio de sesión, ve a la pestaña "Registrarse". Puedes crear un usuario nuevo y seleccionar el rol de "Conductor" o "Administrativo". Al hacerlo, notarás que el menú lateral se adapta según los permisos del rol (por ejemplo, al rol de Conductor se le ocultan las secciones de CO₂ y Combustible y Configuración).
