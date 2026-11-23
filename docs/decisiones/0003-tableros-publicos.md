# 0003 — Tableros públicos como sitio estático (Evidence)

- **Estado:** aceptada (2026-11-23)
- **Fecha:** 2026-11-23
- **Ámbito:** `dashboards/`, publicación

## Contexto

Los tableros deben ser públicos y anónimos, a costo cercano a cero. El patrón
de GRIKY Intelligence (artefactos de Claude con datos en vivo) depende del
conector de quien consulta, por lo que no sirve para público anónimo.

## Decisión

Evidence (open source) en `dashboards/`: páginas en Markdown + SQL, build
contra el Postgres curado (ADR 0002), despliegue estático a GitHub Pages o
Cloudflare Pages, reconstrucción diaria por cron.

Descartados:
- Looker Studio: sin control de versiones.
- Streamlit u otros con servidor: costo o latencia de arranque; innecesario para datos que cambian a diario.
- Observable Framework: alternativa válida; queda como plan B si se requiere diseño a medida en JS.

## Consecuencias

- Costo US$0; sin credenciales expuestas (el sitio solo contiene datos ya agregados).
- Los datos del tablero tienen la frescura del último build.
- Cada página muestra fuente y fecha de corte (regla 9 de `CLAUDE.md`).

## Referencias

`docs/STACK-Y-COSTOS.md`.
