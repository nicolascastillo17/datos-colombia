# Infraestructura

Stack aceptado el 2026-11-23 (ADR 0002, 0003, 0004).

| Componente | Dónde | Estado | Costo/mes | Notas |
|---|---|---|---|---|
| Código | GitHub público [`nicolascastillo17/datos-colombia`](https://github.com/nicolascastillo17/datos-colombia) | creado 2026-11-23 | US$0 | Push por SSH con alias `github-personal`. `main` protegida: PR obligatorio + checks `pruebas (3.10)` y `pruebas (3.12)`; sin aprobaciones requeridas (un mantenedor) |
| CI | GitHub Actions `ci.yml` (pytest, 3.10 y 3.12) | activo, verde | US$0 | Sin secretos; corre en PRs de forks |
| Extracción programada | GitHub Actions `extraer.yml` | listo, cron apagado | US$0 | Encender al tener carga a Postgres |
| Postgres curado | Neon Free, proyecto `datos-colombia`, rama `production`, base `neondb` | creado 2026-11-23 | US$0 | Límites: 1 GB, 100 CU-h/mes. Roles creados por SQL (no consola: heredaría `neon_superuser`): `escritor_cron` (carga raw, sin DDL), `lector` (SELECT); dueño `neondb_owner` solo para `aplicar-sql` |
| Tableros públicos | Evidence → GitHub Pages | por crear | US$0 | Build diario tras la extracción |
| Secretos | GitHub Secrets: `DATABASE_URL` (escritor_cron), `DATOS_GOV_APP_TOKEN`. Local `.env`: además `DATABASE_URL_OWNER` y `DATABASE_URL_LECTOR` | por crear | US$0 | Nunca en el repo; la URL del dueño nunca sale del Mac |
| Consulta desde Claude | Servidor MCP local `datos-colombia-postgres` (`.mcp.json` + `mcp/dbhub.toml`, DBHub) con rol `lector`; Claude Code / Cowork lo cargan en esta carpeta | listo en repo | US$0 | No es `.mcpb`: la cuenta de Claude tiene Allowlist de organización. Requiere `DATABASE_URL_LECTOR` exportada (ver `mcp/README.md`) |
| Consulta desde DBeaver | Conexión `datos-colombia · lector (Neon)` | creada 2026-11-23 | US$0 | Keep-Alive desactivado para no gastar CU-h |

## Acceso desde el Mac del mantenedor

La cuenta personal convive con la de Griky sin cambiar de sesión:
- `~/.ssh/config` → `Host github-personal` con `~/.ssh/id_ed25519_personal`.
- `~/.gitconfig` → `includeIf "gitdir:~/Documents/datos-colombia/"` carga
  `~/.gitconfig-personal` (correo `noreply` de GitHub).
- Remoto: `git@github-personal:nicolascastillo17/datos-colombia.git`.
- VS Code sigue con la cuenta `griky-nc`; no interviene en el push por terminal.

Ruta de escalamiento: Neon Launch (pago por uso, misma cadena) o `pg_dump` a
AWS RDS con ADR nuevo.
