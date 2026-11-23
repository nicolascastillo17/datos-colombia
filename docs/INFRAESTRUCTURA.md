# Infraestructura

Stack aceptado el 2026-11-23 (ADR 0002, 0003, 0004).

| Componente | Dónde | Estado | Costo/mes | Notas |
|---|---|---|---|---|
| Código | GitHub público [`nicolascastillo17/datos-colombia`](https://github.com/nicolascastillo17/datos-colombia) | creado 2026-11-23 | US$0 | Push por SSH con alias `github-personal`. `main` protegida: PR obligatorio + checks `pruebas (3.10)` y `pruebas (3.12)`; sin aprobaciones requeridas (un mantenedor) |
| CI | GitHub Actions `ci.yml` (pytest, 3.10 y 3.12) | activo, verde | US$0 | Sin secretos; corre en PRs de forks |
| Extracción programada | GitHub Actions `extraer.yml` | listo, cron apagado | US$0 | Encender al tener carga a Postgres |
| Postgres curado | Neon Free (1 proyecto, región AWS us-east-1) | por crear | US$0 | Límites: 1 GB, 100 CU-h/mes. Roles: `escritor_cron` (carga raw, sin DDL), `lector` (SELECT); `sql/00_schemas.sql` + `sql/01_grants.sql` |
| Tableros públicos | Evidence → GitHub Pages | por crear | US$0 | Build diario tras la extracción |
| Secretos | GitHub Secrets: `DATABASE_URL`, `DATOS_GOV_APP_TOKEN` | por crear | US$0 | Nunca en el repo |
| Consulta desde Claude | Extensión Postgres en Claude Desktop con rol `lector` | por crear | US$0 | Separada de las extensiones Griky |

## Acceso desde el Mac del mantenedor

La cuenta personal convive con la de Griky sin cambiar de sesión:
- `~/.ssh/config` → `Host github-personal` con `~/.ssh/id_ed25519_personal`.
- `~/.gitconfig` → `includeIf "gitdir:~/Documents/datos-colombia/"` carga
  `~/.gitconfig-personal` (correo `noreply` de GitHub).
- Remoto: `git@github-personal:nicolascastillo17/datos-colombia.git`.
- VS Code sigue con la cuenta `griky-nc`; no interviene en el push por terminal.

Ruta de escalamiento: Neon Launch (pago por uso, misma cadena) o `pg_dump` a
AWS RDS con ADR nuevo.
