# 0001 — Un solo repositorio con un módulo por fuente

- **Estado:** aceptada
- **Fecha:** 2026-11-23
- **Ámbito:** todo el proyecto

## Contexto

En Griky cada pipeline tiene su repo y existe un repo de plataforma
(`griky-data-platform`) para decisiones transversales. Ese modelo responde a
varios dueños, credenciales por pipeline y ciclos de despliegue distintos.
datos-colombia tiene un solo dueño, fuentes pequeñas y un único destino.

## Decisión

Monorepo: `src/datos_colombia/fuentes/<fuente>.py` por fuente, documentación
única en `docs/` (BITACORA, BACKLOG, FUENTES, INFRAESTRUCTURA, decisiones).
Descartado multi-repo: duplica BITACORA/BACKLOG, CI y dependencias sin
beneficio para un solo mantenedor.

## Consecuencias

- Un solo `requirements.txt`, un solo CI, una sola bitácora.
- Las fuentes comparten utilidades (`comun/`): un cambio ahí afecta a todas;
  los tests de parsers cubren ese riesgo.
- Si una fuente crece hasta necesitar despliegue propio (p. ej. procesamiento
  de microdatos), se separa con un ADR nuevo.

## Referencias

BITACORA 2026-11-23.
