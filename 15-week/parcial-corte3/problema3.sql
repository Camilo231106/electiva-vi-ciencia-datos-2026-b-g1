-- ============================================================
-- Problema 3a: Optimización de una consulta lenta
-- Tabla de ejemplo: ventas(id_venta, fecha, id_cliente, id_producto,
--                          monto, observaciones, ...)  → millones de filas
-- ============================================================

-- ❌ CONSULTA LENTA
-- Problemas: (1) SELECT * trae todas las columnas, (2) YEAR()/MONTH() en el WHERE
-- impiden usar un índice sobre 'fecha' (condición NO sargable) → escaneo completo.
SELECT *
FROM ventas
WHERE YEAR(fecha) = 2026
  AND MONTH(fecha) = 10;

-- ✅ CONSULTA OPTIMIZADA
-- 1) Índice sobre la columna de filtro (se crea una sola vez)
CREATE INDEX idx_ventas_fecha ON ventas (fecha);

-- 2) Solo columnas necesarias + filtro por RANGO sobre la columna "limpia"
SELECT id_venta, fecha, id_cliente, monto
FROM ventas
WHERE fecha >= '2026-10-01'      -- inicio inclusivo
  AND fecha <  '2026-11-01';     -- fin exclusivo (funciona aunque 'fecha' tenga hora)

-- 3) Verificación: comparar el plan de ejecución antes y después
--    (Seq Scan / Full Table Scan  →  Index Range Scan)
-- EXPLAIN SELECT ...;            -- MySQL / PostgreSQL

-- OPCIONAL: índice "cubriente" (incluye las columnas del SELECT → no lee la tabla)
-- CREATE INDEX idx_ventas_fecha_cubre ON ventas (fecha, id_cliente, monto);
