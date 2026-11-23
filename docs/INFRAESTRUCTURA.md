# Infraestructura

Stack aceptado el 2026-11-23 (ADR 0002, 0003, 0004). Componentes por crear.

| Componente | Dónde | Estado | Costo/mes | Notas |
|---|---|---|---|---|
| Código | GitHub, repo público `datos-colombia` | por crear | US$0 | `main` protegida; PR + CI |
| CI | GitHub Actions `ci.yml` (pytest, 3.10 y 3.12) | listo en repo | US$0 | Sin secretos; corre en PRs de forks |
| Extracción programada | GitHub Actions `extraer.yml` | listo, cron apagado | US$0 | Encender al tener carga a Postgres |
| Postgres curado | Neon Free (1 proyecto) | por crear | US$0 | Límites: 1 GB, 100 CU-h/mes; roles `escritor_cron`, `lector` |
| Tableros públicos | Evidence → GitHub Pages | por crear | US$0 | Build diario tras la extracción |
| Secretos | GitHub Secrets: `DATABASE_URL`, `DATOS_GOV_APP_TOKEN` | por crear | US$0 | Nunca en el repo |
| Consulta desde Claude | Extensión Postgres en Claude Desktop con rol `lector` | por crear | US$0 | Separada de las extensiones Griky |

Ruta de escalamiento: Neon Launch (pago por uso, misma cadena) o `pg_dump` a
AWS RDS con ADR nuevo.
