-- =====================================================================
-- Datos de DEMOSTRACIÓN (los que antes estaban en los CSV de relleno).
-- Ejecutar DESPUÉS de esquema_logistica.sql, en una base recién creada.
-- Ajustes respecto a los CSV: el costo del diésel usa $26.99/L (Mexicali) y las
-- paradas del mapa son ubicaciones aproximadas de Mexicali. Todo es ficticio.
-- Los usuarios de prueba los crea la app al abrirse.
-- =====================================================================
USE logistica_integral;

INSERT INTO unidades (id_unidad, codigo) VALUES (1,'VAN-01'),(2,'VAN-02'),(3,'VAN-03');

INSERT INTO conductores (id_conductor, clave, nombre) VALUES
 (1,'COND-01','Carlos M.'),(2,'COND-02','Luis R.'),(3,'COND-03','Jorge H.'),(4,'COND-04','Diego S.');

INSERT INTO registros_conductor
 (fecha, id_conductor, id_unidad, km_inicial, km_final, diesel_usado_l,
  paquetes_entregados, entregas_fallidas, tiempo_hr, incidencias) VALUES
 ('2026-11-18',1,1,45120,45245,18.5,42,3,6.5,'Tráfico pesado en av. principal'),
 ('2026-11-18',2,2,38900,39040,22.0,38,5,7.2,'Cliente ausente en 3 domicilios'),
 ('2026-11-18',3,3,51200,51310,15.0,35,2,5.8,'Sin incidencias');

INSERT INTO rutas_entrega
 (fecha, id_unidad, punto_salida, destinos, dist_estimada_km, dist_real_km,
  num_paradas, tiempo_est_hr, tiempo_real_hr, observaciones) VALUES
 ('2026-11-18',1,'CEDIS Central','Zona Norte / Centro',110,125,28,5.5,6.5,'Desvío por obra vial'),
 ('2026-11-18',2,'CEDIS Central','Zona Poniente / Industrial',120,140,32,6.0,7.2,'Ruta con retornos innecesarios'),
 ('2026-11-18',3,'CEDIS Central','Zona Sur / Residencial',100,110,24,5.0,5.8,'Buen rendimiento general');

-- 45 L x 26.99 = 1,214.55   |   50 L x 26.99 = 1,349.50
INSERT INTO cargas_combustible
 (fecha, id_unidad, litros_cargados, costo_mxn, km_unidad, mantenimiento, observaciones) VALUES
 ('2026-11-18',1,45,1214.55,45245,'Revisión de presión de neumáticos','Carga completa al cierre de turno'),
 ('2026-11-18',2,50,1349.50,39040,'Cambio de filtros de aire y diésel','Listo para jornada matutina');

INSERT INTO paradas_ruta (id_unidad, orden, nombre, latitud, longitud, descripcion) VALUES
 (1,1,'CEDIS Central',32.627800,-115.454500,'Punto de salida'),
 (1,2,'Zona Norte',   32.670000,-115.470000,'Parada 1 - Paquetería'),
 (1,3,'Centro',       32.630000,-115.460000,'Parada 2 - Paquetería'),
 (2,1,'CEDIS Central',32.627800,-115.454500,'Punto de salida'),
 (2,2,'Zona Poniente',32.635000,-115.515000,'Parada 1 - Corredor industrial'),
 (2,3,'Zona Industrial',32.610000,-115.500000,'Parada 2 - Paquetería'),
 (3,1,'CEDIS Central',32.627800,-115.454500,'Punto de salida'),
 (3,2,'Zona Sur',     32.590000,-115.460000,'Parada 1 - Residencial'),
 (3,3,'Zona Residencial',32.580000,-115.440000,'Parada 2 - Paquetería');
