# Stack y costos — evaluación inicial (2026-11-23)

Restricción: tope ~US$20/mes. Volumen esperado: series macro y de sentimiento
en el orden de MB; agregados de DANE en decenas de MB. Microdatos (GEIH, ECV)
quedan fuera de fase 1.

## Hechos verificados

| Ítem | Dato | Fuente |
|---|---|---|
| AWS Free Tier (cuentas nuevas desde 2025-07-15) | US$100 al registrarse + hasta US$100 por actividades; plan Free expira a los 6 meses o al agotar créditos; créditos vencen a los 12 meses | aws.amazon.com/free/terms, aws.amazon.com/free/faqs |
| AWS RDS en plan Free | db.t3.micro / db.t4g.micro (PostgreSQL incluido) | aws.amazon.com/rds/free |
| AWS IPv4 pública | US$0,005/IP/hora (≈US$3,65/mes); en RDS no la cubre el free tier de EC2 | blog AWS IPv4, re:Post |
| Neon Free | US$0, sin vencimiento: 100 proyectos, 1 GB Postgres por proyecto, 100 CU-h/mes por proyecto, escala a cero tras 5 min | neon.com/faqs/free-plan-limits-and-quotas |
| Neon Launch | US$0,106/CU-h, US$0,35/GB-mes, sin mínimo; mismo connection string que Free | neon.com/docs/introduction/plans |
| Evidence | Open source (MIT), SQL + Markdown → sitio estático; DuckDB-WASM en el navegador; despliegue a GitHub Pages, Cloudflare Pages, Netlify, etc. | github.com/evidence-dev/evidence, docs |
| Observable Framework | Open source; generador estático con data loaders en cualquier lenguaje | observablehq.com/framework |

## Opciones

| | A. AWS espejo de Griky | B. AWS serverless | C. GitHub Actions + Neon + sitio estático | D. GitHub Actions + DuckDB/Parquet + sitio estático |
|---|---|---|---|---|
| Orquestación | EC2 t4g.nano con cron, o EventBridge + Lambda | EventBridge + Lambda | GitHub Actions (cron) | GitHub Actions (cron) |
| Almacenamiento | RDS Postgres db.t4g.micro | S3 Parquet + Athena / DuckDB | Postgres Neon Free | Parquet/DuckDB en el repo o en almacenamiento de objetos |
| Tableros públicos | sitio estático en S3/CloudFront o Pages | ídem | Evidence en GitHub/Cloudflare Pages | Evidence en GitHub/Cloudflare Pages |
| Costo tras créditos | ≈US$15–20/mes (instancia + 20 GB + IPv4; estimado, validar en AWS Pricing Calculator) | <US$1/mes | US$0 | US$0 |
| Reuso del workflow Griky | Total (mismo motor, mismos patrones) | Bajo (Athena/Lambda) | Alto: Postgres, SQL numerado, capa de vistas, extensión MCP de Postgres en Claude Desktop con la cadena de Neon | Medio: SQL DuckDB; sin servidor que consultar desde Claude Desktop salvo archivo local |
| Riesgo | Gasto fijo desde el día 1 tras créditos; operar VPC/seguridad | Más fontanería IAM/Lambda | Límites Free (1 GB, 100 CU-h); dependencia de un proveedor | Archivos grandes en git; sin concurrencia |
| Ruta de crecimiento | Escalar instancia | Escalar sin cambios | Neon Launch (pago por uso, misma cadena) o migrar a RDS con `pg_dump` | Pasar a C o A |

## Análisis

- Para este volumen, AWS con base dedicada (A) paga un costo fijo por capacidad
  ociosa: la base trabaja minutos al día. El valor de A está en practicar AWS,
  no en el costo.
- C conserva lo que hoy funciona en Griky (Postgres, capas `raw → vistas → kpi`,
  `execute_sql` desde Claude Desktop, SQL versionado) a US$0, con escalamiento
  dentro del presupuesto sin migración de datos.
- D es la opción más simple, pero pierde el patrón de consulta en vivo desde
  Claude Desktop.
- Los créditos de AWS (hasta US$200) cubren A durante el primer año solo si la
  cuenta es nueva; una cuenta existente no recibe créditos.

**Opción más sólida para fase 1: C.** AWS queda como ruta de escalamiento si
aparece procesamiento pesado (microdatos) o cómputo persistente. El margen de
US$20 queda para dominio propio y, si hace falta, Neon Launch.

## Tableros públicos

| Opción | Costo | Encaje | Limitación |
|---|---|---|---|
| Evidence (estático) | US$0 en GitHub/Cloudflare Pages | SQL + Markdown, conecta a Postgres en build, interacción en navegador con DuckDB-WASM | Datos se actualizan al reconstruir (cron diario) |
| Observable Framework | US$0 | Máxima libertad visual (JS), data loaders en Python | Más código por tablero |
| Looker Studio | US$0 | Conecta a Postgres, sin código | No versionable; estilo limitado |
| Artefactos de Claude (patrón GRIKY Intelligence) | — | Mismo flujo de diseño | La consulta en vivo depende del conector de quien mira: no sirve para público anónimo |

**Opción más sólida: Evidence**, por continuidad con SQL y despliegue estático
gratuito. Observable Framework como alternativa si se requiere diseño a medida.

## Resultado

ADR 0002 y 0003 aceptados el 2026-11-23 (opción C + Evidence). Repo público
(ADR 0004): los runners estándar de GitHub Actions son gratuitos en repos
públicos; en privados consumen la cuota del plan (2.000 min/mes en GitHub Free).

Pendiente: prueba de build de Evidence contra Neon desde GitHub Actions (BACKLOG).
