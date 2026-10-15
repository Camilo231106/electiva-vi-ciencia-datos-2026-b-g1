-- Dataset: invernadero inteligente con ESP32 (subconjunto del ERD de la semana 6)
-- Motor: SQLite (también funciona en MySQL/PostgreSQL cambiando tipos menores)

CREATE TABLE invernadero (
    id_invernadero INTEGER PRIMARY KEY,
    nombre         TEXT NOT NULL,
    ubicacion      TEXT
);

CREATE TABLE tipo_sensor (
    id_tipo_sensor INTEGER PRIMARY KEY,
    nombre         TEXT NOT NULL,
    unidad         TEXT NOT NULL
);

CREATE TABLE sensor (
    id_sensor      INTEGER PRIMARY KEY,
    modelo         TEXT,
    id_invernadero INTEGER NOT NULL REFERENCES invernadero(id_invernadero),
    id_tipo_sensor INTEGER NOT NULL REFERENCES tipo_sensor(id_tipo_sensor)
);

CREATE TABLE lectura (
    id_lectura INTEGER PRIMARY KEY,
    valor      REAL NOT NULL,
    fecha_hora TEXT NOT NULL,
    id_sensor  INTEGER NOT NULL REFERENCES sensor(id_sensor)
);

INSERT INTO invernadero VALUES
    (1, 'Invernadero Tomates',  'Zona A'),
    (2, 'Invernadero Lechugas', 'Zona B');

INSERT INTO tipo_sensor VALUES
    (1, 'Temperatura', '°C'),
    (2, 'Luz',         'lux'),
    (3, 'Humedad',     '%');

INSERT INTO sensor VALUES
    (1, 'NTC',      1, 1),
    (2, 'LDR',      1, 2),
    (3, 'DHT22',    1, 3),
    (4, 'NTC',      2, 1),
    (5, 'LDR',      2, 2),
    (6, 'DHT22',    2, 3);

INSERT INTO lectura VALUES
    -- Invernadero 1 · temperatura (sensor 1)
    (1,  22.5, '2026-10-14 06:00:00', 1),
    (2,  31.8, '2026-10-14 12:00:00', 1),
    (3,  29.4, '2026-10-14 16:00:00', 1),
    (4,  24.1, '2026-10-14 20:00:00', 1),
    -- Invernadero 1 · luz (sensor 2)
    (5,  120,  '2026-10-14 06:00:00', 2),
    (6,  850,  '2026-10-14 12:00:00', 2),
    (7,  600,  '2026-10-14 16:00:00', 2),
    (8,  40,   '2026-10-14 20:00:00', 2),
    -- Invernadero 1 · humedad (sensor 3)
    (9,  78,   '2026-10-14 06:00:00', 3),
    (10, 55,   '2026-10-14 12:00:00', 3),
    (11, 60,   '2026-10-14 16:00:00', 3),
    (12, 72,   '2026-10-14 20:00:00', 3),
    -- Invernadero 2 · temperatura (sensor 4)
    (13, 21.0, '2026-10-14 06:00:00', 4),
    (14, 28.6, '2026-10-14 12:00:00', 4),
    (15, 27.2, '2026-10-14 16:00:00', 4),
    (16, 23.0, '2026-10-14 20:00:00', 4),
    -- Invernadero 2 · luz (sensor 5)
    (17, 100,  '2026-10-14 06:00:00', 5),
    (18, 780,  '2026-10-14 12:00:00', 5),
    (19, 520,  '2026-10-14 16:00:00', 5),
    (20, 30,   '2026-10-14 20:00:00', 5),
    -- Invernadero 2 · humedad (sensor 6)
    (21, 80,   '2026-10-14 06:00:00', 6),
    (22, 62,   '2026-10-14 12:00:00', 6),
    (23, 66,   '2026-10-14 16:00:00', 6),
    (24, 75,   '2026-10-14 20:00:00', 6);
