# BACKLOG — datos-colombia

🔴 bloqueante · 🟡 importante · 🟢 mejora · ✅ resuelto (mover a BITACORA con fecha)

## Fase 0 — Arranque

- 🟡 BanRep: `DF_CBR_DAILY_HIST` devuelve 326 obs en 15 días → varias series
  por dataflow. Inspeccionar `SUBJECT` y filtrar/mapear antes de publicar.
- 🟡 Banco Mundial intermitente: si persiste, evaluar API alternativa del Banco
  Mundial o dejarlo como fuente semanal con tolerancia a fallas.
- 🔴 Subir `ci.yml` y plantillas de `.github`; proteger `main` (PR + check `pruebas`).
- 🔴 Crear proyecto Neon Free; aplicar `sql/00_schemas.sql`; roles
  `escritor_cron` (solo `raw_series`) y `lector` (solo SELECT en vistas).
- 🟡 Cargador `raw → Postgres` (`python -m datos_colombia cargar`): upsert de
  Parquet en `raw_series.observaciones` por (fuente, serie_id, fecha).
- 🟡 Secrets en GitHub (`DATABASE_URL`, `DATOS_GOV_APP_TOKEN`) y encender el cron
  de `extraer.yml`.
- 🟡 Crear Proyecto en claude.ai "Datos Colombia" con
  `docs/claude/instrucciones-proyecto.md` y sincronizar el repo.
- 🟡 Extensión Postgres en Claude Desktop con el rol `lector` de Neon.
- 🟢 Solicitar app token de datos.gov.co.
- 🟢 Código de conducta y etiquetas de issues (`fuente`, `datos`, `buena-primera-tarea`).

## Fase 1 — Fuentes

- 🟡 BanRep SDMX: validar series de IBR (varios plazos) y agregados monetarios;
  mapear `SUBJECT` → nombre legible en `docs/FUENTES.md`.
- 🟡 DANE IPC: parser de `anex-IPC-Variacion-<mes><año>.xlsx` (hoy solo se
  descarga). Validar el patrón de URL mes a mes.
- 🟡 DANE mercado laboral (GEIH): desempleo e informalidad mensual desde anexos.
- 🟡 DANE pobreza monetaria y multidimensional (anual) y ECV (anual).
- 🟡 Fedesarrollo ICC / IEC / ICE: carga manual mensual
  (`data/manual/fedesarrollo/eoc.csv`) — no hay API.
- 🟡 GDELT: acumular tono diario (la API cubre una ventana reciente).
  Validar consultas temáticas.
- 🟢 PIB trimestral e ISE mensual (DANE anexos).
- 🟢 FMI (WEO / IFS) como complemento de proyecciones.
- 🟢 DNP TerriData (indicadores municipales).

## Sugeridos (fuera de alcance fase 1)

- 🟢 Google Trends (sin API oficial; librerías no oficiales inestables).
- 🟢 Redes sociales (X / Reddit): APIs de pago o restringidas.
- 🟢 Microdatos ANDA (GEIH, ECV): procesamiento pesado; justificaría AWS (ADR nuevo).

## Publicación

- 🟡 Inicializar Evidence en `dashboards/` y build contra Neon desde Actions →
  GitHub Pages.
- 🟡 Tablero 1: Pulso macro (TPM, TRM, inflación, desempleo, crecimiento).
- 🟡 Tablero 2: Sentimiento (ICC Fedesarrollo vs tono GDELT).
- 🟢 Tablero 3: Condiciones de vida (pobreza, Gini, ECV).
- 🟢 Calendario de publicaciones (BanRep y DANE) para programar extracciones.
