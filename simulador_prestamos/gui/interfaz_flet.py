# ==========================================
# Encabezados y Librerias
# ==========================================
import os
import json
import io
import base64
import subprocess
from datetime import datetime
import flet as ft
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter, MaxNLocator

try:
    from gui.configuracion import (
        cargar_configuracion,
        guardar_configuracion,
        formatear_moneda,
        OPCIONES_DECIMALES,
        OPCIONES_MONEDA,
        FUENTES_DISPONIBLES,
        ESQUEMAS_GRAFICAS,
        FUENTES_PDF,
        COLORES_DISPONIBLES,
        COLORES_GRAFICAS_DEFECTO,
        obtener_color_esquema,
        obtener_color_nombre,
    )
    from gui.indicadores import calcular_indicadores
    from gui.planes import (
        cargar_planes,
        guardar_planes,
        calcular_credito,
        calcular_resumen_plan,
        calcular_evolucion_plan,
        calcular_flujo_plan,
        calcular_resumen_anual,
        sumar_grupo_movimientos,
        valor_fijo_en_mes,
        crear_plan,
        nivel_endeudamiento,
        convertir_a_numero,
        MAX_PLANES,
    )
    from gui.exportar import (
        exportar_tabla_excel,
        exportar_tabla_pdf,
        exportar_comparativa_excel,
        exportar_comparativa_pdf,
        establecer_fuentes_pdf,
    )
    from gui.graficas import (
        generar_figura_comparativa_escenarios,
        establecer_modo_graficas,
        establecer_esquema_graficas,
        establecer_colores_personalizados,
    )
    from gui.ia import (
        explicar_tabla_amortizacion,
        comparar_sistemas,
        simular_escenario_personalizado,
        consultar_plan_ia,
        resumir_chat_ia,
    )
except ImportError:
    from simulador_prestamos.gui.configuracion import (
        cargar_configuracion,
        guardar_configuracion,
        formatear_moneda,
        OPCIONES_DECIMALES,
        OPCIONES_MONEDA,
        FUENTES_DISPONIBLES,
        ESQUEMAS_GRAFICAS,
        FUENTES_PDF,
        COLORES_DISPONIBLES,
        COLORES_GRAFICAS_DEFECTO,
        obtener_color_esquema,
        obtener_color_nombre,
    )
    from simulador_prestamos.gui.indicadores import calcular_indicadores
    from simulador_prestamos.gui.planes import (
        cargar_planes,
        guardar_planes,
        calcular_credito,
        calcular_resumen_plan,
        calcular_evolucion_plan,
        calcular_flujo_plan,
        calcular_resumen_anual,
        sumar_grupo_movimientos,
        valor_fijo_en_mes,
        crear_plan,
        nivel_endeudamiento,
        convertir_a_numero,
        MAX_PLANES,
    )
    from simulador_prestamos.gui.exportar import (
        exportar_tabla_excel,
        exportar_tabla_pdf,
        exportar_comparativa_excel,
        exportar_comparativa_pdf,
        establecer_fuentes_pdf,
    )
    from simulador_prestamos.gui.graficas import (
        generar_figura_comparativa_escenarios,
        establecer_modo_graficas,
        establecer_esquema_graficas,
        establecer_colores_personalizados,
    )
    from simulador_prestamos.gui.ia import (
        explicar_tabla_amortizacion,
        comparar_sistemas,
        simular_escenario_personalizado,
        consultar_plan_ia,
        resumir_chat_ia,
    )

# ==========================================
# Declaracion de Constantes
# ==========================================
TITULO_APP = "Intresta - Simulador de Amortizaciones"
FUENTE_APP = "Segoe UI"
OPCIONES_SISTEMAS = ["Frances", "Aleman", "Americano"]
NOMBRE_ARCHIVO_HISTORIAL = "historial.json"
MAX_REGISTROS_HISTORIAL = 100

DIRECTORIO_RECURSOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Img")
ARCHIVO_LOGO = "intresta-logo-horizontal.png"
ARCHIVO_ICONO = "intresta-icon.ico"

# Paletas tomadas de ventana.py (Tkinter) para conservar la identidad visual.
PALETA_OSCURA = {
    "fondo": "#1E1E2E",
    "primario": "#C9A8FF",
    "secundario": "#E5DE4B",
    "tarjeta": "#2B2B40",
    "texto_claro": "#EAEAF0",
    "texto_suave": "#A7A7C0",
    "campo": "#34344E",
    "seleccion": "#4A4A6A",
    "borde": "#3D3D5C",
    "rojo": "#EF5350",
    "verde": "#66BB6A",
}

PALETA_CLARA = {
    "fondo": "#4A1A6B",
    "primario": "#380057",
    "secundario": "#CFCC27",
    "tarjeta": "#DAD5E3",
    "texto_claro": "#212121",
    "texto_suave": "#546E7A",
    "campo": "#FFFFFF",
    "seleccion": "#C4B0E0",
    "borde": "#A9A9B8",
    "rojo": "#C62828",
    "verde": "#2E7D32",
}

# Paletas de graficas tomadas de graficas.py.
PALETA_GRAFICA_OSCURA = {
    "fondo": "#2B2B40",
    "rejilla": "#44475A",
    "texto": "#EAEAF0",
    "suave": "#A7A7C0",
    "borde": "#1E1E2E",
    "frances": "#64B5F6",
    "aleman": "#66BB6A",
    "americano": "#EF5350",
    "capital": "#66BB6A",
    "interes": "#EF5350",
    "esc_a": "#64B5F6",
    "esc_b": "#FFB74D",
    "ingresos": "#66BB6A",
    "egresos": "#EF5350",
    "creditos": "#E5DE4B",
    "saldo": "#64B5F6",
}

PALETA_GRAFICA_CLARA = {
    "fondo": "#F8F9FA",
    "rejilla": "#E0E0E0",
    "texto": "#212121",
    "suave": "#777777",
    "borde": "white",
    "frances": "#1976D2",
    "aleman": "#2E7D32",
    "americano": "#D32F2F",
    "capital": "#2E7D32",
    "interes": "#C62828",
    "esc_a": "#1976D2",
    "esc_b": "#EF6C00",
    "ingresos": "#2E7D32",
    "egresos": "#C62828",
    "creditos": "#C9A800",
    "saldo": "#1976D2",
}

PALETA_GRAFICA_OSCURA_BASE = dict(PALETA_GRAFICA_OSCURA)
PALETA_GRAFICA_CLARA_BASE = dict(PALETA_GRAFICA_CLARA)


def aplicar_esquema_graficas_interfaz(dict_config: dict):
    """Aplica a las paletas de la interfaz los colores elegidos para cada serie."""
    for paleta in (PALETA_GRAFICA_OSCURA, PALETA_GRAFICA_CLARA):
        paleta["ingresos"] = obtener_color_nombre(dict_config.get("color_ingresos", "Verde"))
        paleta["egresos"] = obtener_color_nombre(dict_config.get("color_egresos", "Rojo"))
        paleta["creditos"] = obtener_color_nombre(dict_config.get("color_creditos", "Amarillo"))
        paleta["saldo"] = obtener_color_nombre(dict_config.get("color_saldo", "Azul"))
        paleta["interes"] = obtener_color_nombre(dict_config.get("color_intereses", "Rojo"))
        paleta["capital"] = obtener_color_nombre(dict_config.get("color_capital", "Verde"))
        paleta["frances"] = paleta["saldo"]
        paleta["esc_a"] = paleta["saldo"]
        paleta["aleman"] = paleta["capital"]
        paleta["americano"] = paleta["interes"]
        paleta["esc_b"] = paleta["creditos"]


TEXTO_BIENVENIDA = (
    "**Hola, soy tu asesor financiero Intresta.**\n\n"
    "Calcula un préstamo y puedo explicarte la tabla, comparar los tres sistemas "
    "de amortización o responder dudas sobre los archivos PDF y Excel exportados."
)


# ==========================================
# Declaracion de Funciones de Apoyo
# ==========================================

def obtener_paleta(modo_tema: str) -> dict:
    """Retorna la paleta de interfaz para el modo 'claro' u 'oscuro'."""
    if modo_tema == "claro":
        return dict(PALETA_CLARA)
    return dict(PALETA_OSCURA)


def obtener_paleta_grafica(modo_tema: str) -> dict:
    """Retorna la paleta de graficas para el modo 'claro' u 'oscuro'."""
    if modo_tema == "claro":
        return dict(PALETA_GRAFICA_CLARA)
    return dict(PALETA_GRAFICA_OSCURA)


def cargar_imagen_base64(nombre_archivo: str) -> str:
    """Lee una imagen de la carpeta Img y la devuelve como data URI Base64."""
    ruta_imagen = os.path.join(DIRECTORIO_RECURSOS, nombre_archivo)
    if not os.path.exists(ruta_imagen):
        return ""
    with open(ruta_imagen, "rb") as archivo_imagen:
        contenido = base64.b64encode(archivo_imagen.read()).decode("ascii")
    return f"data:image/png;base64,{contenido}"


def _ruta_archivo_historial() -> str:
    """Retorna la ruta absoluta del archivo historial.json."""
    dir_actual = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(dir_actual, "..", NOMBRE_ARCHIVO_HISTORIAL))


def formatear_eje_corto(val_numero: float, _posicion=None) -> str:
    """Compacta las cifras del eje Y para que no se encimen en la grafica."""
    valor_abs = abs(val_numero)
    if valor_abs >= 1_000_000:
        return f"${val_numero / 1_000_000:.1f}M"
    if valor_abs >= 1_000:
        return f"${val_numero / 1_000:.0f}k"
    return f"${val_numero:.0f}"


def formatear_eje_plan(val_numero: float, _posicion=None) -> str:
    """Formatea el eje de las graficas del plan sin repetir etiquetas cercanas."""
    valor_abs = abs(val_numero)
    if valor_abs >= 1_000_000:
        return f"${val_numero / 1_000_000:.1f}M"
    if valor_abs >= 10_000:
        return f"${val_numero / 1_000:.0f}k"
    return f"${val_numero:,.0f}"


def formatear_abonos_cli(lista_abonos: list[dict]) -> str:
    """Convierte la lista de abonos a formato CLI 'mes:monto,mes:monto'."""
    partes = []
    for abono in lista_abonos:
        partes.append(f"{int(abono['mes'])}:{float(abono['monto'])}")
    return ",".join(partes)


def ejecutar_calculo_cpp(str_sistema: str, val_monto: float, val_tasa_anual: float,
                         num_meses: int, lista_abonos: list[dict] | None = None) -> list[dict]:
    """
    Invoca al binario compilado de C++ (amortizador.exe) mediante subprocess
    y retorna la tabla de amortizacion en formato de lista de diccionarios.
    """
    dir_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_ejecutable = os.path.join(dir_actual, "..", "core_cpp", "amortizador.exe")

    if not os.path.exists(ruta_ejecutable):
        ruta_ejecutable = os.path.join(os.getcwd(), "simulador_prestamos", "core_cpp", "amortizador.exe")
        if not os.path.exists(ruta_ejecutable):
            raise FileNotFoundError(
                f"No se encontro el binario de calculo en: {ruta_ejecutable}. "
                "Compila core_cpp/amortizador.exe antes de ejecutar la aplicacion."
            )

    cmd_comando = [
        ruta_ejecutable,
        str_sistema.lower(),
        str(val_monto),
        str(val_tasa_anual),
        str(num_meses)
    ]
    if lista_abonos:
        cmd_comando.append(formatear_abonos_cli(lista_abonos))

    obj_proceso = subprocess.run(
        cmd_comando,
        capture_output=True,
        text=True,
        check=True
    )

    datos_json = json.loads(obj_proceso.stdout)
    if isinstance(datos_json, dict) and "error" in datos_json:
        raise ValueError(datos_json["error"])

    return datos_json


def generar_grafica_amortizacion(lista_filas: list[dict], modo_oscuro: bool = True) -> str:
    """
    Genera una grafica moderna con Matplotlib que compara interes y capital
    mes a mes, y devuelve la imagen como data URI Base64 lista para Flet.
    """
    if not lista_filas:
        return ""

    paleta = dict(PALETA_GRAFICA_OSCURA) if modo_oscuro else dict(PALETA_GRAFICA_CLARA)
    meses = [fila["mes"] for fila in lista_filas]
    intereses = [fila["interes"] for fila in lista_filas]
    capitales = [fila["capital"] for fila in lista_filas]
    saldos = [fila["saldo"] for fila in lista_filas]

    figura = Figure(figsize=(9.2, 4.4), facecolor=paleta["fondo"])
    eje_barras, eje_saldo = figura.subplots(1, 2)

    for eje in (eje_barras, eje_saldo):
        eje.set_facecolor(paleta["fondo"])
        eje.set_axisbelow(True)
        eje.grid(axis="y", color=paleta["rejilla"], alpha=0.45, linewidth=0.8)
        eje.tick_params(colors=paleta["suave"], labelsize=8, length=0)
        for lado in ("top", "right"):
            eje.spines[lado].set_visible(False)
        for lado in ("left", "bottom"):
            eje.spines[lado].set_color(paleta["rejilla"])
        eje.xaxis.set_major_locator(MaxNLocator(nbins=8, integer=True))
        eje.yaxis.set_major_formatter(FuncFormatter(formatear_eje_plan))

    # Barras apiladas: capital + interes de cada cuota.
    eje_barras.bar(
        meses, capitales, label="Capital", color=paleta["capital"],
        width=0.62, edgecolor=paleta["borde"], linewidth=0.5
    )
    eje_barras.bar(
        meses, intereses, bottom=capitales, label="Interés", color=paleta["interes"],
        width=0.62, edgecolor=paleta["borde"], linewidth=0.5
    )
    eje_barras.set_title(
        "Composición de la cuota", color=paleta["texto"], fontsize=11,
        fontweight="bold", pad=12
    )
    eje_barras.set_xlabel("Mes", color=paleta["suave"], fontsize=9, labelpad=8)
    eje_barras.set_ylabel("Monto", color=paleta["suave"], fontsize=9, labelpad=8)

    leyenda_barras = eje_barras.legend(loc="upper right", frameon=False, fontsize=8)
    for texto_leyenda in leyenda_barras.get_texts():
        texto_leyenda.set_color(paleta["texto"])

    # Evolucion del saldo con area tenue para resaltar la tendencia.
    eje_saldo.plot(
        meses, saldos, label="Saldo restante", color=paleta["frances"],
        linewidth=2.6, marker="o", markersize=3.5,
        markerfacecolor=paleta["fondo"], markeredgewidth=1.2
    )
    eje_saldo.fill_between(meses, saldos, color=paleta["frances"], alpha=0.12)
    eje_saldo.set_title(
        "Amortización del saldo", color=paleta["texto"], fontsize=11,
        fontweight="bold", pad=12
    )
    eje_saldo.set_xlabel("Mes", color=paleta["suave"], fontsize=9, labelpad=8)
    eje_saldo.set_ylabel("Saldo", color=paleta["suave"], fontsize=9, labelpad=8)

    leyenda_saldo = eje_saldo.legend(loc="upper right", frameon=False, fontsize=8)
    for texto_leyenda in leyenda_saldo.get_texts():
        texto_leyenda.set_color(paleta["texto"])

    figura.tight_layout(pad=1.8)

    buffer = io.BytesIO()
    figura.savefig(buffer, format="png", bbox_inches="tight", dpi=110, facecolor=paleta["fondo"])
    datos_png = base64.b64encode(buffer.getvalue()).decode("ascii")
    buffer.close()
    return f"data:image/png;base64,{datos_png}"


def generar_grafica_comparativa_base64(
    lista_a: list[dict], lista_b: list[dict],
    titulo_a: str = "A", titulo_b: str = "B",
    modo_oscuro: bool = True, dict_colores: dict | None = None
) -> str:
    """
    Construye la grafica comparativa de escenarios A y B usando matplotlib
    y la devuelve como data URI Base64 para Flet.
    """
    establecer_modo_graficas("oscuro" if modo_oscuro else "claro")
    if dict_colores:
        establecer_colores_personalizados(dict_colores, "oscuro" if modo_oscuro else "claro")
    figura = generar_figura_comparativa_escenarios(lista_a, lista_b, titulo_a, titulo_b)
    paleta = dict(PALETA_GRAFICA_OSCURA) if modo_oscuro else dict(PALETA_GRAFICA_CLARA)
    figura.patch.set_facecolor(paleta["fondo"])
    for ax in figura.axes:
        ax.set_facecolor(paleta["fondo"])

    buffer = io.BytesIO()
    figura.savefig(buffer, format="png", bbox_inches="tight", dpi=110, facecolor=paleta["fondo"])
    datos_png = base64.b64encode(buffer.getvalue()).decode("ascii")
    buffer.close()
    return f"data:image/png;base64,{datos_png}"


def generar_grafica_planes_base64(dict_resumen: dict, modo_oscuro: bool = True) -> str:
    """
    Genera la grafica de flujo mensual del plan financiero y la devuelve
    como data URI Base64 para Flet.
    """
    val_ingresos = float(dict_resumen.get("total_ingresos", 0))
    val_egresos = float(dict_resumen.get("total_gastos", 0))
    val_creditos = float(dict_resumen.get("total_cuotas", 0))
    val_saldo = float(dict_resumen.get("balance_mensual", 0))
    if val_ingresos == 0 and val_egresos == 0 and val_creditos == 0:
        return ""

    paleta = dict(PALETA_GRAFICA_OSCURA) if modo_oscuro else dict(PALETA_GRAFICA_CLARA)
    etiquetas = ["Ingresos", "Egresos", "Créditos", "Saldo neto"]
    valores = [val_ingresos, val_egresos, val_creditos, val_saldo]
    colores = [paleta["ingresos"], paleta["egresos"], paleta["creditos"], paleta["saldo"]]

    figura = Figure(figsize=(8.8, 3.9), facecolor=paleta["fondo"])
    eje = figura.subplots()
    eje.set_facecolor(paleta["fondo"])
    eje.set_axisbelow(True)
    eje.grid(axis="y", color=paleta["rejilla"], alpha=0.45, linewidth=0.8)
    eje.tick_params(colors=paleta["suave"], labelsize=9, length=0)
    for lado in ("top", "right"):
        eje.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        eje.spines[lado].set_color(paleta["rejilla"])
    eje.yaxis.set_major_formatter(FuncFormatter(formatear_eje_corto))

    barras = eje.bar(
        etiquetas, valores, color=colores, width=0.56,
        edgecolor=paleta["borde"], linewidth=0.6,
    )
    for barra, valor in zip(barras, valores):
        eje.annotate(
            formatear_eje_corto(valor),
            (barra.get_x() + barra.get_width() / 2, valor),
            ha="center", va="bottom" if valor >= 0 else "top",
            xytext=(0, 5 if valor >= 0 else -5), textcoords="offset points",
            color=paleta["texto"], fontsize=9, fontweight="bold",
        )

    eje.axhline(0, color=paleta["suave"], linewidth=0.9, alpha=0.75)
    eje.set_title(
        "Flujo mensual del plan", color=paleta["texto"], fontsize=12,
        fontweight="bold", pad=12,
    )
    eje.set_ylabel("Monto", color=paleta["suave"], fontsize=9, labelpad=8)

    if val_ingresos > 0:
        val_ratio = float(dict_resumen.get("ratio_endeudamiento", 0))
        eje.text(
            0.99, 0.96, f"Endeudamiento: {val_ratio:.1f}% del ingreso",
            transform=eje.transAxes, ha="right", va="top",
            color=paleta["texto"], fontsize=9, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.35", facecolor=paleta["fondo"],
                      edgecolor=paleta["rejilla"], alpha=0.9),
        )

    figura.tight_layout(pad=1.6)
    buffer = io.BytesIO()
    figura.savefig(buffer, format="png", bbox_inches="tight", dpi=110, facecolor=paleta["fondo"])
    datos_png = base64.b64encode(buffer.getvalue()).decode("ascii")
    buffer.close()
    return f"data:image/png;base64,{datos_png}"


def generar_grafica_evolucion_plan_base64(lista_filas: list[dict], modo_oscuro: bool = True) -> str:
    """
    Genera la grafica de evolucion mensual de los creditos como dispersion de
    puntos unidos por lineas y la devuelve como data URI Base64 para Flet.
    """
    if not lista_filas:
        return ""

    paleta = dict(PALETA_GRAFICA_OSCURA) if modo_oscuro else dict(PALETA_GRAFICA_CLARA)
    meses = [int(fila["mes"]) for fila in lista_filas]
    saldos = [float(fila["saldo_total"]) for fila in lista_filas]
    pagos = [float(fila["pago_total"]) for fila in lista_filas]
    intereses = [float(fila["interes_total"]) for fila in lista_filas]
    capitales = [float(fila["capital_total"]) for fila in lista_filas]

    figura = Figure(figsize=(8.8, 4.2), facecolor=paleta["fondo"])
    eje_saldo = figura.subplots()
    eje_flujo = eje_saldo.twinx()

    for eje in (eje_saldo, eje_flujo):
        eje.set_facecolor(paleta["fondo"])
        eje.set_axisbelow(True)
        eje.tick_params(colors=paleta["suave"], labelsize=8, length=0)
        for lado in ("top",):
            eje.spines[lado].set_visible(False)
        for lado in ("left", "bottom"):
            eje.spines[lado].set_color(paleta["rejilla"])
        eje.yaxis.set_major_formatter(FuncFormatter(formatear_eje_plan))

    eje_saldo.grid(axis="y", color=paleta["rejilla"], alpha=0.45, linewidth=0.8)
    eje_saldo.xaxis.set_major_locator(MaxNLocator(nbins=12, integer=True))

    def _dibujar_serie(eje, valores: list[float], color: str, etiqueta: str):
        """Dibuja la linea y encima los puntos de la serie mensual."""
        eje.plot(meses, valores, color=color, linewidth=1.8, label=etiqueta)
        eje.scatter(
            meses, valores, color=color, s=26, zorder=3,
            edgecolors=paleta["fondo"], linewidths=0.6,
        )

    _dibujar_serie(eje_saldo, saldos, paleta["saldo"], "Saldo pendiente")
    _dibujar_serie(eje_flujo, pagos, paleta["creditos"], "Pago mensual")
    _dibujar_serie(eje_flujo, intereses, paleta["interes"], "Intereses")
    _dibujar_serie(eje_flujo, capitales, paleta["capital"], "Capital")

    eje_saldo.set_title(
        "Evolución mensual de los créditos", color=paleta["texto"], fontsize=12,
        fontweight="bold", pad=12,
    )
    eje_saldo.set_xlabel("Mes", color=paleta["suave"], fontsize=9, labelpad=8)
    eje_saldo.set_ylabel("Saldo pendiente", color=paleta["suave"], fontsize=9, labelpad=8)
    eje_flujo.set_ylabel("Pago, interés y capital", color=paleta["suave"], fontsize=9, labelpad=8)

    lineas = eje_saldo.get_lines() + eje_flujo.get_lines()
    leyenda = eje_saldo.legend(
        lineas, [linea.get_label() for linea in lineas],
        loc="upper right", frameon=False, fontsize=8, ncol=2,
    )
    for texto_leyenda in leyenda.get_texts():
        texto_leyenda.set_color(paleta["texto"])

    figura.tight_layout(pad=1.6)
    buffer = io.BytesIO()
    figura.savefig(buffer, format="png", bbox_inches="tight", dpi=110, facecolor=paleta["fondo"])
    datos_png = base64.b64encode(buffer.getvalue()).decode("ascii")
    buffer.close()
    return f"data:image/png;base64,{datos_png}"


def generar_grafica_flujo_plan_base64(lista_filas: list[dict], modo_oscuro: bool = True) -> str:
    """
    Genera la grafica del flujo del plan mes a mes como dispersion con lineas:
    ingresos, egresos, pago del credito y saldo neto acumulado.
    """
    if not lista_filas:
        return ""

    paleta = dict(PALETA_GRAFICA_OSCURA) if modo_oscuro else dict(PALETA_GRAFICA_CLARA)
    meses = [int(fila["mes"]) for fila in lista_filas]
    ingresos = [float(fila["ingresos"]) for fila in lista_filas]
    egresos = [float(fila["egresos"]) for fila in lista_filas]
    pagos = [float(fila["pago_credito"]) for fila in lista_filas]
    saldos_netos = [float(fila["saldo_neto_acumulado"]) for fila in lista_filas]

    figura = Figure(figsize=(8.8, 4.2), facecolor=paleta["fondo"])
    eje_saldo = figura.subplots()
    eje_flujo = eje_saldo.twinx()

    for eje in (eje_saldo, eje_flujo):
        eje.set_facecolor(paleta["fondo"])
        eje.set_axisbelow(True)
        eje.tick_params(colors=paleta["suave"], labelsize=8, length=0)
        eje.spines["top"].set_visible(False)
        for lado in ("left", "bottom"):
            eje.spines[lado].set_color(paleta["rejilla"])
        eje.yaxis.set_major_formatter(FuncFormatter(formatear_eje_plan))

    eje_saldo.grid(axis="y", color=paleta["rejilla"], alpha=0.45, linewidth=0.8)
    eje_saldo.xaxis.set_major_locator(MaxNLocator(nbins=12, integer=True))

    def _dibujar_serie(eje, valores: list[float], color: str, etiqueta: str):
        """Dibuja la linea y encima los puntos de la serie mensual."""
        eje.plot(meses, valores, color=color, linewidth=1.8, label=etiqueta)
        eje.scatter(
            meses, valores, color=color, s=24, zorder=3,
            edgecolors=paleta["fondo"], linewidths=0.6,
        )

    _dibujar_serie(eje_saldo, saldos_netos, paleta["saldo"], "Saldo neto acumulado")
    _dibujar_serie(eje_flujo, ingresos, paleta["ingresos"], "Ingresos")
    _dibujar_serie(eje_flujo, egresos, paleta["egresos"], "Egresos")
    _dibujar_serie(eje_flujo, pagos, paleta["creditos"], "Pago del crédito")

    eje_saldo.set_title(
        "Flujo del plan mes a mes", color=paleta["texto"], fontsize=12,
        fontweight="bold", pad=12,
    )
    eje_saldo.set_xlabel("Mes", color=paleta["suave"], fontsize=9, labelpad=8)
    eje_saldo.set_ylabel("Saldo neto acumulado", color=paleta["suave"], fontsize=9, labelpad=8)
    eje_flujo.set_ylabel("Ingresos, egresos y pago", color=paleta["suave"], fontsize=9, labelpad=8)

    lineas = eje_saldo.get_lines() + eje_flujo.get_lines()
    leyenda = eje_saldo.legend(
        lineas, [linea.get_label() for linea in lineas],
        loc="upper left", frameon=False, fontsize=8, ncol=2,
    )
    for texto_leyenda in leyenda.get_texts():
        texto_leyenda.set_color(paleta["texto"])

    figura.tight_layout(pad=1.6)
    buffer = io.BytesIO()
    figura.savefig(buffer, format="png", bbox_inches="tight", dpi=110, facecolor=paleta["fondo"])
    datos_png = base64.b64encode(buffer.getvalue()).decode("ascii")
    buffer.close()
    return f"data:image/png;base64,{datos_png}"


# ==========================================
# Controlador de la Interfaz Flet
# ==========================================

class InterfazFletSimulador:
    """
    Controlador de la interfaz grafica basada en Flet para el Simulador
    de Prestamos e integracion con el motor C++.
    """

    def __init__(self, obj_pagina: ft.Page):
        global FUENTE_APP
        self.pagina = obj_pagina
        self.dict_config = cargar_configuracion()
        FUENTE_APP = self.dict_config.get("fuente_app", "Segoe UI")
        aplicar_esquema_graficas_interfaz(self.dict_config)
        self.modo_tema = str(self.dict_config.get("tema", "oscuro")).lower()
        establecer_colores_personalizados(self.dict_config, self.modo_tema)
        self.paleta = obtener_paleta(self.modo_tema)
        self.tabla_actual: list[dict] = []
        self.parametros_actuales: dict = {}
        self.mensajes_chat: list[dict] = []
        self.mensajes_chat_plan: list[dict] = []
        self.ultimo_resumen_chat: str = ""
        self.ia_ocupada: bool = False
        self.selector_carpeta = ft.FilePicker()
        self.pagina.services.append(self.selector_carpeta)
        self.indice_pestana = 0
        self.src_logo = cargar_imagen_base64(ARCHIVO_LOGO)
        self.lista_tabla_a: list[dict] = []
        self.dict_params_a: dict = {}
        self.lista_tabla_b: list[dict] = []
        self.dict_params_b: dict = {}
        self.subvista_comparar_activa: str = "tablas"
        self.lista_abonos: list[dict] = []
        # Estado de la barra de navegación vertical
        self.nav_expandida: bool = True
        self.vista_activa: str = "inicio"
        self.lista_historial: list[dict] = []
        # Estado de los planes financieros
        self.lista_planes: list[dict] = []
        self.plan_ingresos: list[dict] = []
        self.plan_gastos: list[dict] = []
        self.plan_creditos: list[dict] = []
        self.borrador_plan: dict = {}
        self.plan_activo: dict | None = None
        self.planes_consultados: list[dict] = []
        self.indice_plan_activo: int = -1
        self.plan_es_borrador: bool = False
        self.duracion_plan: int = 12
        self.mostrar_editor_plan: bool = False
        self.dic_campos_movimientos: dict = {}
        self.dic_dialogo_movimiento: dict = {}
        self.indice_pestana_plan: int = 0
        self.reconstruyendo_plan: bool = False

        self._configurar_ventana()
        self._inicializar_controles()
        self._cargar_historial()
        self._cargar_planes()
        self._construir_interfaz()
        self._renderizar_chat()
        self.pagina.update()

    # ==========================================
    # Configuracion y Estilos
    # ==========================================

    def _configurar_ventana(self):
        """Configura los parametros visuales y el tema de la ventana."""
        self.pagina.title = TITULO_APP
        self.pagina.padding = 18
        self.pagina.spacing = 14
        self.pagina.bgcolor = self.paleta["fondo"]
        self.pagina.theme_mode = ft.ThemeMode.DARK if self.modo_tema == "oscuro" else ft.ThemeMode.LIGHT
        self.pagina.theme = self._crear_tema(PALETA_CLARA)
        self.pagina.dark_theme = self._crear_tema(PALETA_OSCURA)
        if hasattr(self.pagina, "window"):
            self.pagina.window.width = 1240
            self.pagina.window.height = 820
            self.pagina.window.min_width = 980
            self.pagina.window.min_height = 680
            ruta_icono = os.path.join(DIRECTORIO_RECURSOS, ARCHIVO_ICONO)
            if os.path.exists(ruta_icono):
                try:
                    self.pagina.window.icon = ruta_icono
                except Exception:
                    pass

    def _crear_tema(self, paleta: dict) -> ft.Theme:
        """Construye un tema de Flet con los colores institucionales."""
        color_contraste = "#FFFFFF" if paleta["primario"] == PALETA_CLARA["primario"] else paleta["fondo"]
        return ft.Theme(
            font_family=FUENTE_APP,
            use_material3=True,
            scaffold_bgcolor=paleta["fondo"],
            color_scheme=ft.ColorScheme(
                primary=paleta["primario"],
                on_primary=color_contraste,
                secondary=paleta["secundario"],
                on_secondary=paleta["fondo"],
                surface=paleta["fondo"],
                on_surface=paleta["texto_claro"],
                surface_container=paleta["tarjeta"],
                surface_container_high=paleta["seleccion"],
                surface_container_highest=paleta["seleccion"],
                on_surface_variant=paleta["texto_suave"],
                outline=paleta["borde"],
                outline_variant=paleta["borde"],
                error=paleta["rojo"],
                on_error="#FFFFFF",
            ),
        )

    def _color_contraste(self) -> str:
        """Color legible para textos e iconos sobre el color primario."""
        return "#FFFFFF" if self.modo_tema == "claro" else self.paleta["fondo"]

    def _color_texto_sobre_fondo(self) -> str:
        """Color para textos que se dibujan directamente sobre el fondo."""
        if self.modo_tema == "claro":
            return "#E8E0F5"
        return self.paleta["texto_claro"]

    def _color_cuota(self) -> str:
        """Color del KPI de cuota segun el contraste de la paleta."""
        if self.modo_tema == "claro":
            return self.paleta["primario"]
        return self.paleta["secundario"]

    def _color_encabezado_tabla(self) -> str:
        """Color de los titulos de columna de la tabla."""
        if self.modo_tema == "claro":
            return self.paleta["texto_claro"]
        return self.paleta["secundario"]

    def _estilo_etiqueta(self) -> ft.TextStyle:
        """Estilo uniforme para las etiquetas de los campos."""
        return ft.TextStyle(color=self.paleta["texto_suave"], size=12, font_family=FUENTE_APP)

    def _estilo_texto(self) -> ft.TextStyle:
        """Estilo uniforme para el contenido de los campos."""
        return ft.TextStyle(color=self.paleta["texto_claro"], size=14, font_family=FUENTE_APP)

    def _estilo_markdown(self) -> ft.MarkdownStyleSheet:
        """Estilo de las respuestas del asesor IA."""
        return ft.MarkdownStyleSheet(
            p_text_style=ft.TextStyle(color=self.paleta["texto_claro"], size=13, font_family=FUENTE_APP),
            strong_text_style=ft.TextStyle(
                color=self.paleta["secundario"], weight=ft.FontWeight.BOLD, font_family=FUENTE_APP
            ),
            em_text_style=ft.TextStyle(color=self.paleta["texto_suave"], font_family=FUENTE_APP),
            code_text_style=ft.TextStyle(
                color=self.paleta["primario"],
                bgcolor=ft.Colors.with_opacity(0.12, self.paleta["primario"]),
                size=12,
                font_family="Consolas",
            ),
            h1_text_style=ft.TextStyle(
                color=self.paleta["primario"], size=18, weight=ft.FontWeight.BOLD, font_family=FUENTE_APP
            ),
            h2_text_style=ft.TextStyle(
                color=self.paleta["primario"], size=16, weight=ft.FontWeight.BOLD, font_family=FUENTE_APP
            ),
            h3_text_style=ft.TextStyle(
                color=self.paleta["primario"], size=14, weight=ft.FontWeight.BOLD, font_family=FUENTE_APP
            ),
        )

    def _formatear_valor(self, val_numero: float) -> str:
        """Aplica el formato monetario definido en la configuracion."""
        return formatear_moneda(
            val_numero,
            self.dict_config.get("num_decimales", 2),
            self.dict_config.get("simbolo_moneda", "$")
        )

    def _crear_campo(self, etiqueta: str, valor: str, prefijo=None, sufijo=None,
                     tipo_teclado=ft.KeyboardType.TEXT) -> ft.TextField:
        """Crea un campo de texto con el estilo del tema activo."""
        return ft.TextField(
            label=etiqueta,
            value=valor,
            prefix=prefijo,
            suffix=sufijo,
            keyboard_type=tipo_teclado,
            border_radius=10,
            filled=True,
            fill_color=self.paleta["campo"],
            border_color=self.paleta["borde"],
            focused_border_color=self.paleta["primario"],
            cursor_color=self.paleta["primario"],
            label_style=self._estilo_etiqueta(),
            text_style=self._estilo_texto(),
            content_padding=ft.Padding.symmetric(horizontal=14, vertical=14),
        )

    def _crear_boton_primario(self, str_texto: str, icono: str, manejador) -> ft.FilledButton:
        """Crea el boton de accion principal."""
        color_contraste = self._color_contraste()
        return ft.FilledButton(
            content=ft.Text(str_texto, weight=ft.FontWeight.BOLD, color=color_contraste, font_family=FUENTE_APP),
            icon=icono,
            on_click=manejador,
            height=46,
            style=ft.ButtonStyle(
                bgcolor=self.paleta["primario"],
                color=color_contraste,
                icon_color=color_contraste,
                elevation=0,
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
        )

    def _crear_boton_secundario(self, str_texto: str, icono: str, manejador) -> ft.OutlinedButton:
        """Crea un boton de accion secundaria."""
        return ft.OutlinedButton(
            content=ft.Text(str_texto, color=self.paleta["texto_claro"], font_family=FUENTE_APP),
            icon=icono,
            on_click=manejador,
            style=ft.ButtonStyle(
                color=self.paleta["texto_claro"],
                icon_color=self.paleta["primario"],
                side=ft.BorderSide(1, self.paleta["borde"]),
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
        )

    def _crear_boton_exportacion(self, str_texto: str, icono: str, manejador,
                                 color_icono: str) -> ft.OutlinedButton:
        """Crea un boton compacto para exportar o guardar resultados."""
        return ft.OutlinedButton(
            content=ft.Text(str_texto, size=12, color=self.paleta["texto_claro"], font_family=FUENTE_APP),
            icon=icono,
            on_click=manejador,
            style=ft.ButtonStyle(
                color=self.paleta["texto_claro"],
                icon_color=color_icono,
                side=ft.BorderSide(1, self.paleta["borde"]),
                shape=ft.RoundedRectangleBorder(radius=9),
                padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            ),
        )

    # ==========================================
    # Gestion de Historial
    # ==========================================

    def _cargar_historial(self):
        """Lee historial.json y llena self.lista_historial manejando ambos formatos."""
        ruta = _ruta_archivo_historial()
        if not os.path.exists(ruta):
            self.lista_historial = []
            return
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
            self.lista_historial = datos if isinstance(datos, list) else []
        except Exception:
            self.lista_historial = []

    def _guardar_historial_a_disco(self):
        """Escribe self.lista_historial en historial.json."""
        ruta = _ruta_archivo_historial()
        try:
            with open(ruta, "w", encoding="utf-8") as archivo:
                json.dump(self.lista_historial, archivo, indent=2, ensure_ascii=False)
        except Exception as error:
            self._mostrar_mensaje(f"Error al guardar historial: {error}", es_error=True)

    def _cargar_planes(self):
        """Lee planes.json al iniciar la aplicacion."""
        self.lista_planes = cargar_planes()

    def _guardar_planes_a_disco(self):
        """Escribe self.lista_planes en planes.json."""
        try:
            guardar_planes(self.lista_planes)
        except Exception as error:
            self._mostrar_mensaje(f"Error al guardar planes: {error}", es_error=True)

    def _extraer_params_historial(self, registro: dict) -> dict | None:
        """Extrae el dict de parámetros de un registro del historial (formato nuevo o antiguo)."""
        if "parametros" in registro:
            return registro["parametros"]
        # Formato antiguo de Tkinter
        if "monto" in registro:
            return {
                "sistema": registro.get("sistema", "Frances"),
                "monto": float(registro.get("monto", 0)),
                "tasa_anual": float(registro.get("tasa", registro.get("tasa_anual", 0))),
                "meses": int(registro.get("meses", 12)),
                "fecha": registro.get("fecha", ""),
                "abonos": registro.get("abonos", []),
            }
        return None

    def _evento_cargar_desde_historial(self, dict_registro: dict):
        """Carga un registro del historial, recalcula con C++ y navega a inicio."""
        params = self._extraer_params_historial(dict_registro)
        if params is None:
            self._mostrar_mensaje("Registro del historial no válido.", es_error=True)
            return
        try:
            abonos = params.get("abonos", [])
            tabla = ejecutar_calculo_cpp(
                params["sistema"], float(params["monto"]),
                float(params["tasa_anual"]), int(params["meses"]),
                abonos if abonos else None,
            )
            self.tabla_actual = tabla
            self.parametros_actuales = dict(params)
            self.lista_abonos = list(abonos) if abonos else []
            self.vista_activa = "tablas"
            valores_form = {
                "sistema": params["sistema"],
                "monto": str(params["monto"]),
                "tasa": str(params["tasa_anual"]),
                "plazo": str(params["meses"]),
                "abonos": list(abonos),
            }
            self._inicializar_controles(valores_form)
            self._construir_interfaz()
            self._renderizar_chat()
            self._actualizar_resultados()
            self.pagina.update()
            self._mostrar_mensaje("Simulación cargada desde el historial.")
        except Exception as error:
            self._mostrar_mensaje(f"Error al cargar historial: {error}", es_error=True)

    def _evento_borrar_registro_historial(self, num_indice: int):
        """Elimina un registro del historial por índice y actualiza la vista."""
        if 0 <= num_indice < len(self.lista_historial):
            self.lista_historial.pop(num_indice)
            self._guardar_historial_a_disco()
            self._construir_interfaz()
            self.pagina.update()

    def _evento_limpiar_historial(self, _):
        """Vacía todo el historial."""
        self.lista_historial = []
        self._guardar_historial_a_disco()
        self._construir_interfaz()
        self.pagina.update()
        self._mostrar_mensaje("Historial eliminado.")

    # ==========================================
    # Gestion de Planes Financieros
    # ==========================================

    def _guardar_borrador_plan(self):
        """Conserva en memoria lo escrito en el formulario de nuevo plan."""
        if not hasattr(self, "txt_plan_nombre"):
            return
        self.borrador_plan = {
            "nombre": (self.txt_plan_nombre.value or "").strip(),
            "duracion_meses": self.txt_plan_duracion.value or "12",
            "concepto_ingreso": self.txt_plan_ingreso_concepto.value or "",
            "monto_ingreso": self.txt_plan_ingreso_monto.value or "",
            "concepto_gasto": self.txt_plan_gasto_concepto.value or "",
            "monto_gasto": self.txt_plan_gasto_monto.value or "",
            "concepto_credito": self.txt_plan_credito_concepto.value or "",
            "monto_credito": self.txt_plan_credito_monto.value or "",
            "tasa_credito": self.txt_plan_credito_tasa.value or "",
            "plazo_credito": self.txt_plan_credito_plazo.value or "",
            "sistema_credito": self.dd_plan_credito_sistema.value or "Frances",
        }

    def _refrescar_vista_planes(self):
        """Redibuja la vista de planes conservando la pestaña activa."""
        self.reconstruyendo_plan = True
        try:
            self._construir_interfaz()
        finally:
            self.reconstruyendo_plan = False
        self.pagina.update()

    def _evento_agregar_ingreso(self, _):
        """Agrega un ingreso al borrador del plan."""
        self._agregar_item_plan("ingreso")

    def _evento_agregar_gasto(self, _):
        """Agrega un gasto al borrador del plan."""
        self._agregar_item_plan("gasto")

    def _evento_agregar_credito(self, _):
        """Agrega un credito al borrador del plan."""
        self._agregar_item_plan("credito")

    def _agregar_item_plan(self, str_tipo: str):
        """Valida y registra un ingreso, gasto o credito en el plan actual."""
        self._guardar_borrador_plan()

        if str_tipo == "ingreso":
            str_concepto = (self.borrador_plan.get("concepto_ingreso") or "").strip() or "Ingreso"
            val_monto = convertir_a_numero(self.borrador_plan.get("monto_ingreso", ""))
            if val_monto <= 0:
                self._mostrar_mensaje("Ingresa un monto de ingreso mayor a cero.", es_error=True)
                return
            self.plan_ingresos.append({"concepto": str_concepto, "monto": round(val_monto, 2)})
            self.txt_plan_ingreso_concepto.value = ""
            self.txt_plan_ingreso_monto.value = ""
            self.borrador_plan["concepto_ingreso"] = ""
            self.borrador_plan["monto_ingreso"] = ""
            self._refrescar_vista_planes()
            self._mostrar_mensaje("Ingreso agregado al plan.")

        elif str_tipo == "gasto":
            str_concepto = (self.borrador_plan.get("concepto_gasto") or "").strip() or "Gasto"
            val_monto = convertir_a_numero(self.borrador_plan.get("monto_gasto", ""))
            if val_monto <= 0:
                self._mostrar_mensaje("Ingresa un monto de gasto mayor a cero.", es_error=True)
                return
            self.plan_gastos.append({"concepto": str_concepto, "monto": round(val_monto, 2)})
            self.txt_plan_gasto_concepto.value = ""
            self.txt_plan_gasto_monto.value = ""
            self.borrador_plan["concepto_gasto"] = ""
            self.borrador_plan["monto_gasto"] = ""
            self._refrescar_vista_planes()
            self._mostrar_mensaje("Gasto agregado al plan.")

        else:
            str_concepto = (self.borrador_plan.get("concepto_credito") or "").strip() or "Crédito"
            val_monto = convertir_a_numero(self.borrador_plan.get("monto_credito", ""))
            val_tasa = convertir_a_numero(self.borrador_plan.get("tasa_credito", ""))
            try:
                num_meses = int(self.borrador_plan.get("plazo_credito", ""))
            except (TypeError, ValueError):
                num_meses = 0

            if val_monto <= 0 or num_meses <= 0:
                self._mostrar_mensaje("El crédito necesita un monto y un plazo mayores a cero.", es_error=True)
                return
            if val_tasa < 0:
                self._mostrar_mensaje("La tasa del crédito no puede ser negativa.", es_error=True)
                return

            dict_credito = {
                "concepto": str_concepto,
                "monto": round(val_monto, 2),
                "tasa_anual": val_tasa,
                "meses": num_meses,
                "sistema": self.borrador_plan.get("sistema_credito", "Frances"),
            }
            self.plan_creditos.append(dict_credito)
            credito_calculado = calcular_credito(dict_credito)
            self.txt_plan_credito_concepto.value = ""
            self.txt_plan_credito_monto.value = ""
            self.txt_plan_credito_tasa.value = ""
            self.txt_plan_credito_plazo.value = ""
            self.borrador_plan.update({
                "concepto_credito": "",
                "monto_credito": "",
                "tasa_credito": "",
                "plazo_credito": "",
            })
            self._refrescar_vista_planes()
            self._mostrar_mensaje(
                f"Crédito agregado. {credito_calculado['tipo_cuota']}: "
                f"{self._formatear_valor(credito_calculado['cuota_mensual'])}."
            )

    def _evento_quitar_item_plan(self, str_tipo: str, num_indice: int):
        """Elimina un ingreso, gasto o credito del borrador del plan."""
        listas = {
            "ingreso": self.plan_ingresos,
            "gasto": self.plan_gastos,
            "credito": self.plan_creditos,
        }
        lista_destino = listas.get(str_tipo)
        if lista_destino is None or not (0 <= num_indice < len(lista_destino)):
            return
        lista_destino.pop(num_indice)
        self._refrescar_vista_planes()

    def _limpiar_campos_plan(self):
        """Vacía los campos de captura del formulario de planes."""
        if not hasattr(self, "txt_plan_nombre"):
            return
        self.txt_plan_nombre.value = ""
        self.txt_plan_duracion.value = "12"
        self.txt_plan_ingreso_concepto.value = ""
        self.txt_plan_ingreso_monto.value = ""
        self.txt_plan_gasto_concepto.value = ""
        self.txt_plan_gasto_monto.value = ""
        self.txt_plan_credito_concepto.value = ""
        self.txt_plan_credito_monto.value = ""
        self.txt_plan_credito_tasa.value = ""
        self.txt_plan_credito_plazo.value = ""
        self.dd_plan_credito_sistema.value = "Frances"

    def _evento_limpiar_plan(self, _):
        """Descarta el borrador actual sin afectar los planes guardados."""
        self.plan_ingresos.clear()
        self.plan_gastos.clear()
        self.plan_creditos.clear()
        self.borrador_plan = {}
        self._limpiar_campos_plan()
        self._refrescar_vista_planes()
        self._mostrar_mensaje("Borrador del plan limpiado.")

    def _evento_guardar_plan(self, _):
        """Guarda el plan activo (nuevo o editado) en planes.json."""
        if self.mostrar_editor_plan:
            self._sincronizar_plan_activo_desde_editor()
        dict_plan = self.plan_activo
        if dict_plan and dict_plan.get("movimientos"):
            self._capturar_campos_movimientos()
            dict_plan["resumen"] = calcular_resumen_plan(dict_plan)
        if not dict_plan:
            self._mostrar_mensaje("No hay un plan activo para guardar.", es_error=True)
            return
        str_nombre = str(dict_plan.get("nombre", "")).strip()
        if not str_nombre:
            self._mostrar_mensaje("Escribe un nombre para el plan.", es_error=True)
            return
        if not dict_plan.get("creditos"):
            self._mostrar_mensaje("Agrega al menos un crédito antes de guardar el plan.", es_error=True)
            return

        dict_plan["nombre"] = str_nombre
        if self.plan_es_borrador or not dict_plan.get("fecha"):
            dict_plan["fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            if self.plan_es_borrador or not (0 <= self.indice_plan_activo < len(self.lista_planes)):
                self.lista_planes.insert(0, dict_plan)
                self.indice_plan_activo = 0
            else:
                self.lista_planes[self.indice_plan_activo] = dict_plan
            self.lista_planes = self.lista_planes[:MAX_PLANES]
            self._guardar_planes_a_disco()
        except Exception as error:
            self._mostrar_mensaje(f"Error al guardar el plan: {error}", es_error=True)
            return

        self.plan_activo = dict_plan
        self.plan_es_borrador = False
        self.mostrar_editor_plan = False
        self._refrescar_vista_planes()
        self._mostrar_mensaje(f"Plan '{str_nombre}' guardado correctamente.")

    def _evento_borrar_plan(self, num_indice: int):
        """Elimina un plan guardado por indice."""
        if 0 <= num_indice < len(self.lista_planes):
            self.lista_planes.pop(num_indice)
            self._guardar_planes_a_disco()
            if self.indice_plan_activo == num_indice:
                self._evento_volver_planes()
                return
            if self.indice_plan_activo > num_indice:
                self.indice_plan_activo -= 1
            self._refrescar_vista_planes()
            self._mostrar_mensaje("Plan eliminado.")

    def _evento_simular_credito_plan(self, dict_credito: dict):
        """Carga un credito del plan en el simulador y ejecuta el calculo en C++."""
        if not isinstance(dict_credito, dict):
            return
        valores = {
            "sistema": dict_credito.get("sistema", "Frances"),
            "monto": str(dict_credito.get("monto", 10000)),
            "tasa": str(dict_credito.get("tasa_anual", 12)),
            "plazo": str(dict_credito.get("meses", 12)),
            "abonos": [],
        }
        self.lista_abonos = []
        self.vista_activa = "tablas"
        self._inicializar_controles(valores)
        self._construir_interfaz()
        self._renderizar_chat()
        self.pagina.update()
        self._evento_calcular(None)

    def _mostrar_dialogo_nuevo_plan(self, _):
        """Abre el mini menu para crear un plan con duracion, credito e ingresos."""
        paleta = self.paleta
        txt_nombre = self._crear_campo("Nombre del plan", "")
        txt_nombre.hint_text = "ej. Plan familiar 2026"
        txt_duracion = self._crear_campo(
            "Duración del plan en meses", "12",
            sufijo=ft.Text("meses", color=paleta["texto_suave"]),
            tipo_teclado=ft.KeyboardType.NUMBER,
        )
        txt_monto = self._crear_campo(
            "Monto del crédito", "", prefijo=ft.Text("$", color=paleta["texto_suave"]),
            tipo_teclado=ft.KeyboardType.NUMBER,
        )
        txt_tasa = self._crear_campo(
            "Tasa anual", "12", sufijo=ft.Text("%", color=paleta["texto_suave"]),
            tipo_teclado=ft.KeyboardType.NUMBER,
        )
        txt_plazo = self._crear_campo(
            "Plazo del crédito", "12",
            sufijo=ft.Text("meses", color=paleta["texto_suave"]),
            tipo_teclado=ft.KeyboardType.NUMBER,
        )
        dd_sistema = ft.Dropdown(
            label="Sistema de amortización",
            options=[ft.DropdownOption(text=sistema, key=sistema) for sistema in OPCIONES_SISTEMAS],
            value="Frances",
            border_radius=10,
            filled=True,
            fill_color=paleta["campo"],
            border_color=paleta["borde"],
            focused_border_color=paleta["primario"],
            label_style=self._estilo_etiqueta(),
            text_style=self._estilo_texto(),
            menu_style=ft.MenuStyle(bgcolor=paleta["tarjeta"]),
        )

        def _crear_plan(_evento):
            str_nombre = (txt_nombre.value or "").strip()
            if not str_nombre:
                self._mostrar_mensaje("Escribe un nombre para el plan.", es_error=True)
                return
            try:
                num_duracion = max(1, int(convertir_a_numero(txt_duracion.value, 12)))
                num_plazo = max(0, int(convertir_a_numero(txt_plazo.value, 0)))
            except (TypeError, ValueError):
                self._mostrar_mensaje("La duración y el plazo deben ser números enteros.", es_error=True)
                return
            val_monto = convertir_a_numero(txt_monto.value)
            val_tasa = convertir_a_numero(txt_tasa.value, 12)

            if val_monto <= 0 or num_plazo <= 0:
                self._mostrar_mensaje("Indica un monto de crédito y un plazo mayores a cero.", es_error=True)
                return
            if val_tasa < 0:
                self._mostrar_mensaje("La tasa no puede ser negativa.", es_error=True)
                return

            str_ajuste = ""
            if num_plazo > num_duracion:
                num_duracion = num_plazo
                str_ajuste = f" Duración ajustada a {num_duracion} meses para cubrir el crédito."

            dict_credito = {
                "concepto": "Crédito del plan",
                "monto": round(val_monto, 2),
                "tasa_anual": val_tasa,
                "meses": num_plazo,
                "sistema": dd_sistema.value or "Frances",
            }
            dict_plan = crear_plan(
                str_nombre, [], [], [dict_credito], num_duracion
            )
            dict_plan["fecha"] = ""

            self.plan_activo = dict_plan
            self.indice_plan_activo = -1
            self.plan_es_borrador = True
            self.mostrar_editor_plan = False
            self.duracion_plan = num_duracion
            self.plan_ingresos = []
            self.plan_gastos = []
            self.plan_creditos = [dict(dict_credito)]
            self.borrador_plan = {"nombre": str_nombre, "duracion_meses": str(num_duracion)}
            self._limpiar_campos_plan()
            self.txt_plan_nombre.value = str_nombre
            self.txt_plan_duracion.value = str(num_duracion)
            dialogo.open = False
            self._refrescar_vista_planes()
            self._mostrar_mensaje(
                "Plan creado. Registra tus ingresos y gastos mes a mes." + str_ajuste
            )

        dialogo = ft.AlertDialog(
            modal=True,
            bgcolor=paleta["tarjeta"],
            title=ft.Text("Nuevo plan", color=paleta["primario"], size=16,
                          weight=ft.FontWeight.BOLD, font_family=FUENTE_APP),
            content=ft.Column(
                controls=[
                    txt_nombre, txt_duracion, ft.Divider(height=1, color=paleta["borde"]),
                    txt_monto, txt_tasa, txt_plazo, dd_sistema,
                ],
                tight=True,
                spacing=10,
                width=430,
                height=520,
                scroll=ft.ScrollMode.AUTO,
            ),
            scrollable=True,
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancelar", color=paleta["texto_suave"], font_family=FUENTE_APP),
                    on_click=lambda _evento: setattr(dialogo, "open", False) or self.pagina.update(),
                ),
                self._crear_boton_primario("Crear plan", ft.Icons.CHECK, _crear_plan),
            ],
        )
        self.pagina.overlay.append(dialogo)
        dialogo.open = True
        self.pagina.update()

    def _sincronizar_plan_activo_desde_editor(self):
        """Recalcula el plan activo con los cambios hechos en el editor."""
        if self.plan_activo is None:
            return
        self._guardar_borrador_plan()
        try:
            num_duracion = max(1, int(convertir_a_numero(
                self.borrador_plan.get("duracion_meses", 12), 12
            )))
        except (TypeError, ValueError):
            num_duracion = 12
        self.duracion_plan = num_duracion
        str_nombre = (self.borrador_plan.get("nombre")
                      or self.plan_activo.get("nombre") or "Plan").strip()
        str_fecha = self.plan_activo.get("fecha", "")
        self.plan_activo = crear_plan(
            str_nombre, self.plan_ingresos, self.plan_gastos,
            self.plan_creditos, num_duracion,
        )
        self.plan_activo["fecha"] = str_fecha

    def _cargar_editor_desde_plan(self, dict_plan: dict):
        """Carga los datos de un plan en el editor detallado."""
        if not dict_plan:
            return
        self.plan_ingresos = [dict(item) for item in dict_plan.get("ingresos", [])]
        self.plan_gastos = [dict(item) for item in dict_plan.get("gastos", [])]
        self.plan_creditos = [dict(item) for item in dict_plan.get("creditos", [])]
        try:
            num_duracion = max(1, int(dict_plan.get("duracion_meses", 12)))
        except (TypeError, ValueError):
            num_duracion = 12
        self.duracion_plan = num_duracion
        str_nombre = dict_plan.get("nombre", "Plan")
        self.borrador_plan = {
            "nombre": str_nombre,
            "duracion_meses": str(num_duracion),
        }
        self._limpiar_campos_plan()
        self.txt_plan_nombre.value = str_nombre
        self.txt_plan_duracion.value = str(num_duracion)

    def _evento_cambiar_movimiento_plan(self, evento, num_mes: int, str_campo: str):
        """Guarda en memoria el ingreso o gasto escrito para un mes del plan."""
        if self.plan_activo is None:
            return
        val_nuevo = convertir_a_numero(evento.control.value)
        for movimiento in self.plan_activo.get("movimientos", []):
            if int(movimiento.get("mes", 0)) == num_mes:
                movimiento[str_campo] = round(val_nuevo, 2)
                break

    def _capturar_campos_movimientos(self):
        """Traslada lo escrito en los campos mensuales al diccionario del plan."""
        if self.plan_activo is None or not self.dic_campos_movimientos:
            return
        valores_por_mes: dict[int, dict] = {}
        for (num_mes, str_campo), control in self.dic_campos_movimientos.items():
            valores_por_mes.setdefault(num_mes, {})[str_campo] = round(
                convertir_a_numero(control.value), 2
            )
        for movimiento in self.plan_activo.get("movimientos", []):
            num_mes = int(movimiento.get("mes", 0))
            if num_mes not in valores_por_mes:
                continue
            valores = valores_por_mes[num_mes]
            movimiento["ingresos"] = valores.get("ingresos", movimiento.get("ingresos", 0))
            movimiento["egresos"] = valores.get("egresos", movimiento.get("egresos", 0))

    def _evento_aplicar_movimientos_plan(self, _=None):
        """Guarda los montos mensuales capturados y recalcula el plan."""
        if self.plan_activo is None:
            return
        self._capturar_campos_movimientos()
        self.plan_activo["resumen"] = calcular_resumen_plan(self.plan_activo)
        self._refrescar_vista_planes()
        self._mostrar_mensaje("Ingresos y egresos guardados. Plan recalculado.")

    def _evento_recalcular_plan(self, _=None):
        """Recalcula resumen, gráficas y tablas con los movimientos capturados."""
        self._evento_aplicar_movimientos_plan(_)

    def _evento_alternar_editor_plan(self, _):
        """Muestra u oculta el editor de ingresos, gastos y créditos del plan."""
        if self.plan_activo is None:
            return
        if self.mostrar_editor_plan:
            self._sincronizar_plan_activo_desde_editor()
            self.mostrar_editor_plan = False
        else:
            self._cargar_editor_desde_plan(self.plan_activo)
            self.mostrar_editor_plan = True
        self._refrescar_vista_planes()

    def _evento_abrir_plan(self, dict_plan: dict, num_indice: int):
        """Abre un plan guardado para ver su progreso mes a mes."""
        self.plan_activo = dict_plan
        self.indice_plan_activo = num_indice
        self.plan_es_borrador = False
        self.mostrar_editor_plan = False
        if dict_plan is not None:
            self.planes_consultados = [
                plan for plan in self.planes_consultados
                if plan.get("nombre") != dict_plan.get("nombre")
            ]
            self.planes_consultados.insert(0, dict_plan)
            self.planes_consultados = self.planes_consultados[:3]
        self._refrescar_vista_planes()

    def _evento_volver_planes(self, _=None):
        """Regresa al listado de planes y descarta cualquier borrador activo."""
        self.plan_activo = None
        self.indice_plan_activo = -1
        self.plan_es_borrador = False
        self.mostrar_editor_plan = False
        self._refrescar_vista_planes()


    # ==========================================
    # Barra de Navegacion Vertical
    # ==========================================

    def _crear_barra_navegacion(self) -> ft.Container:
        """Construye la barra lateral con Inicio, Tablas, Planes, Historial y Configuración."""
        paleta = self.paleta
        ancho = 210 if self.nav_expandida else 60

        def _btn_nav(icono: str, etiqueta: str, destino: str) -> ft.Container:
            es_activo = self.vista_activa == destino
            color_icono = paleta["primario"] if es_activo else paleta["texto_suave"]
            bgcolor_btn = ft.Colors.with_opacity(0.14, paleta["primario"]) if es_activo else "transparent"

            def _click(_e, d=destino):
                self.vista_activa = d
                self._construir_interfaz()
                if self.tabla_actual and self.parametros_actuales:
                    self._actualizar_resultados()
                self.pagina.update()

            contenido_fila = [ft.Icon(icono, size=20, color=color_icono)]
            if self.nav_expandida:
                contenido_fila.append(
                    ft.Text(etiqueta, size=13, color=color_icono,
                            font_family=FUENTE_APP, weight=ft.FontWeight.BOLD if es_activo else ft.FontWeight.NORMAL)
                )
            return ft.Container(
                content=ft.Row(controls=contenido_fila, spacing=10,
                               vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=bgcolor_btn,
                border_radius=10,
                padding=ft.Padding.symmetric(horizontal=10, vertical=12),
                on_click=_click,
                ink=True,
                width=ancho - 10,
            )

        def _btn_config(_e):
            self._mostrar_dialogo_configuracion(_e)

        icono_config = ft.Icons.SETTINGS_ROUNDED
        color_cfg = paleta["texto_suave"]
        contenido_cfg = [ft.Icon(icono_config, size=20, color=color_cfg)]
        if self.nav_expandida:
            contenido_cfg.append(ft.Text("Configuración", size=13, color=color_cfg, font_family=FUENTE_APP))
        btn_config = ft.Container(
            content=ft.Row(controls=contenido_cfg, spacing=10,
                           vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="transparent",
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=10, vertical=12),
            on_click=_btn_config,
            ink=True,
            width=ancho - 10,
        )

        # Botón hamburguesa para expandir/colapsar
        def _toggle_nav(_e):
            self.nav_expandida = not self.nav_expandida
            self._construir_interfaz()
            if self.tabla_actual and self.parametros_actuales:
                self._actualizar_resultados()
            self.pagina.update()

        icono_hamburguesa = ft.Icons.MENU_OPEN_ROUNDED if self.nav_expandida else ft.Icons.MENU_ROUNDED
        btn_hamburguesa = ft.IconButton(
            icon=icono_hamburguesa,
            icon_color=paleta["primario"],
            icon_size=22,
            tooltip="Expandir / Colapsar menú",
            on_click=_toggle_nav,
        )

        encabezado_barra = ft.Row(
            controls=[btn_hamburguesa] + (
                [ft.Text("Menú", size=14, weight=ft.FontWeight.BOLD,
                         color=paleta["texto_claro"], font_family=FUENTE_APP)]
                if self.nav_expandida else []
            ),
            spacing=4,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        controles_nav = ft.Column(
            controls=[
                ft.Container(content=encabezado_barra, padding=ft.Padding.only(bottom=8)),
                ft.Divider(height=1, color=paleta["borde"]),
                _btn_nav(ft.Icons.HOME_ROUNDED, "Inicio", "inicio"),
                _btn_nav(ft.Icons.TABLE_CHART_ROUNDED, "Tablas", "tablas"),
                _btn_nav(ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, "Planes", "planes"),
                _btn_nav(ft.Icons.HISTORY_ROUNDED, "Historial", "historial"),
                ft.Container(expand=True),
                ft.Divider(height=1, color=paleta["borde"]),
                btn_config,
            ],
            spacing=4,
            expand=True,
        )

        return ft.Container(
            content=controles_nav,
            width=ancho,
            bgcolor=paleta["tarjeta"],
            border=ft.Border.only(right=ft.BorderSide(1, paleta["borde"])),
            border_radius=ft.BorderRadius.only(top_left=16, bottom_left=16, top_right=0, bottom_right=0),
            padding=ft.Padding.symmetric(horizontal=5, vertical=12),
        )

    def _crear_vista_historial(self) -> ft.Container:
        """Construye el panel del historial de simulaciones guardadas."""
        paleta = self.paleta

        if not self.lista_historial:
            cuerpo = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.HISTORY_ROUNDED, size=48, color=paleta["texto_suave"]),
                        ft.Text("No hay simulaciones guardadas.", size=14, color=paleta["texto_suave"],
                                font_family=FUENTE_APP, italic=True),
                        ft.Text("Calcula un préstamo y usa 'Guardar en historial'.", size=11,
                                color=paleta["texto_suave"], font_family=FUENTE_APP),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
            )
        else:
            tarjetas: list[ft.Control] = []
            for num_indice, registro in enumerate(self.lista_historial):
                params = self._extraer_params_historial(registro)
                if params is None:
                    continue
                fecha = params.get("fecha", "Sin fecha")
                sistema = params.get("sistema", "?")
                monto = self._formatear_valor(float(params.get("monto", 0)))
                tasa = params.get("tasa_anual", params.get("tasa", 0))
                meses = params.get("meses", 0)
                texto_resumen = f"{sistema} | {monto} | {tasa}% | {meses} meses"

                # Indicadores si están disponibles (formato nuevo)
                indicadores = registro.get("indicadores", {})
                texto_ind = ""
                if indicadores:
                    total = self._formatear_valor(indicadores.get("total_pagado", 0))
                    interes = self._formatear_valor(indicadores.get("total_interes", 0))
                    texto_ind = f"Total: {total} | Intereses: {interes}"

                tarjeta = ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(fecha, size=10, color=paleta["texto_suave"], font_family=FUENTE_APP),
                                    ft.Text(texto_resumen, size=13, weight=ft.FontWeight.BOLD,
                                            color=paleta["texto_claro"], font_family=FUENTE_APP),
                                ] + ([ft.Text(texto_ind, size=11, color=paleta["verde"], font_family=FUENTE_APP)]
                                     if texto_ind else []),
                                spacing=2,
                                expand=True,
                            ),
                            ft.Row(
                                controls=[
                                    ft.OutlinedButton(
                                        content=ft.Text("Cargar", size=11, font_family=FUENTE_APP),
                                        icon=ft.Icons.UPLOAD_ROUNDED,
                                        on_click=lambda _e, r=registro: self._evento_cargar_desde_historial(r),
                                        style=ft.ButtonStyle(
                                            color=paleta["primario"],
                                            icon_color=paleta["primario"],
                                            side=ft.BorderSide(1, paleta["primario"]),
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                                        ),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_ROUNDED,
                                        icon_color=paleta["rojo"],
                                        icon_size=18,
                                        tooltip="Eliminar registro",
                                        on_click=lambda _e, i=num_indice: self._evento_borrar_registro_historial(i),
                                    ),
                                ],
                                spacing=4,
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=paleta["campo"],
                    border=ft.Border.all(1, paleta["borde"]),
                    border_radius=12,
                    padding=12,
                )
                tarjetas.append(tarjeta)

            cuerpo = ft.Container(
                content=ft.ListView(controls=tarjetas, expand=True, spacing=10,
                                    padding=ft.Padding.only(bottom=10)),
                expand=True,
            )

        barra_top = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text("Historial de simulaciones", size=18, weight=ft.FontWeight.BOLD,
                                color=paleta["primario"], font_family=FUENTE_APP),
                        ft.Text(f"{len(self.lista_historial)} registro(s) guardado(s).",
                                size=11, color=paleta["texto_suave"], font_family=FUENTE_APP),
                    ],
                    spacing=0, expand=True,
                ),
                ft.OutlinedButton(
                    content=ft.Text("Limpiar todo", size=12, font_family=FUENTE_APP),
                    icon=ft.Icons.DELETE_SWEEP_ROUNDED,
                    on_click=self._evento_limpiar_historial,
                    style=ft.ButtonStyle(
                        color=paleta["rojo"],
                        icon_color=paleta["rojo"],
                        side=ft.BorderSide(1, paleta["rojo"]),
                        shape=ft.RoundedRectangleBorder(radius=9),
                    ),
                ) if self.lista_historial else ft.Container(),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return ft.Container(
            content=ft.Column(
                controls=[barra_top, ft.Divider(height=1, color=paleta["borde"]), cuerpo],
                expand=True, spacing=14,
            ),
            padding=20,
            bgcolor=paleta["tarjeta"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=16,
            expand=True,
        )

    # ==========================================
    # Vista de Planes Financieros
    # ==========================================

    def _color_nivel_endeudamiento(self, str_nivel: str) -> str:
        """Retorna el color asociado al nivel de endeudamiento."""
        colores = {
            "saludable": self.paleta["verde"],
            "moderado": self.paleta["secundario"],
            "alto": self.paleta["rojo"],
        }
        return colores.get(str_nivel, self.paleta["texto_suave"])

    def _texto_nivel_endeudamiento(self, str_nivel: str) -> str:
        """Traduce el nivel de endeudamiento a una etiqueta legible."""
        textos = {
            "saludable": "Saludable (hasta 30% del ingreso)",
            "moderado": "Moderado (entre 30% y 40%)",
            "alto": "Alto riesgo (más del 40%)",
            "sin_ingresos": "Agrega ingresos para evaluar tu capacidad",
        }
        return textos.get(str_nivel, "Sin evaluar")

    def _crear_fila_item_plan(self, str_titulo: str, str_detalle: str, str_monto: str,
                              num_indice: int, str_tipo: str) -> ft.Container:
        """Crea una fila con un movimiento del plan y su boton para eliminarlo."""
        paleta = self.paleta
        configuracion = {
            "ingreso": (ft.Icons.ARROW_DOWNWARD_ROUNDED, paleta["verde"]),
            "gasto": (ft.Icons.ARROW_UPWARD_ROUNDED, paleta["rojo"]),
            "credito": (ft.Icons.CREDIT_CARD_ROUNDED, paleta["secundario"]),
        }
        icono, color = configuracion.get(str_tipo, (ft.Icons.CIRCLE, paleta["texto_suave"]))
        controles_columna = [
            ft.Text(str_titulo, size=12, weight=ft.FontWeight.BOLD,
                    color=paleta["texto_claro"], font_family=FUENTE_APP,
                    max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
        ]
        if str_detalle:
            controles_columna.append(
                ft.Text(str_detalle, size=10, color=paleta["texto_suave"], font_family=FUENTE_APP)
            )
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icono, size=15, color=color),
                    ft.Column(controls=controles_columna, spacing=1, expand=True),
                    ft.Text(str_monto, size=12, weight=ft.FontWeight.BOLD,
                            color=color, font_family=FUENTE_APP),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE_ROUNDED,
                        icon_size=14,
                        icon_color=paleta["texto_suave"],
                        tooltip="Quitar del plan",
                        on_click=lambda _e, t=str_tipo, i=num_indice: self._evento_quitar_item_plan(t, i),
                    ),
                ],
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.with_opacity(0.05, paleta["texto_claro"]),
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
        )

    def _crear_tarjeta_seccion_plan(self, str_titulo: str, str_subtitulo: str,
                                    icono: str, color: str, list_controles: list[ft.Control],
                                    str_total: str) -> ft.Container:
        """Agrupa los controles de una seccion del plan (ingresos, gastos o creditos)."""
        paleta = self.paleta
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(icono, size=18, color=color),
                            ft.Column(
                                controls=[
                                    ft.Text(str_titulo, size=13, weight=ft.FontWeight.BOLD,
                                            color=color, font_family=FUENTE_APP),
                                    ft.Text(str_subtitulo, size=10, color=paleta["texto_suave"],
                                            font_family=FUENTE_APP),
                                ],
                                spacing=0,
                                expand=True,
                            ),
                            ft.Text(str_total, size=13, weight=ft.FontWeight.BOLD,
                                    color=color, font_family=FUENTE_APP),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=paleta["borde"]),
                    *list_controles,
                ],
                spacing=8,
            ),
            bgcolor=paleta["campo"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=12,
            padding=12,
        )

    def _crear_tarjeta_resumen_borrador(self, dict_resumen: dict | None = None) -> ft.Container:
        """Muestra el balance mensual y el nivel de endeudamiento del plan actual."""
        paleta = self.paleta
        resumen = dict_resumen or calcular_resumen_plan({
            "ingresos": self.plan_ingresos,
            "gastos": self.plan_gastos,
            "creditos": self.plan_creditos,
        })
        val_ratio = float(resumen["ratio_endeudamiento"])
        val_ingresos = float(resumen["total_ingresos"])
        str_nivel = nivel_endeudamiento(val_ratio, val_ingresos)
        color_nivel = self._color_nivel_endeudamiento(str_nivel)

        def _metrica(str_titulo: str, str_valor: str, color: str) -> ft.Container:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(str_titulo, size=10, color=paleta["texto_suave"], font_family=FUENTE_APP),
                        ft.Text(str_valor, size=14, weight=ft.FontWeight.BOLD,
                                color=color, font_family=FUENTE_APP,
                                max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ],
                    spacing=1,
                ),
                bgcolor=paleta["tarjeta"],
                border_radius=9,
                padding=10,
                expand=True,
            )

        color_balance = paleta["verde"] if resumen.get("balance_total", resumen["balance_mensual"]) >= 0 else paleta["rojo"]
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.INSIGHTS_ROUNDED, size=18, color=paleta["primario"]),
                            ft.Text("Resumen del plan", size=13, weight=ft.FontWeight.BOLD,
                                    color=paleta["primario"], font_family=FUENTE_APP, expand=True),
                            ft.Text(f"{resumen['num_creditos']} crédito(s)", size=11,
                                    color=paleta["texto_suave"], font_family=FUENTE_APP),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        controls=[
                            _metrica("Ingresos", self._formatear_valor(resumen["total_ingresos"]), paleta["verde"]),
                            _metrica("Gastos", self._formatear_valor(resumen["total_gastos"]), paleta["rojo"]),
                            _metrica("Cuotas totales", self._formatear_valor(resumen["total_cuotas"]), paleta["secundario"]),
                            _metrica("Balance del plan", self._formatear_valor(resumen.get("balance_total", resumen["balance_mensual"])), color_balance),
                        ],
                        spacing=8,
                    ),
                    ft.ProgressBar(
                        value=min(val_ratio / 100.0, 1.0),
                        color=color_nivel,
                        bgcolor=paleta["seleccion"],
                        height=9,
                        border_radius=5,
                    ),
                    ft.Row(
                        controls=[
                            ft.Text(f"Endeudamiento: {val_ratio:.1f}% del ingreso",
                                    size=11, weight=ft.FontWeight.BOLD, color=color_nivel,
                                    font_family=FUENTE_APP, expand=True),
                            ft.Text(self._texto_nivel_endeudamiento(str_nivel), size=10,
                                    color=paleta["texto_suave"], font_family=FUENTE_APP),
                        ],
                        spacing=8,
                    ),
                    ft.Text(
                        f"Intereses totales de los créditos: {self._formatear_valor(resumen['total_intereses'])}",
                        size=10, color=paleta["texto_suave"], font_family=FUENTE_APP,
                    ),
                ],
                spacing=10,
            ),
            bgcolor=paleta["campo"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=14,
            padding=14,
        )

    def _crear_tarjeta_grafica_plan(self, dict_resumen: dict) -> ft.Container:
        """Muestra la grafica de flujo del plan actual y permite ampliarla con un clic."""
        paleta = self.paleta
        src_grafica = generar_grafica_planes_base64(
            dict_resumen, modo_oscuro=self.modo_tema == "oscuro"
        )
        if src_grafica:
            contenido_grafica = ft.GestureDetector(
                content=ft.Image(src=src_grafica, fit=ft.BoxFit.CONTAIN, expand=True),
                on_tap=lambda _e, s=src_grafica: self._mostrar_grafica_ampliada(
                    s, "Flujo mensual del plan"
                ),
                mouse_cursor=ft.MouseCursor.ZOOM_IN,
                expand=True,
            )
        else:
            contenido_grafica = ft.Container(
                content=ft.Text(
                    "Agrega ingresos, gastos o créditos para ver la gráfica del plan.",
                    italic=True, size=11, color=paleta["texto_suave"], font_family=FUENTE_APP,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
            )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.INSERT_CHART_ROUNDED, size=17, color=paleta["primario"]),
                            ft.Text("Gráfica del plan", size=13, weight=ft.FontWeight.BOLD,
                                    color=paleta["primario"], font_family=FUENTE_APP, expand=True),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(
                        content=contenido_grafica,
                        height=280,
                        bgcolor=paleta["tarjeta"],
                        border_radius=10,
                        padding=6,
                    ),
                ],
                spacing=8,
            ),
            bgcolor=paleta["campo"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=14,
            padding=14,
        )

    def _crear_tarjeta_evolucion_plan(self, lista_creditos: list[dict] | None = None) -> ft.Container:
        """Muestra la evolucion mensual de los creditos como dispersion con linea."""
        paleta = self.paleta
        creditos = lista_creditos if lista_creditos is not None else self.plan_creditos
        lista_filas = calcular_evolucion_plan(creditos)
        src_grafica = generar_grafica_evolucion_plan_base64(
            lista_filas, modo_oscuro=self.modo_tema == "oscuro"
        )
        if src_grafica:
            contenido_grafica = ft.GestureDetector(
                content=ft.Image(src=src_grafica, fit=ft.BoxFit.CONTAIN, expand=True),
                on_tap=lambda _e, s=src_grafica: self._mostrar_grafica_ampliada(
                    s, "Evolución mensual de los créditos"
                ),
                mouse_cursor=ft.MouseCursor.ZOOM_IN,
                expand=True,
            )
        else:
            contenido_grafica = ft.Container(
                content=ft.Text(
                    "Agrega créditos para ver su evolución mes a mes.",
                    italic=True, size=11, color=paleta["texto_suave"], font_family=FUENTE_APP,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
            )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.SCATTER_PLOT_ROUNDED, size=17, color=paleta["primario"]),
                            ft.Text("Evolución mensual (dispersión + línea)", size=13,
                                    weight=ft.FontWeight.BOLD, color=paleta["primario"],
                                    font_family=FUENTE_APP, expand=True),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(
                        content=contenido_grafica,
                        height=300,
                        bgcolor=paleta["tarjeta"],
                        border_radius=10,
                        padding=6,
                    ),
                ],
                spacing=8,
            ),
            bgcolor=paleta["campo"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=14,
            padding=14,
        )

    def _crear_tarjeta_flujo_temporal_plan(self, dict_plan: dict) -> ft.Container:
        """Muestra el flujo del plan mes a mes con dispersion y lineas."""
        paleta = self.paleta
        lista_filas = calcular_flujo_plan(dict_plan)
        src_grafica = generar_grafica_flujo_plan_base64(
            lista_filas, modo_oscuro=self.modo_tema == "oscuro"
        )
        if src_grafica:
            contenido_grafica = ft.GestureDetector(
                content=ft.Image(src=src_grafica, fit=ft.BoxFit.CONTAIN, expand=True),
                on_tap=lambda _e, s=src_grafica: self._mostrar_grafica_ampliada(
                    s, f"Flujo mensual · {dict_plan.get('nombre', 'Plan')}"
                ),
                mouse_cursor=ft.MouseCursor.ZOOM_IN,
                expand=True,
            )
        else:
            contenido_grafica = ft.Container(
                content=ft.Text("Sin datos para graficar el flujo del plan.", size=11,
                                italic=True, color=paleta["texto_suave"], font_family=FUENTE_APP),
                alignment=ft.Alignment.CENTER,
                expand=True,
            )
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.SHOW_CHART_ROUNDED, size=17, color=paleta["primario"]),
                            ft.Text("Flujo del plan mes a mes (dispersión + línea)", size=13,
                                    weight=ft.FontWeight.BOLD, color=paleta["primario"],
                                    font_family=FUENTE_APP, expand=True),
                            ft.Text(f"{len(lista_filas)} meses", size=10,
                                    color=paleta["texto_suave"], font_family=FUENTE_APP),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(
                        content=contenido_grafica,
                        height=300,
                        bgcolor=paleta["tarjeta"],
                        border_radius=10,
                        padding=6,
                    ),
                ],
                spacing=8,
            ),
            bgcolor=paleta["campo"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=14,
            padding=14,
        )

    def _crear_tabla_desglose_plan(self, lista_filas: list[dict],
                                   es_anual: bool = False) -> ft.Container:
        """Construye la tabla de desglose mensual o anual del plan."""
        paleta = self.paleta
        estilo = ft.TextStyle(
            color=self._color_encabezado_tabla(), size=10,
            weight=ft.FontWeight.BOLD, font_family=FUENTE_APP,
        )
        if es_anual:
            titulos = ["Año", "Ingresos", "Egresos", "Crédito", "Intereses",
                       "Capital", "Saldo neto", "Saldo crédito"]
        else:
            titulos = ["Mes", "Año", "Ingresos", "Egresos", "Crédito",
                       "Intereses", "Capital", "Saldo neto", "Saldo crédito"]
        columnas = [
            ft.DataColumn(ft.Text(titulo, style=estilo), numeric=indice > 0)
            for indice, titulo in enumerate(titulos)
        ]
        claves = (
            ["anio", "ingresos", "egresos", "pago_credito", "intereses",
             "capital", "saldo_neto", "saldo_credito"]
            if es_anual else
            ["mes", "anio", "ingresos", "egresos", "pago_credito", "intereses",
             "capital", "saldo_neto", "saldo_credito"]
        )
        colores = {
            "ingresos": paleta["verde"],
            "egresos": paleta["rojo"],
            "pago_credito": paleta["secundario"],
            "saldo_neto": paleta["primario"],
        }
        filas_tabla = []
        for fila in lista_filas:
            celdas = []
            for indice, clave in enumerate(claves):
                valor = fila.get(clave, 0)
                if clave == "anio":
                    texto = f"Año {int(valor)}"
                elif clave in ("mes",):
                    texto = str(int(valor))
                else:
                    texto = self._formatear_valor(float(valor))
                celdas.append(ft.DataCell(ft.Text(
                    texto, size=11, font_family=FUENTE_APP,
                    color=colores.get(clave, paleta["texto_claro"]),
                    weight=ft.FontWeight.W_500,
                )))
            filas_tabla.append(ft.DataRow(cells=celdas))

        tabla = ft.DataTable(
            columns=columnas,
            rows=filas_tabla,
            bgcolor=paleta["campo"],
            border=ft.Border.all(0, paleta["borde"]),
            border_radius=10,
            heading_row_color=paleta["seleccion"],
            heading_row_height=36,
            data_row_min_height=32,
            data_row_max_height=38,
            column_spacing=16,
            horizontal_margin=12,
        )
        return ft.Container(
            content=ft.ListView(
                controls=[ft.Row(controls=[tabla], scroll=ft.ScrollMode.AUTO)],
                expand=True,
                spacing=0,
            ),
            height=260 if not es_anual else 190,
            bgcolor=ft.Colors.with_opacity(0.35, paleta["tarjeta"]),
            border_radius=10,
            padding=6,
        )

    def _crear_tarjeta_montos_fijos_plan(self, dict_plan: dict) -> ft.Container:
        """Muestra los montos fijos vigentes y su historial de cambios por mes."""
        paleta = self.paleta
        try:
            num_duracion = max(1, int(dict_plan.get("duracion_meses", 12)))
        except (TypeError, ValueError):
            num_duracion = 12
        historial_ingresos = dict_plan.get("ingresos_fijos_historial", [])
        historial_gastos = dict_plan.get("egresos_fijos_historial", [])
        val_ingreso = valor_fijo_en_mes(
            historial_ingresos, num_duracion
        ) or convertir_a_numero(dict_plan.get("ingreso_fijo", 0))
        val_gasto = valor_fijo_en_mes(
            historial_gastos, num_duracion
        ) or convertir_a_numero(dict_plan.get("egreso_fijo", 0))

        def _historial(historial: list, color: str) -> list[ft.Control]:
            if not historial:
                return [
                    ft.Text("Sin cambios registrados.", size=10, italic=True,
                            color=paleta["texto_suave"], font_family=FUENTE_APP)
                ]
            return [
                ft.Row(
                    controls=[
                        ft.Text(f"Desde mes {int(entrada.get('desde_mes', 1))}", size=10,
                                color=paleta["texto_suave"], font_family=FUENTE_APP, expand=True),
                        ft.Text(self._formatear_valor(float(entrada.get("monto", 0))), size=10,
                                color=color, font_family=FUENTE_APP),
                    ],
                    spacing=6,
                )
                for entrada in sorted(
                    historial, key=lambda item: int(item.get("desde_mes", 1))
                )
                if isinstance(entrada, dict)
            ]

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ATTACH_MONEY_ROUNDED, size=17, color=paleta["primario"]),
                            ft.Text("Ingresos fijos y egresos fijos", size=13,
                                    weight=ft.FontWeight.BOLD, color=paleta["primario"],
                                    font_family=FUENTE_APP, expand=True),
                            ft.Text("Solo lectura · se editan con confirmación",
                                    size=9, color=paleta["texto_suave"], font_family=FUENTE_APP),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Text("Se suman a cada mes del crédito: sueldo, renta, colegiaturas, etc.",
                            size=10, color=paleta["texto_suave"], font_family=FUENTE_APP),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text("Ingreso fijo (sueldo)", size=10,
                                                color=paleta["texto_suave"], font_family=FUENTE_APP),
                                        ft.Text(self._formatear_valor(float(val_ingreso)), size=16,
                                                weight=ft.FontWeight.BOLD, color=paleta["verde"],
                                                font_family=FUENTE_APP),
                                    ],
                                    spacing=2,
                                ),
                                expand=True,
                                bgcolor=paleta["tarjeta"],
                                border_radius=10,
                                padding=10,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text("Egreso fijo (renta)", size=10,
                                                color=paleta["texto_suave"], font_family=FUENTE_APP),
                                        ft.Text(self._formatear_valor(float(val_gasto)), size=16,
                                                weight=ft.FontWeight.BOLD, color=paleta["rojo"],
                                                font_family=FUENTE_APP),
                                    ],
                                    spacing=2,
                                ),
                                expand=True,
                                bgcolor=paleta["tarjeta"],
                                border_radius=10,
                                padding=10,
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Row(
                        controls=[
                            ft.FilledTonalButton(
                                content=ft.Text("Editar ingreso fijo", size=11,
                                                font_family=FUENTE_APP),
                                icon=ft.Icons.EDIT_ROUNDED,
                                on_click=lambda _e: self._mostrar_dialogo_monto_fijo("ingresos"),
                                height=36,
                                expand=True,
                            ),
                            ft.FilledTonalButton(
                                content=ft.Text("Editar egreso fijo", size=11,
                                                font_family=FUENTE_APP),
                                icon=ft.Icons.EDIT_ROUNDED,
                                on_click=lambda _e: self._mostrar_dialogo_monto_fijo("egresos"),
                                height=36,
                                expand=True,
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Divider(height=1, color=paleta["borde"]),
                    ft.Text("Historial del ingreso fijo", size=10,
                            color=paleta["verde"], font_family=FUENTE_APP),
                    *_historial(historial_ingresos, paleta["verde"]),
                    ft.Text("Historial del egreso fijo", size=10,
                            color=paleta["rojo"], font_family=FUENTE_APP),
                    *_historial(historial_gastos, paleta["rojo"]),
                ],
                spacing=8,
            ),
            bgcolor=paleta["campo"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=14,
            padding=14,
        )

    def _mostrar_dialogo_monto_fijo(self, str_tipo: str):
        """Pregunta el monto y el mes desde el que regirá un cambio fijo."""
        if self.plan_activo is None:
            return
        paleta = self.paleta
        es_ingreso = str_tipo == "ingresos"
        str_titulo = "ingreso fijo" if es_ingreso else "egreso fijo"
        clave_historial = (
            "ingresos_fijos_historial" if es_ingreso else "egresos_fijos_historial"
        )
        clave_valor = "ingreso_fijo" if es_ingreso else "egreso_fijo"
        try:
            num_duracion = max(1, int(self.plan_activo.get("duracion_meses", 12)))
        except (TypeError, ValueError):
            num_duracion = 12

        txt_monto = self._crear_campo(
            f"Nuevo {str_titulo}", "",
            prefijo=ft.Text("$", color=paleta["texto_suave"]),
            tipo_teclado=ft.KeyboardType.TEXT,
        )
        txt_desde = self._crear_campo(
            "¿Desde qué mes comenzará?", "1",
            sufijo=ft.Text("mes", color=paleta["texto_suave"]),
            tipo_teclado=ft.KeyboardType.NUMBER,
        )

        def _guardar(_evento):
            val_monto = convertir_a_numero(txt_monto.value)
            if val_monto < 0:
                self._mostrar_mensaje("El monto no puede ser negativo.", es_error=True)
                return
            try:
                num_desde = max(1, int(convertir_a_numero(txt_desde.value, 1)))
            except (TypeError, ValueError):
                num_desde = 1
            num_desde = min(num_desde, num_duracion)

            historial = [
                dict(item) for item in (self.plan_activo.get(clave_historial) or [])
                if isinstance(item, dict)
            ]
            historial = [
                item for item in historial
                if int(item.get("desde_mes", 1)) != num_desde
            ]
            historial.append({"monto": round(val_monto, 2), "desde_mes": num_desde})
            historial.sort(key=lambda item: int(item.get("desde_mes", 1)))
            self.plan_activo[clave_historial] = historial
            self.plan_activo[clave_valor] = valor_fijo_en_mes(historial, num_duracion)
            self.plan_activo["resumen"] = calcular_resumen_plan(self.plan_activo)
            dialogo.open = False
            self._refrescar_vista_planes()
            self._mostrar_mensaje(
                f"{str_titulo.capitalize()} actualizado desde el mes {num_desde}."
            )

        dialogo = ft.AlertDialog(
            modal=True,
            bgcolor=paleta["tarjeta"],
            title=ft.Text(f"Editar {str_titulo}", color=paleta["primario"], size=16,
                          weight=ft.FontWeight.BOLD, font_family=FUENTE_APP),
            content=ft.Column(
                controls=[
                    ft.Text("El valor anterior se conserva en el historial.", size=10,
                            color=paleta["texto_suave"], font_family=FUENTE_APP),
                    txt_monto,
                    txt_desde,
                ],
                tight=True,
                spacing=10,
                width=360,
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancelar", color=paleta["texto_suave"],
                                    font_family=FUENTE_APP),
                    on_click=lambda _evento: setattr(dialogo, "open", False) or self.pagina.update(),
                ),
                self._crear_boton_primario("Guardar cambio", ft.Icons.CHECK, _guardar),
            ],
        )
        self.pagina.overlay.append(dialogo)
        dialogo.open = True
        self.pagina.update()

    def _crear_tarjeta_grafica_hasta_mes(self, dict_plan: dict) -> ft.Container:
        """Muestra el flujo del plan aunque no haya meses editados."""
        paleta = self.paleta
        try:
            num_mes = max(0, int(dict_plan.get("ultimo_mes_editado", 0)))
        except (TypeError, ValueError):
            num_mes = 0
        try:
            num_duracion = max(1, int(dict_plan.get("duracion_meses", 12)))
        except (TypeError, ValueError):
            num_duracion = 12
        num_limite = num_duracion
        lista_filas = calcular_flujo_plan(dict_plan)[:num_limite]
        src_grafica = generar_grafica_flujo_plan_base64(
            lista_filas, modo_oscuro=self.modo_tema == "oscuro"
        ) if lista_filas else ""
        if src_grafica:
            contenido_grafica = ft.GestureDetector(
                content=ft.Image(src=src_grafica, fit=ft.BoxFit.CONTAIN, expand=True),
                on_tap=lambda _e, s=src_grafica: self._mostrar_grafica_ampliada(
                    s, f"Progreso del plan hasta el mes {num_limite}"
                ),
                mouse_cursor=ft.MouseCursor.ZOOM_IN,
                expand=True,
            )
        else:
            contenido_grafica = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.SHOW_CHART_ROUNDED, size=40, color=paleta["texto_suave"]),
                        ft.Text("No se pudo generar la gráfica del plan.",
                                size=12, italic=True, color=paleta["texto_suave"],
                                font_family=FUENTE_APP),
                    ],
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
            )
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.SHOW_CHART_ROUNDED, size=17, color=paleta["primario"]),
                            ft.Text("Gráfica del plan", size=13,
                                    weight=ft.FontWeight.BOLD, color=paleta["primario"],
                                    font_family=FUENTE_APP, expand=True),
                            ft.Text(
                                f"Editado hasta mes {num_mes} · {num_duracion} meses"
                                if num_mes > 0 else f"{num_duracion} meses",
                                size=10, color=paleta["texto_suave"], font_family=FUENTE_APP,
                            ),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(
                        content=contenido_grafica,
                        height=390,
                        bgcolor=paleta["tarjeta"],
                        border_radius=10,
                        padding=6,
                    ),
                    ft.Text("Editar un mes:", size=10, color=paleta["texto_suave"],
                            font_family=FUENTE_APP),
                    ft.Row(
                        controls=[
                            ft.OutlinedButton(
                                content=ft.Text(f"Mes {num}", size=10,
                                                color=paleta["primario"], font_family=FUENTE_APP),
                                on_click=lambda _e, m=num: self._evento_editar_mes_desde_grafica(m),
                                height=28,
                                style=ft.ButtonStyle(
                                    side=ft.BorderSide(1, paleta["borde"]),
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                            )
                            for num in range(1, num_duracion + 1)
                        ],
                        wrap=True,
                        spacing=6,
                        run_spacing=4,
                    ),
                ],
                spacing=8,
            ),
            bgcolor=paleta["campo"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=14,
            padding=14,
        )

    def _evento_cambiar_pestana_plan(self, evento):
        """Conserva la pestaña activa del registro/gráfica/IA del plan."""
        if getattr(self, "reconstruyendo_plan", False):
            return
        self.indice_pestana_plan = evento.control.selected_index

    def _evento_agregar_movimiento_mes(self, txt_concepto, txt_monto, str_tipo: str):
        """Agrega un ingreso o gasto al dialogo del mes actual."""
        estado = getattr(self, "dic_dialogo_movimiento", {}) or {}
        if not estado:
            return
        str_concepto = (txt_concepto.value or "").strip() or ("Ingreso" if str_tipo == "ingresos" else "Gasto")
        val_monto = convertir_a_numero(txt_monto.value)
        if val_monto <= 0:
            self._mostrar_mensaje("El monto debe ser mayor a cero.", es_error=True)
            return
        estado[str_tipo].append({"concepto": str_concepto, "monto": round(val_monto, 2)})
        txt_concepto.value = ""
        txt_monto.value = ""
        self._refrescar_dialogo_movimiento_mes()

    def _evento_quitar_movimiento_mes(self, str_tipo: str, num_indice: int):
        """Quita un ingreso o gasto del dialogo del mes actual."""
        estado = getattr(self, "dic_dialogo_movimiento", {}) or {}
        if not estado or not (0 <= num_indice < len(estado.get(str_tipo, []))):
            return
        estado[str_tipo].pop(num_indice)
        self._refrescar_dialogo_movimiento_mes()

    def _refrescar_dialogo_movimiento_mes(self):
        """Redibuja el contenido del dialogo de registro mensual."""
        estado = getattr(self, "dic_dialogo_movimiento", {}) or {}
        if not estado:
            return
        func_refrescar = estado.get("refrescar")
        if func_refrescar is not None:
            func_refrescar()

    def _evento_editar_mes_desde_grafica(self, num_mes: int):
        """Abre el registro mensual asegurando que la pestaña Gráfica siga activa."""
        self.indice_pestana_plan = 1
        self._mostrar_dialogo_movimiento_mes(num_mes)

    def _evento_registrar_mes_desde_registro(self, num_mes: int):
        """Abre el registro mensual manteniendo la pestaña Registro activa."""
        self.indice_pestana_plan = 0
        self._mostrar_dialogo_movimiento_mes(num_mes)

    def _mostrar_dialogo_movimiento_mes(self, num_mes: int):
        """Abre un menú mensual para capturar varios ingresos y varios gastos."""
        if self.plan_activo is None:
            return
        paleta = self.paleta
        movimiento = next(
            (item for item in self.plan_activo.get("movimientos", [])
             if int(item.get("mes", 0)) == num_mes),
            None,
        )
        if movimiento is None:
            return

        lista_ingresos = [
            dict(item) for item in movimiento.get("ingresos", []) if isinstance(item, dict)
        ]
        lista_egresos = [
            dict(item) for item in movimiento.get("egresos", []) if isinstance(item, dict)
        ]

        txt_ing_concepto = self._crear_campo("Concepto del ingreso", "")
        txt_ing_concepto.expand = True
        txt_ing_monto = self._crear_campo(
            "Monto", "", prefijo=ft.Text("$", color=paleta["texto_suave"]),
            tipo_teclado=ft.KeyboardType.TEXT,
        )
        txt_ing_monto.width = 130
        txt_gas_concepto = self._crear_campo("Concepto del gasto", "")
        txt_gas_concepto.expand = True
        txt_gas_monto = self._crear_campo(
            "Monto", "", prefijo=ft.Text("$", color=paleta["texto_suave"]),
            tipo_teclado=ft.KeyboardType.TEXT,
        )
        txt_gas_monto.width = 130

        contenido = ft.Column(
            controls=[],
            tight=True,
            spacing=8,
            width=430,
            height=470,
            scroll=ft.ScrollMode.AUTO,
        )

        def _filas_items(lista_items: list[dict], str_tipo: str) -> list[ft.Control]:
            if not lista_items:
                return [
                    ft.Text(f"Sin {str_tipo} registrados en este mes.", size=10, italic=True,
                            color=paleta["texto_suave"], font_family=FUENTE_APP)
                ]
            color = paleta["verde"] if str_tipo == "ingresos" else paleta["rojo"]
            filas = []
            for num_indice, item in enumerate(lista_items):
                filas.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.ARROW_CIRCLE_DOWN_ROUNDED if str_tipo == "ingresos"
                                        else ft.Icons.ARROW_CIRCLE_UP_ROUNDED,
                                        size=14, color=color),
                                ft.Text(item.get("concepto", ""), size=11,
                                        color=paleta["texto_claro"], font_family=FUENTE_APP, expand=True),
                                ft.Text(self._formatear_valor(float(item.get("monto", 0))),
                                        size=11, weight=ft.FontWeight.BOLD,
                                        color=color, font_family=FUENTE_APP),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE_ROUNDED,
                                    icon_size=14,
                                    icon_color=paleta["rojo"],
                                    tooltip="Quitar",
                                    on_click=lambda _e, t=str_tipo, i=num_indice: self._evento_quitar_movimiento_mes(t, i),
                                ),
                            ],
                            spacing=6,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        bgcolor=paleta["campo"],
                        border_radius=8,
                        padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                    )
                )
            return filas

        def _refrescar_contenido():
            contenido.controls.clear()
            contenido.controls.extend([
                ft.Text("Captura todos los ingresos y gastos reales de este mes.",
                        size=10, color=paleta["texto_suave"], font_family=FUENTE_APP),
                ft.Text("Ingresos", size=12, weight=ft.FontWeight.BOLD,
                        color=paleta["verde"], font_family=FUENTE_APP),
                ft.Row(
                    controls=[
                        txt_ing_concepto,
                        txt_ing_monto,
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE_ROUNDED,
                            icon_color=paleta["verde"],
                            tooltip="Agregar ingreso",
                            on_click=lambda _e: self._evento_agregar_movimiento_mes(
                                txt_ing_concepto, txt_ing_monto, "ingresos"
                            ),
                        ),
                    ],
                    spacing=6,
                ),
                *_filas_items(lista_ingresos, "ingresos"),
                ft.Divider(height=1, color=paleta["borde"]),
                ft.Text("Gastos", size=12, weight=ft.FontWeight.BOLD,
                        color=paleta["rojo"], font_family=FUENTE_APP),
                ft.Row(
                    controls=[
                        txt_gas_concepto,
                        txt_gas_monto,
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE_ROUNDED,
                            icon_color=paleta["rojo"],
                            tooltip="Agregar gasto",
                            on_click=lambda _e: self._evento_agregar_movimiento_mes(
                                txt_gas_concepto, txt_gas_monto, "egresos"
                            ),
                        ),
                    ],
                    spacing=6,
                ),
                *_filas_items(lista_egresos, "gastos"),
            ])
            self.pagina.update()

        def _guardar(_evento):
            movimiento["ingresos"] = [dict(item) for item in lista_ingresos]
            movimiento["egresos"] = [dict(item) for item in lista_egresos]
            self.plan_activo["ultimo_mes_editado"] = max(
                int(self.plan_activo.get("ultimo_mes_editado", 0)), num_mes
            )
            self.plan_activo["resumen"] = calcular_resumen_plan(self.plan_activo)
            dialogo.open = False
            self.dic_dialogo_movimiento = {}
            self._refrescar_vista_planes()
            self._mostrar_mensaje(f"Movimientos del mes {num_mes} guardados.")

        dialogo = ft.AlertDialog(
            modal=True,
            bgcolor=paleta["tarjeta"],
            title=ft.Text(f"Registro del mes {num_mes}", color=paleta["primario"], size=16,
                          weight=ft.FontWeight.BOLD, font_family=FUENTE_APP),
            content=contenido,
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancelar", color=paleta["texto_suave"], font_family=FUENTE_APP),
                    on_click=lambda _evento: setattr(dialogo, "open", False) or self.pagina.update(),
                ),
                self._crear_boton_primario("Guardar mes", ft.Icons.CHECK, _guardar),
            ],
        )
        self.dic_dialogo_movimiento = {
            "dialogo": dialogo,
            "num_mes": num_mes,
            "ingresos": lista_ingresos,
            "egresos": lista_egresos,
            "contenido": contenido,
            "paleta": paleta,
            "refrescar": _refrescar_contenido,
        }
        self.pagina.overlay.append(dialogo)
        dialogo.open = True
        _refrescar_contenido()

    def _crear_tarjeta_registro_mensual_plan(self, dict_plan: dict) -> ft.Container:
        """Muestra una fila por mes del crédito para registrar ingresos y gastos."""
        paleta = self.paleta
        movimientos = dict_plan.get("movimientos") or []
        self.dic_campos_movimientos = {}
        mapa_flujo = {
            int(fila["mes"]): fila for fila in calcular_flujo_plan(dict_plan)
        }
        filas_registro = []
        for movimiento in movimientos:
            num_mes = int(movimiento.get("mes", 0))
            num_anio = (num_mes - 1) // 12 + 1
            fila_flujo = mapa_flujo.get(num_mes, {})
            saldo_neto = float(fila_flujo.get("saldo_neto", 0))
            valor_ingreso = sumar_grupo_movimientos(movimiento.get("ingresos", 0))
            valor_gasto = sumar_grupo_movimientos(movimiento.get("egresos", 0))
            num_ingresos = len(movimiento.get("ingresos", [])) if isinstance(movimiento.get("ingresos"), list) else 0
            num_gastos = len(movimiento.get("egresos", [])) if isinstance(movimiento.get("egresos"), list) else 0
            texto_ingreso = ft.Text(
                self._formatear_valor(valor_ingreso) if valor_ingreso else "Sin registrar",
                size=11,
                color=paleta["verde"] if valor_ingreso else paleta["texto_suave"],
                font_family=FUENTE_APP,
                width=120,
            )
            texto_gasto = ft.Text(
                self._formatear_valor(valor_gasto) if valor_gasto else "Sin registrar",
                size=11,
                color=paleta["rojo"] if valor_gasto else paleta["texto_suave"],
                font_family=FUENTE_APP,
                width=120,
            )
            filas_registro.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(f"Mes {num_mes}", size=11, weight=ft.FontWeight.BOLD,
                                    color=paleta["texto_claro"], font_family=FUENTE_APP, width=60),
                            ft.Text(f"Año {num_anio}", size=10, color=paleta["texto_suave"],
                                    font_family=FUENTE_APP, width=50),
                            ft.Text(f"Ingresos ({num_ingresos})", size=10, color=paleta["verde"],
                                    font_family=FUENTE_APP, width=70),
                            texto_ingreso,
                            ft.Text(f"Gastos ({num_gastos})", size=10, color=paleta["rojo"],
                                    font_family=FUENTE_APP, width=60),
                            texto_gasto,
                            ft.Text("Cuota", size=10, color=paleta["secundario"],
                                    font_family=FUENTE_APP, width=45),
                            ft.Text(self._formatear_valor(float(fila_flujo.get("pago_credito", 0))),
                                    size=11, color=paleta["secundario"], font_family=FUENTE_APP, width=100),
                            ft.Text("Neto", size=10, color=paleta["texto_suave"],
                                    font_family=FUENTE_APP, width=35),
                            ft.Text(
                                self._formatear_valor(saldo_neto), size=11,
                                color=paleta["verde"] if saldo_neto >= 0 else paleta["rojo"],
                                font_family=FUENTE_APP, width=100,
                            ),
                            ft.FilledTonalButton(
                                content=ft.Text("Registrar", size=10, weight=ft.FontWeight.BOLD,
                                                color=paleta["primario"], font_family=FUENTE_APP),
                                icon=ft.Icons.EDIT_ROUNDED,
                                on_click=lambda _e, m=num_mes: self._evento_registrar_mes_desde_registro(m),
                                height=32,
                            ),
                        ],
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=ft.Colors.with_opacity(0.05, paleta["texto_claro"]),
                    border_radius=8,
                    padding=ft.Padding.symmetric(horizontal=6, vertical=3),
                )
            )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.EDIT_CALENDAR_ROUNDED, size=17, color=paleta["primario"]),
                            ft.Text("Registro mensual de ingresos y gastos", size=13,
                                    weight=ft.FontWeight.BOLD, color=paleta["primario"],
                                    font_family=FUENTE_APP, expand=True),
                            ft.Text(f"{len(movimientos)} meses", size=10,
                                    color=paleta["texto_suave"], font_family=FUENTE_APP),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Text("Pulsa 'Registrar' en cada mes para capturar su ingreso y su gasto.",
                            size=10, color=paleta["texto_suave"], font_family=FUENTE_APP),
                    ft.Container(
                        content=ft.ListView(controls=filas_registro, expand=True, spacing=4),
                        height=290,
                        bgcolor=paleta["tarjeta"],
                        border_radius=10,
                        padding=6,
                    ),
                ],
                spacing=8,
            ),
            bgcolor=paleta["campo"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=14,
            padding=14,
        )

    def _crear_tarjeta_desglose_plan(self, dict_plan: dict) -> ft.Container:
        """Muestra el desglose de ingresos, egresos y créditos por mes y por año."""
        paleta = self.paleta
        filas_mensuales = calcular_flujo_plan(dict_plan)
        filas_anuales = calcular_resumen_anual(filas_mensuales)
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, size=17, color=paleta["primario"]),
                            ft.Text("Desglose por mes y por año", size=13,
                                    weight=ft.FontWeight.BOLD, color=paleta["primario"],
                                    font_family=FUENTE_APP, expand=True),
                            ft.Text(f"{len(filas_mensuales)} meses · {len(filas_anuales)} año(s)",
                                    size=10, color=paleta["texto_suave"], font_family=FUENTE_APP),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Text("Mensual", size=11, weight=ft.FontWeight.BOLD,
                            color=paleta["texto_suave"], font_family=FUENTE_APP),
                    self._crear_tabla_desglose_plan(filas_mensuales),
                    ft.Text("Anual", size=11, weight=ft.FontWeight.BOLD,
                            color=paleta["texto_suave"], font_family=FUENTE_APP),
                    self._crear_tabla_desglose_plan(filas_anuales, es_anual=True),
                ],
                spacing=8,
            ),
            bgcolor=paleta["campo"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=14,
            padding=14,
        )

    def _crear_tarjeta_plan_guardado(self, dict_plan: dict, num_indice: int) -> ft.Container:
        """Dibuja un plan guardado con su resumen y sus creditos simulables."""
        paleta = self.paleta
        resumen = dict_plan.get("resumen") or calcular_resumen_plan(dict_plan)
        val_ratio = float(resumen.get("ratio_endeudamiento", 0))
        str_nivel = nivel_endeudamiento(val_ratio, float(resumen.get("total_ingresos", 0)))
        color_nivel = self._color_nivel_endeudamiento(str_nivel)

        filas_creditos = []
        for dict_credito in dict_plan.get("creditos", []):
            str_detalle = (
                f"{dict_credito.get('sistema', 'Frances')} · "
                f"{dict_credito.get('meses', 0)} meses · "
                f"Intereses {self._formatear_valor(float(dict_credito.get('total_interes', 0)))}"
            )
            fila = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.CREDIT_CARD_ROUNDED, size=14, color=paleta["secundario"]),
                        ft.Column(
                            controls=[
                                ft.Text(dict_credito.get("concepto", "Crédito"), size=12,
                                        weight=ft.FontWeight.BOLD, color=paleta["texto_claro"],
                                        font_family=FUENTE_APP),
                                ft.Text(str_detalle, size=10, color=paleta["texto_suave"],
                                        font_family=FUENTE_APP),
                            ],
                            spacing=0,
                            expand=True,
                        ),
                        ft.Text(
                            f"{self._formatear_valor(float(dict_credito.get('cuota_mensual', 0)))}/mes",
                            size=11, weight=ft.FontWeight.BOLD, color=paleta["secundario"],
                            font_family=FUENTE_APP,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.PLAY_CIRCLE_FILL_ROUNDED,
                            icon_size=20,
                            icon_color=paleta["primario"],
                            tooltip="Enviar este crédito al simulador",
                            on_click=lambda _e, c=dict_credito: self._evento_simular_credito_plan(c),
                        ),
                    ],
                    spacing=6,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding.symmetric(horizontal=4, vertical=2),
            )
            filas_creditos.append(fila)

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED,
                                                 size=20, color=paleta["primario"]),
                                width=38, height=38,
                                bgcolor=ft.Colors.with_opacity(0.14, paleta["primario"]),
                                border_radius=10,
                                alignment=ft.Alignment.CENTER,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(dict_plan.get("nombre", "Plan sin nombre"), size=14,
                                            weight=ft.FontWeight.BOLD, color=paleta["texto_claro"],
                                            font_family=FUENTE_APP),
                                    ft.Text(dict_plan.get("fecha", "Sin fecha"), size=10,
                                            color=paleta["texto_suave"], font_family=FUENTE_APP),
                                ],
                                spacing=1,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ANALYTICS_ROUNDED,
                                icon_color=paleta["primario"],
                                icon_size=19,
                                tooltip="Abrir plan y ver su progreso",
                                on_click=lambda _e, p=dict_plan, i=num_indice: self._evento_abrir_plan(p, i),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_ROUNDED,
                                icon_color=paleta["rojo"],
                                icon_size=18,
                                tooltip="Eliminar plan",
                                on_click=lambda _e, i=num_indice: self._evento_borrar_plan(i),
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        controls=[
                            ft.Text(f"Ingresos: {self._formatear_valor(resumen.get('total_ingresos', 0))}",
                                    size=11, color=paleta["verde"], font_family=FUENTE_APP),
                            ft.Text(f"Gastos: {self._formatear_valor(resumen.get('total_gastos', 0))}",
                                    size=11, color=paleta["rojo"], font_family=FUENTE_APP),
                            ft.Text(f"Cuotas: {self._formatear_valor(resumen.get('total_cuotas', 0))}",
                                    size=11, color=paleta["secundario"], font_family=FUENTE_APP),
                            ft.Text(f"Balance: {self._formatear_valor(resumen.get('balance_total', resumen.get('balance_mensual', 0)))}",
                                    size=11, weight=ft.FontWeight.BOLD,
                                    color=paleta["verde"] if resumen.get("balance_total", resumen.get("balance_mensual", 0)) >= 0 else paleta["rojo"],
                                    font_family=FUENTE_APP),
                        ],
                        spacing=14,
                        wrap=True,
                    ),
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.SPEED_ROUNDED, size=14, color=color_nivel),
                            ft.Text(f"Endeudamiento: {val_ratio:.1f}% · {self._texto_nivel_endeudamiento(str_nivel)}",
                                    size=10, color=color_nivel, font_family=FUENTE_APP),
                        ],
                        spacing=4,
                    ),
                    ft.Divider(height=1, color=paleta["borde"]),
                    *(filas_creditos if filas_creditos else [
                        ft.Text("Este plan no tiene créditos registrados.", size=10,
                                italic=True, color=paleta["texto_suave"], font_family=FUENTE_APP)
                    ]),
                ],
                spacing=8,
            ),
            bgcolor=paleta["campo"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=14,
            padding=14,
        )

    def _evento_ir_a_tablas(self, _=None):
        """Navega a la vista de tablas y simulación."""
        self.vista_activa = "tablas"
        self._construir_interfaz()
        self.pagina.update()

    def _evento_ir_a_planes(self, _=None):
        """Navega al listado de planes financieros."""
        self.vista_activa = "planes"
        self.plan_activo = None
        self.mostrar_editor_plan = False
        self._construir_interfaz()
        self.pagina.update()

    def _evento_ir_a_historial(self, _=None):
        """Navega al historial completo de simulaciones."""
        self.vista_activa = "historial"
        self._construir_interfaz()
        self.pagina.update()

    def _evento_abrir_plan_desde_inicio(self, dict_plan: dict):
        """Abre un plan reciente desde el inicio."""
        num_indice = next(
            (i for i, plan in enumerate(self.lista_planes)
             if plan is dict_plan or plan.get("nombre") == dict_plan.get("nombre")),
            -1,
        )
        self.vista_activa = "planes"
        self._evento_abrir_plan(dict_plan, num_indice)

    def _obtener_saludo(self) -> str:
        """Devuelve un saludo según la hora del sistema."""
        hora_actual = datetime.now().hour
        if 5 <= hora_actual < 12:
            return "Buenos días"
        if 12 <= hora_actual < 20:
            return "Buenas tardes"
        return "Buenas noches"

    def _crear_vista_inicio(self) -> ft.Container:
        """Panel de inicio con las últimas operaciones y los últimos planes."""
        paleta = self.paleta

        encabezado = ft.Row(
            controls=[
                ft.Container(expand=True),
                ft.FilledButton(
                    content=ft.Text("Ir a Tablas", color=self._color_contraste(),
                                    size=12, weight=ft.FontWeight.BOLD, font_family=FUENTE_APP),
                    icon=ft.Icons.TABLE_CHART_ROUNDED,
                    on_click=self._evento_ir_a_tablas,
                    height=42,
                    style=ft.ButtonStyle(
                        bgcolor=paleta["primario"],
                        color=self._color_contraste(),
                        icon_color=self._color_contraste(),
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                ),
                ft.FilledTonalButton(
                    content=ft.Text("Ir a Planes", color=paleta["primario"],
                                    size=12, weight=ft.FontWeight.BOLD, font_family=FUENTE_APP),
                    icon=ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED,
                    on_click=self._evento_ir_a_planes,
                    height=42,
                ),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Saludo dinámico según la hora del sistema
        str_saludo = self._obtener_saludo()
        icono_saludo = (ft.Icons.NIGHTLIGHT_ROUNDED if str_saludo == "Buenas noches"
                        else ft.Icons.WB_SUNNY_ROUNDED)
        saludo = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Icon(icono_saludo, size=38, color=paleta["secundario"]),
                        ft.Text(str_saludo, size=36, weight=ft.FontWeight.BOLD,
                                color=paleta["secundario"], font_family=FUENTE_APP),
                        ft.Text("Bienvenido a tu simulador financiero.", size=12,
                                color=paleta["texto_suave"], font_family=FUENTE_APP),
                    ],
                    spacing=6,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                )
            ],
        )

        # Últimas 3 operaciones del historial
        tarjetas_operaciones: list[ft.Control] = []
        for registro in self.lista_historial[:3]:
            params = self._extraer_params_historial(registro) or {}
            indicadores = registro.get("indicadores", {}) or {}
            resumen_secundario = ""
            if indicadores:
                resumen_secundario = f"Intereses: {self._formatear_valor(float(indicadores.get('total_interes', 0)))}"
            tarjetas_operaciones.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CALCULATE_ROUNDED, size=18, color=paleta["secundario"]),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        f"{params.get('sistema', 'Sistema')} | "
                                        f"{self._formatear_valor(float(params.get('monto', 0)))} | "
                                        f"{params.get('tasa_anual', params.get('tasa', 0))}% | "
                                        f"{params.get('meses', 0)} meses",
                                        size=12, weight=ft.FontWeight.BOLD,
                                        color=paleta["texto_claro"], font_family=FUENTE_APP,
                                    ),
                                    ft.Text(
                                        f"{params.get('fecha', 'Sin fecha')} · {resumen_secundario}",
                                        size=10, color=paleta["texto_suave"], font_family=FUENTE_APP,
                                    ),
                                ],
                                spacing=1,
                                expand=True,
                            ),
                            ft.OutlinedButton(
                                content=ft.Text("Ver en Tablas", size=10, font_family=FUENTE_APP),
                                on_click=lambda _e, r=registro: self._evento_cargar_desde_historial(r),
                            ),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=paleta["campo"],
                    border=ft.Border.all(1, paleta["borde"]),
                    border_radius=10,
                    padding=10,
                )
            )
        if not tarjetas_operaciones:
            tarjetas_operaciones.append(
                ft.Text("Aún no hay operaciones guardadas en el historial.",
                        size=11, italic=True, color=paleta["texto_suave"], font_family=FUENTE_APP)
            )

        # Últimos 3 planes
        tarjetas_planes: list[ft.Control] = []
        planes_recientes = self.planes_consultados or self.lista_planes
        for dict_plan in planes_recientes[:3]:
            resumen = dict_plan.get("resumen") or calcular_resumen_plan(dict_plan)
            try:
                num_duracion = int(dict_plan.get("duracion_meses", 12))
            except (TypeError, ValueError):
                num_duracion = 12
            tarjetas_planes.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, size=18,
                                    color=paleta["primario"]),
                            ft.Column(
                                controls=[
                                    ft.Text(dict_plan.get("nombre", "Plan"), size=12,
                                            weight=ft.FontWeight.BOLD, color=paleta["texto_claro"],
                                            font_family=FUENTE_APP),
                                    ft.Text(
                                        f"{dict_plan.get('fecha', 'Sin fecha')} · {num_duracion} meses · "
                                        f"{len(dict_plan.get('creditos', []))} crédito(s)",
                                        size=10, color=paleta["texto_suave"], font_family=FUENTE_APP,
                                    ),
                                    ft.Text(
                                        f"Balance: {self._formatear_valor(float(resumen.get('balance_total', 0)))}",
                                        size=10, color=paleta["verde"], font_family=FUENTE_APP,
                                    ),
                                ],
                                spacing=1,
                                expand=True,
                            ),
                            ft.FilledTonalButton(
                                content=ft.Text("Abrir plan", size=10, font_family=FUENTE_APP),
                                icon=ft.Icons.OPEN_IN_NEW_ROUNDED,
                                on_click=lambda _e, p=dict_plan: self._evento_abrir_plan_desde_inicio(p),
                            ),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=paleta["campo"],
                    border=ft.Border.all(1, paleta["borde"]),
                    border_radius=10,
                    padding=10,
                )
            )
        if not tarjetas_planes:
            tarjetas_planes.append(
                ft.Text("Aún no hay planes guardados.",
                        size=11, italic=True, color=paleta["texto_suave"], font_family=FUENTE_APP)
            )

        seccion_operaciones = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("Últimas 3 operaciones", size=14, weight=ft.FontWeight.BOLD,
                                    color=paleta["primario"], font_family=FUENTE_APP, expand=True),
                            ft.TextButton(
                                content=ft.Text("Ver historial", size=11, font_family=FUENTE_APP),
                                on_click=self._evento_ir_a_historial,
                            ),
                        ],
                    ),
                    *tarjetas_operaciones,
                ],
                spacing=8,
            ),
            bgcolor=paleta["tarjeta"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=14,
            padding=14,
        )

        seccion_planes = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("Últimos 3 planes", size=14, weight=ft.FontWeight.BOLD,
                                    color=paleta["primario"], font_family=FUENTE_APP, expand=True),
                            ft.TextButton(
                                content=ft.Text("Ver planes", size=11, font_family=FUENTE_APP),
                                on_click=self._evento_ir_a_planes,
                            ),
                        ],
                    ),
                    *tarjetas_planes,
                ],
                spacing=8,
            ),
            bgcolor=paleta["tarjeta"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=14,
            padding=14,
        )

        seccion_operaciones.col = {"xs": 12, "md": 6}
        seccion_planes.col = {"xs": 12, "md": 6}
        seccion_operaciones.height = 340
        seccion_planes.height = 340
        columnas = ft.ResponsiveRow(
            controls=[seccion_operaciones, seccion_planes],
            spacing=14,
            run_spacing=14,
        )
        return ft.Container(
            content=ft.Column(
                controls=[encabezado, saludo, columnas],
                spacing=14,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            expand=True,
        )

    def _crear_vista_planes(self) -> ft.Container:
        """Muestra solo el listado de planes y el boton para crear uno nuevo."""
        paleta = self.paleta
        if self.plan_activo is not None:
            return self._crear_detalle_plan()

        if self.lista_planes:
            tarjetas_guardadas = [
                self._crear_tarjeta_plan_guardado(dict_plan, num_indice)
                for num_indice, dict_plan in enumerate(self.lista_planes)
            ]
        else:
            tarjetas_guardadas = [
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, size=42,
                                    color=paleta["texto_suave"]),
                            ft.Text("Aún no hay planes guardados.", size=13, italic=True,
                                    color=paleta["texto_suave"], font_family=FUENTE_APP),
                            ft.Text("Pulsa 'Nuevo plan' para empezar.",
                                    size=10, color=paleta["texto_suave"], font_family=FUENTE_APP),
                        ],
                        spacing=6,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    alignment=ft.Alignment.CENTER,
                    padding=24,
                )
            ]

        encabezado = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text("Planes financieros", size=18, weight=ft.FontWeight.BOLD,
                                color=paleta["primario"], font_family=FUENTE_APP),
                        ft.Text("Administra tus ingresos, gastos y créditos en un solo lugar.",
                                size=11, color=paleta["texto_suave"], font_family=FUENTE_APP),
                    ],
                    spacing=0,
                    expand=True,
                ),
                ft.FilledButton(
                    content=ft.Text("Nuevo plan", size=12, weight=ft.FontWeight.BOLD,
                                    color=self._color_contraste(), font_family=FUENTE_APP),
                    icon=ft.Icons.ADD_ROUNDED,
                    on_click=self._mostrar_dialogo_nuevo_plan,
                    height=44,
                    style=ft.ButtonStyle(
                        bgcolor=paleta["primario"],
                        color=self._color_contraste(),
                        icon_color=self._color_contraste(),
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        lista_planes = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("Planes guardados", size=13, weight=ft.FontWeight.BOLD,
                                    color=paleta["primario"], font_family=FUENTE_APP, expand=True),
                            ft.Text(f"{len(self.lista_planes)} plan(es)", size=11,
                                    color=paleta["texto_suave"], font_family=FUENTE_APP),
                        ],
                    ),
                    *tarjetas_guardadas,
                ],
                spacing=10,
            ),
            bgcolor=paleta["tarjeta"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=16,
            padding=16,
        )

        return ft.Container(
            content=ft.Column(
                controls=[encabezado, lista_planes],
                spacing=14,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            expand=True,
        )

    def _crear_detalle_plan(self) -> ft.Container:
        """Construye la vista de progreso de un plan con montos fijos, registro y gráfica."""
        paleta = self.paleta
        if self.mostrar_editor_plan:
            self._sincronizar_plan_activo_desde_editor()
        dict_plan = self.plan_activo or {}
        resumen = calcular_resumen_plan(dict_plan)
        dict_plan["resumen"] = resumen
        lista_creditos = dict_plan.get("creditos", [])
        try:
            num_duracion = int(dict_plan.get("duracion_meses", 12))
        except (TypeError, ValueError):
            num_duracion = 12

        encabezado = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK_ROUNDED,
                    icon_color=paleta["primario"],
                    tooltip="Volver al listado",
                    on_click=self._evento_volver_planes,
                ),
                ft.Column(
                    controls=[
                        ft.Text(dict_plan.get("nombre", "Plan"), size=18,
                                weight=ft.FontWeight.BOLD, color=paleta["primario"],
                                font_family=FUENTE_APP),
                        ft.Text(
                            f"Duración: {num_duracion} meses · {len(lista_creditos)} crédito(s) · "
                            f"{dict_plan.get('fecha') or 'Borrador sin guardar'}",
                            size=11, color=paleta["texto_suave"], font_family=FUENTE_APP,
                        ),
                    ],
                    spacing=0,
                    expand=True,
                ),
                *(
                    [ft.OutlinedButton(
                        content=ft.Text("Ocultar editor" if self.mostrar_editor_plan else "Editar datos",
                                        size=11, font_family=FUENTE_APP),
                        icon=ft.Icons.TUNE_ROUNDED,
                        on_click=self._evento_alternar_editor_plan,
                    )] if not dict_plan.get("movimientos") else []
                ),
                self._crear_boton_primario(
                    "Actualizar plan" if not self.plan_es_borrador else "Guardar plan",
                    ft.Icons.SAVE_ROUNDED,
                    self._evento_guardar_plan,
                ),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        controles = [
            encabezado,
            self._crear_tarjeta_resumen_borrador(resumen),
            self._crear_tarjeta_montos_fijos_plan(dict_plan),
        ]
        pestanas_plan = ft.Tabs(
            length=3,
            selected_index=self.indice_pestana_plan,
            expand=True,
            on_change=self._evento_cambiar_pestana_plan,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Registro", icon=ft.Icons.EDIT_CALENDAR_ROUNDED),
                            ft.Tab(label="Gráfica", icon=ft.Icons.SHOW_CHART_ROUNDED),
                            ft.Tab(label="IA", icon=ft.Icons.AUTO_AWESOME_ROUNDED),
                        ],
                        indicator_color=paleta["secundario"],
                        label_color=paleta["secundario"],
                        unselected_label_color=paleta["texto_suave"],
                        divider_color=paleta["borde"],
                    ),
                    ft.TabBarView(
                        controls=[
                            self._crear_tarjeta_registro_mensual_plan(dict_plan),
                            self._crear_tarjeta_grafica_hasta_mes(dict_plan),
                            self._crear_vista_chat_plan(),
                        ],
                        expand=True,
                    ),
                ],
            ),
        )
        controles.append(ft.Container(content=pestanas_plan, height=570))
        if self.mostrar_editor_plan and not dict_plan.get("movimientos"):
            controles.append(self._crear_formulario_editor_plan())

        return ft.Container(
            content=ft.Column(
                controls=controles,
                spacing=14,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            expand=True,
        )

    def _crear_formulario_editor_plan(self) -> ft.Container:
        """Formulario detallado de ingresos, gastos y creditos del plan activo."""
        paleta = self.paleta
        resumen = calcular_resumen_plan({
            "ingresos": self.plan_ingresos,
            "gastos": self.plan_gastos,
            "creditos": self.plan_creditos,
        })

        filas_ingresos = [
            self._crear_fila_item_plan(
                item.get("concepto", "Ingreso"), "",
                self._formatear_valor(float(item.get("monto", 0))),
                num_indice, "ingreso",
            )
            for num_indice, item in enumerate(self.plan_ingresos)
        ]
        seccion_ingresos = self._crear_tarjeta_seccion_plan(
            "Ingresos", "Dinero que recibes cada mes.", ft.Icons.ARROW_DOWNWARD_ROUNDED,
            paleta["verde"],
            [
                ft.Row(
                    controls=[
                        self.txt_plan_ingreso_concepto,
                        self.txt_plan_ingreso_monto,
                        ft.IconButton(icon=ft.Icons.ADD_CIRCLE_ROUNDED, icon_color=paleta["verde"],
                                      tooltip="Agregar ingreso", on_click=self._evento_agregar_ingreso),
                    ],
                    spacing=6,
                ),
                *(filas_ingresos if filas_ingresos else [
                    ft.Text("Sin ingresos registrados.", size=10, italic=True,
                            color=paleta["texto_suave"], font_family=FUENTE_APP)
                ]),
            ],
            self._formatear_valor(resumen["total_ingresos"]),
        )
        seccion_ingresos.col = {"xs": 12, "md": 6}

        filas_gastos = [
            self._crear_fila_item_plan(
                item.get("concepto", "Gasto"), "",
                self._formatear_valor(float(item.get("monto", 0))),
                num_indice, "gasto",
            )
            for num_indice, item in enumerate(self.plan_gastos)
        ]
        seccion_gastos = self._crear_tarjeta_seccion_plan(
            "Gastos", "Pagos fijos y variables del mes.", ft.Icons.ARROW_UPWARD_ROUNDED,
            paleta["rojo"],
            [
                ft.Row(
                    controls=[
                        self.txt_plan_gasto_concepto,
                        self.txt_plan_gasto_monto,
                        ft.IconButton(icon=ft.Icons.ADD_CIRCLE_ROUNDED, icon_color=paleta["rojo"],
                                      tooltip="Agregar gasto", on_click=self._evento_agregar_gasto),
                    ],
                    spacing=6,
                ),
                *(filas_gastos if filas_gastos else [
                    ft.Text("Sin gastos registrados.", size=10, italic=True,
                            color=paleta["texto_suave"], font_family=FUENTE_APP)
                ]),
            ],
            self._formatear_valor(resumen["total_gastos"]),
        )
        seccion_gastos.col = {"xs": 12, "md": 6}

        filas_creditos = []
        for num_indice, dict_credito in enumerate(self.plan_creditos):
            credito_calculado = calcular_credito(dict_credito)
            filas_creditos.append(
                self._crear_fila_item_plan(
                    credito_calculado["concepto"],
                    f"{credito_calculado['sistema']} · {credito_calculado['meses']} meses · "
                    f"Intereses {self._formatear_valor(credito_calculado['total_interes'])}",
                    f"{self._formatear_valor(credito_calculado['cuota_mensual'])}/mes",
                    num_indice, "credito",
                )
            )
        seccion_creditos = self._crear_tarjeta_seccion_plan(
            "Créditos", "Cada crédito con su cuota mensual estimada.", ft.Icons.CREDIT_CARD_ROUNDED,
            paleta["secundario"],
            [
                ft.Row(controls=[self.txt_plan_credito_concepto], spacing=6),
                ft.Row(
                    controls=[
                        self.txt_plan_credito_monto,
                        self.txt_plan_credito_tasa,
                        self.txt_plan_credito_plazo,
                    ],
                    spacing=6,
                ),
                ft.Row(
                    controls=[
                        self.dd_plan_credito_sistema,
                        ft.FilledTonalButton(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.ADD, size=15, color=paleta["primario"]),
                                    ft.Text("Agregar crédito", size=11, weight=ft.FontWeight.BOLD,
                                            color=paleta["primario"], font_family=FUENTE_APP),
                                ],
                                spacing=4,
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            on_click=self._evento_agregar_credito,
                            height=42,
                            expand=True,
                        ),
                    ],
                    spacing=6,
                ),
                *(filas_creditos if filas_creditos else [
                    ft.Text("Agrega al menos un crédito para que el plan sea útil.",
                            size=10, italic=True, color=paleta["texto_suave"], font_family=FUENTE_APP)
                ]),
            ],
            self._formatear_valor(resumen["total_cuotas"]),
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Editar datos del plan", size=13, weight=ft.FontWeight.BOLD,
                            color=paleta["primario"], font_family=FUENTE_APP),
                    ft.Row(controls=[self.txt_plan_nombre, self.txt_plan_duracion], spacing=10),
                    ft.ResponsiveRow(
                        controls=[seccion_ingresos, seccion_gastos],
                        spacing=10,
                        run_spacing=10,
                    ),
                    seccion_creditos,
                ],
                spacing=12,
            ),
            bgcolor=paleta["tarjeta"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=16,
            padding=16,
        )

    # ==========================================
    # Construccion de Controles
    # ==========================================

    def _inicializar_controles(self, valores: dict | None = None):
        """Inicializa los campos de entrada, botones y contenedores reactivos."""
        valores = valores or {}
        paleta = self.paleta

        # Conserva el borrador del plan al reconstruir la interfaz (ej. cambio de tema).
        self.borrador_plan = dict(
            valores.get("borrador_plan", getattr(self, "borrador_plan", {}) or {})
        )

        self.dd_sistema = ft.Dropdown(
            label="Sistema de amortización",
            options=[ft.DropdownOption(text=sistema, key=sistema) for sistema in OPCIONES_SISTEMAS],
            value=valores.get("sistema", "Frances"),
            border_radius=10,
            filled=True,
            fill_color=paleta["campo"],
            border_color=paleta["borde"],
            focused_border_color=paleta["primario"],
            label_style=self._estilo_etiqueta(),
            text_style=self._estilo_texto(),
            menu_style=ft.MenuStyle(bgcolor=paleta["tarjeta"]),
        )
        self.txt_monto = self._crear_campo(
            "Monto del préstamo", valores.get("monto", "10000.00"),
            prefijo=ft.Text("$", color=paleta["texto_suave"]),
            tipo_teclado=ft.KeyboardType.NUMBER
        )
        self.txt_tasa = self._crear_campo(
            "Tasa de interés anual", valores.get("tasa", "12.0"),
            sufijo=ft.Text("%", color=paleta["texto_suave"]),
            tipo_teclado=ft.KeyboardType.NUMBER
        )
        self.txt_plazo = self._crear_campo(
            "Plazo en meses", valores.get("plazo", "12"),
            sufijo=ft.Text("meses", color=paleta["texto_suave"]),
            tipo_teclado=ft.KeyboardType.NUMBER
        )

        # Abonos y adelantos extraordinarios a capital
        self.lista_abonos = [dict(a) for a in valores.get("abonos", getattr(self, "lista_abonos", []))]
        self.txt_abono_mes = ft.TextField(
            label="Mes",
            hint_text="ej. 3",
            value="",
            width=85,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=10,
            filled=True,
            fill_color=paleta["campo"],
            border_color=paleta["borde"],
            focused_border_color=paleta["primario"],
            cursor_color=paleta["primario"],
            label_style=self._estilo_etiqueta(),
            text_style=self._estilo_texto(),
            content_padding=ft.Padding.symmetric(horizontal=10, vertical=12),
        )
        self.txt_abono_monto = ft.TextField(
            label="Monto adelanto",
            hint_text="ej. 2000",
            value="",
            expand=True,
            prefix=ft.Text("$", color=paleta["texto_suave"]),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=10,
            filled=True,
            fill_color=paleta["campo"],
            border_color=paleta["borde"],
            focused_border_color=paleta["primario"],
            cursor_color=paleta["primario"],
            label_style=self._estilo_etiqueta(),
            text_style=self._estilo_texto(),
            content_padding=ft.Padding.symmetric(horizontal=10, vertical=12),
        )
        self.col_lista_abonos = ft.Column(spacing=6)
        self.lbl_ahorro_abonos = ft.Text(
            "", size=11, weight=ft.FontWeight.W_500, color=paleta["verde"], font_family=FUENTE_APP
        )
        self.contenedor_ahorro_abonos = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SAVINGS_ROUNDED, size=16, color=paleta["verde"]),
                    ft.Container(content=self.lbl_ahorro_abonos, expand=True),
                ],
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.with_opacity(0.12, paleta["verde"]),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.3, paleta["verde"])),
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=10, vertical=8),
            visible=False,
        )
        self._refrescar_lista_abonos()

        # Campos del modulo de planes financieros
        borrador_plan = self.borrador_plan or {}
        self.txt_plan_nombre = self._crear_campo(
            "Nombre del plan", borrador_plan.get("nombre", "")
        )
        self.txt_plan_nombre.hint_text = "ej. Plan familiar 2026"
        self.txt_plan_nombre.width = 260
        self.txt_plan_duracion = self._crear_campo(
            "Duración del plan", str(borrador_plan.get("duracion_meses", 12)),
            sufijo=ft.Text("meses", color=paleta["texto_suave"]),
            tipo_teclado=ft.KeyboardType.NUMBER,
        )
        self.txt_plan_duracion.width = 150

        self.txt_plan_ingreso_concepto = self._crear_campo(
            "Concepto del ingreso", borrador_plan.get("concepto_ingreso", "")
        )
        self.txt_plan_ingreso_concepto.hint_text = "ej. Sueldo"
        self.txt_plan_ingreso_concepto.expand = True
        self.txt_plan_ingreso_monto = self._crear_campo(
            "Monto", borrador_plan.get("monto_ingreso", ""),
            prefijo=ft.Text("$", color=paleta["texto_suave"]),
            tipo_teclado=ft.KeyboardType.NUMBER,
        )
        self.txt_plan_ingreso_monto.width = 130

        self.txt_plan_gasto_concepto = self._crear_campo(
            "Concepto del gasto", borrador_plan.get("concepto_gasto", "")
        )
        self.txt_plan_gasto_concepto.hint_text = "ej. Renta"
        self.txt_plan_gasto_concepto.expand = True
        self.txt_plan_gasto_monto = self._crear_campo(
            "Monto", borrador_plan.get("monto_gasto", ""),
            prefijo=ft.Text("$", color=paleta["texto_suave"]),
            tipo_teclado=ft.KeyboardType.NUMBER,
        )
        self.txt_plan_gasto_monto.width = 130

        self.txt_plan_credito_concepto = self._crear_campo(
            "Concepto del crédito", borrador_plan.get("concepto_credito", "")
        )
        self.txt_plan_credito_concepto.hint_text = "ej. Crédito automotriz"
        self.txt_plan_credito_concepto.expand = True
        self.txt_plan_credito_monto = self._crear_campo(
            "Monto", borrador_plan.get("monto_credito", ""),
            prefijo=ft.Text("$", color=paleta["texto_suave"]),
            tipo_teclado=ft.KeyboardType.NUMBER,
        )
        self.txt_plan_credito_monto.width = 130
        self.txt_plan_credito_tasa = self._crear_campo(
            "Tasa anual", borrador_plan.get("tasa_credito", ""),
            sufijo=ft.Text("%", color=paleta["texto_suave"]),
            tipo_teclado=ft.KeyboardType.NUMBER,
        )
        self.txt_plan_credito_tasa.width = 115
        self.txt_plan_credito_plazo = self._crear_campo(
            "Plazo", borrador_plan.get("plazo_credito", ""),
            sufijo=ft.Text("meses", color=paleta["texto_suave"]),
            tipo_teclado=ft.KeyboardType.NUMBER,
        )
        self.txt_plan_credito_plazo.width = 125
        self.dd_plan_credito_sistema = ft.Dropdown(
            label="Sistema",
            options=[ft.DropdownOption(text=sistema, key=sistema) for sistema in OPCIONES_SISTEMAS],
            value=borrador_plan.get("sistema_credito", "Frances"),
            width=160,
            border_radius=10,
            filled=True,
            fill_color=paleta["campo"],
            border_color=paleta["borde"],
            focused_border_color=paleta["primario"],
            label_style=self._estilo_etiqueta(),
            text_style=self._estilo_texto(),
            menu_style=ft.MenuStyle(bgcolor=paleta["tarjeta"]),
        )

        self.btn_calcular = self._crear_boton_primario(
            "Calcular préstamo", ft.Icons.CALCULATE, self._evento_calcular
        )
        self.btn_limpiar = self._crear_boton_secundario(
            "Limpiar campos", ft.Icons.CLEAR_ALL, self._evento_limpiar
        )

        # Tarjetas de indicadores (KPIs)
        self.lbl_kpi_cuota = ft.Text(
            self._formatear_valor(0), size=16, weight=ft.FontWeight.BOLD,
            color=self._color_cuota(), max_lines=1, overflow=ft.TextOverflow.ELLIPSIS
        )
        self.lbl_kpi_interes = ft.Text(
            self._formatear_valor(0), size=16, weight=ft.FontWeight.BOLD,
            color=paleta["rojo"], max_lines=1, overflow=ft.TextOverflow.ELLIPSIS
        )
        self.lbl_kpi_total = ft.Text(
            self._formatear_valor(0), size=16, weight=ft.FontWeight.BOLD,
            color=paleta["verde"], max_lines=1, overflow=ft.TextOverflow.ELLIPSIS
        )
        self.lbl_kpi_cruce = ft.Text(
            "N/A", size=16, weight=ft.FontWeight.BOLD,
            color=paleta["primario"], max_lines=1, overflow=ft.TextOverflow.ELLIPSIS
        )

        # Tabla de amortizacion
        self.col_tabla = ft.DataTable(
            columns=self._crear_columnas_tabla(),
            rows=[],
            bgcolor=paleta["campo"],
            border=ft.Border.all(0, paleta["borde"]),
            border_radius=12,
            heading_row_color=paleta["seleccion"],
            heading_row_height=48,
            heading_text_style=ft.TextStyle(
                color=self._color_encabezado_tabla(), weight=ft.FontWeight.BOLD,
                size=12, font_family=FUENTE_APP
            ),
            data_text_style=ft.TextStyle(
                color=paleta["texto_claro"], size=13, font_family=FUENTE_APP
            ),
            data_row_min_height=42,
            data_row_max_height=50,
            divider_thickness=0.6,
            horizontal_lines=ft.BorderSide(0.6, paleta["borde"]),
            column_spacing=32,
            horizontal_margin=20,
        )
        self.fila_tabla = ft.Row(
            controls=[self.col_tabla],
            scroll=ft.ScrollMode.AUTO,
        )
        self.contenedor_tabla = ft.ListView(
            controls=[self.fila_tabla],
            expand=True,
            spacing=0,
            padding=ft.Padding.only(bottom=6),
        )

        # Grafica y estado vacio
        self.img_grafica = ft.Image(src="", fit=ft.BoxFit.CONTAIN, expand=True)
        self.texto_grafica_vacia = ft.Text(
            "Calcula un préstamo para ver la evolución de tu saldo.",
            italic=True, color=paleta["texto_suave"], size=13, font_family=FUENTE_APP
        )
        self.stack_grafica = ft.Stack(
            controls=[
                self.img_grafica,
                ft.Container(
                    content=self.texto_grafica_vacia,
                    alignment=ft.Alignment.CENTER,
                    expand=True,
                ),
            ],
            expand=True,
        )

        # Controles de IA
        self.txt_pregunta_ia = self._crear_campo(
            "Consulta al asesor financiero IA",
            "",
        )
        self.txt_pregunta_ia.hint_text = "Pregunta sobre tu tabla o los archivos exportados..."
        self.txt_pregunta_ia.on_submit = self._evento_consultar_ia
        self.txt_pregunta_ia.expand = True
        self.btn_enviar_ia = ft.IconButton(
            icon=ft.Icons.SEND_ROUNDED,
            on_click=self._evento_consultar_ia,
            tooltip="Enviar consulta",
            icon_color=self._color_contraste(),
            style=ft.ButtonStyle(
                bgcolor=paleta["primario"],
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
        )
        # Controles de IA reutilizados dentro del apartado Planes
        self.txt_pregunta_ia_plan = self._crear_campo(
            "Consulta sobre tu plan financiero", ""
        )
        self.txt_pregunta_ia_plan.hint_text = "Pregunta por tus ingresos, gastos, crédito o montos fijos..."
        self.txt_pregunta_ia_plan.on_submit = self._evento_consultar_ia_plan
        self.txt_pregunta_ia_plan.expand = True
        self.btn_enviar_ia_plan = ft.IconButton(
            icon=ft.Icons.SEND_ROUNDED,
            on_click=self._evento_consultar_ia_plan,
            tooltip="Enviar consulta sobre el plan",
            icon_color=self._color_contraste(),
            style=ft.ButtonStyle(
                bgcolor=paleta["primario"],
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
        )
        self.lista_chat = ft.ListView(
            controls=[],
            expand=True,
            spacing=10,
            padding=ft.Padding.only(right=4, bottom=4),
        )
        self.lista_chat_plan = ft.ListView(
            controls=[],
            expand=True,
            spacing=10,
            padding=ft.Padding.only(right=4, bottom=4),
        )

        # Controles especificos de la pestana Comparativa de tablas
        def _crear_columnas_comp() -> list[ft.DataColumn]:
            estilo_comp = ft.TextStyle(
                color=self._color_encabezado_tabla(), size=11, weight=ft.FontWeight.BOLD, font_family=FUENTE_APP
            )
            return [
                ft.DataColumn(ft.Text("Mes", style=estilo_comp)),
                ft.DataColumn(ft.Text("Cuota", style=estilo_comp), numeric=True),
                ft.DataColumn(ft.Text("Interés", style=estilo_comp), numeric=True),
                ft.DataColumn(ft.Text("Capital", style=estilo_comp), numeric=True),
                ft.DataColumn(ft.Text("Saldo", style=estilo_comp), numeric=True),
            ]

        self.col_tabla_comp_a = ft.DataTable(
            columns=_crear_columnas_comp(),
            rows=[],
            bgcolor=paleta["campo"],
            border=ft.Border.all(0, paleta["borde"]),
            border_radius=10,
            heading_row_color=paleta["seleccion"],
            heading_row_height=38,
            data_row_min_height=34,
            data_row_max_height=40,
            column_spacing=18,
            horizontal_margin=12,
            horizontal_lines=ft.BorderSide(0.6, paleta["borde"]),
        )
        self.contenedor_tabla_comp_a = ft.ListView(
            controls=[ft.Row(controls=[self.col_tabla_comp_a], scroll=ft.ScrollMode.AUTO)],
            expand=True,
            spacing=0,
            padding=ft.Padding.only(bottom=4),
        )

        self.col_tabla_comp_b = ft.DataTable(
            columns=_crear_columnas_comp(),
            rows=[],
            bgcolor=paleta["campo"],
            border=ft.Border.all(0, paleta["borde"]),
            border_radius=10,
            heading_row_color=paleta["seleccion"],
            heading_row_height=38,
            data_row_min_height=34,
            data_row_max_height=40,
            column_spacing=18,
            horizontal_margin=12,
            horizontal_lines=ft.BorderSide(0.6, paleta["borde"]),
        )
        self.contenedor_tabla_comp_b = ft.ListView(
            controls=[ft.Row(controls=[self.col_tabla_comp_b], scroll=ft.ScrollMode.AUTO)],
            expand=True,
            spacing=0,
            padding=ft.Padding.only(bottom=4),
        )

        self.lbl_titulo_comp_a = ft.Text(
            "Escenario A: sin fijar", size=13, weight=ft.FontWeight.BOLD,
            color=paleta["secundario"], font_family=FUENTE_APP
        )
        self.lbl_resumen_comp_a = ft.Text(
            "Calcula y presiona 'Fijar actual como A'.", size=11,
            color=paleta["texto_suave"], font_family=FUENTE_APP
        )

        self.lbl_titulo_comp_b = ft.Text(
            "Escenario B: sin fijar", size=13, weight=ft.FontWeight.BOLD,
            color=paleta["primario"], font_family=FUENTE_APP
        )
        self.lbl_resumen_comp_b = ft.Text(
            "Calcula y presiona 'Fijar actual como B'.", size=11,
            color=paleta["texto_suave"], font_family=FUENTE_APP
        )

        self.lbl_diferencia_comp = ft.Text(
            "Fija dos escenarios para analizar diferencias de costo e intereses.",
            size=12, weight=ft.FontWeight.W_500, color=paleta["texto_claro"], font_family=FUENTE_APP
        )

        self.img_grafica_comp = ft.Image(src="", fit=ft.BoxFit.CONTAIN, expand=True)
        self.texto_grafica_comp_vacia = ft.Text(
            "No hay escenarios para comparar. Fija A y B primero.",
            italic=True, color=paleta["texto_suave"], size=13, font_family=FUENTE_APP
        )
        self.stack_grafica_comp = ft.Stack(
            controls=[
                self.img_grafica_comp,
                ft.Container(
                    content=self.texto_grafica_comp_vacia,
                    alignment=ft.Alignment.CENTER,
                    expand=True,
                ),
            ],
            expand=True,
        )
        self.contenedor_cuerpo_comp = ft.Container(expand=True)

        # Pestanas principales (ahora con 4 pestanas)
        self.pestanas = ft.Tabs(
            length=4,
            selected_index=self.indice_pestana,
            expand=True,
            on_change=self._evento_cambiar_pestana,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Tabla de amortización", icon=ft.Icons.TABLE_CHART_ROUNDED),
                            ft.Tab(label="Gráficas financieras", icon=ft.Icons.BAR_CHART_ROUNDED),
                            ft.Tab(label="Comparativa de tablas", icon=ft.Icons.COMPARE_ARROWS_ROUNDED),
                            ft.Tab(label="Asesor IA", icon=ft.Icons.AUTO_AWESOME_ROUNDED),
                        ],
                        indicator_color=paleta["secundario"],
                        label_color=paleta["secundario"],
                        unselected_label_color=self._color_texto_sobre_fondo(),
                        divider_color=paleta["borde"],
                        label_text_style=ft.TextStyle(
                            size=13, weight=ft.FontWeight.BOLD, font_family=FUENTE_APP
                        ),
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            self._crear_vista_tabla(),
                            self._crear_vista_grafica(),
                            self._crear_vista_comparar(),
                            self._crear_vista_chat(),
                        ]
                    )
                ]
            )
        )

    def _crear_columnas_tabla(self) -> list[ft.DataColumn]:
        """Crea los encabezados de la tabla de amortizacion."""
        color_encabezado = self._color_encabezado_tabla()
        estilo_encabezado = ft.TextStyle(
            color=color_encabezado, size=12, weight=ft.FontWeight.BOLD, font_family=FUENTE_APP
        )

        def _crear_columna(str_titulo: str, es_numerica: bool = False) -> ft.DataColumn:
            return ft.DataColumn(
                label=ft.Text(str_titulo, style=estilo_encabezado),
                numeric=es_numerica,
            )

        return [
            _crear_columna("Mes"),
            _crear_columna("Cuota", es_numerica=True),
            _crear_columna("Interés", es_numerica=True),
            _crear_columna("Capital", es_numerica=True),
            _crear_columna("Saldo", es_numerica=True),
        ]

    def _crear_tarjeta_kpi(self, str_titulo: str, obj_control_texto: ft.Text,
                           icono: str, color_acento: str) -> ft.Container:
        """Crea una tarjeta contenedora de una metrica clave."""
        return ft.Container(
            col={"xs": 12, "sm": 6, "md": 3},
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon(icono, size=22, color=color_acento),
                        width=42,
                        height=42,
                        bgcolor=ft.Colors.with_opacity(0.14, color_acento),
                        border_radius=12,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                str_titulo, size=11, color=self.paleta["texto_suave"],
                                font_family=FUENTE_APP
                            ),
                            obj_control_texto,
                        ],
                        spacing=2,
                        expand=True,
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=14,
            bgcolor=self.paleta["tarjeta"],
            border=ft.Border.all(1, self.paleta["borde"]),
            border_radius=14,
        )

    def _crear_vista_tabla(self) -> ft.Container:
        """Construye la pestana con la tabla de amortizacion y sus acciones."""
        paleta = self.paleta
        botones_accion = ft.Row(
            controls=[
                self._crear_boton_exportacion(
                    "Exportar Excel", ft.Icons.TABLE_VIEW, self._evento_exportar_excel, paleta["verde"]
                ),
                self._crear_boton_exportacion(
                    "Exportar PDF", ft.Icons.PICTURE_AS_PDF, self._evento_exportar_pdf, paleta["rojo"]
                ),
                self._crear_boton_exportacion(
                    "Guardar en historial", ft.Icons.BOOKMARK_ADD, self._evento_guardar_historial, paleta["primario"]
                ),
            ],
            spacing=10,
            wrap=True,
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Detalle mes a mes", size=16, weight=ft.FontWeight.BOLD,
                                        color=paleta["primario"], font_family=FUENTE_APP
                                    ),
                                    ft.Text(
                                        "Cuota, interés, capital y saldo restante de cada periodo.",
                                        size=11, color=paleta["texto_suave"], font_family=FUENTE_APP
                                    ),
                                ],
                                spacing=0,
                            ),
                        ]
                    ),
                    botones_accion,
                    ft.Container(
                        content=self.contenedor_tabla,
                        expand=True,
                        bgcolor=paleta["campo"],
                        border=ft.Border.all(1, paleta["borde"]),
                        border_radius=14,
                        padding=ft.Padding.only(left=10, right=10, bottom=10),
                    ),
                ],
                expand=True,
                spacing=12,
            ),
            padding=16,
            bgcolor=paleta["tarjeta"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=16,
            expand=True,
        )

    def _crear_vista_grafica(self) -> ft.Container:
        """Construye la pestana con la grafica financiera."""
        paleta = self.paleta
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Evolución del préstamo", size=16, weight=ft.FontWeight.BOLD,
                        color=paleta["primario"], font_family=FUENTE_APP
                    ),
                    ft.Text(
                        "Composición de la cuota y amortización del saldo.",
                        size=11, color=paleta["texto_suave"], font_family=FUENTE_APP
                    ),
                    ft.Container(
                        content=self.stack_grafica,
                        expand=True,
                        alignment=ft.Alignment.CENTER,
                        bgcolor=paleta["campo"],
                        border=ft.Border.all(1, paleta["borde"]),
                        border_radius=14,
                        padding=12,
                        on_click=self._evento_ampliar_grafica_amortizacion,
                    ),
                ],
                expand=True,
                spacing=12,
            ),
            padding=16,
            bgcolor=paleta["tarjeta"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=16,
            expand=True,
        )

    def _crear_vista_comparar(self) -> ft.Container:
        """Construye la pestana con la comparativa de escenarios A y B."""
        paleta = self.paleta

        # Botones de accion para fijar escenarios y exportar
        botones_acciones_comp = ft.Row(
            controls=[
                ft.FilledButton(
                    content=ft.Text("Fijar actual como A", font_family=FUENTE_APP, size=12, weight=ft.FontWeight.BOLD),
                    icon=ft.Icons.LOOKS_ONE_ROUNDED,
                    on_click=lambda _: self._fijar_escenario_comparar("A"),
                    style=ft.ButtonStyle(
                        bgcolor=paleta["secundario"],
                        color="#1E1E2E" if self.modo_tema == "oscuro" else "#FFFFFF",
                        icon_color="#1E1E2E" if self.modo_tema == "oscuro" else "#FFFFFF",
                        shape=ft.RoundedRectangleBorder(radius=9),
                    ),
                    height=38,
                ),
                ft.FilledButton(
                    content=ft.Text("Fijar actual como B", font_family=FUENTE_APP, size=12, weight=ft.FontWeight.BOLD),
                    icon=ft.Icons.LOOKS_TWO_ROUNDED,
                    on_click=lambda _: self._fijar_escenario_comparar("B"),
                    style=ft.ButtonStyle(
                        bgcolor=paleta["primario"],
                        color=self._color_contraste(),
                        icon_color=self._color_contraste(),
                        shape=ft.RoundedRectangleBorder(radius=9),
                    ),
                    height=38,
                ),
                self._crear_boton_exportacion(
                    "Limpiar", ft.Icons.CLEAR_ALL, self._limpiar_comparar, paleta["texto_suave"]
                ),
                self._crear_boton_exportacion(
                    "Exportar Excel", ft.Icons.TABLE_VIEW, self._evento_exportar_comparar_excel, paleta["verde"]
                ),
                self._crear_boton_exportacion(
                    "Exportar PDF", ft.Icons.PICTURE_AS_PDF, self._evento_exportar_comparar_pdf, paleta["rojo"]
                ),
            ],
            spacing=8,
            wrap=True,
        )

        self.btn_subvista_tablas = ft.OutlinedButton(
            content=ft.Text("Tablas paralelas", size=12, font_family=FUENTE_APP, weight=ft.FontWeight.BOLD),
            icon=ft.Icons.TABLE_ROWS_ROUNDED,
            on_click=lambda _: self._alternar_subvista_comparar("tablas"),
            style=ft.ButtonStyle(
                color=paleta["secundario"] if self.subvista_comparar_activa == "tablas" else paleta["texto_suave"],
                icon_color=paleta["secundario"] if self.subvista_comparar_activa == "tablas" else paleta["texto_suave"],
                side=ft.BorderSide(
                    1.5 if self.subvista_comparar_activa == "tablas" else 1,
                    paleta["secundario"] if self.subvista_comparar_activa == "tablas" else paleta["borde"]
                ),
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        self.btn_subvista_grafica = ft.OutlinedButton(
            content=ft.Text("Gráfica A vs B", size=12, font_family=FUENTE_APP, weight=ft.FontWeight.BOLD),
            icon=ft.Icons.ANALYTICS_ROUNDED,
            on_click=lambda _: self._alternar_subvista_comparar("grafica"),
            style=ft.ButtonStyle(
                color=paleta["primario"] if self.subvista_comparar_activa == "grafica" else paleta["texto_suave"],
                icon_color=paleta["primario"] if self.subvista_comparar_activa == "grafica" else paleta["texto_suave"],
                side=ft.BorderSide(
                    1.5 if self.subvista_comparar_activa == "grafica" else 1,
                    paleta["primario"] if self.subvista_comparar_activa == "grafica" else paleta["borde"]
                ),
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        barra_superior = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(
                            "Comparativa de dos cálculos", size=16, weight=ft.FontWeight.BOLD,
                            color=paleta["primario"], font_family=FUENTE_APP
                        ),
                        ft.Text(
                            "Calcula en el formulario y fija el escenario como A o B para contrastar amortizaciones.",
                            size=11, color=paleta["texto_suave"], font_family=FUENTE_APP
                        ),
                    ],
                    spacing=0,
                    expand=True,
                ),
                ft.Row(
                    controls=[self.btn_subvista_tablas, self.btn_subvista_grafica],
                    spacing=6,
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        banner_diferencias = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.AUTO_GRAPH_ROUNDED, size=20, color=paleta["secundario"]),
                    self.lbl_diferencia_comp,
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=paleta["campo"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
        )

        # Paneles lado a lado
        panel_a = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(
                                    "A", weight=ft.FontWeight.BOLD, size=11,
                                    color="#1E1E2E" if self.modo_tema == "oscuro" else "#FFFFFF"
                                ),
                                bgcolor=paleta["secundario"],
                                width=22, height=22, border_radius=11, alignment=ft.Alignment.CENTER,
                            ),
                            ft.Column(
                                controls=[
                                    self.lbl_titulo_comp_a,
                                    self.lbl_resumen_comp_a,
                                ],
                                spacing=0,
                                expand=True,
                            ),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=paleta["borde"]),
                    ft.Container(
                        content=self.contenedor_tabla_comp_a,
                        expand=True,
                        bgcolor=paleta["campo"],
                        border_radius=10,
                    ),
                ],
                expand=True,
                spacing=8,
            ),
            expand=True,
            bgcolor=paleta["campo"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=12,
            padding=10,
        )

        panel_b = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(
                                    "B", weight=ft.FontWeight.BOLD, size=11,
                                    color=self._color_contraste()
                                ),
                                bgcolor=paleta["primario"],
                                width=22, height=22, border_radius=11, alignment=ft.Alignment.CENTER,
                            ),
                            ft.Column(
                                controls=[
                                    self.lbl_titulo_comp_b,
                                    self.lbl_resumen_comp_b,
                                ],
                                spacing=0,
                                expand=True,
                            ),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=paleta["borde"]),
                    ft.Container(
                        content=self.contenedor_tabla_comp_b,
                        expand=True,
                        bgcolor=paleta["campo"],
                        border_radius=10,
                    ),
                ],
                expand=True,
                spacing=8,
            ),
            expand=True,
            bgcolor=paleta["campo"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=12,
            padding=10,
        )

        self.vista_tablas_paralelas = ft.Row(
            controls=[panel_a, panel_b],
            expand=True,
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        self.vista_grafica_comparar = ft.Container(
            content=self.stack_grafica_comp,
            expand=True,
            bgcolor=paleta["campo"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=12,
            padding=12,
            alignment=ft.Alignment.CENTER,
            on_click=self._evento_ampliar_grafica_comparativa,
        )

        self.contenedor_cuerpo_comp.content = (
            self.vista_tablas_paralelas if self.subvista_comparar_activa == "tablas" else self.vista_grafica_comparar
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    barra_superior,
                    botones_acciones_comp,
                    banner_diferencias,
                    self.contenedor_cuerpo_comp,
                ],
                expand=True,
                spacing=12,
            ),
            padding=16,
            bgcolor=paleta["tarjeta"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=16,
            expand=True,
        )

    def _crear_vista_chat(self) -> ft.Container:
        """Construye la pestana del asesor financiero IA."""
        paleta = self.paleta
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Asesor financiero IA", size=16, weight=ft.FontWeight.BOLD,
                                        color=paleta["primario"], font_family=FUENTE_APP
                                    ),
                                    ft.Text(
                                        "Interpreta tus resultados; el cálculo siempre lo hace el motor C++.",
                                        size=11, color=paleta["texto_suave"], font_family=FUENTE_APP
                                    ),
                                ],
                                spacing=0,
                            ),
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.FilledTonalButton(
                                content=ft.Text("Explicar tabla", font_family=FUENTE_APP),
                                icon=ft.Icons.LIGHTBULB_OUTLINE,
                                on_click=self._evento_explicar_ia,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.with_opacity(0.14, paleta["primario"]),
                                    color=paleta["texto_claro"],
                                    icon_color=paleta["primario"],
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                ),
                            ),
                            ft.FilledTonalButton(
                                content=ft.Text("Comparar 3 sistemas", font_family=FUENTE_APP),
                                icon=ft.Icons.COMPARE_ARROWS,
                                on_click=self._evento_comparar_sistemas_ia,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.with_opacity(0.14, paleta["secundario"]),
                                    color=paleta["texto_claro"],
                                    icon_color=paleta["secundario"],
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                ),
                            ),
                        ],
                        spacing=10,
                        wrap=True,
                    ),
                    ft.Container(
                        content=self.lista_chat,
                        expand=True,
                        bgcolor=paleta["campo"],
                        border=ft.Border.all(1, paleta["borde"]),
                        border_radius=14,
                        padding=12,
                    ),
                    ft.Row(
                        controls=[self.txt_pregunta_ia, self.btn_enviar_ia],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                expand=True,
                spacing=12,
            ),
            padding=16,
            bgcolor=paleta["tarjeta"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=16,
            expand=True,
        )

    def _construir_interfaz(self):
        """Ensambla el arbol de componentes en la pagina principal."""
        paleta = self.paleta
        self.pagina.controls.clear()
        self.pagina.appbar = None

        # Encabezado con logo institucional y acciones globales.
        encabezado = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Image(
                        src=self.src_logo,
                        height=48,
                        fit=ft.BoxFit.CONTAIN,
                        border_radius=10,
                    ) if self.src_logo else ft.Icon(
                        ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, size=36, color=paleta["primario"]
                    ),
                    ft.Container(width=2, height=44, bgcolor=paleta["borde"]),
                    ft.Column(
                        controls=[
                            ft.Text(
                                "Simulador de Intereses y Amortizaciones",
                                size=20, weight=ft.FontWeight.BOLD,
                                color=paleta["secundario"], font_family=FUENTE_APP,
                                max_lines=1, overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                "Compara sistemas, visualiza tus saldos y entiende cuánto pagas.",
                                size=11, color=self._color_texto_sobre_fondo(), font_family=FUENTE_APP,
                                max_lines=1, overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        spacing=0,
                        expand=True,
                    ),
                    # Botones eliminados: ahora están en la barra lateral izquierda.
                ],
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=paleta["fondo"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=16,
            padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        )

        # Tarjeta para abonos y adelantos extraordinarios a capital
        tarjeta_adelantos = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.PAYMENTS_ROUNDED, size=15, color=paleta["primario"]),
                            ft.Text(
                                "Adelanto o bono a capital",
                                size=12, weight=ft.FontWeight.BOLD,
                                color=paleta["primario"], font_family=FUENTE_APP,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_SWEEP_ROUNDED,
                                icon_size=16,
                                icon_color=paleta["texto_suave"],
                                tooltip="Limpiar todos los adelantos",
                                on_click=self._evento_limpiar_abonos,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    ft.Text(
                        "Pagos directos a capital para reducir intereses y plazo.",
                        size=10, color=paleta["texto_suave"], font_family=FUENTE_APP,
                    ),
                    ft.Row(
                        controls=[
                            self.txt_abono_mes,
                            self.txt_abono_monto,
                        ],
                        spacing=6,
                    ),
                    ft.FilledTonalButton(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.ADD, size=15, color=paleta["primario"]),
                                ft.Text(
                                    "Agregar adelanto", size=12,
                                    weight=ft.FontWeight.BOLD, color=paleta["primario"],
                                    font_family=FUENTE_APP
                                ),
                            ],
                            spacing=4,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        on_click=self._evento_agregar_abono,
                        height=36,
                    ),
                    self.col_lista_abonos,
                    self.contenedor_ahorro_abonos,
                ],
                spacing=8,
            ),
            bgcolor=ft.Colors.with_opacity(0.04, paleta["primario"]),
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=12,
            padding=10,
        )

        # Panel izquierdo con el formulario.
        panel_formulario = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.TUNE, size=18, color=paleta["primario"]),
                            ft.Text(
                                "Parámetros del crédito", size=15, weight=ft.FontWeight.BOLD,
                                color=paleta["primario"], font_family=FUENTE_APP
                            ),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Text(
                        "Define el monto, la tasa y el plazo para calcular tu tabla.",
                        size=11, color=paleta["texto_suave"], font_family=FUENTE_APP,
                    ),
                    ft.Divider(height=1, color=paleta["borde"]),
                    self.dd_sistema,
                    self.txt_monto,
                    self.txt_tasa,
                    self.txt_plazo,
                    tarjeta_adelantos,
                    ft.Container(height=4),
                    self.btn_calcular,
                    self.btn_limpiar,
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.CODE, size=14, color=paleta["texto_suave"]),
                                ft.Text(
                                    "Cálculo procesado por el motor C++",
                                    size=10, color=paleta["texto_suave"], font_family=FUENTE_APP,
                                ),
                            ],
                            spacing=6,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        bgcolor=ft.Colors.with_opacity(0.07, paleta["texto_claro"]),
                        border_radius=9,
                        padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                    ),
                ],
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=18,
            width=330,
            bgcolor=paleta["tarjeta"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=18,
        )

        # Fila de indicadores clave.
        fila_kpis = ft.ResponsiveRow(
            controls=[
                self._crear_tarjeta_kpi(
                    "Cuota mensual", self.lbl_kpi_cuota, ft.Icons.PAYMENTS_ROUNDED, paleta["secundario"]
                ),
                self._crear_tarjeta_kpi(
                    "Intereses totales", self.lbl_kpi_interes, ft.Icons.TRENDING_UP_ROUNDED, paleta["rojo"]
                ),
                self._crear_tarjeta_kpi(
                    "Total a pagar", self.lbl_kpi_total, ft.Icons.SAVINGS_ROUNDED, paleta["verde"]
                ),
                self._crear_tarjeta_kpi(
                    "Cruce capital/interés", self.lbl_kpi_cruce, ft.Icons.SWAP_VERT_ROUNDED, paleta["primario"]
                ),
            ],
            spacing=12,
            run_spacing=12,
        )

        contenido_derecho = ft.Column(
            controls=[fila_kpis, self.pestanas],
            expand=True,
            spacing=14,
        )

        # Contenido principal: inicio, tablas, planes o historial según la vista activa
        if self.vista_activa == "historial":
            contenido_principal = self._crear_vista_historial()
        elif self.vista_activa == "planes":
            contenido_principal = self._crear_vista_planes()
        elif self.vista_activa == "inicio":
            contenido_principal = self._crear_vista_inicio()
        else:
            contenido_principal = ft.Row(
                controls=[panel_formulario, contenido_derecho],
                expand=True,
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            )

        barra_nav = self._crear_barra_navegacion()

        layout_completo = ft.Row(
            controls=[barra_nav, contenido_principal],
            expand=True,
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        self.pagina.add(
            ft.Column(
                controls=[encabezado, layout_completo],
                expand=True,
                spacing=14,
            )
        )

    # ==========================================
    # Renderizado de Datos
    # ==========================================

    def _crear_fila_tabla(self, fila: dict, indice: int) -> ft.DataRow:
        """Crea una fila con color alternado y acentos por tipo de importe."""
        paleta = self.paleta
        color_fondo = paleta["tarjeta"] if indice % 2 == 0 else paleta["campo"]
        estilo_numero = dict(size=13, font_family=FUENTE_APP)

        return ft.DataRow(
            color=color_fondo,
            cells=[
                ft.DataCell(ft.Text(str(fila["mes"]), color=paleta["texto_suave"], **estilo_numero)),
                ft.DataCell(ft.Text(
                    self._formatear_valor(fila["cuota"]), color=paleta["texto_claro"],
                    weight=ft.FontWeight.W_600, **estilo_numero
                )),
                ft.DataCell(ft.Text(self._formatear_valor(fila["interes"]), color=paleta["rojo"], **estilo_numero)),
                ft.DataCell(ft.Text(self._formatear_valor(fila["capital"]), color=paleta["verde"], **estilo_numero)),
                ft.DataCell(ft.Text(self._formatear_valor(fila["saldo"]), color=paleta["texto_claro"], **estilo_numero)),
            ],
        )

    def _actualizar_resultados(self):
        """Refresca KPIs, tabla y grafica con la simulacion activa."""
        if not self.tabla_actual or not self.parametros_actuales:
            return

        paleta = self.paleta
        indicadores = calcular_indicadores(
            self.tabla_actual, self.parametros_actuales.get("tasa_anual", 0)
        )

        if self.parametros_actuales.get("sistema") == "Frances":
            self.lbl_kpi_cuota.value = self._formatear_valor(self.tabla_actual[0]["cuota"])
        else:
            cuota_min = self._formatear_valor(indicadores["cuota_min"])
            cuota_max = self._formatear_valor(indicadores["cuota_max"])
            self.lbl_kpi_cuota.value = f"{cuota_min} - {cuota_max}"

        self.lbl_kpi_interes.value = self._formatear_valor(indicadores["total_interes"])
        self.lbl_kpi_total.value = self._formatear_valor(indicadores["total_pagado"])
        self.lbl_kpi_cruce.value = (
            f"Mes {indicadores['mes_cruce']}" if indicadores["mes_cruce"] > 0 else "N/A"
        )

        self.col_tabla.rows = [
            self._crear_fila_tabla(fila, indice)
            for indice, fila in enumerate(self.tabla_actual)
        ]
        self.img_grafica.src = generar_grafica_amortizacion(
            self.tabla_actual, modo_oscuro=self.modo_tema == "oscuro"
        )
        self.texto_grafica_vacia.visible = False
        self.lbl_kpi_cuota.color = self._color_cuota()

    def _renderizar_tabla_vacia(self):
        """Deja la tabla sin filas y restaura el estado vacio de la grafica."""
        self.col_tabla.rows.clear()
        self.img_grafica.src = ""
        self.texto_grafica_vacia.visible = True

    def _renderizar_chat(self):
        """Dibuja la conversacion del asesor IA y del chat de planes con el estilo del tema."""
        if not self.mensajes_chat:
            self.mensajes_chat.append({"rol": "ia", "texto": TEXTO_BIENVENIDA})
        self.lista_chat.controls = [
            self._crear_mensaje_chat(mensaje) for mensaje in self.mensajes_chat
        ]
        if not self.mensajes_chat_plan:
            self.mensajes_chat_plan.append({
                "rol": "ia",
                "texto": (
                    "**Hola, soy tu asesor del plan financiero.**\n\n"
                    "Puedo analizar tus ingresos, egresos, montos fijos y créditos mes por mes."
                ),
            })
        self.lista_chat_plan.controls = [
            self._crear_mensaje_chat(mensaje) for mensaje in self.mensajes_chat_plan
        ]

    def _crear_mensaje_chat(self, mensaje: dict) -> ft.Control:
        """Crea la burbuja visual de un mensaje del chat."""
        paleta = self.paleta
        rol = mensaje.get("rol", "ia")
        texto = mensaje.get("texto", "")

        if rol == "sistema":
            return ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=14, color=paleta["texto_suave"]),
                        ft.Text(
                            texto, italic=True, size=12, color=paleta["texto_suave"],
                            font_family=FUENTE_APP, expand=True,
                        ),
                    ],
                    spacing=6,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                bgcolor=ft.Colors.with_opacity(0.06, paleta["texto_claro"]),
                border_radius=10,
            )

        es_usuario = rol == "usuario"
        color_rol = paleta["secundario"] if es_usuario else paleta["primario"]
        etiqueta = "Tú" if es_usuario else "Asesor IA"
        icono = ft.Icons.PERSON if es_usuario else ft.Icons.AUTO_AWESOME
        color_fondo = paleta["seleccion"] if es_usuario else paleta["tarjeta"]

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(icono, size=14, color=color_rol),
                            ft.Text(
                                etiqueta, size=10, weight=ft.FontWeight.BOLD,
                                color=color_rol, font_family=FUENTE_APP
                            ),
                        ],
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Markdown(
                        texto,
                        selectable=True,
                        md_style_sheet=self._estilo_markdown(),
                    ),
                ],
                spacing=6,
                tight=True,
            ),
            padding=12,
            bgcolor=color_fondo,
            border=ft.Border(left=ft.BorderSide(3, color_rol)),
            border_radius=12,
        )

    # ==========================================
    # Manejadores de Eventos
    # ==========================================

    def _leer_valores_formulario(self) -> dict:
        """Captura los valores actuales del formulario para conservarlos."""
        borrador_plan = dict(getattr(self, "borrador_plan", {}) or {})
        if hasattr(self, "txt_plan_nombre"):
            borrador_plan.update({
                "nombre": self.txt_plan_nombre.value or "",
                "duracion_meses": self.txt_plan_duracion.value or "12",
                "concepto_ingreso": self.txt_plan_ingreso_concepto.value or "",
                "monto_ingreso": self.txt_plan_ingreso_monto.value or "",
                "concepto_gasto": self.txt_plan_gasto_concepto.value or "",
                "monto_gasto": self.txt_plan_gasto_monto.value or "",
                "concepto_credito": self.txt_plan_credito_concepto.value or "",
                "monto_credito": self.txt_plan_credito_monto.value or "",
                "tasa_credito": self.txt_plan_credito_tasa.value or "",
                "plazo_credito": self.txt_plan_credito_plazo.value or "",
                "sistema_credito": self.dd_plan_credito_sistema.value or "Frances",
            })
        return {
            "sistema": self.dd_sistema.value or "Frances",
            "monto": self.txt_monto.value or "10000.00",
            "tasa": self.txt_tasa.value or "12.0",
            "plazo": self.txt_plazo.value or "12",
            "abonos": [dict(a) for a in self.lista_abonos],
            "borrador_plan": borrador_plan,
        }

    def _evento_cambiar_pestana(self, evento):
        """Guarda la pestana seleccionada para conservarla al cambiar de tema."""
        self.indice_pestana = evento.control.selected_index

    def _evento_agregar_abono(self, _):
        """Registra un nuevo adelanto extraordinario directo a capital."""
        str_mes = (self.txt_abono_mes.value or "").strip()
        str_monto = (self.txt_abono_monto.value or "").strip().replace(",", "")
        if not str_mes or not str_monto:
            self._mostrar_mensaje("Ingresa el mes y el monto del adelanto.", es_error=True)
            return

        try:
            num_mes = int(str_mes)
            val_monto = float(str_monto)
        except ValueError:
            self._mostrar_mensaje("El mes debe ser un número entero y el monto un valor válido.", es_error=True)
            return

        if num_mes < 1:
            self._mostrar_mensaje("El mes del adelanto debe ser mayor o igual a 1.", es_error=True)
            return
        if val_monto <= 0:
            self._mostrar_mensaje("El monto del adelanto debe ser mayor a cero.", es_error=True)
            return

        try:
            plazo_max = int(self.txt_plazo.value)
            if num_mes > plazo_max:
                self._mostrar_mensaje(f"El mes {num_mes} supera el plazo actual de {plazo_max} meses.", es_error=True)
                return
        except ValueError:
            pass

        abono_existente = next((a for a in self.lista_abonos if a["mes"] == num_mes), None)
        if abono_existente:
            abono_existente["monto"] += val_monto
            self._mostrar_mensaje(f"Se sumó al adelanto existente del mes {num_mes}.")
        else:
            self.lista_abonos.append({"mes": num_mes, "monto": val_monto})
            self.lista_abonos.sort(key=lambda a: a["mes"])
            self._mostrar_mensaje(f"Adelanto de {self._formatear_valor(val_monto)} en mes {num_mes} agregado.")

        self.txt_abono_mes.value = ""
        self.txt_abono_monto.value = ""
        self._refrescar_lista_abonos()
        self.pagina.update()

    def _evento_quitar_abono(self, num_mes: int):
        """Elimina el abono del mes especificado."""
        self.lista_abonos = [a for a in self.lista_abonos if a["mes"] != num_mes]
        self._refrescar_lista_abonos()
        self.pagina.update()
        self._mostrar_mensaje(f"Adelanto del mes {num_mes} eliminado.")

    def _evento_limpiar_abonos(self, _):
        """Elimina todos los abonos extraordinarios."""
        if not self.lista_abonos:
            return
        self.lista_abonos.clear()
        self.contenedor_ahorro_abonos.visible = False
        self._refrescar_lista_abonos()
        self.pagina.update()
        self._mostrar_mensaje("Todos los adelantos fueron removidos.")

    def _refrescar_lista_abonos(self):
        """Dibuja en pantalla los chips de los abonos registrados."""
        paleta = self.paleta
        self.col_lista_abonos.controls.clear()
        if not self.lista_abonos:
            self.col_lista_abonos.controls.append(
                ft.Text("Sin adelantos registrados.", size=11, color=paleta["texto_suave"],
                        italic=True, font_family=FUENTE_APP)
            )
            return

        for abono in self.lista_abonos:
            mes = abono["mes"]
            monto = abono["monto"]
            fila_abono = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.SAVINGS_ROUNDED, size=14, color=paleta["secundario"]),
                        ft.Text(
                            f"Mes {mes}: {self._formatear_valor(monto)}",
                            size=11, weight=ft.FontWeight.W_500, color=paleta["texto_claro"],
                            font_family=FUENTE_APP, expand=True,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE_ROUNDED,
                            icon_size=14,
                            icon_color=paleta["rojo"],
                            tooltip="Quitar adelanto",
                            on_click=lambda _e, m=mes: self._evento_quitar_abono(m),
                        ),
                    ],
                    spacing=4,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=paleta["campo"],
                border=ft.Border.all(1, paleta["borde"]),
                border_radius=8,
                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
            )
            self.col_lista_abonos.controls.append(fila_abono)

    def _evento_calcular(self, _):
        """Valida entradas y delega el cálculo al binario compilado de C++."""
        try:
            val_monto = float(self.txt_monto.value.replace(",", ""))
            val_tasa = float(self.txt_tasa.value.replace(",", ""))
            num_meses = int(self.txt_plazo.value)
            str_sistema = str(self.dd_sistema.value)

            if val_monto <= 0 or val_tasa <= 0 or num_meses <= 0:
                self._mostrar_mensaje("Error: Monto, tasa y plazo deben ser mayores a cero.", es_error=True)
                return

            hay_abonos = len(self.lista_abonos) > 0
            lista_base = ejecutar_calculo_cpp(str_sistema, val_monto, val_tasa, num_meses)

            if hay_abonos:
                abonos_validos = [a for a in self.lista_abonos if 1 <= int(a["mes"]) <= num_meses]
                if not abonos_validos:
                    self._mostrar_mensaje("Los adelantos deben corresponder a meses dentro del plazo.", es_error=True)
                    return
                self.tabla_actual = ejecutar_calculo_cpp(str_sistema, val_monto, val_tasa, num_meses, abonos_validos)
            else:
                self.tabla_actual = lista_base

            self.parametros_actuales = {
                "sistema": str_sistema,
                "monto": val_monto,
                "tasa_anual": val_tasa,
                "meses": num_meses,
                "abonos": [dict(a) for a in self.lista_abonos],
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            self._actualizar_resultados()

            if hay_abonos:
                total_base = sum(f["cuota"] for f in lista_base)
                interes_base = sum(f["interes"] for f in lista_base)
                total_abono = sum(f["cuota"] for f in self.tabla_actual)
                interes_abono = sum(f["interes"] for f in self.tabla_actual)
                ahorro_interes = max(0.0, interes_base - interes_abono)
                meses_ahorrados = max(0, len(lista_base) - len(self.tabla_actual))
                texto_meses = f" y {meses_ahorrados} meses menos" if meses_ahorrados > 0 else ""
                self.lbl_ahorro_abonos.value = f"Ahorro: {self._formatear_valor(ahorro_interes)} en intereses{texto_meses}."
                self.contenedor_ahorro_abonos.visible = True

                # Preconfigurar comparativa A (base sin adelantos) vs B (con adelantos)
                self.lista_tabla_a = list(lista_base)
                self.dict_params_a = {
                    "sistema": str_sistema, "monto": val_monto, "tasa_anual": val_tasa,
                    "meses": num_meses, "abonos": [], "etiqueta": f"{str_sistema} (Sin adelanto)"
                }
                self.lista_tabla_b = list(self.tabla_actual)
                self.dict_params_b = {
                    "sistema": str_sistema, "monto": val_monto, "tasa_anual": val_tasa,
                    "meses": num_meses, "abonos": [dict(a) for a in self.lista_abonos],
                    "etiqueta": f"{str_sistema} (Con adelanto)"
                }
                self._actualizar_vista_comparar()
            else:
                self.lbl_ahorro_abonos.value = ""
                self.contenedor_ahorro_abonos.visible = False

            self.pestanas.selected_index = 0
            self.indice_pestana = 0
            self.pagina.update()
            self._mostrar_mensaje("Cálculo realizado con éxito mediante el núcleo en C++.")

        except Exception as error:
            self._mostrar_mensaje(f"Fallo en el cálculo: {error}", es_error=True)

    def _evento_limpiar(self, _):
        """Restablece los campos de entrada y limpia la tabla calculada."""
        self.txt_monto.value = "10000.00"
        self.txt_tasa.value = "12.0"
        self.txt_plazo.value = "12"
        self.dd_sistema.value = "Frances"
        self.lista_abonos.clear()
        self.txt_abono_mes.value = ""
        self.txt_abono_monto.value = ""
        self._refrescar_lista_abonos()
        self.lbl_ahorro_abonos.value = ""
        self.contenedor_ahorro_abonos.visible = False
        self.tabla_actual = []
        self.parametros_actuales = {}
        self._renderizar_tabla_vacia()
        self.lbl_kpi_cuota.value = self._formatear_valor(0)
        self.lbl_kpi_interes.value = self._formatear_valor(0)
        self.lbl_kpi_total.value = self._formatear_valor(0)
        self.lbl_kpi_cruce.value = "N/A"
        self.pestanas.selected_index = 0
        self.indice_pestana = 0
        self.pagina.update()

    def _evento_alternar_tema(self, _):
        """Cambia entre tema claro y oscuro conservando los datos capturados."""
        nuevo_tema = "claro" if self.modo_tema == "oscuro" else "oscuro"
        self._aplicar_tema(nuevo_tema)

    def _aplicar_tema(self, nuevo_tema: str):
        """Aplica el tema seleccionado (oscuro o claro) reconstruyendo la vista."""
        valores = self._leer_valores_formulario()
        indice_pestana = self.indice_pestana

        self.modo_tema = nuevo_tema
        self.dict_config["tema"] = self.modo_tema
        self.paleta = obtener_paleta(self.modo_tema)
        guardar_configuracion(self.dict_config)

        self._configurar_ventana()
        self.indice_pestana = indice_pestana
        self._inicializar_controles(valores)
        self._cargar_historial()
        self._cargar_planes()
        self._construir_interfaz()
        self._renderizar_chat()

        if self.tabla_actual and self.parametros_actuales:
            self._actualizar_resultados()
        else:
            self._renderizar_tabla_vacia()

        self._actualizar_vista_comparar()
        self.pagina.update()

    def _ruta_exportacion(self) -> str:
        """Devuelve la carpeta configurada para exportar, o el directorio actual."""
        ruta_configurada = str(self.dict_config.get("carpeta_exportacion", "") or "").strip()
        if ruta_configurada and os.path.isdir(ruta_configurada):
            return ruta_configurada
        return os.getcwd()

    def _ejecutar_exportacion_tabla(self, str_formato: str, cad_opinion_ia: str | None = None) -> str:
        """Escribe el archivo Excel o PDF de la tabla activa y retorna su ruta."""
        ruta_carpeta = self._ruta_exportacion()
        if str_formato == "excel":
            nombre_archivo = f"amortizacion_{self.parametros_actuales['sistema'].lower()}.xlsx"
            ruta_destino = os.path.join(ruta_carpeta, nombre_archivo)
            return exportar_tabla_excel(
                self.tabla_actual, self.parametros_actuales, ruta_destino,
                int(self.dict_config.get("num_decimales", 2)),
                self.dict_config.get("simbolo_moneda", "$"),
                cad_opinion_ia=cad_opinion_ia,
            )

        nombre_archivo = f"amortizacion_{self.parametros_actuales['sistema'].lower()}.pdf"
        ruta_destino = os.path.join(ruta_carpeta, nombre_archivo)
        establecer_fuentes_pdf(self.dict_config.get("fuente_pdf", "Segoe UI"))
        establecer_colores_personalizados(self.dict_config, self.modo_tema)
        try:
            return exportar_tabla_pdf(
                self.tabla_actual, self.parametros_actuales, ruta_destino,
                num_decimales=int(self.dict_config.get("decimales_pdf", 2)),
                simbolo_moneda=self.dict_config.get("simbolo_moneda", "$"),
                incluir_logo=bool(self.dict_config.get("incluir_logo_pdf", True)),
                incluir_pie=bool(self.dict_config.get("incluir_pie_pdf", True)),
                cad_opinion_ia=cad_opinion_ia,
            )
        finally:
            establecer_colores_personalizados(self.dict_config, self.modo_tema)

    def _exportar_tabla_con_resumen(self, str_formato: str):
        """Exporta la tabla a Excel o PDF resumiendo automáticamente el chat IA si existe."""
        if not self.tabla_actual:
            self._mostrar_mensaje("Debes calcular un préstamo antes de exportar.", es_error=True)
            return

        mensajes_reales = [
            m for m in self.mensajes_chat
            if m.get("rol") in ("usuario", "ia") and m.get("texto") != TEXTO_BIENVENIDA
        ]
        if not mensajes_reales:
            try:
                ruta_destino = self._ejecutar_exportacion_tabla(str_formato, None)
                self._mostrar_mensaje(f"Archivo {str_formato.upper()} exportado con éxito en: {ruta_destino}")
            except Exception as error:
                self._mostrar_mensaje(f"Error al exportar {str_formato.upper()}: {error}", es_error=True)
            return

        if self.ia_ocupada:
            self._mostrar_mensaje("Ya hay una consulta de IA en curso, espera un momento.")
            return

        self.ia_ocupada = True
        self._mostrar_mensaje(f"Resumiendo conversación del chat y exportando a {str_formato.upper()}...")
        copia_mensajes = list(mensajes_reales)

        def _trabajar():
            resumen = None
            aviso_ia = ""
            try:
                resumen = resumir_chat_ia(copia_mensajes)
                self.ultimo_resumen_chat = resumen
            except Exception as error_ia:
                aviso_ia = f" (sin resumen IA: {error_ia})"
            try:
                ruta_destino = self._ejecutar_exportacion_tabla(str_formato, resumen)
                self._mostrar_mensaje(f"Archivo {str_formato.upper()} exportado en: {ruta_destino}{aviso_ia}")
            except Exception as error:
                self._mostrar_mensaje(f"Error al exportar {str_formato.upper()}: {error}", es_error=True)
            finally:
                self.ia_ocupada = False

        self.pagina.run_thread(_trabajar)

    def _evento_exportar_excel(self, _):
        """Exporta la tabla activa a un archivo Excel (.xlsx) incluyendo resumen del chat."""
        self._exportar_tabla_con_resumen("excel")

    def _evento_exportar_pdf(self, _):
        """Exporta la tabla activa a un archivo PDF incluyendo resumen del chat."""
        self._exportar_tabla_con_resumen("pdf")

    def _evento_guardar_historial(self, _):
        """Almacena la simulación activa en historial.json y actualiza self.lista_historial."""
        if not self.tabla_actual:
            self._mostrar_mensaje("No hay simulación para guardar.", es_error=True)
            return
        try:
            nuevo_registro = {
                "parametros": self.parametros_actuales,
                "indicadores": calcular_indicadores(
                    self.tabla_actual, self.parametros_actuales["tasa_anual"]
                ),
            }
            self.lista_historial.insert(0, nuevo_registro)
            self.lista_historial = self.lista_historial[:MAX_REGISTROS_HISTORIAL]
            self._guardar_historial_a_disco()
            self._mostrar_mensaje("Simulación guardada en el historial.")
        except Exception as error:
            self._mostrar_mensaje(f"Error al guardar historial: {error}", es_error=True)

    def _agregar_mensaje(self, str_rol: str, str_texto: str, es_plan: bool = False):
        """Agrega un mensaje al chat correspondiente y refresca su vista."""
        lista_destino = self.mensajes_chat_plan if es_plan else self.mensajes_chat
        lista_destino.append({"rol": str_rol, "texto": str_texto})
        self._renderizar_chat()
        self.pagina.update()

    def _ejecutar_tarea_ia(self, funcion_ia, titulo_respuesta: str, es_plan: bool = False):
        """Ejecuta una consulta de IA en segundo plano sin congelar la interfaz."""
        self.ia_ocupada = True
        lista_destino = self.mensajes_chat_plan if es_plan else self.mensajes_chat

        def _trabajar():
            try:
                respuesta = funcion_ia()
                lista_destino[-1] = {
                    "rol": "ia",
                    "texto": f"**{titulo_respuesta}:**\n\n{respuesta}",
                }
            except Exception as error:
                lista_destino[-1] = {
                    "rol": "sistema",
                    "texto": f"Error de IA: {error}",
                }
            finally:
                self.ia_ocupada = False
                self._renderizar_chat()
                self.pagina.update()

        self.pagina.run_thread(_trabajar)

    def _evento_explicar_ia(self, _):
        """Solicita al asesor de IA un desglose explicativo de la tabla."""
        if not self.tabla_actual:
            self._mostrar_mensaje("Primero calcula una amortización.", es_error=True)
            return
        if self.ia_ocupada:
            self._mostrar_mensaje("Ya hay una consulta de IA en curso, espera un momento.")
            return
        self._agregar_mensaje("sistema", "Consultando a Gemini...")
        resumen_ia = dict(self.parametros_actuales)
        resumen_ia["plazo"] = self.parametros_actuales.get("meses", 0)
        resumen_ia["tasa"] = self.parametros_actuales.get("tasa_anual", 0)
        indicadores = calcular_indicadores(
            self.tabla_actual, self.parametros_actuales.get("tasa_anual", 0)
        )
        resumen_ia.update({
            "total_intereses": indicadores["total_interes"],
            "pago_total": indicadores["total_pagado"],
            "cat": f"{indicadores['tasa_efectiva_anual']:.2f}",
        })
        tabla_copia = list(self.tabla_actual)
        self._ejecutar_tarea_ia(
            lambda: explicar_tabla_amortizacion(resumen_ia, tabla_copia),
            "Análisis de la amortización",
        )

    def _evento_comparar_sistemas_ia(self, _):
        """Compara los tres sistemas de amortización con IA."""
        if not self.parametros_actuales:
            self._mostrar_mensaje("Primero calcula una amortización.", es_error=True)
            return
        if self.ia_ocupada:
            self._mostrar_mensaje("Ya hay una consulta de IA en curso, espera un momento.")
            return
        self._agregar_mensaje("sistema", "Comparando los 3 sistemas con Gemini...")
        monto = self.parametros_actuales["monto"]
        tasa = self.parametros_actuales["tasa_anual"]
        plazo = self.parametros_actuales["meses"]

        def _consultar():
            tabla_frances = ejecutar_calculo_cpp("frances", monto, tasa, plazo)
            tabla_aleman = ejecutar_calculo_cpp("aleman", monto, tasa, plazo)
            tabla_americano = ejecutar_calculo_cpp("americano", monto, tasa, plazo)

            def _resumen_sistema(lista_tabla: list[dict]) -> dict:
                indicadores = calcular_indicadores(lista_tabla, tasa)
                return {
                    "total_intereses": indicadores["total_interes"],
                    "pago_total": indicadores["total_pagado"],
                    "primera_cuota": lista_tabla[0]["cuota"] if lista_tabla else 0,
                    "ultima_cuota": lista_tabla[-1]["cuota"] if lista_tabla else 0,
                    "cuota_interes": lista_tabla[0]["interes"] if lista_tabla else 0,
                    "cuota_final": lista_tabla[-1]["cuota"] if lista_tabla else 0,
                }

            return comparar_sistemas(
                _resumen_sistema(tabla_frances),
                _resumen_sistema(tabla_aleman),
                _resumen_sistema(tabla_americano),
            )

        self._ejecutar_tarea_ia(_consultar, "Comparativa de sistemas")

    def _evento_consultar_ia(self, _):
        """Envía una pregunta libre del usuario al asesor IA."""
        pregunta = (self.txt_pregunta_ia.value or "").strip()
        if not pregunta:
            return
        if self.ia_ocupada:
            self._mostrar_mensaje("Ya hay una consulta de IA en curso, espera un momento.")
            return
        self.txt_pregunta_ia.value = ""
        self._agregar_mensaje("usuario", pregunta)
        self._agregar_mensaje("sistema", "Pensando...")
        resumen = dict(self.parametros_actuales)
        resumen["plazo"] = self.parametros_actuales.get("meses", 0)
        resumen["tasa"] = self.parametros_actuales.get("tasa_anual", 0)
        if self.tabla_actual:
            indicadores = calcular_indicadores(
                self.tabla_actual, self.parametros_actuales.get("tasa_anual", 0)
            )
            resumen.update({
                "total_intereses": indicadores["total_interes"],
                "pago_total": indicadores["total_pagado"],
                "cat": f"{indicadores['tasa_efectiva_anual']:.2f}",
            })
        tabla_copia = list(self.tabla_actual)
        self._ejecutar_tarea_ia(
            lambda: simular_escenario_personalizado(pregunta, resumen, tabla_copia),
            "Asesor IA",
        )

    def _evento_consultar_ia_plan(self, _):
        """Consulta al asesor IA usando los datos del plan activo."""
        pregunta = (self.txt_pregunta_ia_plan.value or "").strip()
        if not pregunta:
            return
        if self.ia_ocupada:
            self._mostrar_mensaje("Ya hay una consulta de IA en curso, espera un momento.")
            return
        self.txt_pregunta_ia_plan.value = ""
        self._agregar_mensaje("usuario", pregunta, es_plan=True)
        self._agregar_mensaje("sistema", "Pensando...", es_plan=True)
        dict_plan = dict(self.plan_activo or {})
        self._ejecutar_tarea_ia(
            lambda: consultar_plan_ia(pregunta, dict_plan, calcular_flujo_plan(dict_plan)),
            "Asesor del plan",
            es_plan=True,
        )

    def _crear_vista_chat_plan(self) -> ft.Container:
        """Pestaña del asesor IA con acceso a ingresos, egresos y crédito del plan."""
        paleta = self.paleta
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, size=18, color=paleta["primario"]),
                            ft.Column(
                                controls=[
                                    ft.Text("Asesor IA del plan", size=14,
                                            weight=ft.FontWeight.BOLD, color=paleta["primario"],
                                            font_family=FUENTE_APP),
                                    ft.Text("Lee ingresos, egresos, montos fijos y crédito mes por mes.",
                                            size=10, color=paleta["texto_suave"], font_family=FUENTE_APP),
                                ],
                                spacing=0,
                                expand=True,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Container(
                        content=self.lista_chat_plan,
                        height=350,
                        bgcolor=paleta["campo"],
                        border=ft.Border.all(1, paleta["borde"]),
                        border_radius=12,
                        padding=8,
                    ),
                    ft.Row(
                        controls=[self.txt_pregunta_ia_plan, self.btn_enviar_ia_plan],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=10,
            ),
            bgcolor=paleta["tarjeta"],
            border=ft.Border.all(1, paleta["borde"]),
            border_radius=14,
            padding=14,
        )

    def _formatear_titulo_escenario(self, letra_escenario: str, dict_params: dict, num_filas: int) -> str:
        """Arma el titulo descriptivo de un escenario fijado."""
        if not dict_params:
            return f"Escenario {letra_escenario}: sin datos fijados"
        texto_abonos = f" | {len(dict_params['abonos'])} adelanto(s)" if dict_params.get("abonos") else ""
        return (
            f"Escenario {letra_escenario}: {dict_params.get('sistema', '')} | "
            f"Monto {self._formatear_valor(dict_params.get('monto', 0))} | "
            f"Tasa {dict_params.get('tasa_anual', dict_params.get('tasa', 0))}% | "
            f"{dict_params.get('meses', 0)} m ({num_filas} cuotas){texto_abonos}"
        )

    def _fijar_escenario_comparar(self, letra_escenario: str):
        """Guarda el cálculo actual como escenario A o B."""
        if not self.tabla_actual or not self.parametros_actuales:
            self._mostrar_mensaje("Primero calcula un préstamo en el formulario para poder fijarlo.", es_error=True)
            return

        if letra_escenario == "A":
            self.lista_tabla_a = list(self.tabla_actual)
            self.dict_params_a = dict(self.parametros_actuales)
            self._mostrar_mensaje("Escenario actual fijado como A.")
        else:
            self.lista_tabla_b = list(self.tabla_actual)
            self.dict_params_b = dict(self.parametros_actuales)
            self._mostrar_mensaje("Escenario actual fijado como B.")

        self._actualizar_vista_comparar()
        self.pestanas.selected_index = 2
        self.indice_pestana = 2
        self.pagina.update()

    def _limpiar_comparar(self, _=None):
        """Limpia los dos escenarios fijados."""
        self.lista_tabla_a = []
        self.dict_params_a = {}
        self.lista_tabla_b = []
        self.dict_params_b = {}
        self._actualizar_vista_comparar()
        self.pagina.update()
        self._mostrar_mensaje("Comparativa reiniciada.")

    def _alternar_subvista_comparar(self, modo: str):
        """Alterna entre la vista de tablas paralelas y la grafica comparativa A-B."""
        self.subvista_comparar_activa = modo
        paleta = self.paleta

        if modo == "tablas":
            self.contenedor_cuerpo_comp.content = self.vista_tablas_paralelas
            self.btn_subvista_tablas.style.color = paleta["secundario"]
            self.btn_subvista_tablas.style.icon_color = paleta["secundario"]
            self.btn_subvista_tablas.style.side = ft.BorderSide(1.5, paleta["secundario"])
            self.btn_subvista_grafica.style.color = paleta["texto_suave"]
            self.btn_subvista_grafica.style.icon_color = paleta["texto_suave"]
            self.btn_subvista_grafica.style.side = ft.BorderSide(1, paleta["borde"])
        else:
            self.contenedor_cuerpo_comp.content = self.vista_grafica_comparar
            self.btn_subvista_tablas.style.color = paleta["texto_suave"]
            self.btn_subvista_tablas.style.icon_color = paleta["texto_suave"]
            self.btn_subvista_tablas.style.side = ft.BorderSide(1, paleta["borde"])
            self.btn_subvista_grafica.style.color = paleta["primario"]
            self.btn_subvista_grafica.style.icon_color = paleta["primario"]
            self.btn_subvista_grafica.style.side = ft.BorderSide(1.5, paleta["primario"])

        self.pagina.update()

    def _actualizar_vista_comparar(self):
        """Refresca las tablas, titulos, diferencias y grafica de la comparativa."""
        paleta = self.paleta
        num_a = len(self.lista_tabla_a)
        num_b = len(self.lista_tabla_b)

        self.col_tabla_comp_a.rows = [
            self._crear_fila_tabla(fila, indice)
            for indice, fila in enumerate(self.lista_tabla_a)
        ]
        self.col_tabla_comp_b.rows = [
            self._crear_fila_tabla(fila, indice)
            for indice, fila in enumerate(self.lista_tabla_b)
        ]

        self.lbl_titulo_comp_a.value = self._formatear_titulo_escenario("A", self.dict_params_a, num_a)
        self.lbl_titulo_comp_b.value = self._formatear_titulo_escenario("B", self.dict_params_b, num_b)

        total_a = sum(f["cuota"] for f in self.lista_tabla_a) if self.lista_tabla_a else 0.0
        interes_a = sum(f["interes"] for f in self.lista_tabla_a) if self.lista_tabla_a else 0.0
        total_b = sum(f["cuota"] for f in self.lista_tabla_b) if self.lista_tabla_b else 0.0
        interes_b = sum(f["interes"] for f in self.lista_tabla_b) if self.lista_tabla_b else 0.0

        if self.lista_tabla_a:
            self.lbl_resumen_comp_a.value = f"Total: {self._formatear_valor(total_a)} | Intereses: {self._formatear_valor(interes_a)}"
        else:
            self.lbl_resumen_comp_a.value = "Calcula y presiona 'Fijar actual como A'."

        if self.lista_tabla_b:
            self.lbl_resumen_comp_b.value = f"Total: {self._formatear_valor(total_b)} | Intereses: {self._formatear_valor(interes_b)}"
        else:
            self.lbl_resumen_comp_b.value = "Calcula y presiona 'Fijar actual como B'."

        if self.lista_tabla_a and self.lista_tabla_b:
            dif_total = total_a - total_b
            dif_interes = interes_a - interes_b
            if dif_total > 0:
                ganador = f"Escenario B es más económico por {self._formatear_valor(abs(dif_total))} (ahorras {self._formatear_valor(abs(dif_interes))} en intereses)"
            elif dif_total < 0:
                ganador = f"Escenario A es más económico por {self._formatear_valor(abs(dif_total))} (ahorras {self._formatear_valor(abs(dif_interes))} en intereses)"
            else:
                ganador = "Ambos escenarios tienen exactamente el mismo costo total"

            self.lbl_diferencia_comp.value = f"Diferencia: {ganador}."
            self.lbl_diferencia_comp.color = paleta["verde"]
        else:
            self.lbl_diferencia_comp.value = "Fija dos escenarios para analizar diferencias de costo e intereses."
            self.lbl_diferencia_comp.color = paleta["texto_suave"]

        if self.lista_tabla_a or self.lista_tabla_b:
            self.img_grafica_comp.src = generar_grafica_comparativa_base64(
                self.lista_tabla_a, self.lista_tabla_b,
                self.dict_params_a.get("sistema", "A"),
                self.dict_params_b.get("sistema", "B"),
                modo_oscuro=self.modo_tema == "oscuro",
                dict_colores=self.dict_config,
            )
            self.texto_grafica_comp_vacia.visible = False
        else:
            self.img_grafica_comp.src = ""
            self.texto_grafica_comp_vacia.visible = True

    def _evento_exportar_comparar_excel(self, _=None):
        """Exporta la comparativa A vs B a Excel."""
        if not self.lista_tabla_a or not self.lista_tabla_b:
            self._mostrar_mensaje("Debes fijar los escenarios A y B antes de exportar la comparativa.", es_error=True)
            return
        try:
            ruta_destino = os.path.join(self._ruta_exportacion(), "comparativa_escenarios_A_B.xlsx")
            exportar_comparativa_excel(
                self.lista_tabla_a, self.dict_params_a,
                self.lista_tabla_b, self.dict_params_b,
                ruta_destino,
                self.dict_config.get("num_decimales", 2),
                self.dict_config.get("simbolo_moneda", "$")
            )
            self._mostrar_mensaje(f"Comparativa Excel exportada con éxito en: {ruta_destino}")
        except Exception as error:
            self._mostrar_mensaje(f"Error al exportar comparativa Excel: {error}", es_error=True)

    def _evento_exportar_comparar_pdf(self, _=None):
        """Exporta la comparativa A vs B a PDF."""
        if not self.lista_tabla_a or not self.lista_tabla_b:
            self._mostrar_mensaje("Debes fijar los escenarios A y B antes de exportar la comparativa.", es_error=True)
            return
        try:
            ruta_destino = os.path.join(self._ruta_exportacion(), "comparativa_escenarios_A_B.pdf")
            establecer_fuentes_pdf(self.dict_config.get("fuente_pdf", "Segoe UI"))
            establecer_colores_personalizados(self.dict_config, self.modo_tema)
            try:
                exportar_comparativa_pdf(
                    self.lista_tabla_a, self.dict_params_a,
                    self.lista_tabla_b, self.dict_params_b,
                    ruta_destino,
                    int(self.dict_config.get("decimales_pdf", 2)),
                    self.dict_config.get("simbolo_moneda", "$"),
                    bool(self.dict_config.get("incluir_logo_pdf", True)),
                    bool(self.dict_config.get("incluir_pie_pdf", True))
                )
            finally:
                establecer_colores_personalizados(self.dict_config, self.modo_tema)
            self._mostrar_mensaje(f"Comparativa PDF exportada con éxito en: {ruta_destino}")
        except Exception as error:
            self._mostrar_mensaje(f"Error al exportar comparativa PDF: {error}", es_error=True)

    def _mostrar_grafica_ampliada(self, str_src: str, str_titulo: str):
        """Abre una grafica en un dialogo modal para verla en detalle."""
        if not str_src:
            self._mostrar_mensaje("No hay una gráfica disponible para ampliar.", es_error=True)
            return
        paleta = self.paleta
        dialogo = ft.AlertDialog(
            modal=True,
            bgcolor=paleta["tarjeta"],
            inset_padding=ft.Padding.all(20),
            title=ft.Text(str_titulo, color=paleta["primario"], size=16,
                          weight=ft.FontWeight.BOLD, font_family=FUENTE_APP),
            content=ft.Container(
                content=ft.Image(src=str_src, fit=ft.BoxFit.CONTAIN),
                width=900,
                height=520,
                bgcolor=paleta["campo"],
                border_radius=12,
                padding=8,
                alignment=ft.Alignment.CENTER,
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cerrar", color=paleta["texto_suave"], font_family=FUENTE_APP),
                    on_click=lambda _evento: setattr(dialogo, "open", False) or self.pagina.update(),
                ),
            ],
        )
        self.pagina.overlay.append(dialogo)
        dialogo.open = True
        self.pagina.update()

    def _evento_ampliar_grafica_amortizacion(self, _=None):
        """Amplia la grafica de evolucion del prestamo activo."""
        self._mostrar_grafica_ampliada(self.img_grafica.src, "Evolución del préstamo")

    def _evento_ampliar_grafica_comparativa(self, _=None):
        """Amplia la grafica comparativa de los escenarios A y B."""
        self._mostrar_grafica_ampliada(self.img_grafica_comp.src, "Comparativa de escenarios A vs B")

    def _evento_ver_grafica_plan(self, dict_plan: dict):
        """Genera y amplia la grafica de un plan guardado."""
        resumen = dict_plan.get("resumen") or calcular_resumen_plan(dict_plan)
        str_src = generar_grafica_planes_base64(
            resumen, modo_oscuro=self.modo_tema == "oscuro"
        )
        if not str_src:
            self._mostrar_mensaje("El plan no tiene montos para graficar.", es_error=True)
            return
        str_titulo = f"Flujo mensual · {dict_plan.get('nombre', 'Plan')}"
        self._mostrar_grafica_ampliada(str_src, str_titulo)

    def _evento_ver_evolucion_plan(self, dict_plan: dict):
        """Genera y amplia la evolucion mensual de los creditos de un plan guardado."""
        lista_filas = calcular_evolucion_plan(dict_plan.get("creditos", []))
        str_src = generar_grafica_evolucion_plan_base64(
            lista_filas, modo_oscuro=self.modo_tema == "oscuro"
        )
        if not str_src:
            self._mostrar_mensaje("El plan no tiene créditos para graficar.", es_error=True)
            return
        str_titulo = f"Evolución mensual · {dict_plan.get('nombre', 'Plan')}"
        self._mostrar_grafica_ampliada(str_src, str_titulo)

    def _mostrar_mensaje(self, str_mensaje: str, es_error: bool = False):
        """Muestra una notificación emergente tipo SnackBar."""
        color_fondo = self.paleta["rojo"] if es_error else self.paleta["verde"]
        aviso = ft.SnackBar(
            content=ft.Text(str_mensaje, color="#FFFFFF", font_family=FUENTE_APP),
            bgcolor=color_fondo,
            duration=3500,
        )
        self.pagina.overlay.append(aviso)
        aviso.open = True
        self.pagina.update()

    def _mostrar_dialogo_configuracion(self, _):
        """Abre el diálogo de configuración general, PDF y exportación."""
        global FUENTE_APP
        paleta = self.paleta

        def _dropdown(str_etiqueta: str, lista_opciones: list, valor_actual):
            return ft.Dropdown(
                label=str_etiqueta,
                options=[ft.DropdownOption(text=str(opcion), key=str(opcion)) for opcion in lista_opciones],
                value=str(valor_actual),
                width=260,
                border_radius=10,
                filled=True,
                fill_color=paleta["campo"],
                border_color=paleta["borde"],
                focused_border_color=paleta["primario"],
                label_style=self._estilo_etiqueta(),
                text_style=self._estilo_texto(),
                menu_style=ft.MenuStyle(bgcolor=paleta["tarjeta"]),
            )

        dd_decimales = _dropdown("Cantidad de decimales", OPCIONES_DECIMALES,
                                 self.dict_config.get("num_decimales", 2))
        dd_moneda = _dropdown("Moneda", OPCIONES_MONEDA, self.dict_config.get("simbolo_moneda", "$"))
        dd_tema = _dropdown("Tema", ["Oscuro", "Claro"],
                            "Claro" if self.dict_config.get("tema") == "claro" else "Oscuro")
        dd_fuente = _dropdown("Fuente (letra)", FUENTES_DISPONIBLES,
                              self.dict_config.get("fuente_app", "Segoe UI"))
        dds_colores = {
            "ingresos": _dropdown("Color de ingresos", list(COLORES_DISPONIBLES.keys()),
                                  self.dict_config.get("color_ingresos", "Verde")),
            "egresos": _dropdown("Color de egresos", list(COLORES_DISPONIBLES.keys()),
                                 self.dict_config.get("color_egresos", "Rojo")),
            "creditos": _dropdown("Color de pagos de crédito", list(COLORES_DISPONIBLES.keys()),
                                  self.dict_config.get("color_creditos", "Amarillo")),
            "saldo": _dropdown("Color de saldo neto", list(COLORES_DISPONIBLES.keys()),
                               self.dict_config.get("color_saldo", "Azul")),
            "intereses": _dropdown("Color de intereses", list(COLORES_DISPONIBLES.keys()),
                                   self.dict_config.get("color_intereses", "Rojo")),
            "capital": _dropdown("Color de capital", list(COLORES_DISPONIBLES.keys()),
                                 self.dict_config.get("color_capital", "Verde")),
        }

        dd_decimales_pdf = _dropdown("Decimales para PDF", OPCIONES_DECIMALES,
                                     self.dict_config.get("decimales_pdf", 2))
        dd_fuente_pdf = _dropdown("Fuente para PDF", FUENTES_PDF,
                                  self.dict_config.get("fuente_pdf", "Segoe UI"))
        chk_logo_pdf = ft.Checkbox(
            label="Incluir logo en el PDF",
            value=bool(self.dict_config.get("incluir_logo_pdf", True)),
            active_color=paleta["primario"],
        )
        chk_pie_pdf = ft.Checkbox(
            label="Incluir pie de página en el PDF",
            value=bool(self.dict_config.get("incluir_pie_pdf", True)),
            active_color=paleta["primario"],
        )

        self.txt_carpeta_config = ft.TextField(
            label="Carpeta donde guardar los archivos exportados",
            value=self.dict_config.get("carpeta_exportacion", "") or "",
            hint_text="Selecciona o pega la ruta completa de la carpeta",
            border_radius=10,
            filled=True,
            fill_color=paleta["campo"],
            border_color=paleta["borde"],
            focused_border_color=paleta["primario"],
            label_style=self._estilo_etiqueta(),
            text_style=self._estilo_texto(),
            expand=True,
        )

        async def _elegir_carpeta(_evento):
            ruta = await self.selector_carpeta.get_directory_path(
                dialog_title="Elige la carpeta para guardar los archivos exportados"
            )
            if ruta:
                self.txt_carpeta_config.value = ruta
                self.pagina.update()

        fila_carpeta_config = ft.Row(
            controls=[
                self.txt_carpeta_config,
                ft.IconButton(
                    icon=ft.Icons.FOLDER_OPEN_ROUNDED,
                    tooltip="Elegir carpeta",
                    icon_color=paleta["primario"],
                    on_click=_elegir_carpeta,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.with_opacity(0.12, paleta["primario"]),
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                ),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        txt_api_key = ft.TextField(
            label="API Key de Gemini",
            value=self.dict_config.get("api_key", "") or "",
            hint_text="Pega tu API Key (AQ... o AIza...)",
            password=True,
            can_reveal_password=True,
            border_radius=10,
            filled=True,
            fill_color=paleta["campo"],
            border_color=paleta["borde"],
            focused_border_color=paleta["primario"],
            label_style=self._estilo_etiqueta(),
            text_style=self._estilo_texto(),
            expand=True,
        )
        def _titulo(str_texto: str) -> ft.Text:
            return ft.Text(str_texto, size=12, weight=ft.FontWeight.BOLD,
                           color=paleta["primario"], font_family=FUENTE_APP)

        def _guardar_y_cerrar(_evento):
            global FUENTE_APP
            nuevo_tema = str(dd_tema.value).lower()
            cambio_tema = (nuevo_tema != self.modo_tema)
            cambio_fuente = str(dd_fuente.value) != FUENTE_APP
            self.dict_config.update({
                "num_decimales": int(dd_decimales.value),
                "simbolo_moneda": dd_moneda.value,
                "tema": nuevo_tema,
                "fuente_app": dd_fuente.value,
                "color_graficas": "Personalizado",
                "color_graficas_pdf": "Personalizado",
                "decimales_pdf": int(dd_decimales_pdf.value),
                "fuente_pdf": dd_fuente_pdf.value,
                "incluir_logo_pdf": chk_logo_pdf.value,
                "incluir_pie_pdf": chk_pie_pdf.value,
                "carpeta_exportacion": (self.txt_carpeta_config.value or "").strip(),
                "api_key": (txt_api_key.value or "").strip(),
            })
            for clave, control in dds_colores.items():
                self.dict_config[f"color_{clave}"] = control.value
            guardar_configuracion(self.dict_config)

            FUENTE_APP = self.dict_config["fuente_app"]
            aplicar_esquema_graficas_interfaz(self.dict_config)
            establecer_colores_personalizados(self.dict_config, nuevo_tema)

            dialogo.open = False
            if cambio_tema or cambio_fuente:
                self._aplicar_tema(nuevo_tema)
            elif self.tabla_actual and self.parametros_actuales:
                self._actualizar_resultados()
            self.pagina.update()
            self._mostrar_mensaje("Configuración guardada exitosamente.")

        dialogo = ft.AlertDialog(
            modal=True,
            bgcolor=paleta["tarjeta"],
            title=ft.Text("Configuración general", color=paleta["primario"],
                          weight=ft.FontWeight.BOLD, font_family=FUENTE_APP),
            content=ft.Column(
                controls=[
                    _titulo("Destino de los archivos exportados"),
                    fila_carpeta_config,
                    ft.Divider(height=1, color=paleta["borde"]),
                    _titulo("Asesor IA (Gemini)"),
                    txt_api_key,
                    ft.Divider(height=1, color=paleta["borde"]),
                    _titulo("General"),
                    dd_decimales, dd_moneda, dd_tema, dd_fuente,
                    ft.Text("Colores de las gráficas", size=11, weight=ft.FontWeight.BOLD,
                            color=paleta["primario"], font_family=FUENTE_APP),
                    *dds_colores.values(),
                    ft.Divider(height=1, color=paleta["borde"]),
                    _titulo("Configuración para PDF"),
                    dd_decimales_pdf, dd_fuente_pdf,
                    ft.Text("Las gráficas del PDF usan los colores elegidos arriba.",
                            size=10, color=paleta["texto_suave"], font_family=FUENTE_APP),
                    chk_logo_pdf, chk_pie_pdf,
                ],
                tight=True,
                spacing=10,
                width=340,
                height=600,
                scroll=ft.ScrollMode.AUTO,
            ),
            scrollable=True,
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancelar", color=paleta["texto_suave"], font_family=FUENTE_APP),
                    on_click=lambda _evento: setattr(dialogo, "open", False) or self.pagina.update(),
                ),
                self._crear_boton_primario("Guardar", ft.Icons.CHECK, _guardar_y_cerrar),
            ],
        )
        self.pagina.overlay.append(dialogo)
        dialogo.open = True
        self.pagina.update()

# ==========================================
# Proceso Principal
# ==========================================

def main(obj_pagina: ft.Page):
    """Punto de entrada de Flet."""
    InterfazFletSimulador(obj_pagina)


def iniciar_interfaz_flet():
    """Lanza la aplicacion Flet en modo escritorio."""
    ft.run(main)


if __name__ == "__main__":
    iniciar_interfaz_flet()

