-- Capas del Postgres curado (ADR 0002). Aplicar en orden numérico.
-- raw_*   : copia de los Parquet de data/raw (esquema observaciones)
-- macro / sentimiento / vida : vistas curadas por tema
-- kpi     : una vista por indicador publicado en tableros

CREATE SCHEMA IF NOT EXISTS raw_series;
CREATE SCHEMA IF NOT EXISTS macro;
CREATE SCHEMA IF NOT EXISTS sentimiento;
CREATE SCHEMA IF NOT EXISTS vida;
CREATE SCHEMA IF NOT EXISTS kpi;

CREATE TABLE IF NOT EXISTS raw_series.observaciones (
    fuente       text        NOT NULL,
    conjunto     text        NOT NULL,
    serie_id     text        NOT NULL,
    fecha        date        NOT NULL,
    valor        double precision,
    unidad       text,
    frecuencia   text,
    extraido_en  timestamptz NOT NULL,
    PRIMARY KEY (fuente, serie_id, fecha)
);

CREATE INDEX IF NOT EXISTS observaciones_serie_fecha
    ON raw_series.observaciones (serie_id, fecha DESC);
