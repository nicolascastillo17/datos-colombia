# Conector local de Postgres para Claude

`.mcp.json` (raíz del repo) declara un servidor MCP local que Claude Code y
Cowork cargan al abrir esta carpeta. Expone `execute_sql` (solo lectura,
máx. 1000 filas, 30 s) contra Neon con el rol `lector`, usando DBHub
(Bytebase), el mismo servidor que la extensión Griky · Postgres.

No es una extensión de Claude Desktop (`.mcpb`): la cuenta de Claude usada
tiene Allowlist de organización y no acepta extensiones fuera de su registro.
El conector local por carpeta no pasa por ese registro.

## Requisitos

- Node ≥ 22 (`node --version`); `npx` descarga DBHub la primera vez.
- `DATABASE_URL_LECTOR` exportada en el shell que lanza Claude. `.mcp.json`
  no lee `.env`; la forma más simple es agregar a `~/.zshrc`:

  ```bash
  export DATABASE_URL_LECTOR="$(grep '^DATABASE_URL_LECTOR=' ~/Documents/datos-colombia/.env | cut -d= -f2-)"
  ```

  Solo se exporta la cadena del rol `lector`; las de `escritor_cron` y del
  dueño se quedan en `.env`.

## Probar

Desde la carpeta del repo, en Claude Code: `/mcp` debe listar
`datos-colombia-postgres` como conectado. Consulta de prueba:

```sql
SELECT fuente, count(*) FROM raw_series.observaciones GROUP BY 1;
```

## Reglas (CLAUDE.md)

Solo lectura; los cambios de esquema siguen entrando por `sql/NN_*.sql` y
`python -m datos_colombia aplicar-sql`.
