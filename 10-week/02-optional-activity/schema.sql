-- Modelo de datos del invernadero inteligente (subconjunto del ERD de la Semana 6)
-- Motor: SQLite

CREATE TABLE invernadero (
    id_invernadero INTEGER PRIMARY KEY,
    nombre         TEXT NOT NULL UNIQUE
);

CREATE TABLE tipo_sensor (
    id_tipo_sensor INTEGER PRIMARY KEY,
    nombre         TEXT NOT NULL UNIQUE,   -- Temperatura, Luz, Humedad
    unidad         TEXT NOT NULL           -- °C, lux, %
);

CREATE TABLE sensor (
    id_sensor      INTEGER PRIMARY KEY,
    modelo         TEXT,                   -- NTC, LDR, DHT22
    id_invernadero INTEGER NOT NULL REFERENCES invernadero(id_invernadero),
    id_tipo_sensor INTEGER NOT NULL REFERENCES tipo_sensor(id_tipo_sensor)
);

CREATE TABLE lectura (
    id_lectura     INTEGER PRIMARY KEY,
    valor          REAL    NOT NULL,
    fecha_hora     TEXT    NOT NULL,       -- formato ISO: AAAA-MM-DD HH:MM:SS
    valor_imputado INTEGER NOT NULL DEFAULT 0,  -- 1 si el valor se imputó en la limpieza
    id_sensor      INTEGER NOT NULL REFERENCES sensor(id_sensor)
);
