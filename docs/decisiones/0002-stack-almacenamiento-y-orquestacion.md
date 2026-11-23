# 0002 — Orquestación en GitHub Actions + Postgres serverless (Neon Free)

- **Estado:** aceptada (2026-11-23)
- **Fecha:** 2026-11-23
- **Ámbito:** extracción programada, almacenamiento curado, consulta desde Claude

## Contexto

Tope de ~US$20/mes. Volumen de fase 1 en MB. El workflow de Griky se apoya en
Postgres (capas raw/vistas/KPI, SQL numerado, `execute_sql` desde Claude
Desktop). Evaluación completa en `docs/STACK-Y-COSTOS.md`.

## Decisión

- Extracción: GitHub Actions con cron, ejecutando `python -m datos_colombia extraer todas`.
- Aterrizaje: Parquet (`data/raw/...`) como formato neutro.
- Curado: Postgres en Neon Free (1 GB, escala a cero), DDL por `sql/NN_*.sql`.
- Consulta: extensión de Postgres en Claude Desktop con usuario de solo lectura.

Descartadas:
- AWS RDS + EC2 (espejo Griky): ≈US$15–20/mes fijo para una base que trabaja minutos al día.
- AWS serverless (S3 + Lambda + Athena): costo mínimo, pero más fontanería y menos reuso del workflow.
- Solo DuckDB/Parquet: sin servidor para consultas en vivo desde Claude.

## Consecuencias

- US$0/mes mientras se respeten 1 GB y 100 CU-h por proyecto.
- Al superar límites: Neon Launch (pago por uso, misma cadena) o `pg_dump` a RDS (ADR nuevo).
- Dependencia de GitHub y Neon; Parquet en `raw` permite reconstruir el curado en otro motor.

## Referencias

`docs/STACK-Y-COSTOS.md`; BITACORA 2026-11-23.
