# Decisiones (ADRs)

Registro inmutable. Cada ADR: contexto / decisión / consecuencias. No se
editan: una reversión es un ADR nuevo que declara "reemplaza a NNNN", y el
anterior solo cambia su línea de estado. Una herramienta probada y no adoptada
queda como ADR `rechazada`.

Estados: `propuesta` · `aceptada` · `rechazada` · `reemplazada por NNNN` · `retirada`.

## Índice

| # | Fecha | Decisión | Estado |
|---|---|---|---|
| [0001](0001-monorepo.md) | 2026-11-23 | Un solo repositorio con un módulo por fuente | aceptada |
| [0002](0002-stack-almacenamiento-y-orquestacion.md) | 2026-11-23 | Orquestación en GitHub Actions + Postgres serverless (Neon Free); AWS como ruta de escalamiento | aceptada |
| [0003](0003-tableros-publicos.md) | 2026-11-23 | Tableros públicos como sitio estático (Evidence) en GitHub Pages / Cloudflare Pages | aceptada |
| [0004](0004-repo-publico-colaborativo.md) | 2026-11-23 | Repositorio público y colaborativo: PRs con pruebas, secretos solo en GitHub, licencia MIT para código | aceptada |
