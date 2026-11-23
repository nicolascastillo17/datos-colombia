# Reglas para Claude en datos-colombia

Proyecto abierto y colaborativo; mantenedor Nicolás Castillo. Separado de Griky:
no leer, escribir ni referenciar archivos de `griky-pipelines`, ni usar sus
conexiones (Griky · Postgres, Griky · Collate). Repo público (ADR 0004): nada de
credenciales ni datos de `data/` en commits.

## Dónde vive cada cosa

- ¿Qué significa una serie / cómo se calcula un indicador? → `docs/FUENTES.md`
  y, cuando exista, `docs/INDICADORES.md`.
- ¿Qué pasó y por qué? → `docs/BITACORA.md`.
- ¿Qué está pendiente? → `docs/BACKLOG.md` (🔴 bloqueante, 🟡 importante, 🟢 mejora).
- ¿Qué se decidió y por qué? → `docs/decisiones/` (ADRs inmutables; una
  reversión es un ADR nuevo que referencia al anterior).
- ¿Qué corre y dónde? → `docs/INFRAESTRUCTURA.md`.

## Reglas de trabajo

1. Antes de proponer un cambio: revisar BITACORA, BACKLOG y ADRs. Si la idea ya
   está en el BACKLOG, decirlo con su prioridad en vez de presentarla como nueva.
2. Al diagnosticar una falla: ubicar primero la fase (extracción / carga /
   transformación) y luego la causa.
3. Consultas analíticas: solo lectura (rol `lector`). Cambios de esquema solo por
   archivos `sql/NN_*.sql` numerados e idempotentes, aplicados con
   `python -m datos_colombia aplicar-sql` (rol dueño, local); nunca DDL suelto.
   El cron (`escritor_cron`) no ejecuta DDL.
4. Toda serie nueva entra por un módulo en `src/datos_colombia/fuentes/`, con
   parser puro probado en `tests/` con un fixture real recortado.
5. Toda fuente nueva se registra en `docs/FUENTES.md` con estado
   (✅ operativa, ⚠️ con fallas conocidas o manual, ⏸ pausada / descontinuada).
6. Antes de publicar cifras de una fuente ⚠️ o ⏸, advertir estado y fecha de corte.
7. Al cerrar una sesión de trabajo real: proponer la entrada de BITACORA y la
   actualización de BACKLOG; si se tomó o revirtió una decisión, redactar el ADR.
8. Sin credenciales en el repo: `.env` está en `.gitignore`; solo `.env.example`.
9. Tableros públicos: cada cifra muestra fuente y fecha de corte; sin datos
   personales ni microdatos sin agregar.
