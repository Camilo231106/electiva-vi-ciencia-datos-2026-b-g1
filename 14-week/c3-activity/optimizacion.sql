-- ANTES: la función sobre la columna impide usar índices (SCAN completo)
SELECT maquina_id, SUM(piezas) AS total
FROM produccion
WHERE strftime('%Y', fecha) = '2025'
GROUP BY maquina_id;

-- DESPUÉS: filtro de rango (sargable) + índice cubridor
CREATE INDEX idx_prod_fecha_maq ON produccion(fecha, maquina_id, piezas);

SELECT maquina_id, SUM(piezas) AS total
FROM produccion
WHERE fecha >= '2025-01-01' AND fecha < '2026-01-01'
GROUP BY maquina_id;
