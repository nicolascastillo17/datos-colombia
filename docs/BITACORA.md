# BITÁCORA — datos-colombia

Registro cronológico (más reciente arriba). Cada entrada: qué pasó, por qué,
qué quedó pendiente. Formato:

```
## AAAA-MM-DD — título corto
**Fase:** extracción | carga | transformación | publicación | infraestructura | docs
**Qué pasó:** …
**Por qué:** …
**Pendiente:** … (→ BACKLOG)
```

---

## 2026-11-23 — BanRep recargado; DBeaver y conector MCP local

**Fase:** carga / infraestructura

- `.env` tenía cruzadas `DATABASE_URL` y `DATABASE_URL_OWNER` (la primera carga
  entró como `neondb_owner`). Corregido; `verificar_dueno()` en `aplicar-sql`
  ahora detecta el caso. BanRep borrado con el dueño y recargado con el nuevo
  `serie_id`; consulta de verificación OK desde DBeaver (rol `lector`).
- Conector para Claude: servidor MCP local (`.mcp.json` + `mcp/dbhub.toml`,
  DBHub 1.2.3, solo lectura) en vez de extensión `.mcpb`, porque la cuenta de
  Claude en uso pertenece a la organización Griky, cuyo Allowlist bloquea
  extensiones fuera de su registro.

## 2026-11-23 — Primera carga real a Neon y corrección de `serie_id` BanRep

**Fase:** extracción (parser) / carga

**Resultado de la primera corrida:**
- `extraer todas`: banrep 124,5 s (historia completa: tpm 10.510, trm 21.797,
  ibr 28.280, dtf 15.659, uvr 19.326, colcap 226, agregados 2.570, tes 855);
  datos_gov 8.391; banco_mundial 396 (respondió); gdelt ❌ 429; dane ✅;
  fedesarrollo ❌ (debía ser aviso).
- `cargar`: 108.010 filas → 83.362 nuevas y **24.648 "duplicadas en lote"**.

**Diagnóstico:** las duplicadas no eran repeticiones. BanRep publica varias
series con el mismo `SUBJECT` distinguidas por otras dimensiones; en IBR,
`IRIBRM00` existe con `UNIT_MEASURE=ER` (efectiva) y `NR` (nominal). El
`serie_id` solo usaba `SUBJECT` → el cargador se quedó con una de las dos al
azar. Datos de BanRep en Neon quedaron mezclados.

**Corrección:**
- `serie_id` BanRep = `<conjunto>:<SUBJECT>.<dimensiones ≠ _Z>`, p. ej.
  `ibr:IRIBRM00.ER`, `tpm:IRCBRM01.PA`.
- El cargador ahora **aborta** si un lote trae valores distintos para la misma
  (fuente, serie_id, fecha) (`SerieAmbigua`); solo descarta duplicados idénticos.
- GDELT: sin reintentos ante 429 (insistir prolonga el bloqueo); pausa 10 s.
- Fedesarrollo sin CSV en `extraer` → ⚠️ aviso, no ❌.
- `startPeriod` de BanRep se respeta solo por año (desde 2026-11-01 → desde 2026-01-02).
- Pruebas: 17 (nuevas: series ER/NR, carga que aborta ante `serie_id` ambiguo).

**Pendiente:** borrar filas `banrep` de Neon (rol dueño), re-extraer y recargar.

## 2026-11-23 — Neon creado; `aplicar-sql` y `cargar`

**Fase:** carga / infraestructura

**Qué pasó:**
- Proyecto Neon `datos-colombia` (rama `production`, base `neondb`).
- Hallazgo: los roles creados desde la consola de Neon heredan `neon_superuser`
  (CREATEDB, CREATEROLE, BYPASSRLS). `escritor_cron` y `lector` se crearon por
  SQL; verificado `pg_has_role(..., 'neon_superuser', 'member') = false`.
- Nuevo `python -m datos_colombia aplicar-sql`: aplica `sql/NN_*.sql` en orden,
  una transacción por archivo, con el rol dueño (equivalente a `setup_schema.py`
  de Griky). Los archivos deben ser idempotentes.
- Nuevo `python -m datos_colombia cargar [fuente] [--todo]`: upsert de la última
  partición Parquet por fuente/conjunto en `raw_series.observaciones`; solo
  actualiza si cambió valor/unidad/frecuencia; resuelve duplicados del lote.
  La base acumula la historia (GDELT solo expone una ventana reciente).
- `tests/test_db.py` contra Postgres 16 real: idempotencia de `aplicar-sql`,
  upsert, revisión de un valor, `escritor_cron` sin DDL y `lector` sin escritura.
  Se omiten sin `TEST_DATABASE_URL` (CI no tiene Postgres).
- Corrección del diagnóstico anterior: las 326 obs de TPM no son varias series
  sino ≈ los días desde 2026-01-01; `startPeriod` parece ignorarse.

**Pendiente:** completar `.env`, primera carga real, secret en GitHub y cron.

## 2026-11-23 — CI activo y `main` protegida

**Fase:** infraestructura

- `ci.yml` subido; primer CI en verde (3.10 y 3.12).
- Regla de protección en `main`: PR obligatorio, checks `pruebas (3.10)` y
  `pruebas (3.12)` requeridos, sin aprobaciones (un solo mantenedor).
- Desde aquí todo cambio entra por rama + PR, incluida esta entrada.
- `sql/01_grants.sql`: roles `escritor_cron` (sin DDL, como en Griky) y `lector`.

## 2026-11-23 — Repo público creado

**Fase:** infraestructura

**Qué pasó:**
- Repo `nicolascastillo17/datos-colombia` creado y primer push (`f2d1a9a`).
- Cuenta personal separada de Griky por alias SSH e `includeIf` de git (ver
  INFRAESTRUCTURA). El primer commit salió firmado con el correo de Griky; se
  corrigió con `--amend --reset-author` antes del push.
- `src/datos_colombia.egg-info/` (generado por `pip install -e`) se había
  incluido; se agregó `*.egg-info/` a `.gitignore` y se retiró del índice.
- `ci.yml` y las plantillas de `.github` no entraron en el primer push (el zip
  no se descomprimió); se suben en el segundo commit.

**Pendiente:** proteger `main` tras el primer CI verde.

## 2026-11-23 — Tercera corrida: GDELT 429

**Fase:** extracción

GDELT respondió 429 (límite de tasa por IP) tras tres corridas de `probar` en
10 minutos. No es falla del código: el 429 ahora se reporta como ⚠️ Aviso con
instrucción de esperar, y la sesión no reintenta 429 en caliente (`probar` sin
reintentos; `extraer` con 2). GDELT queda validado por la 1.ª corrida (37 puntos).

## 2026-11-23 — Segunda ejecución de `probar`

**Fase:** extracción

| Fuente | Resultado | Diagnóstico |
|---|---|---|
| banrep | ✅ 7,1 s, 326 obs, TPM 2026-11-23 = 12,25 | Corrección de periodos `AAAAMMDD` confirmada. 326 obs en 15 días → el dataflow trae varias series (`SUBJECT`); mapearlas (BACKLOG) |
| datos_gov | ✅ 2,1 s | — |
| banco_mundial | ❌ 40,6 s, read timeout 20 s × 2 | Servidor intermitente: la misma URL respondió desde otra red a las 11:50. Sin cambio de código; la extracción tiene 4 reintentos |
| gdelt | ❌ 20,3 s, read timeout | Fase extracción: GDELT responde lento (50 s en la 1.ª corrida) aun sano; el timeout corto de `probar` lo mataba. Nuevo `TIMEOUT_LENTO` (90 s) solo para GDELT |
| dane_ipc | ✅ | — |
| fedesarrollo | ⚠️ carga manual pendiente | Comportamiento esperado |

**Pendiente:** tercera corrida para confirmar GDELT; mapa de `SUBJECT` BanRep.

## 2026-11-23 — Primera ejecución de `probar` en el Mac

**Fase:** extracción

**Resultado:**

| Fuente | Resultado | Diagnóstico |
|---|---|---|
| banrep | ❌ 7,2 s `ValueError: Periodo SDMX no reconocido: '20260101'` | Fase extracción/parseo: BanRep entrega `TIME_PERIOD` como `AAAAMMDD`, no ISO. `_fecha()` ahora acepta `AAAAMMDD`, `AAAAMM`, ISO con hora y `AAAA-Mmm` |
| datos_gov | ✅ 0,6 s, TRM 2026-11-21 = 3461,92 | — |
| banco_mundial | ❌ 328,9 s, `ReadTimeoutError` (60 s × 5 intentos) | Fase extracción: la API no respondió; desde la web también falló minutos después → problema del servidor, no de la red local |
| gdelt | ✅ 50,4 s, 37 puntos, tono hoy = 0.0 | El día en curso llega incompleto (0.0). Con `timespan=7d` la resolución puede ser menor a un día |
| dane_ipc | ✅ 0,1 s, anexo oct-2026 (41 KB) | — |
| fedesarrollo | ✅ archivo manual ausente | Era un aviso, no un éxito |

**Cambios:**
- `probar` falla rápido: 1 reintento y 20 s de lectura (`TIMEOUT_PROBAR`); la extracción conserva 4 reintentos y 60 s.
- Banco Mundial: `probar` usa `mrv=5` (consulta liviana).
- GDELT: promedio por día UTC, exclusión del día en curso; `probar` usa `timespan=1m` y reporta la resolución.
- Nuevo estado ⚠️ (`Aviso`) en el CLI para condiciones esperadas (carga manual pendiente).
- 11 pruebas en verde (nuevas: formatos de periodo BanRep, agregación GDELT).

**Pendiente:** re-ejecutar `probar`; alternativa si Banco Mundial sigue intermitente (BACKLOG).

## 2026-11-23 — Stack aceptado y repo colaborativo

**Fase:** infraestructura / docs

**Qué pasó:**
- ADR 0002 (GitHub Actions + Neon Free) y ADR 0003 (Evidence estático) pasan a aceptados.
- ADR 0004: repo público y colaborativo. Se agregan `LICENSE` (MIT),
  `CONTRIBUTING.md`, `ci.yml` (pytest en 3.10 y 3.12 sin secretos), plantillas
  de issues y de PR.
- Primera ejecución de `probar` en el Mac falló antes de correr:
  `zsh: command not found: python`. Causa: macOS solo trae `python3`; el
  comando `python` existe dentro del venv. README y CONTRIBUTING actualizados.

**Por qué:** en repos públicos los runners estándar de Actions no consumen
minutos; el stack queda en US$0/mes.

**Pendiente:** crear repo y proyecto Neon, cargador raw → Postgres (BACKLOG 🔴/🟡).

## 2026-11-23 — Arranque del proyecto

**Fase:** docs / extracción

**Qué pasó:**
- Esqueleto del monorepo creado (docs, ADRs, CLI, módulos por fuente, tests).
- Decisiones iniciales: monorepo (ADR 0001); presupuesto tope ~US$20/mes;
  sentimiento en fase 1 = índices de confianza + tono de noticias GDELT.
- Endpoints verificados el 2026-11-23 vía consulta web:
  - BanRep SDMX (`totoro.banrep.gov.co/nsi-jax-ws/rest`): lista de dataflows
    (TPM, TRM, IBR, DTF, UVR, COLCAP, agregados monetarios, TES) y datos de
    `DF_CBR_DAILY_HIST` (TPM 12,25 % al 2026-11-23).
  - datos.gov.co `32sa-8pi3` (TRM): responde JSON con `valor`, `vigenciadesde`.
  - Banco Mundial API v2: responde para Colombia (`NY.GDP.MKTP.KD.ZG`).
  - GDELT DOC 2.0 `timelinetone`: responde con `timeline[0].data[{date,value}]`;
    un primer intento devolvió error del servidor y el segundo funcionó.
- Las conexiones no se pudieron ejecutar desde el entorno de Claude (red
  restringida): la prueba real es `python -m datos_colombia probar` en el Mac.

**Por qué:** aprovechar el workflow Griky (bitácora, backlog, ADRs, fuentes con
estado) en un proyecto personal de datos abiertos.

**Pendiente:** ver BACKLOG (prueba real de conexiones, decisión de stack, IPC DANE,
Fedesarrollo manual).
