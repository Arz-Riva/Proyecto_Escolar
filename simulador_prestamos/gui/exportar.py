# ==========================================
# Encabezados y Librerias
# ==========================================
import os
import tempfile
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as ImagenExcel
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as ImagenPDF

try:
    from gui.graficas import generar_figura_relacion_interes_capital, generar_figura_comparativa_escenarios
    from gui.indicadores import calcular_indicadores, formatear_mes_cruce
except ImportError:
    try:
        from simulador_prestamos.gui.graficas import generar_figura_relacion_interes_capital, generar_figura_comparativa_escenarios
        from simulador_prestamos.gui.indicadores import calcular_indicadores, formatear_mes_cruce
    except ImportError:
        from graficas import generar_figura_relacion_interes_capital, generar_figura_comparativa_escenarios
        from indicadores import calcular_indicadores, formatear_mes_cruce

# ==========================================
# Declaracion de Constantes
# ==========================================
ENCABEZADOS_TABLA = ["Mes", "Cuota ($)", "Interes ($)", "Capital ($)", "Saldo ($)"]
COLOR_CABECERA_EXCEL = "380057"
COLOR_FUENTE_CABECERA = "FFFFFF"
NOMBRE_LOGO_PDF = "intresta-logo-horizontal.png"
TEXTO_PIE_PDF = "Generado por Intresta - Simulador de Intereses y Amortizaciones"
COLOR_MORADO_PDF = "#380057"
COLOR_AMARILLO_PDF = "#E5DE4B"
ALTURA_ENCABEZADO_PDF = 62
ALTURA_PIE_PDF = 30
# Titulos con la fuente del logo, resto no-tabla/grafica en Arial
FUENTE_TITULO_EXCEL = "Segoe UI"
FUENTE_TEXTO_EXCEL = "Arial"
FUENTE_TITULO_PDF = "SegoeUI-Bold"
FUENTE_TEXTO_PDF = "Arial"


def _registrar_fuentes_pdf():
    """Registra Segoe UI y Arial para PDF; si falla usa Helvetica."""
    global FUENTE_TITULO_PDF, FUENTE_TEXTO_PDF
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        dir_fuentes = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
        ruta_segoe_bold = os.path.join(dir_fuentes, "segoeuib.ttf")
        ruta_arial = os.path.join(dir_fuentes, "arial.ttf")
        ruta_arial_bold = os.path.join(dir_fuentes, "arialbd.ttf")
        if os.path.exists(ruta_segoe_bold):
            pdfmetrics.registerFont(TTFont("SegoeUI-Bold", ruta_segoe_bold))
            FUENTE_TITULO_PDF = "SegoeUI-Bold"
        if os.path.exists(ruta_arial):
            pdfmetrics.registerFont(TTFont("Arial", ruta_arial))
            FUENTE_TEXTO_PDF = "Arial"
        if os.path.exists(ruta_arial_bold):
            pdfmetrics.registerFont(TTFont("Arial-Bold", ruta_arial_bold))
    except Exception:
        FUENTE_TITULO_PDF = "Helvetica-Bold"
        FUENTE_TEXTO_PDF = "Helvetica"


_registrar_fuentes_pdf()

# ==========================================
# Declaracion de Funciones
# ==========================================

def _calcular_totales(lista_filas: list[dict]):
    """Suma cuota e interes de una lista de filas inmutables."""
    total_pagado = sum(fila["cuota"] for fila in lista_filas)
    total_interes = sum(fila["interes"] for fila in lista_filas)
    return total_pagado, total_interes


def _texto_abonos(dict_params: dict, num_decimales: int = 2, simbolo_moneda: str = "$") -> str:
    """Arma el fragmento de abonos para resumenes de exportacion."""
    lista_abonos = dict_params.get("abonos", [])
    if not lista_abonos:
        return ""
    partes = []
    for abono in lista_abonos:
        if isinstance(abono, dict):
            val_monto = _formatear_moneda_export(float(abono.get('monto', 0)), num_decimales, simbolo_moneda)
            partes.append(f"m{abono.get('mes')}: {val_monto}")
        else:
            partes.append(str(abono))
    return " | Abonos: " + ", ".join(partes)


def _formatear_moneda_export(val_monto: float, num_decimales: int = 2, simbolo_moneda: str = "$") -> str:
    """Formatea moneda para PDF segun configuracion (sin depender de tkinter)."""
    try:
        num_dec = int(num_decimales)
    except (TypeError, ValueError):
        num_dec = 2
    if num_dec not in (0, 1, 2):
        num_dec = 2
    formato = f",.{num_dec}f" if num_dec > 0 else ",.0f"
    return f"{simbolo_moneda}{val_monto:{formato}}"


def _formato_num_excel(num_decimales: int = 2, simbolo_moneda: str = "$") -> str:
    """Arma el number_format de Excel segun decimales y simbolo."""
    try:
        num_dec = int(num_decimales)
    except (TypeError, ValueError):
        num_dec = 2
    if num_dec not in (0, 1, 2):
        num_dec = 2
    str_simbolo = simbolo_moneda.strip() if simbolo_moneda.strip() else "$"
    if num_dec == 0:
        return f'"{str_simbolo}"#,##0'
    ceros = "0" * num_dec
    return f'"{str_simbolo}"#,##0.{ceros}'


def _texto_resumen(dict_params: dict, total_pagado: float, total_interes: float,
                   num_decimales: int = 2, simbolo_moneda: str = "$") -> str:
    """Arma una linea de resumen con parametros y totales."""
    return (
        f"Sistema: {dict_params.get('sistema', '')} | "
        f"Monto: {_formatear_moneda_export(dict_params.get('monto', 0), num_decimales, simbolo_moneda)} | "
        f"Tasa: {dict_params.get('tasa', 0)}% | "
        f"Meses: {dict_params.get('meses', 0)} | "
        f"Total: {_formatear_moneda_export(total_pagado, num_decimales, simbolo_moneda)} | "
        f"Intereses: {_formatear_moneda_export(total_interes, num_decimales, simbolo_moneda)}"
        f"{_texto_abonos(dict_params, num_decimales, simbolo_moneda)}"
    )


def _ruta_logo_pdf() -> str | None:
    """Retorna la ruta del logo horizontal si existe para el encabezado pdf."""
    dir_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_logo = os.path.join(dir_actual, "Img", NOMBRE_LOGO_PDF)
    return ruta_logo if os.path.exists(ruta_logo) else None


def _dibujar_pie_pdf(lienzo, doc):
    """Compat: pie simple sin fondo para usos internos."""
    decorar = _fabrica_decoracion_pdf("Intresta")
    decorar(lienzo, doc)


def _fabrica_decoracion_pdf(titulo_doc: str, incluir_logo: bool = True, incluir_pie: bool = True):
    """Crea decorador con encabezado morado (logo+titulo amarillo) y pie morado."""
    def _decorar(lienzo, doc):
        from datetime import datetime
        lienzo.saveState()
        ancho_pag, alto_pag = A4
        # Encabezado morado en todas las paginas
        lienzo.setFillColor(colors.HexColor(COLOR_MORADO_PDF))
        lienzo.rect(0, alto_pag - ALTURA_ENCABEZADO_PDF, ancho_pag,
                    ALTURA_ENCABEZADO_PDF, stroke=0, fill=1)
        if incluir_logo:
            ruta_logo = _ruta_logo_pdf()
            if ruta_logo:
                try:
                    lienzo.drawImage(ruta_logo, 40, alto_pag - 52, width=120,
                                     height=28, preserveAspectRatio=True, mask="auto")
                except Exception:
                    pass
        try:
            lienzo.setFont(FUENTE_TITULO_PDF, 12)
        except Exception:
            lienzo.setFont("Helvetica-Bold", 12)
        lienzo.setFillColor(colors.HexColor(COLOR_AMARILLO_PDF))
        lienzo.drawRightString(ancho_pag - 40, alto_pag - 38, titulo_doc)
        # Pie morado en todas las paginas con letras blancas
        if incluir_pie:
            lienzo.setFillColor(colors.HexColor(COLOR_MORADO_PDF))
            lienzo.rect(0, 0, ancho_pag, ALTURA_PIE_PDF, stroke=0, fill=1)
            try:
                lienzo.setFont(FUENTE_TEXTO_PDF, 7)
            except Exception:
                lienzo.setFont("Helvetica", 7)
            lienzo.setFillColor(colors.white)
            texto_izq = f"{TEXTO_PIE_PDF} | {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            lienzo.drawString(40, 12, texto_izq)
            lienzo.drawRightString(ancho_pag - 40, 12, f"Pag. {doc.page}")
        lienzo.restoreState()
    return _decorar


def _parte_logo_pdf():
    """Sin uso: logo y titulo ahora van en el encabezado de pagina."""
    return []


def _estilos_pdf():
    """Retorna estilos con titulos en Segoe UI y resto en Arial."""
    estilos = getSampleStyleSheet()
    estilos["Title"].fontName = FUENTE_TITULO_PDF
    estilos["Title"].textColor = colors.HexColor("#380057")
    estilos["Normal"].fontName = FUENTE_TEXTO_PDF
    estilos["Heading2"].fontName = "Arial-Bold" if FUENTE_TEXTO_PDF == "Arial" else FUENTE_TEXTO_PDF
    return estilos


def _guardar_grafica_temporal(lista_filas: list[dict]) -> str:
    """Genera la grafica interes-capital y la guarda en un png temporal."""
    figura = generar_figura_relacion_interes_capital(lista_filas)
    archivo_tmp = tempfile.NamedTemporaryFile(delete=False, suffix="_grafica.png")
    ruta_png = archivo_tmp.name
    archivo_tmp.close()
    figura.savefig(ruta_png, dpi=150, bbox_inches="tight")
    try:
        import matplotlib.pyplot as plt
        plt.close(figura)
    except Exception:
        pass
    return ruta_png


def _guardar_grafica_comparativa_temporal(lista_a: list[dict], lista_b: list[dict]) -> str:
    """Genera la grafica A vs B y la guarda en un png temporal."""
    figura = generar_figura_comparativa_escenarios(lista_a, lista_b, "A", "B")
    archivo_tmp = tempfile.NamedTemporaryFile(delete=False, suffix="_comparativa.png")
    ruta_png = archivo_tmp.name
    archivo_tmp.close()
    figura.savefig(ruta_png, dpi=150, bbox_inches="tight")
    try:
        import matplotlib.pyplot as plt
        plt.close(figura)
    except Exception:
        pass
    return ruta_png


def _titulo_escenario(letra: str, dict_params: dict, num_decimales: int = 2, simbolo_moneda: str = "$") -> str:
    """Arma el titulo corto de un escenario para el export."""
    if not dict_params:
        return f"Escenario {letra}: sin datos"
    return (f"Escenario {letra}: {dict_params.get('sistema', '')} | "
            f"Monto {_formatear_moneda_export(dict_params.get('monto', 0), num_decimales, simbolo_moneda)} | "
            f"Tasa {dict_params.get('tasa', 0)}% | {dict_params.get('meses', 0)} meses"
            f"{_texto_abonos(dict_params, num_decimales, simbolo_moneda)}")


def _linea_indicadores(lista_filas: list[dict], dict_params: dict,
                       num_decimales: int = 2, simbolo_moneda: str = "$") -> str:
    """Arma la linea de indicadores para PDF y Excel."""
    dict_ind = calcular_indicadores(lista_filas, dict_params.get("tasa", 0))
    return (f"% Interes: {dict_ind['porc_interes']:.1f}% | "
            f"Cuota min-max: {_formatear_moneda_export(dict_ind['cuota_min'], num_decimales, simbolo_moneda)} - "
            f"{_formatear_moneda_export(dict_ind['cuota_max'], num_decimales, simbolo_moneda)} | "
            f"Cruce: {formatear_mes_cruce(dict_ind['mes_cruce'])} | "
            f"Tasa efectiva anual: {dict_ind['tasa_efectiva_anual']:.2f}%")

# ==========================================
# Proceso Principal de Exportacion
# ==========================================

def exportar_tabla_excel(lista_filas: list[dict], dict_params: dict, ruta_archivo: str,
                         num_decimales: int = 2, simbolo_moneda: str = "$") -> str:
    """Guarda tabla + grafica en .xlsx con titulo Segoe UI y texto Arial."""
    if not lista_filas:
        raise ValueError("No hay datos para exportar. Calcula una tabla primero.")
    total_pagado, total_interes = _calcular_totales(lista_filas)
    formato_excel = _formato_num_excel(num_decimales, simbolo_moneda)

    libro = Workbook()
    hoja = libro.active
    hoja.title = "Amortizacion"
    hoja.append(["Intresta - Tabla de Amortizacion"])
    hoja["A1"].font = Font(name=FUENTE_TITULO_EXCEL, bold=True, size=14, color=COLOR_CABECERA_EXCEL)
    hoja.append([_texto_resumen(dict_params, total_pagado, total_interes, num_decimales, simbolo_moneda)])
    hoja["A2"].font = Font(name=FUENTE_TEXTO_EXCEL, size=10)
    hoja.append([_linea_indicadores(lista_filas, dict_params, num_decimales, simbolo_moneda)])
    hoja["A3"].font = Font(name=FUENTE_TEXTO_EXCEL, size=10, italic=True)
    hoja.append(ENCABEZADOS_TABLA)

    # Estilo de cabecera con color corporativo
    fuente_cab = Font(bold=True, color=COLOR_FUENTE_CABECERA, size=10)
    relleno_cab = PatternFill("solid", fgColor=COLOR_CABECERA_EXCEL)
    for num_col in range(1, len(ENCABEZADOS_TABLA) + 1):
        celda = hoja.cell(row=4, column=num_col)
        celda.font = fuente_cab
        celda.fill = relleno_cab
        celda.alignment = Alignment(horizontal="center")

    for fila in lista_filas:
        hoja.append([fila["mes"], fila["cuota"], fila["interes"], fila["capital"], fila["saldo"]])

    # Formato moneda y anchos legibles
    for fila_excel in hoja.iter_rows(min_row=5, max_row=hoja.max_row, min_col=2, max_col=5):
        for celda in fila_excel:
            celda.number_format = formato_excel
    anchos = [8, 14, 14, 14, 16]
    for num_col, val_ancho in enumerate(anchos, start=1):
        hoja.column_dimensions[hoja.cell(row=4, column=num_col).column_letter].width = val_ancho

    hoja.append([])
    hoja.append(["Total Pagado:", total_pagado])
    hoja.append(["Total Intereses:", total_interes])
    for fila_tot in (hoja.max_row - 1, hoja.max_row):
        hoja.cell(row=fila_tot, column=1).font = Font(name=FUENTE_TEXTO_EXCEL, bold=True, size=10)
        hoja.cell(row=fila_tot, column=2).font = Font(name=FUENTE_TEXTO_EXCEL, size=10)
    hoja["B%d" % hoja.max_row].number_format = formato_excel
    hoja["B%d" % (hoja.max_row - 1)].number_format = formato_excel

    # Grafica conjunta en la misma hoja, sin botones separados
    ruta_png = _guardar_grafica_temporal(lista_filas)
    try:
        img_excel = ImagenExcel(ruta_png)
        img_excel.width = 620
        img_excel.height = 380
        hoja.add_image(img_excel, "G2")
        libro.save(ruta_archivo)
    finally:
        try:
            os.remove(ruta_png)
        except Exception:
            pass
    return os.path.abspath(ruta_archivo)


def exportar_tabla_pdf(lista_filas: list[dict], dict_params: dict, ruta_archivo: str,
                       num_decimales: int = 2, simbolo_moneda: str = "$",
                       incluir_logo: bool = True, incluir_pie: bool = True) -> str:
    """Guarda tabla + grafica con encabezado y pie morados y retorna la ruta."""
    if not lista_filas:
        raise ValueError("No hay datos para exportar. Calcula una tabla primero.")
    total_pagado, total_interes = _calcular_totales(lista_filas)
    titulo_doc = "Tabla de Amortizacion"

    doc = SimpleDocTemplate(ruta_archivo, pagesize=A4, topMargin=85, bottomMargin=45)
    estilos = _estilos_pdf()
    partes = [
        Paragraph(_texto_resumen(dict_params, total_pagado, total_interes, num_decimales, simbolo_moneda), estilos["Normal"]),
        Paragraph(_linea_indicadores(lista_filas, dict_params, num_decimales, simbolo_moneda), estilos["Normal"]),
        Spacer(1, 12),
    ]

    datos = [ENCABEZADOS_TABLA]
    for fila in lista_filas:
        datos.append([
            str(fila["mes"]),
            _formatear_moneda_export(fila['cuota'], num_decimales, simbolo_moneda),
            _formatear_moneda_export(fila['interes'], num_decimales, simbolo_moneda),
            _formatear_moneda_export(fila['capital'], num_decimales, simbolo_moneda),
            _formatear_moneda_export(fila['saldo'], num_decimales, simbolo_moneda),
        ])
    datos.append(["", f"Total: {_formatear_moneda_export(total_pagado, num_decimales, simbolo_moneda)}",
                  f"Intereses: {_formatear_moneda_export(total_interes, num_decimales, simbolo_moneda)}", "", ""])

    tabla = Table(datos, repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#380057")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
    ]))
    partes.append(tabla)

    # Grafica conjunta en el mismo pdf, sin botones separados
    ruta_png = _guardar_grafica_temporal(lista_filas)
    decorar = _fabrica_decoracion_pdf(titulo_doc, incluir_logo, incluir_pie)
    try:
        partes.append(Spacer(1, 12))
        partes.append(Paragraph("Relacion Interes-Capital", estilos["Heading2"]))
        partes.append(ImagenPDF(ruta_png, width=440, height=270))
        doc.build(partes, onFirstPage=decorar, onLaterPages=decorar)
    finally:
        try:
            os.remove(ruta_png)
        except Exception:
            pass
    return os.path.abspath(ruta_archivo)


def _escribir_bloque_escenario_excel(hoja, lista_filas: list[dict], dict_params: dict, letra: str,
                                     num_decimales: int = 2, simbolo_moneda: str = "$"):
    """Escribe titulo Segoe UI + resumen Arial + tabla de un escenario."""
    total_pagado, total_interes = _calcular_totales(lista_filas)
    formato_excel = _formato_num_excel(num_decimales, simbolo_moneda)
    hoja.append([_titulo_escenario(letra, dict_params, num_decimales, simbolo_moneda)])
    hoja.cell(row=hoja.max_row, column=1).font = Font(name=FUENTE_TITULO_EXCEL, bold=True, size=11)
    hoja.append([f"Total: {_formatear_moneda_export(total_pagado, num_decimales, simbolo_moneda)} | "
                 f"Intereses: {_formatear_moneda_export(total_interes, num_decimales, simbolo_moneda)}"])
    hoja.cell(row=hoja.max_row, column=1).font = Font(name=FUENTE_TEXTO_EXCEL, size=10)
    hoja.append(ENCABEZADOS_TABLA)
    fila_cab = hoja.max_row
    fuente_cab = Font(bold=True, color=COLOR_FUENTE_CABECERA, size=10)
    relleno_cab = PatternFill("solid", fgColor=COLOR_CABECERA_EXCEL)
    for num_col in range(1, len(ENCABEZADOS_TABLA) + 1):
        celda = hoja.cell(row=fila_cab, column=num_col)
        celda.font = fuente_cab
        celda.fill = relleno_cab
        celda.alignment = Alignment(horizontal="center")
    fila_ini = hoja.max_row + 1
    for fila in lista_filas:
        hoja.append([fila["mes"], fila["cuota"], fila["interes"], fila["capital"], fila["saldo"]])
    for fila_excel in hoja.iter_rows(min_row=fila_ini, max_row=hoja.max_row, min_col=2, max_col=5):
        for celda in fila_excel:
            celda.number_format = formato_excel
    hoja.append([])
    return total_pagado, total_interes


def exportar_comparativa_excel(lista_a: list[dict], params_a: dict,
                               lista_b: list[dict], params_b: dict, ruta_archivo: str,
                               num_decimales: int = 2, simbolo_moneda: str = "$") -> str:
    """Guarda A + B + grafica con titulos Segoe UI y texto Arial."""
    if not lista_a or not lista_b:
        raise ValueError("Fija los escenarios A y B antes de exportar.")
    libro = Workbook()
    hoja = libro.active
    hoja.title = "Comparativa A-B"
    hoja.append(["Intresta - Comparativa A vs B"])
    hoja.cell(row=1, column=1).font = Font(name=FUENTE_TITULO_EXCEL, bold=True, size=14,
                                           color=COLOR_CABECERA_EXCEL)
    hoja.append(["Comparativa de dos calculos distintos (A vs B)"])
    hoja.cell(row=2, column=1).font = Font(name=FUENTE_TEXTO_EXCEL, size=10)
    total_a, interes_a = _escribir_bloque_escenario_excel(hoja, lista_a, params_a, "A", num_decimales, simbolo_moneda)
    hoja.append([_linea_indicadores(lista_a, params_a, num_decimales, simbolo_moneda)])
    hoja.cell(row=hoja.max_row, column=1).font = Font(name=FUENTE_TEXTO_EXCEL, size=9, italic=True)
    total_b, interes_b = _escribir_bloque_escenario_excel(hoja, lista_b, params_b, "B", num_decimales, simbolo_moneda)
    hoja.append([_linea_indicadores(lista_b, params_b, num_decimales, simbolo_moneda)])
    hoja.cell(row=hoja.max_row, column=1).font = Font(name=FUENTE_TEXTO_EXCEL, size=9, italic=True)
    hoja.append([f"Diferencia A-B: Total {_formatear_moneda_export(total_a - total_b, num_decimales, simbolo_moneda)} | "
                 f"Intereses {_formatear_moneda_export(interes_a - interes_b, num_decimales, simbolo_moneda)}"])
    hoja.cell(row=hoja.max_row, column=1).font = Font(name=FUENTE_TEXTO_EXCEL, bold=True, size=10)
    hoja.append([])
    anchos = [10, 16, 16, 16, 18]
    for num_col, val_ancho in enumerate(anchos, start=1):
        hoja.column_dimensions[hoja.cell(row=3, column=num_col).column_letter].width = val_ancho
    ruta_png = _guardar_grafica_comparativa_temporal(lista_a, lista_b)
    try:
        img_excel = ImagenExcel(ruta_png)
        img_excel.width = 760
        img_excel.height = 360
        hoja.add_image(img_excel, f"A{hoja.max_row + 2}")
        libro.save(ruta_archivo)
    finally:
        try:
            os.remove(ruta_png)
        except Exception:
            pass
    return os.path.abspath(ruta_archivo)


def _bloque_datos_escenario(lista_filas: list[dict], total: float, interes: float,
                            num_decimales: int = 2, simbolo_moneda: str = "$"):
    """Arma las filas de tabla para el pdf comparativo."""
    datos = [ENCABEZADOS_TABLA]
    for fila in lista_filas:
        datos.append([str(fila["mes"]),
                      _formatear_moneda_export(fila['cuota'], num_decimales, simbolo_moneda),
                      _formatear_moneda_export(fila['interes'], num_decimales, simbolo_moneda),
                      _formatear_moneda_export(fila['capital'], num_decimales, simbolo_moneda),
                      _formatear_moneda_export(fila['saldo'], num_decimales, simbolo_moneda)])
    datos.append(["", f"Total: {_formatear_moneda_export(total, num_decimales, simbolo_moneda)}",
                  f"Intereses: {_formatear_moneda_export(interes, num_decimales, simbolo_moneda)}", "", ""])
    return datos


def _estilo_tabla_pdf():
    """Retorna el estilo morado compartido de tablas en pdf."""
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#380057")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
    ])


def exportar_comparativa_pdf(lista_a: list[dict], params_a: dict,
                             lista_b: list[dict], params_b: dict, ruta_archivo: str,
                             num_decimales: int = 2, simbolo_moneda: str = "$",
                             incluir_logo: bool = True, incluir_pie: bool = True) -> str:
    """Guarda A + B + grafica con encabezado y pie morados."""
    if not lista_a or not lista_b:
        raise ValueError("Fija los escenarios A y B antes de exportar.")
    total_a, interes_a = _calcular_totales(lista_a)
    total_b, interes_b = _calcular_totales(lista_b)
    titulo_doc = "Comparativa A vs B"
    doc = SimpleDocTemplate(ruta_archivo, pagesize=A4, topMargin=85, bottomMargin=45)
    estilos = _estilos_pdf()
    partes = [
        Paragraph(_titulo_escenario("A", params_a, num_decimales, simbolo_moneda), estilos["Normal"]),
        Paragraph(f"Total: {_formatear_moneda_export(total_a, num_decimales, simbolo_moneda)} | "
                  f"Intereses: {_formatear_moneda_export(interes_a, num_decimales, simbolo_moneda)}", estilos["Normal"]),
        Paragraph(_linea_indicadores(lista_a, params_a, num_decimales, simbolo_moneda), estilos["Normal"]),
        Spacer(1, 8),
        Table(_bloque_datos_escenario(lista_a, total_a, interes_a, num_decimales, simbolo_moneda), repeatRows=1, style=_estilo_tabla_pdf()),
        Spacer(1, 12),
        Paragraph(_titulo_escenario("B", params_b, num_decimales, simbolo_moneda), estilos["Normal"]),
        Paragraph(f"Total: {_formatear_moneda_export(total_b, num_decimales, simbolo_moneda)} | "
                  f"Intereses: {_formatear_moneda_export(interes_b, num_decimales, simbolo_moneda)}", estilos["Normal"]),
        Paragraph(_linea_indicadores(lista_b, params_b, num_decimales, simbolo_moneda), estilos["Normal"]),
        Spacer(1, 8),
        Table(_bloque_datos_escenario(lista_b, total_b, interes_b, num_decimales, simbolo_moneda), repeatRows=1, style=_estilo_tabla_pdf()),
        Spacer(1, 8),
        Paragraph(f"Diferencia A-B: Total {_formatear_moneda_export(total_a - total_b, num_decimales, simbolo_moneda)} | "
                  f"Intereses {_formatear_moneda_export(interes_a - interes_b, num_decimales, simbolo_moneda)}", estilos["Normal"]),
        Spacer(1, 12),
        Paragraph("Grafica comparativa A vs B", estilos["Heading2"]),
    ]
    ruta_png = _guardar_grafica_comparativa_temporal(lista_a, lista_b)
    decorar = _fabrica_decoracion_pdf(titulo_doc, incluir_logo, incluir_pie)
    try:
        partes.append(ImagenPDF(ruta_png, width=460, height=220))
        doc.build(partes, onFirstPage=decorar, onLaterPages=decorar)
    finally:
        try:
            os.remove(ruta_png)
        except Exception:
            pass
    return os.path.abspath(ruta_archivo)
