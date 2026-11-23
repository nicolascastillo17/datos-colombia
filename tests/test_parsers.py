"""Pruebas offline de parsers con fixtures que reproducen la forma de cada respuesta.

Reemplazar cada fixture por un recorte real al validar la fuente desde el Mac.
"""

from datetime import date

import pyarrow.parquet as pq

from datos_colombia.comun.almacen import a_float, guardar_observaciones
from datos_colombia.fuentes import banco_mundial, banrep_sdmx, dane, datos_gov, fedesarrollo, gdelt

SDMX_GENERICO = b"""<?xml version="1.0" encoding="UTF-8"?>
<message:GenericData xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message"
  xmlns:generic="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic">
 <message:DataSet>
  <generic:Series>
   <generic:SeriesKey>
    <generic:Value id="REFERENCE_AREA" value="CO"/>
    <generic:Value id="SUBJECT" value="IRCBRM01"/>
    <generic:Value id="UNIT_MEASURE" value="PA"/>
    <generic:Value id="FREQ" value="D"/>
   </generic:SeriesKey>
   <generic:Obs><generic:ObsDimension value="2026-11-22"/><generic:ObsValue value="12.25"/></generic:Obs>
   <generic:Obs><generic:ObsDimension value="2026-11-23"/><generic:ObsValue value="12.25"/></generic:Obs>
  </generic:Series>
 </message:DataSet>
</message:GenericData>"""

SDMX_ESPECIFICO = b"""<?xml version="1.0"?>
<message:StructureSpecificData xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message">
 <message:DataSet>
  <Series REFERENCE_AREA="CO" SUBJECT="CCUSMA02" UNIT_MEASURE="COP" FREQ="M">
   <Obs TIME_PERIOD="2026-10" OBS_VALUE="3850.5"/>
   <Obs TIME_PERIOD="2026-Q3" OBS_VALUE="NaN"/>
  </Series>
 </message:DataSet>
</message:StructureSpecificData>"""


def test_banrep_generico():
    obs = banrep_sdmx.parsear(SDMX_GENERICO, "tpm")
    assert [(o.fecha, o.valor) for o in obs] == [(date(2026, 11, 22), 12.25), (date(2026, 11, 23), 12.25)]
    assert obs[0].serie_id == "tpm:IRCBRM01" and obs[0].frecuencia == "diaria" and obs[0].unidad == "PA"


def test_banrep_formatos_de_periodo():
    f = banrep_sdmx._fecha
    assert f("20260101") == date(2026, 1, 1)  # formato real observado en BanRep
    assert f("202603") == date(2026, 3, 1)
    assert f("2026-11-21T00:00:00") == date(2026, 11, 21)
    assert f("2026-M11") == date(2026, 11, 1)
    assert f("2026") == date(2026, 1, 1)


def test_banrep_especifico_y_periodos():
    obs = banrep_sdmx.parsear(SDMX_ESPECIFICO, "trm")
    assert obs[0].fecha == date(2026, 10, 1) and obs[0].valor == 3850.5 and obs[0].frecuencia == "mensual"
    assert obs[1].fecha == date(2026, 7, 1) and obs[1].valor is None


def test_datos_gov_trm():
    filas = [{"valor": "3461.92", "unidad": "COP", "vigenciadesde": "2026-11-21T00:00:00.000", "vigenciahasta": "2026-11-23T00:00:00.000"}]
    (o,) = datos_gov.parsear(filas, "trm")
    assert o.fecha == date(2026, 11, 21) and o.valor == 3461.92 and o.unidad == "COP"


def test_banco_mundial():
    resp = [
        {"page": 1, "pages": 1, "total": 2},
        [
            {"indicator": {"id": "NY.GDP.MKTP.KD.ZG", "value": "GDP growth"}, "date": "2025", "value": 2.6},
            {"indicator": {"id": "NY.GDP.MKTP.KD.ZG", "value": "GDP growth"}, "date": "2024", "value": None},
        ],
    ]
    obs = banco_mundial.parsear(resp)
    assert obs[0].fecha == date(2025, 1, 1) and obs[0].valor == 2.6 and obs[1].valor is None
    assert banco_mundial.parsear([{"message": "error"}]) == []


def test_gdelt():
    resp = {
        "query_details": {"title": "colombia sourcecountry:CO", "date_resolution": "day"},
        "timeline": [{"series": "Average Tone", "data": [{"date": "20261025T000000Z", "value": -0.34}, {"date": "20261027T000000Z", "value": 1.6201}]}],
    }
    obs = gdelt.parsear(resp, "general", excluir_desde=date(2026, 11, 23))
    assert obs[0].fecha == date(2026, 10, 25) and obs[1].valor == 1.6201
    assert obs[0].serie_id == "timelinetone:general"
    assert gdelt.parsear({}, "general") == []


def test_gdelt_promedia_subdiario_y_excluye_dia_en_curso():
    resp = {"timeline": [{"data": [
        {"date": "20261122T000000Z", "value": -1.0},
        {"date": "20261122T060000Z", "value": 1.0},
        {"date": "20261122T120000Z", "value": 3.0},
        {"date": "20261123T000000Z", "value": 0.0},
    ]}]}
    obs = gdelt.parsear(resp, "general", excluir_desde=date(2026, 11, 23))
    assert [(o.fecha, o.valor) for o in obs] == [(date(2026, 11, 22), 1.0)]


def test_fedesarrollo_csv():
    obs = fedesarrollo.parsear(["fecha,icc,iec,ice\n", "2026-10,-2.4,5.1,-13.2\n"])
    assert {o.serie_id: o.valor for o in obs} == {"icc": -2.4, "iec": 5.1, "ice": -13.2}
    assert obs[0].fecha == date(2026, 10, 1)


def test_dane_url_y_mes_publicado():
    assert dane.url_anexo_ipc(2024, 12).endswith("/IPC/dic2024/anex-IPC-Variacion-dic2024.xlsx")
    assert dane._ultimo_mes_publicado(date(2026, 11, 23)) == (2026, 10)
    assert dane._ultimo_mes_publicado(date(2026, 1, 5)) == (2025, 11)


def test_a_float():
    assert a_float("12,25") == 12.25 and a_float("3461.92") == 3461.92
    assert a_float("") is None and a_float(None) is None and a_float("NaN") is None


def test_guardar_parquet(tmp_path):
    obs = banrep_sdmx.parsear(SDMX_GENERICO, "tpm")
    ruta = guardar_observaciones(obs, "banrep", "tpm", base=tmp_path)
    tabla = pq.read_table(ruta)
    assert tabla.num_rows == 2
    assert tabla.column_names == ["fuente", "conjunto", "serie_id", "fecha", "valor", "unidad", "frecuencia", "extraido_en"]
