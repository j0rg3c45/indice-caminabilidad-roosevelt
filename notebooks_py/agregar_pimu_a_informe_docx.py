from pathlib import Path
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

DOCX = Path('outputs/informes/informe_caminabilidad_barrio_obrero.docx')
FUENTE = "Arial"
SIZE_CUERPO = Pt(11)
SIZE_H1 = Pt(14)
AZUL = RGBColor(0x1B, 0x4F, 0x8A)
GRIS = RGBColor(0x44, 0x44, 0x44)

doc = Document(DOCX)

if any("Plan Integral de Movilidad" in p.text for p in doc.paragraphs):
    print("La seccion PIMU ya existe; no se modifica.")
    raise SystemExit(0)

def _run(par, texto, size=SIZE_CUERPO, bold=False, color=None):
    r = par.add_run(texto)
    r.font.name = FUENTE; r.font.size = size; r.bold = bold
    if color is not None:
        r.font.color.rgb = color
    return r

# Localizar el encabezado "Métricas de línea base" para insertar antes
anchor_p = None
for p in doc.paragraphs:
    if p.text.strip() == "Métricas de línea base":
        anchor_p = p
        break

# Construir los elementos de la nueva sección en una lista de (tipo, contenido)
def _mk_par(texto, size=SIZE_CUERPO, bold=False, color=None, justify=True, space_after=8, space_before=0):
    p = doc.add_paragraph()
    _run(p, texto, size=size, bold=bold, color=color)
    if justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(space_after)
    if space_before:
        p.paragraph_format.space_before = Pt(space_before)
    return p

# Título
p_tit = _mk_par("Contexto de la malla vial de Cali (PIMU)", size=SIZE_H1, bold=True, color=AZUL,
                justify=False, space_after=6, space_before=12)
p1 = _mk_par("Para situar la jerarquía de las vías analizadas, tomamos como soporte documental "
             "el Documento Técnico de Soporte del Plan Integral de Movilidad Urbana (PIMU) de "
             "Santiago de Cali. Según esta fuente, la malla vial principal de la ciudad se "
             "distribuye en arterias primarias (459,9 km, ~45%), arterias secundarias "
             "(306,6 km, ~30%) y vías colectoras (245,28 km, ~24%), para un total aproximado de "
             "1.012 km.")
p2 = _mk_par("Conviene precisar que esa cifra corresponde únicamente a la malla vial principal "
             "vehicular, y no a la malla total. Al incorporar las vías locales y barriales, la "
             "red vial urbana total de Cali supera los 2.600–2.800 km lineales. La red peatonal "
             "que se calcula en este informe con OSMnx es todavía más densa, ya que contabiliza "
             "andenes a ambos costados, senderos, callejones y cruces que no forman parte del "
             "inventario vehicular formal. Por ello, los kilómetros de red peatonal de las zonas "
             "de estudio no son comparables de forma directa con los del PIMU: responden a "
             "definiciones, escalas y coberturas distintas.")
p3 = _mk_par("En la práctica, este dato nos sirve para caracterizar la jerarquía de los "
             "corredores —por ejemplo, la Av. Roosevelt como vía arteria secundaria o colectora "
             "según el tramo, frente a las vías locales que predominan en el Barrio Obrero— y no "
             "como referencia numérica de la longitud de la red peatonal.")
p4 = _mk_par("Fuente: Alcaldía de Santiago de Cali & Secretaría de Movilidad (2018). Plan "
             "Integral de Movilidad Urbana de Santiago de Cali (PIMU) — Documento Técnico de "
             "Soporte (DTS). Santiago de Cali, Colombia. Cap. Diagnóstico de la Malla Vial "
             "Principal (en el marco del POT — Acuerdo 0373 de 2014).",
             size=Pt(9.5), color=GRIS)

nuevos = [p_tit._p, p1._p, p2._p, p3._p, p4._p]

# Mover los nuevos párrafos justo antes del ancla (si existe); si no, quedan al final
if anchor_p is not None:
    anchor_el = anchor_p._p
    for el in nuevos:
        el.getparent().remove(el)
        anchor_el.addprevious(el)
    print("Seccion PIMU insertada antes de 'Metricas de linea base'.")
else:
    print("No se encontro ancla; la seccion PIMU quedo al final.")

doc.save(DOCX)
print("Word guardado.")
