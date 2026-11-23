# Cómo contribuir

## Entorno

```bash
python3 --version                 # requiere 3.10 o superior
python3 -m venv .venv
source .venv/bin/activate         # dentro del venv, `python` ya existe
pip install -e ".[dev]"
pytest -q
python -m datos_colombia probar   # requiere internet; no escribe nada
```

No se necesita acceso a la base de datos: `extraer` deja Parquet en `data/`.
Las pruebas de base de datos (`tests/test_db.py`) se omiten salvo que
`TEST_DATABASE_URL` apunte a un Postgres desechable con rol dueño.

## Flujo

1. Abrir un issue (plantillas: *Nueva fuente*, *Error en datos*) o tomar uno del
   BACKLOG.
2. Rama desde `main`; PR con CI en verde.
3. Todo PR que cambie comportamiento agrega su entrada en `docs/BITACORA.md`.
   Una decisión nueva va como ADR en `docs/decisiones/` (copiar `PLANTILLA.md`).

## Agregar una fuente (checklist)

- [ ] Módulo `src/datos_colombia/fuentes/<fuente>.py` con `parsear()` puro,
      `extraer()` y `probar()`.
- [ ] Salida en el esquema `observaciones` (`comun/almacen.py`).
- [ ] Fixture real recortado + prueba en `tests/`.
- [ ] Registro en `FUENTES` de `cli.py`.
- [ ] Fila en `docs/FUENTES.md`: acceso, frecuencia, términos de uso y estado.
- [ ] Entrada en `docs/BITACORA.md`.

## Reglas

- Nunca versionar credenciales, `.env` ni archivos de `data/`.
- Respetar los límites de cada API (pausas, token de datos.gov.co).
- Sin microdatos ni datos personales en tableros: solo agregados publicados.
- Código bajo licencia MIT; los datos conservan los términos de cada fuente.
