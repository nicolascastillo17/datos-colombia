-- Permisos (ADR 0002, 0004). Aplicar con el rol dueño de la base (en Neon: neondb_owner).
-- Prerrequisito: crear los roles `escritor_cron` y `lector` desde la consola de Neon
-- (Roles → New role). La consola genera la contraseña; nunca se escribe en el repo.
--
-- escritor_cron : solo carga raw (INSERT/UPDATE). Sin DDL: los cambios de esquema
--                 van por sql/NN_*.sql aplicados por el dueño.
-- lector        : solo SELECT en todas las capas. Lo usan Claude Desktop, el build
--                 de Evidence y colaboradores que pidan acceso.

-- escritor_cron
GRANT USAGE ON SCHEMA raw_series TO escritor_cron;
GRANT SELECT, INSERT, UPDATE ON raw_series.observaciones TO escritor_cron;

-- lector
GRANT USAGE ON SCHEMA raw_series, macro, sentimiento, vida, kpi TO lector;
GRANT SELECT ON ALL TABLES IN SCHEMA raw_series, macro, sentimiento, vida, kpi TO lector;
ALTER DEFAULT PRIVILEGES IN SCHEMA raw_series, macro, sentimiento, vida, kpi
    GRANT SELECT ON TABLES TO lector;

-- Nadie más crea objetos en public
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
