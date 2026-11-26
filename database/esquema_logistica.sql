-- =====================================================================
-- Base de datos: Logística Integral MX (paquetería en línea, flota de VANs)
-- Compatible con MySQL 5.7+ / MariaDB 10.2+ (InnoDB, utf8mb4)
-- Reemplaza los CSV: registro_conductores, registro_rutas y registro_combustible
-- =====================================================================

DROP DATABASE IF EXISTS logistica_integral;
CREATE DATABASE logistica_integral
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE logistica_integral;

-- ---------------------------------------------------------------------
-- Usuarios: se entra con "usuario" (no con correo)
-- ---------------------------------------------------------------------
CREATE TABLE usuarios (
  id_usuario     INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  usuario        VARCHAR(40)  NOT NULL UNIQUE,
  nombre         VARCHAR(120) NOT NULL,
  email          VARCHAR(150) NULL,
  password_hash  VARCHAR(255) NOT NULL,            -- bcrypt (la sal va dentro del hash)
  rol            ENUM('administrador','administrativo','conductor') NOT NULL DEFAULT 'conductor',
  activo         BOOLEAN NOT NULL DEFAULT TRUE,
  creado_en      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Flota y personal de ruta
-- ---------------------------------------------------------------------
CREATE TABLE unidades (
  id_unidad  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  codigo     VARCHAR(10) NOT NULL UNIQUE,          -- VAN-01
  placas     VARCHAR(15) NULL,
  activa     BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

CREATE TABLE conductores (
  id_conductor INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  clave        VARCHAR(10)  NOT NULL UNIQUE,       -- COND-01
  nombre       VARCHAR(100) NOT NULL,
  id_usuario   INT UNSIGNED NULL UNIQUE,           -- si tiene cuenta para entrar al sistema
  activo       BOOLEAN NOT NULL DEFAULT TRUE,
  FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Formato 1: registro diario del conductor
-- ---------------------------------------------------------------------
CREATE TABLE registros_conductor (
  id_registro          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  fecha                DATE NOT NULL,
  id_conductor         INT UNSIGNED NOT NULL,
  id_unidad            INT UNSIGNED NOT NULL,
  km_inicial           DECIMAL(10,1) NOT NULL,
  km_final             DECIMAL(10,1) NOT NULL,
  diesel_usado_l       DECIMAL(7,2)  NOT NULL,
  paquetes_entregados  INT UNSIGNED  NOT NULL DEFAULT 0,
  entregas_fallidas    INT UNSIGNED  NOT NULL DEFAULT 0,
  tiempo_hr            DECIMAL(5,2)  NOT NULL,
  incidencias          VARCHAR(500)  NOT NULL DEFAULT 'Sin incidencias',
  registrado_por       INT UNSIGNED  NULL,
  creado_en            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  km_recorridos        DECIMAL(10,1) GENERATED ALWAYS AS (km_final - km_inicial) STORED,
  CONSTRAINT ck_km CHECK (km_final >= km_inicial),
  FOREIGN KEY (id_conductor)  REFERENCES conductores(id_conductor),
  FOREIGN KEY (id_unidad)     REFERENCES unidades(id_unidad),
  FOREIGN KEY (registrado_por) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
  INDEX idx_rc_fecha (fecha),
  INDEX idx_rc_unidad (id_unidad, fecha)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Formato 2: registro de rutas de entrega (estimado vs. real)
-- ---------------------------------------------------------------------
CREATE TABLE rutas_entrega (
  id_ruta          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  fecha            DATE NOT NULL,
  id_unidad        INT UNSIGNED NOT NULL,
  punto_salida     VARCHAR(100) NOT NULL,
  destinos         VARCHAR(300) NOT NULL DEFAULT 'No especificados',
  dist_estimada_km DECIMAL(8,1) NOT NULL,
  dist_real_km     DECIMAL(8,1) NOT NULL,
  num_paradas      INT UNSIGNED NOT NULL,
  tiempo_est_hr    DECIMAL(5,2) NOT NULL,
  tiempo_real_hr   DECIMAL(5,2) NOT NULL,
  observaciones    VARCHAR(500) NOT NULL DEFAULT 'Sin observaciones',
  registrado_por   INT UNSIGNED NULL,
  creado_en        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  km_extra         DECIMAL(8,1) GENERATED ALWAYS AS (dist_real_km - dist_estimada_km) STORED,
  FOREIGN KEY (id_unidad)      REFERENCES unidades(id_unidad),
  FOREIGN KEY (registrado_por) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
  INDEX idx_re_fecha (fecha)
) ENGINE=InnoDB;

-- Paradas de ejemplo de cada unidad (para dibujar el mapa)
CREATE TABLE paradas_ruta (
  id_unidad    INT UNSIGNED NOT NULL,
  orden        TINYINT UNSIGNED NOT NULL,
  nombre       VARCHAR(100) NOT NULL,
  latitud      DECIMAL(9,6) NOT NULL,
  longitud     DECIMAL(9,6) NOT NULL,
  descripcion  VARCHAR(150) NULL,
  PRIMARY KEY (id_unidad, orden),
  FOREIGN KEY (id_unidad) REFERENCES unidades(id_unidad) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Formato 3: combustible y mantenimiento
-- ---------------------------------------------------------------------
CREATE TABLE cargas_combustible (
  id_carga         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  fecha            DATE NOT NULL,
  id_unidad        INT UNSIGNED NOT NULL,
  litros_cargados  DECIMAL(7,2) NOT NULL,
  costo_mxn        DECIMAL(10,2) NOT NULL,
  km_unidad        DECIMAL(10,1) NOT NULL,
  mantenimiento    VARCHAR(300) NOT NULL DEFAULT 'Ninguno',
  observaciones    VARCHAR(500) NOT NULL DEFAULT 'Sin observaciones',
  registrado_por   INT UNSIGNED NULL,
  creado_en        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_unidad)      REFERENCES unidades(id_unidad),
  FOREIGN KEY (registrado_por) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
  INDEX idx_cc_fecha (fecha)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Parámetros editables por el administrador
-- ---------------------------------------------------------------------
CREATE TABLE parametros (
  clave           VARCHAR(40) PRIMARY KEY,
  valor           DECIMAL(10,4) NOT NULL,
  descripcion     VARCHAR(200) NULL,
  actualizado_por INT UNSIGNED NULL,
  actualizado_en  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (actualizado_por) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
) ENGINE=InnoDB;

INSERT INTO parametros (clave, valor, descripcion) VALUES
 ('factor_co2_diesel',   2.6800, 'kg de CO2 por litro de diésel'),
 ('precio_litro_diesel', 26.9900, 'Precio del diésel en Mexicali ($/L)'),
 ('co2_kg_por_km_extra', 0.2200, 'kg de CO2 estimados por cada km recorrido de más'),
 ('umbral_km_extra',     5.0000, 'km de diferencia (real vs. estimado) a partir de los cuales se alerta');

-- ---------------------------------------------------------------------
-- Vistas
-- ---------------------------------------------------------------------
CREATE VIEW vw_resumen_unidad AS
SELECT u.codigo                                   AS camioneta,
       SUM(r.km_recorridos)                       AS km_totales,
       SUM(r.diesel_usado_l)                      AS diesel_l,
       SUM(r.paquetes_entregados)                 AS entregas,
       SUM(r.entregas_fallidas)                   AS fallidas,
       ROUND(SUM(r.km_recorridos) / NULLIF(SUM(r.diesel_usado_l), 0), 2) AS rendimiento_km_l,
       ROUND(SUM(r.diesel_usado_l) *
             (SELECT valor FROM parametros WHERE clave = 'factor_co2_diesel'), 2) AS co2_kg
FROM registros_conductor r
JOIN unidades u ON u.id_unidad = r.id_unidad
GROUP BY u.id_unidad, u.codigo;

CREATE VIEW vw_pct_fallidas_conductor AS
SELECT c.clave, c.nombre,
       SUM(r.paquetes_entregados) AS entregados,
       SUM(r.entregas_fallidas)   AS fallidas,
       ROUND(100 * SUM(r.entregas_fallidas) /
             NULLIF(SUM(r.paquetes_entregados + r.entregas_fallidas), 0), 1) AS pct_fallidas
FROM registros_conductor r
JOIN conductores c ON c.id_conductor = r.id_conductor
GROUP BY c.id_conductor, c.clave, c.nombre;
