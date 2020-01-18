CREATE TABLE "dht22" (
    time        TIMESTAMPTZ NOT NULL,
    temperature DOUBLE PRECISION  NULL,
    humidity    DOUBLE PRECISION  NULL,
    location    TEXT NULL
);
SELECT create_hypertable('dht22', 'time');
