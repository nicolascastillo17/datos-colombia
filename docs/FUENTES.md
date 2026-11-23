# Fuentes de datos

Estado: ✅ operativa · ⚠️ fallas conocidas, sin API o carga manual · ⏸ pausada / descontinuada · 🔎 por validar

Verificación inicial: 2026-11-23 (consulta web + primera ejecución de `probar` en el Mac).

## Macroeconomía

| Fuente | Conjunto | Acceso | Frecuencia | Módulo | Estado |
|---|---|---|---|---|---|
| Banco de la República | TPM, TRM, IBR, DTF, UVR, COLCAP, agregados monetarios, TES | SDMX REST `https://totoro.banrep.gov.co/nsi-jax-ws/rest/data/ESTAT,<DF>,1.0/all/ALL` | diaria / mensual | `banrep_sdmx` | ✅ historia completa en 125 s (~100 mil obs). Varias series por `SUBJECT` (p. ej. IBR efectiva `ER` y nominal `NR`): `serie_id` = `<conjunto>:<SUBJECT>.<dims ≠ _Z>`. `startPeriod` se respeta solo por año |
| Banco de la República | Series históricas (PIB, sector externo, fiscal, IPC BanRep) | Portal SUAMECA (catálogo, descarga múltiple) | varias | — | 🔎 sin API documentada para estas series; descarga manual |
| datos.gov.co (Socrata) | TRM `32sa-8pi3` y otros conjuntos | SODA `https://www.datos.gov.co/resource/<id>.json` | diaria | `datos_gov` | ✅ 0,6 s sin token |
| DANE | IPC (variaciones mensuales, anuales, por división) | Anexo xlsx `files/operaciones/IPC/<mes><año>/anex-IPC-Variacion-<mes><año>.xlsx` | mensual | `dane` (solo descarga) | ⚠️ sin API; anexo oct-2026 disponible (41 KB); parser pendiente |
| DANE | GEIH (desempleo, informalidad), PIB, ISE | Anexos xlsx por publicación | mensual / trimestral | — | ⚠️ sin API |
| Banco Mundial | WDI: crecimiento PIB, inflación, desempleo, Gini, pobreza | API v2 `https://api.worldbank.org/v2/country/COL/indicator/<id>?format=json` | anual | `banco_mundial` | ⚠️ intermitente (respondió en la extracción de las 13:54): 2 corridas con timeout desde el Mac (11:40 y 11:45) mientras respondía desde otra red a las 11:50; la extracción tolera con 4 reintentos |
| FMI | WEO / IFS | API SDMX | anual / trimestral | — | 🟢 backlog |

## Sentimiento

| Fuente | Conjunto | Acceso | Frecuencia | Módulo | Estado |
|---|---|---|---|---|---|
| Fedesarrollo | Encuesta de Opinión del Consumidor: ICC, IEC, ICE | Boletín mensual (PDF/xlsx en web) | mensual | `fedesarrollo` (CSV manual) | ⚠️ sin API; microdatos 2001–2016 en ANDA |
| GDELT | Tono promedio de noticias de medios colombianos | DOC 2.0 API `mode=timelinetone` | diaria (ventana reciente) | `gdelt` | ✅ validado (37 puntos en la 1.ª corrida). Lento (20-50 s) y con límite de tasa: 429 tras 3 consultas en 10 min; máximo una corrida cada ~15 min. El día en curso se excluye |
| DANE | Encuesta Pulso Social (confianza, bienestar subjetivo) | Microdatos ANDA | — | — | ⏸ cerrada tras 36 rondas (2023); solo histórico |

## Condiciones de vida

| Fuente | Conjunto | Acceso | Frecuencia | Módulo | Estado |
|---|---|---|---|---|---|
| DANE | Pobreza monetaria y multidimensional | Anexos xlsx | anual | — | 🟡 backlog |
| DANE | Encuesta de Calidad de Vida (ECV) | Anexos + microdatos ANDA | anual | — | 🟡 backlog |
| Banco Mundial | Gini, pobreza (línea nacional) | API v2 | anual | `banco_mundial` | 🔎 |
| DNP | TerriData (indicadores municipales) | Descarga | anual | — | 🟢 backlog |

## Notas de acceso

- **BanRep SDMX**: lista de dataflows en `.../rest/dataflow/all/all/latest`
  (agencia `ESTAT`, 33 dataflows al 2026-11-23). La serie se identifica por
  dimensiones OECD/STES (`REFERENCE_AREA`, `SUBJECT`, `UNIT_MEASURE`, `FREQ`).
- **datos.gov.co**: sin token se comparte el límite por IP; con token
  (`X-App-Token`) el límite sube. SODA3 exige identificación por token.
- **GDELT**: consultas con `sourcecountry:CO` restringen a medios de Colombia.
  La API cubre una ventana reciente: la serie histórica se construye
  acumulando ejecuciones diarias.
- **Fedesarrollo**: el ICC es el promedio de los balances de cinco preguntas
  de la EOC; publicación mensual. Carga manual en `data/manual/fedesarrollo/`.
