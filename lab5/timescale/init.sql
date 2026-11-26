-- ПР5, завдання 5: таблиця під телеметрію панелі (ті самі поля, що в MQTT-повідомленні)
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS telemetry (
    time        TIMESTAMPTZ      NOT NULL,
    device      TEXT             NOT NULL,
    irradiance  DOUBLE PRECISION,          -- Вт/м²
    temp        DOUBLE PRECISION,          -- °C
    power       DOUBLE PRECISION,          -- Вт
    pr          DOUBLE PRECISION,          -- performance ratio
    status      TEXT
);

-- hypertable: Timescale сам ріже таблицю на шматки за часом
SELECT create_hypertable('telemetry', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS telemetry_device_time ON telemetry (device, time DESC);
