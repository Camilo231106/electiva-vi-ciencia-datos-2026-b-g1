-- 1) WHERE: lecturas de temperatura del sensor 1 por encima de 28 °C
SELECT id_lectura, valor, fecha_hora
FROM lectura
WHERE id_sensor = 1
  AND valor > 28
ORDER BY fecha_hora;

-- 2) JOIN: lecturas de temperatura con el nombre del invernadero y la unidad
SELECT i.nombre AS invernadero,
       l.fecha_hora,
       l.valor,
       t.unidad
FROM lectura l
JOIN sensor s       ON s.id_sensor = l.id_sensor
JOIN tipo_sensor t  ON t.id_tipo_sensor = s.id_tipo_sensor
JOIN invernadero i  ON i.id_invernadero = s.id_invernadero
WHERE t.nombre = 'Temperatura'
ORDER BY i.nombre, l.fecha_hora;

-- 3) GROUP BY: promedio, mínimo, máximo y número de lecturas
--    por invernadero y tipo de sensor
SELECT i.nombre  AS invernadero,
       t.nombre  AS variable,
       t.unidad,
       COUNT(*)              AS n_lecturas,
       ROUND(AVG(l.valor),2) AS promedio,
       MIN(l.valor)          AS minimo,
       MAX(l.valor)          AS maximo
FROM lectura l
JOIN sensor s       ON s.id_sensor = l.id_sensor
JOIN tipo_sensor t  ON t.id_tipo_sensor = s.id_tipo_sensor
JOIN invernadero i  ON i.id_invernadero = s.id_invernadero
GROUP BY i.nombre, t.nombre, t.unidad
ORDER BY i.nombre, t.nombre;
