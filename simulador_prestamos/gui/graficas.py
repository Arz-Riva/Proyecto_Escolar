# ==========================================
# Encabezados y Librerias
# ==========================================
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ==========================================
# Declaracion de Constantes
# ==========================================
COLOR_FONDO_GRAFICA = "#F8F9FA"
COLOR_REJILLA = "#E0E0E0"

# Colores distintivos por sistema de amortizacion
COLOR_FRANCES = "#1976D2"      # Azul corporativo
COLOR_ALEMAN = "#2E7D32"       # Verde esmeralda
COLOR_AMERICANO = "#D32F2F"    # Rojo rubi

# Colores para la relacion interes-capital del sistema seleccionado
COLOR_CAPITAL = "#2E7D32"
COLOR_INTERES = "#C62828"

# Colores para escenarios A y B de la comparativa
COLOR_ESCENARIO_A = "#1976D2"
COLOR_ESCENARIO_B = "#EF6C00"

# ==========================================
# Declaracion de Funciones de Graficacion
# ==========================================

def generar_figura_comparativa_saldos(dict_tablas: dict[str, list[dict]], val_monto_inicial: float) -> Figure:
    """
    Construye una figura comparativa de lineas superpuestas que visualiza
    la reduccion de saldo deudor para los sistemas Frances, Aleman y Americano.
    """
    figura = Figure(figsize=(6, 4.2), dpi=100)
    figura.patch.set_facecolor(COLOR_FONDO_GRAFICA)
    eje = figura.add_subplot(111)
    eje.set_facecolor(COLOR_FONDO_GRAFICA)

    if not dict_tablas or "frances" not in dict_tablas or not dict_tablas["frances"]:
        eje.text(0.5, 0.5, "No hay datos para comparar.\nEjecuta una simulacion primero.",
                 horizontalalignment="center", verticalalignment="center",
                 transform=eje.transAxes, color="#777777", fontsize=11)
        eje.set_xticks([])
        eje.set_yticks([])
        return figura

    # Curva Sistema Frances
    filas_frances = dict_tablas.get("frances", [])
    meses_frances = [0] + [fila["mes"] for fila in filas_frances]
    saldos_frances = [val_monto_inicial] + [fila["saldo"] for fila in filas_frances]
    eje.plot(meses_frances, saldos_frances, color=COLOR_FRANCES, marker="o",
             markersize=4, linewidth=2, label="Frances (Amortizacion Curva)")

    # Curva Sistema Aleman
    filas_aleman = dict_tablas.get("aleman", [])
    meses_aleman = [0] + [fila["mes"] for fila in filas_aleman]
    saldos_aleman = [val_monto_inicial] + [fila["saldo"] for fila in filas_aleman]
    eje.plot(meses_aleman, saldos_aleman, color=COLOR_ALEMAN, marker="s",
             markersize=4, linewidth=2, linestyle="--", label="Aleman (Capital Lineal Fijo)")

    # Curva Sistema Americano
    filas_americano = dict_tablas.get("americano", [])
    meses_americano = [0] + [fila["mes"] for fila in filas_americano]
    saldos_americano = [val_monto_inicial] + [fila["saldo"] for fila in filas_americano]
    eje.plot(meses_americano, saldos_americano, color=COLOR_AMERICANO, marker="^",
             markersize=4, linewidth=2, linestyle=":", label="Americano (Saldo al Vencimiento)")

    # Formato visual
    eje.set_title("Comparativa de Evolucion del Saldo Deudor", fontsize=12, fontweight="bold", pad=10)
    eje.set_xlabel("Mes", fontsize=10)
    eje.set_ylabel("Saldo Pendiente ($)", fontsize=10)
    eje.grid(True, linestyle="--", alpha=0.6, color=COLOR_REJILLA)
    eje.legend(loc="upper right", frameon=True, fontsize=9)
    eje.yaxis.set_major_formatter("${x:,.0f}")

    figura.tight_layout()
    return figura


def generar_figura_comparativa_cuotas(dict_tablas: dict[str, list[dict]]) -> Figure:
    """
    Construye una figura de lineas que contrasta la variacion de las cuotas
    mensuales a lo largo del tiempo entre los tres sistemas.
    """
    figura = Figure(figsize=(6, 4.2), dpi=100)
    figura.patch.set_facecolor(COLOR_FONDO_GRAFICA)
    eje = figura.add_subplot(111)
    eje.set_facecolor(COLOR_FONDO_GRAFICA)

    if not dict_tablas or "frances" not in dict_tablas or not dict_tablas["frances"]:
        eje.text(0.5, 0.5, "No hay datos para comparar.\nEjecuta una simulacion primero.",
                 horizontalalignment="center", verticalalignment="center",
                 transform=eje.transAxes, color="#777777", fontsize=11)
        eje.set_xticks([])
        eje.set_yticks([])
        return figura

    filas_frances = dict_tablas.get("frances", [])
    filas_aleman = dict_tablas.get("aleman", [])
    filas_americano = dict_tablas.get("americano", [])

    meses = [fila["mes"] for fila in filas_frances]
    cuotas_frances = [fila["cuota"] for fila in filas_frances]
    cuotas_aleman = [fila["cuota"] for fila in filas_aleman]
    cuotas_americano = [fila["cuota"] for fila in filas_americano]

    # Trazado de las tres series de cuotas
    eje.plot(meses, cuotas_frances, color=COLOR_FRANCES, marker="o",
             markersize=4, linewidth=2, label="Frances (Cuota Constante)")
    eje.plot(meses, cuotas_aleman, color=COLOR_ALEMAN, marker="s",
             markersize=4, linewidth=2, linestyle="--", label="Aleman (Cuota Decreciente)")
    eje.plot(meses, cuotas_americano, color=COLOR_AMERICANO, marker="^",
             markersize=4, linewidth=2, linestyle=":", label="Americano (Interes + Balon Final)")

    # Formato visual
    eje.set_title("Comparativa del Monto de Cuota Mensual", fontsize=12, fontweight="bold", pad=10)
    eje.set_xlabel("Mes", fontsize=10)
    eje.set_ylabel("Monto de Cuota ($)", fontsize=10)
    eje.grid(True, linestyle="--", alpha=0.6, color=COLOR_REJILLA)
    eje.legend(loc="upper left", frameon=True, fontsize=9)
    eje.yaxis.set_major_formatter("${x:,.0f}")

    figura.tight_layout()
    return figura


def generar_figura_comparativa_costos(dict_tablas: dict[str, list[dict]]) -> Figure:
    """
    Construye un grafico de barras que compara el costo financiero total
    (intereses totales generados) en cada uno de los tres sistemas de amortizacion.
    """
    figura = Figure(figsize=(6, 4.2), dpi=100)
    figura.patch.set_facecolor(COLOR_FONDO_GRAFICA)
    eje = figura.add_subplot(111)
    eje.set_facecolor(COLOR_FONDO_GRAFICA)

    if not dict_tablas or "frances" not in dict_tablas or not dict_tablas["frances"]:
        eje.text(0.5, 0.5, "No hay datos para comparar.\nEjecuta una simulacion primero.",
                 horizontalalignment="center", verticalalignment="center",
                 transform=eje.transAxes, color="#777777", fontsize=11)
        eje.set_xticks([])
        eje.set_yticks([])
        return figura

    # Suma de intereses acumulados por sistema
    interes_frances = sum(fila["interes"] for fila in dict_tablas.get("frances", []))
    interes_aleman = sum(fila["interes"] for fila in dict_tablas.get("aleman", []))
    interes_americano = sum(fila["interes"] for fila in dict_tablas.get("americano", []))

    nombres_sistemas = ["Aleman\n(Menor Interes)", "Frances\n(Intermedio)", "Americano\n(Mayor Interes)"]
    valores_intereses = [interes_aleman, interes_frances, interes_americano]
    colores_barras = [COLOR_ALEMAN, COLOR_FRANCES, COLOR_AMERICANO]

    barras = eje.bar(nombres_sistemas, valores_intereses, color=colores_barras, width=0.55, alpha=0.88)

    # Anotaciones sobre cada barra con el valor exacto en formato moneda
    for barra in barras:
        altura = barra.get_height()
        eje.annotate(f"${altura:,.2f}",
                     xy=(barra.get_x() + barra.get_width() / 2, altura),
                     xytext=(0, 4),
                     textcoords="offset points",
                     ha="center", va="bottom",
                     fontweight="bold", fontsize=10)

    # Formato visual
    eje.set_title("Comparativa de Intereses Totales Pagados", fontsize=12, fontweight="bold", pad=12)
    eje.set_ylabel("Total de Intereses ($)", fontsize=10)
    eje.grid(True, axis="y", linestyle="--", alpha=0.6, color=COLOR_REJILLA)
    eje.yaxis.set_major_formatter("${x:,.0f}")

    # Margen superior para las etiquetas de texto
    if valores_intereses:
        eje.set_ylim(0, max(valores_intereses) * 1.18)

    figura.tight_layout()
    return figura


def generar_figura_relacion_interes_capital(lista_filas: list[dict]) -> Figure:
    """
    Construye un grafico de barras del sistema seleccionado que muestra
    la relacion entre capital total e interes total pagados.
    """
    figura = Figure(figsize=(6.2, 3.8), dpi=100)
    figura.patch.set_facecolor(COLOR_FONDO_GRAFICA)
    eje = figura.add_subplot(111)
    eje.set_facecolor(COLOR_FONDO_GRAFICA)

    if not lista_filas:
        eje.text(0.5, 0.5, "No hay datos para mostrar.\nEjecuta una simulacion primero.",
                 horizontalalignment="center", verticalalignment="center",
                 transform=eje.transAxes, color="#777777", fontsize=10)
        eje.set_xticks([])
        eje.set_yticks([])
        figura.tight_layout(pad=2.0)
        return figura

    # Totales del sistema seleccionado con funciones puras
    total_capital = sum(fila["capital"] for fila in lista_filas)
    total_interes = sum(fila["interes"] for fila in lista_filas)
    total_pagado = total_capital + total_interes
    porc_interes = (total_interes / total_pagado * 100.0) if total_pagado > 0 else 0.0

    nombres = ["Capital", "Interes"]
    valores = [total_capital, total_interes]
    colores = [COLOR_CAPITAL, COLOR_INTERES]

    barras = eje.bar(nombres, valores, color=colores, width=0.45, alpha=0.9, edgecolor="white")

    for barra in barras:
        altura = barra.get_height()
        eje.annotate(f"${altura:,.2f}",
                     xy=(barra.get_x() + barra.get_width() / 2, altura),
                     xytext=(0, 4),
                     textcoords="offset points",
                     ha="center", va="bottom",
                     fontweight="bold", fontsize=9)

    eje.set_title(f"Relacion Interes-Capital (Interes: {porc_interes:.1f}% del total)",
                  fontsize=11, fontweight="bold", pad=10)
    eje.set_ylabel("Monto ($)", fontsize=9)
    eje.tick_params(labelsize=8)
    eje.grid(True, axis="y", linestyle="--", alpha=0.6, color=COLOR_REJILLA)
    eje.set_axisbelow(True)
    eje.yaxis.set_major_formatter("${x:,.0f}")

    if valores and max(valores) > 0:
        eje.set_ylim(0, max(valores) * 1.25)

    figura.tight_layout(pad=2.0)
    return figura


def generar_figura_comparativa_escenarios(lista_a: list[dict], lista_b: list[dict], titulo_a: str = "A", titulo_b: str = "B") -> Figure:
    """
    Construye una figura con dos paneles que compara los escenarios A y B:
    barras de capital e interes totales y evolucion del saldo.
    """
    figura = Figure(figsize=(8.0, 3.8), dpi=100)
    figura.patch.set_facecolor(COLOR_FONDO_GRAFICA)

    if not lista_a and not lista_b:
        eje = figura.add_subplot(111)
        eje.set_facecolor(COLOR_FONDO_GRAFICA)
        eje.text(0.5, 0.5, "No hay escenarios para comparar.\nFija A y B primero.",
                 horizontalalignment="center", verticalalignment="center",
                 transform=eje.transAxes, color="#777777", fontsize=10)
        eje.set_xticks([])
        eje.set_yticks([])
        figura.tight_layout(pad=2.0)
        return figura

    # Totales puros de cada escenario
    capital_a = sum(fila["capital"] for fila in lista_a) if lista_a else 0.0
    interes_a = sum(fila["interes"] for fila in lista_a) if lista_a else 0.0
    capital_b = sum(fila["capital"] for fila in lista_b) if lista_b else 0.0
    interes_b = sum(fila["interes"] for fila in lista_b) if lista_b else 0.0

    # Panel 1: barras agrupadas capital e interes
    eje_barras = figura.add_subplot(121)
    eje_barras.set_facecolor(COLOR_FONDO_GRAFICA)
    etiquetas = ["Capital", "Interes"]
    pos = [0, 1]
    ancho = 0.32
    barras_a = eje_barras.bar([p - ancho / 2 for p in pos], [capital_a, interes_a],
                              width=ancho, color=COLOR_ESCENARIO_A, label=f"Escenario {titulo_a}",
                              alpha=0.9, edgecolor="white")
    barras_b = eje_barras.bar([p + ancho / 2 for p in pos], [capital_b, interes_b],
                              width=ancho, color=COLOR_ESCENARIO_B, label=f"Escenario {titulo_b}",
                              alpha=0.9, edgecolor="white")
    for barra in list(barras_a) + list(barras_b):
        altura = barra.get_height()
        if altura > 0:
            eje_barras.annotate(f"${altura:,.0f}",
                                xy=(barra.get_x() + barra.get_width() / 2, altura),
                                xytext=(0, 3), textcoords="offset points",
                                ha="center", va="bottom", fontsize=7)
    eje_barras.set_title("Capital vs Interes A-B", fontsize=10, fontweight="bold", pad=8)
    eje_barras.set_xticks(pos)
    eje_barras.set_xticklabels(etiquetas, fontsize=8)
    eje_barras.tick_params(labelsize=7)
    eje_barras.grid(True, axis="y", linestyle="--", alpha=0.6, color=COLOR_REJILLA)
    eje_barras.set_axisbelow(True)
    eje_barras.legend(fontsize=7, loc="best", frameon=True)
    eje_barras.yaxis.set_major_formatter("${x:,.0f}")
    max_barra = max([capital_a, interes_a, capital_b, interes_b, 1.0])
    eje_barras.set_ylim(0, max_barra * 1.3)

    # Panel 2: evolucion del saldo de ambos escenarios
    eje_saldo = figura.add_subplot(122)
    eje_saldo.set_facecolor(COLOR_FONDO_GRAFICA)
    if lista_a:
        meses_a = [0] + [fila["mes"] for fila in lista_a]
        saldos_a = [capital_a] + [fila["saldo"] for fila in lista_a]
        eje_saldo.plot(meses_a, saldos_a, color=COLOR_ESCENARIO_A, marker="o",
                       markersize=3, linewidth=1.8, label=f"Saldo {titulo_a}")
    if lista_b:
        meses_b = [0] + [fila["mes"] for fila in lista_b]
        saldos_b = [capital_b] + [fila["saldo"] for fila in lista_b]
        eje_saldo.plot(meses_b, saldos_b, color=COLOR_ESCENARIO_B, marker="s",
                       markersize=3, linewidth=1.8, linestyle="--", label=f"Saldo {titulo_b}")
    eje_saldo.set_title("Evolucion del Saldo A-B", fontsize=10, fontweight="bold", pad=8)
    eje_saldo.set_xlabel("Mes", fontsize=8)
    eje_saldo.set_ylabel("Saldo ($)", fontsize=8)
    eje_saldo.tick_params(labelsize=7)
    eje_saldo.grid(True, linestyle="--", alpha=0.6, color=COLOR_REJILLA)
    eje_saldo.set_axisbelow(True)
    eje_saldo.legend(fontsize=7, loc="best", frameon=True)
    eje_saldo.yaxis.set_major_formatter("${x:,.0f}")
    eje_saldo.margins(x=0.02)

    figura.subplots_adjust(wspace=0.35, left=0.08, right=0.97, top=0.88, bottom=0.15)
    figura.tight_layout(pad=2.0)
    return figura


def renderizar_lienzo_en_contenedor(figura: Figure, obj_contenedor: tk.Widget) -> FigureCanvasTkAgg:
    """
    Limpia los widgets anteriores de un contenedor Tkinter y monta el lienzo
    de la figura de matplotlib especificada.
    """
    for widget_hijo in obj_contenedor.winfo_children():
        widget_hijo.destroy()

    lienzo = FigureCanvasTkAgg(figura, master=obj_contenedor)
    lienzo.draw()
    lienzo.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    return lienzo
