# datos-colombia

Observatorio personal de datos abiertos de Colombia: macroeconomía, sentimiento
(confianza del consumidor, tono de noticias) y condiciones de vida. Los datos
se extraen de fuentes públicas, se normalizan y se publican en tableros
abiertos al público.

Proyecto abierto y colaborativo (ver `CONTRIBUTING.md`). Mantenedor: Nicolás
Castillo. Documentación por BITACORA, BACKLOG, ADRs y fuentes con estado.

Stack (ADR 0002, 0003): GitHub Actions (cron) → Parquet → Postgres en Neon →
tableros estáticos con Evidence en GitHub Pages / Cloudflare Pages. Costo: US$0/mes.

## Estructura

```
datos-colombia/
├── CLAUDE.md                  # reglas para Claude (Code / Desktop / Proyecto)
├── docs/
│   ├── BITACORA.md            # qué pasó y por qué (cronológico)
│   ├── BACKLOG.md             # pendientes priorizados 🔴🟡🟢
│   ├── FUENTES.md             # inventario de fuentes, estado y método de acceso
│   ├── INFRAESTRUCTURA.md     # qué corre y dónde (se llena al decidir stack)
│   ├── STACK-Y-COSTOS.md      # evaluación AWS vs alternativas de bajo costo
│   ├── decisiones/            # ADRs inmutables (una reversión es un ADR nuevo)
│   └── claude/                # instrucciones para el Proyecto de claude.ai
├── src/datos_colombia/
│   ├── comun/                 # HTTP con reintentos, escritura Parquet
│   ├── fuentes/               # un módulo por fuente (extraer + parsear)
│   └── cli.py                 # python -m datos_colombia ...
├── sql/                       # DDL numerado (se aplica al decidir el motor)
├── dashboards/                # sitio público (Evidence u otro, ver ADR 0003)
├── tests/                     # pruebas offline de los parsers con fixtures
└── data/                      # aterrizaje local (gitignored)
```

## Uso rápido

```bash
python3 --version                # 3.10+ (el python3 de Xcode en macOS es 3.9)
python3 -m venv .venv && source .venv/bin/activate   # dentro del venv existe `python`
pip install -e ".[dev]"
cp .env.example .env            # token opcional de datos.gov.co

python -m datos_colombia probar          # ping a cada fuente, sin escribir nada
python -m datos_colombia extraer banrep  # escribe data/raw/banrep/...parquet
python -m datos_colombia extraer todas
pytest -q
```

## Capas de datos

| Capa | Dónde | Contenido |
|---|---|---|
| raw | `data/raw/<fuente>/<conjunto>/extraido=AAAA-MM-DD/*.parquet` | Respuesta normalizada al esquema `observaciones`, sin transformar valores |
| curada | motor SQL (ADR 0002) | Vistas por tema: `macro`, `sentimiento`, `vida` |
| indicadores | `docs/` + vistas `kpi_*` | Definición única de cada indicador publicado |

Esquema `observaciones` (todas las series de tiempo):
`fuente, conjunto, serie_id, fecha, valor, unidad, frecuencia, extraido_en`.

## Licencias

Código: MIT (`LICENSE`).

Datos: cada fuente conserva sus términos de uso (ver `docs/FUENTES.md`). Los tableros
citan la fuente y la fecha de corte de cada cifra.
