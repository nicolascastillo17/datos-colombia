# 0004 — Repositorio público y colaborativo

- **Estado:** aceptada
- **Fecha:** 2026-11-23
- **Ámbito:** GitHub, CI, secretos, contribuciones, licencia

## Contexto

El proyecto se publica en GitHub con intención colaborativa. En repos públicos
los runners estándar de GitHub Actions no consumen minutos (ADR 0002 depende de
eso). Un repo público expone todo lo versionado y recibe PRs desde forks.

## Decisión

- Repo público; rama `main` protegida: cambios solo por PR con CI en verde
  (`pytest`) y revisión del mantenedor.
- Secretos (`DATABASE_URL` de escritura, `DATOS_GOV_APP_TOKEN`) solo en GitHub
  Secrets; los workflows con secretos corren en `main` (cron / manual), nunca
  en PRs de forks.
- Colaboradores no necesitan acceso a la base: trabajan con
  `python -m datos_colombia extraer` y Parquet locales. Acceso de lectura a
  Neon solo para quien lo pida, con rol `lector` (BACKLOG).
- Licencia MIT para el código. Los datos conservan los términos de cada fuente
  (`docs/FUENTES.md`); los tableros citan fuente y fecha de corte.
- Las convenciones de BITACORA / BACKLOG / ADR aplican a todos: un PR que cambia
  comportamiento incluye su entrada de BITACORA; una decisión nueva, su ADR.

Descartado: repo privado con colaboradores invitados (consume minutos de
Actions y limita la colaboración abierta).

## Consecuencias

- US$0 en CI y extracción programada.
- Cualquier archivo versionado es público: `.env`, `data/` y credenciales
  quedan fuera por `.gitignore`; revisar cada PR por secretos.
- Un PR de un fork no puede probar contra la base: las pruebas son offline
  (fixtures), por diseño.

## Referencias

ADR 0002; `CONTRIBUTING.md`; documentación de facturación de GitHub Actions.
