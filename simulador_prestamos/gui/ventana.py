# ==========================================
# Encabezados y Librerias
# ==========================================
import os
import json
import subprocess
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    from gui.graficas import (
        generar_figura_relacion_interes_capital,
        generar_figura_comparativa_escenarios,
        renderizar_lienzo_en_contenedor,
        establecer_modo_graficas,
    )
    from gui.exportar import (exportar_tabla_excel, exportar_tabla_pdf,
                              exportar_comparativa_excel, exportar_comparativa_pdf)
    from gui.indicadores import calcular_indicadores, formatear_mes_cruce
    from gui.configuracion import (cargar_configuracion, guardar_configuracion,
                                   obtener_ajuste_fuente, formatear_moneda,
                                   OPCIONES_TAMANO_LETRA, OPCIONES_DECIMALES,
                                   OPCIONES_MONEDA)
except ImportError:
    try:
        from simulador_prestamos.gui.graficas import (
            generar_figura_relacion_interes_capital,
            generar_figura_comparativa_escenarios,
            renderizar_lienzo_en_contenedor,
            establecer_modo_graficas,
        )
        from simulador_prestamos.gui.exportar import (exportar_tabla_excel, exportar_tabla_pdf,
                                                      exportar_comparativa_excel,
                                                      exportar_comparativa_pdf)
        from simulador_prestamos.gui.indicadores import calcular_indicadores, formatear_mes_cruce
        from simulador_prestamos.gui.configuracion import (cargar_configuracion, guardar_configuracion,
                                                           obtener_ajuste_fuente, formatear_moneda,
                                                           OPCIONES_TAMANO_LETRA, OPCIONES_DECIMALES,
                                                           OPCIONES_MONEDA)
    except ImportError:
        from graficas import (
            generar_figura_relacion_interes_capital,
            generar_figura_comparativa_escenarios,
            renderizar_lienzo_en_contenedor,
            establecer_modo_graficas,
        )
        from exportar import (exportar_tabla_excel, exportar_tabla_pdf,
                              exportar_comparativa_excel, exportar_comparativa_pdf)
        from indicadores import calcular_indicadores, formatear_mes_cruce
        from configuracion import (cargar_configuracion, guardar_configuracion,
                                   obtener_ajuste_fuente, formatear_moneda,
                                   OPCIONES_TAMANO_LETRA, OPCIONES_DECIMALES,
                                   OPCIONES_MONEDA)



# ==========================================
# Declaracion de Constantes y Clases
# ==========================================

TITULO_APLICACION = "Intresta"
ANCHO_VENTANA = 1150
ALTO_VENTANA = 720
ANCHO_MINIMO = 900
ALTO_MINIMO = 620
OPCIONES_SISTEMAS = ["Frances", "Aleman", "Americano"]
NOMBRE_ARCHIVO_HISTORIAL = "historial.json"
MAX_ENTRADAS_HISTORIAL = 100

# Paletas seleccionables claro / oscuro (abajo del titulo hay boton para alternar)
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
    "fondo": "#380057",
    "primario": "#380057",
    "secundario": "#CFCC27",
    "tarjeta": "#CFCFCF",
    "texto_claro": "#212121",
    "texto_suave": "#546E7A",
    "campo": "#FFFFFF",
    "seleccion": "#B39DDB",
    "borde": "#9E9E9E",
    "rojo": "#C62828",
    "verde": "#2E7D32",
}

MODO_TEMA_INICIAL = "oscuro"

# Colores activos (inician en oscuro para cuidar la vista)
COLOR_FONDO = PALETA_OSCURA["fondo"] # Fondo general oscuro
COLOR_PRIMARIO = PALETA_OSCURA["primario"] # Acento morado claro para titulos de seccion
COLOR_SECUNDARIO = PALETA_OSCURA["secundario"] # Amarillo claro para titulo principal y encabezados
COLOR_FONDO_TARJETA = PALETA_OSCURA["tarjeta"] # Fondo de tarjetas y tablas en oscuro
COLOR_TEXTO_CLARO = PALETA_OSCURA["texto_claro"] # Texto principal claro
COLOR_TEXTO_SUAVE = PALETA_OSCURA["texto_suave"] # Texto secundario gris azulado
COLOR_CAMPO = PALETA_OSCURA["campo"] # Fondo de campos de entrada
COLOR_SELECCION = PALETA_OSCURA["seleccion"] # Fondo de seleccion en tablas y pestanas
COLOR_BORDE = PALETA_OSCURA["borde"] # Borde sutil de tarjetas
COLOR_ROJO = PALETA_OSCURA["rojo"]
COLOR_VERDE = PALETA_OSCURA["verde"]


def obtener_colores_tema(modo_tema: str) -> dict:
    """Retorna el diccionario de colores para 'claro' u 'oscuro'."""
    if modo_tema == "claro":
        return dict(PALETA_CLARA)
    return dict(PALETA_OSCURA)


def formatear_abonos_cli(lista_abonos: list[dict]) -> str:
    """Convierte la lista de abonos a texto CLI 'mes:monto,mes:monto'."""
    partes = []
    for abono in lista_abonos:
        partes.append(f"{int(abono['mes'])}:{float(abono['monto'])}")
    return ",".join(partes)


def calcular_amortizacion(str_sistema: str, val_monto: float, val_tasa_anual: float, num_meses: int,
                          lista_abonos: list[dict] | None = None) -> list[dict]:
    """
    Invoca al binario compilado de C++ (amortizador.exe) mediante subprocess
    y retorna la tabla de amortizacion en formato de lista de diccionarios.
    """
    # Busqueda robusta del ejecutable en rutas relativas y absolutas
    dir_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_ejecutable = os.path.join(dir_actual, "..", "core_cpp", "amortizador.exe")

    if not os.path.exists(ruta_ejecutable):
        ruta_ejecutable = os.path.join(os.getcwd(), "simulador_prestamos", "core_cpp", "amortizador.exe")
        if not os.path.exists(ruta_ejecutable):
            raise FileNotFoundError(
                f"No se encontro el binario de calculo en: {ruta_ejecutable}. "
                "Asegurate de compilar core_cpp/amortizador.exe antes de ejecutar la aplicacion."
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


class AplicacionSimulador:
    """
    Controlador principal de la interfaz grafica tkinter que gestiona
    el formulario de parametros, la tabla de amortizacion, el resumen financiero
    y las graficas interactivas con matplotlib.
    """

    def __init__(self, obj_ventana_raiz: tk.Tk):
        self.raiz = obj_ventana_raiz
        self.dict_config = cargar_configuracion()
        self.modo_tema = self.dict_config.get("tema", MODO_TEMA_INICIAL)
        self.dict_colores = obtener_colores_tema(self.modo_tema)
        establecer_modo_graficas(self.modo_tema)
        self._configurar_ventana()
        self._configurar_estilos()
        self._crear_componentes()
        self._construir_disposicion()
        self._cargar_historial_desde_json()
        self._actualizar_vista_historial()

    def _alternar_tema(self):
        """Alterna entre tema claro y oscuro y refresca toda la interfaz."""
        self.modo_tema = "claro" if self.modo_tema == "oscuro" else "oscuro"
        self.dict_config["tema"] = self.modo_tema
        self.dict_colores = obtener_colores_tema(self.modo_tema)
        establecer_modo_graficas(self.modo_tema)
        self._configurar_estilos()
        self._refrescar_tema()
        self._guardar_config_actual()

    def _formatear_moneda(self, val_monto: float) -> str:
        """Formatea un monto segun decimales y simbolo de la configuracion."""
        return formatear_moneda(val_monto,
                                self.dict_config.get("num_decimales", 2),
                                self.dict_config.get("simbolo_moneda", "$"))

    def _guardar_config_actual(self):
        """Persiste la configuracion actual en config.json sin mostrar alertas."""
        try:
            guardar_configuracion(self.dict_config)
        except Exception:
            pass

    def _aplicar_configuracion(self):
        """Aplica tamano de letra y formato numerico a toda la interfaz."""
        self._configurar_estilos()
        self._refrescar_tema()
        if self.lista_filas_actual:
            self._actualizar_tabla(self.lista_filas_actual)
            self._actualizar_resumen(self.lista_filas_actual,
                                     self.dict_params_actual.get("tasa", 0.0))
        if self.lista_tabla_a or self.lista_tabla_b:
            self._actualizar_vista_comparar()
        self._guardar_config_actual()

    def _refrescar_tema(self):
        """Aplica los colores activos a widgets tk directos y re-renderiza graficas."""
        col = self.dict_colores
        self.raiz.configure(bg=col["fondo"])
        if hasattr(self, "lbl_logo"):
            self.lbl_logo.configure(bg=col["fondo"])
        if hasattr(self, "var_texto_tema"):
            self.var_texto_tema.set("Tema: Claro" if self.modo_tema == "claro" else "Tema: Oscuro")
        if hasattr(self, "lienzo_historial"):
            self.lienzo_historial.configure(bg=col["tarjeta"])
        if hasattr(self, "lienzo_formulario"):
            self.lienzo_formulario.configure(bg=col["tarjeta"])
        # Re-renderizar vistas con la nueva paleta
        if hasattr(self, "lista_filas_actual"):
            if self.lista_filas_actual:
                self._actualizar_graficas(self.lista_filas_actual)
            else:
                self._limpiar_graficas()
        if hasattr(self, "marco_vista_grafica"):
            self._actualizar_grafica_comparar()
        if hasattr(self, "marco_filas_historial"):
            self._actualizar_vista_historial()

    def _configurar_ventana(self):
        """Ajusta las propiedades globales, iconos y titulo de la ventana."""
        col_fondo = getattr(self, "dict_colores", {}).get("fondo", COLOR_FONDO)
        self.raiz.title(TITULO_APLICACION)
        self.raiz.geometry(f"{ANCHO_VENTANA}x{ALTO_VENTANA}")
        self.raiz.minsize(ANCHO_MINIMO, ALTO_MINIMO)
        self.raiz.configure(bg=col_fondo)

        # Identificador explicito para que Windows aplique el icono propio en la barra de tareas
        try:
            import ctypes
            str_app_id = "antigravity.simulador_prestamos.intresta.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(str_app_id)
        except Exception:
            pass

        # Carga del icono para la barra de tareas y el marco de la ventana
        dir_img = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Img")
        ruta_ico = os.path.join(dir_img, "intresta-icon.ico")
        ruta_png_icono = os.path.join(dir_img, "intresta-icon.png")

        if os.path.exists(ruta_ico):
            try:
                self.raiz.iconbitmap(ruta_ico)
            except Exception:
                pass
        if os.path.exists(ruta_png_icono):
            try:
                self.img_icono_ventana = tk.PhotoImage(file=ruta_png_icono)
                self.raiz.iconphoto(True, self.img_icono_ventana)
            except Exception:
                pass

    def _configurar_estilos(self):

        """Configura los estilos de ttk para el tema claro u oscuro."""
        col = getattr(self, "dict_colores", obtener_colores_tema(MODO_TEMA_INICIAL))
        num_ajuste = obtener_ajuste_fuente(getattr(self, "dict_config", {}).get("tamano_letra", "Normal"))
        if not hasattr(self, "estilo"):
            self.estilo = ttk.Style()
        self.estilo.theme_use("clam")

        # Estilo general de los frames
        self.estilo.configure("Tarjeta.TFrame", background=col["tarjeta"])
        self.estilo.configure("Fondo.TFrame", background=col["fondo"])

        # Etiquetas en tema activo
        self.estilo.configure("Titulo.TLabel",
                              background=col["fondo"],
                              foreground=col["secundario"],
                              font=("Segoe UI", 22 + num_ajuste, "bold"))
        self.estilo.configure("Subtitulo.TLabel",
                              background=col["fondo"],
                              foreground=col["texto_suave"],
                              font=("Segoe UI", max(7, 9 + num_ajuste)))
        self.estilo.configure("Seccion.TLabel",
                              background=col["tarjeta"],
                              foreground=col["primario"],
                              font=("Segoe UI", 12 + num_ajuste, "bold"))
        self.estilo.configure("Normal.TLabel",
                              background=col["tarjeta"],
                              foreground=col["texto_claro"],
                              font=("Segoe UI", 10 + num_ajuste))
        self.estilo.configure("Resumen.TLabel",
                              background=col["tarjeta"],
                              foreground=col["texto_claro"],
                              font=("Segoe UI", 11 + num_ajuste, "bold"))
        self.estilo.configure("ResumenRojo.TLabel",
                              background=col["tarjeta"],
                              foreground=col["rojo"],
                              font=("Segoe UI", 11 + num_ajuste, "bold"))
        self.estilo.configure("ResumenVerde.TLabel",
                              background=col["tarjeta"],
                              foreground=col["verde"],
                              font=("Segoe UI", 11 + num_ajuste, "bold"))

        # Botones en tema activo
        self.estilo.configure("Calcular.TButton",
                              font=("Segoe UI", 10 + num_ajuste, "bold"),
                              padding=8)
        self.estilo.configure("Limpiar.TButton",
                              font=("Segoe UI", 10 + num_ajuste),
                              padding=8)
        self.estilo.configure("Tema.TButton",
                              font=("Segoe UI", 9 + num_ajuste, "bold"),
                              padding=6)

        # Campos de entrada y combos en tema activo
        self.estilo.configure("TEntry",
                              fieldbackground=col["campo"],
                              foreground=col["texto_claro"],
                              insertcolor=col["texto_claro"])
        self.estilo.configure("TCombobox",
                              fieldbackground=col["campo"],
                              background=col["campo"],
                              foreground=col["texto_claro"],
                              arrowcolor=col["texto_claro"])
        self.estilo.map("TCombobox",
                        fieldbackground=[("readonly", col["campo"])],
                        foreground=[("readonly", col["texto_claro"])])

        # Pestanas (Notebook) en tema activo
        self.estilo.configure("TNotebook", background=col["fondo"],
                              borderwidth=0)
        self.estilo.configure("TNotebook.Tab",
                              background=col["tarjeta"],
                              foreground=col["texto_suave"],
                              font=("Segoe UI", 10 + num_ajuste, "bold"),
                              padding=[12, 6])
        self.estilo.map("TNotebook.Tab",
                        background=[("selected", col["seleccion"])],
                        foreground=[("selected", col["texto_claro"])])

        # Pestanas de navegacion principal
        self.estilo.configure("NavegacionPrincipal.TNotebook", background=col["fondo"],
                              borderwidth=0)
        self.estilo.configure("NavegacionPrincipal.TNotebook.Tab",
                              background=col["tarjeta"],
                              foreground=col["texto_suave"],
                              font=("Segoe UI", 10 + num_ajuste, "bold"),
                              padding=[16, 6])
        self.estilo.map("NavegacionPrincipal.TNotebook.Tab",
                        background=[("selected", col["seleccion"])],
                        foreground=[("selected", col["secundario"])])

        # Treeview (tabla de datos) en tema activo
        self.estilo.configure("Tabla.Treeview",
                              background=col["campo"],
                              fieldbackground=col["campo"],
                              foreground=col["texto_claro"],
                              font=("Segoe UI", 10 + num_ajuste),
                              rowheight=28 + num_ajuste * 2,
                              borderwidth=0)
        self.estilo.configure("Tabla.Treeview.Heading",
                              background=col["seleccion"],
                              foreground=col["secundario"],
                              font=("Segoe UI", 10 + num_ajuste, "bold"))
        self.estilo.map("Tabla.Treeview",
                        background=[("selected", col["seleccion"])],
                        foreground=[("selected", col["texto_claro"])])
        self.estilo.map("Tabla.Treeview.Heading",
                        background=[("active", col["seleccion"])])

        # Scrollbar y separador acordes al tema activo
        self.estilo.configure("Vertical.TScrollbar",
                              background=col["seleccion"],
                              troughcolor=col["tarjeta"],
                              borderwidth=0,
                              arrowcolor=col["texto_claro"])
        self.estilo.configure("TSeparator", background=col["borde"])


    def _crear_componentes(self):
        """Inicializa las variables y widgets del formulario y la tabla."""
        # Variables vinculadas a los campos de entrada
        self.var_monto = tk.StringVar(value="10000")
        self.var_tasa_anual = tk.StringVar(value="12.0")
        self.var_plazo_meses = tk.StringVar(value="12")
        self.var_sistema = tk.StringVar(value="Frances")

        # Variables vinculadas al resumen financiero
        self.var_total_pagado = tk.StringVar(value="Total Pagado: $0.00")
        self.var_total_interes = tk.StringVar(value="Total Intereses: $0.00")
        self.var_cuota_inicial = tk.StringVar(value="Cuota Mes 1: $0.00")

        # Variables del panel de indicadores (idea 3)
        self.var_porc_interes = tk.StringVar(value="% Interes: 0.0%")
        self.var_cuota_rango = tk.StringVar(value="Cuota min-max: $0.00 - $0.00")
        self.var_mes_cruce = tk.StringVar(value="Cruce capital>interes: Sin cruce")
        self.var_tasa_efectiva = tk.StringVar(value="Tasa efectiva anual: 0.00%")

        # Estado de abonos extra a capital (idea 2)
        self.lista_abonos = []
        self.var_abono_mes = tk.StringVar(value="")
        self.var_abono_monto = tk.StringVar(value="")
        self.var_ahorro_abonos = tk.StringVar(value="Sin abonos extra.")

        # Estado para la comparativa de dos calculos distintos (pestana Comparar)
        self.lista_filas_actual = []
        self.dict_params_actual = {}
        self.lista_tabla_a = []
        self.lista_tabla_b = []
        self.dict_params_a = {}
        self.dict_params_b = {}
        self.var_titulo_a = tk.StringVar(value="Escenario A: sin datos")
        self.var_titulo_b = tk.StringVar(value="Escenario B: sin datos")
        self.var_resumen_a = tk.StringVar(value="Total: $0.00 | Intereses: $0.00")
        self.var_resumen_b = tk.StringVar(value="Total: $0.00 | Intereses: $0.00")
        self.var_diferencia = tk.StringVar(value="Calcula y fija dos escenarios para comparar.")

        # Estado del historial persistente (pestana Historial)
        self.lista_historial = []
        self.var_contador_historial = tk.StringVar(value="0 calculos guardados")

        # Texto del boton de tema claro / oscuro (vive en Configuracion)
        texto_inicial = "Tema: Claro" if self.modo_tema == "claro" else "Tema: Oscuro"
        self.var_texto_tema = tk.StringVar(value=texto_inicial)

        # Variables de configuracion persistente (tamano, formato, exportacion)
        self.var_tamano_letra = tk.StringVar(value=self.dict_config.get("tamano_letra", "Normal"))
        self.var_decimales = tk.StringVar(value=str(self.dict_config.get("num_decimales", 2)))
        self.var_moneda = tk.StringVar(value=self.dict_config.get("simbolo_moneda", "$"))
        self.var_carpeta_export = tk.StringVar(value=self.dict_config.get("carpeta_exportacion", ""))
        self.var_incluir_logo = tk.BooleanVar(value=bool(self.dict_config.get("incluir_logo_pdf", True)))
        self.var_incluir_pie = tk.BooleanVar(value=bool(self.dict_config.get("incluir_pie_pdf", True)))

        # Estado de navegacion lateral (hamburguesa)
        self.vista_actual = "area"
        self.barra_lateral_visible = True
        self.botones_menu = {}

    def _construir_disposicion(self):
        """Organiza header con hamburguesa, sidebar y vistas conmutables."""
        # Marco principal con padding
        marco_principal = ttk.Frame(self.raiz, style="Fondo.TFrame", padding=15)
        marco_principal.pack(fill=tk.BOTH, expand=True)

        # --- Encabezado fijo: titulo mas grande sin desplazar el trabajo ---
        marco_header = ttk.Frame(marco_principal, style="Fondo.TFrame", height=80)
        marco_header.pack(fill=tk.X, pady=(0, 10))
        marco_header.pack_propagate(False)
        self.marco_header = marco_header

        marco_izq_header = ttk.Frame(marco_header, style="Fondo.TFrame")
        marco_izq_header.pack(side=tk.LEFT, anchor=tk.W)
        ttk.Button(marco_izq_header, text="☰", width=3,
                   style="Tema.TButton",
                   command=self._alternar_barra_lateral).pack(side=tk.LEFT, padx=(0, 10))

        # Cargar logo de la aplicacion en el encabezado si existe
        dir_img = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Img")
        ruta_logo = os.path.join(dir_img, "intresta-logo-horizontal.png")

        if os.path.exists(ruta_logo):
            try:
                self.img_logo_encabezado = tk.PhotoImage(file=ruta_logo)
                self.lbl_logo = tk.Label(marco_izq_header, image=self.img_logo_encabezado,
                                         bg=self.dict_colores["fondo"],
                                         borderwidth=0, highlightthickness=0)
                self.lbl_logo.pack(side=tk.LEFT, anchor=tk.W)
            except Exception:
                pass

        # Titulo a la derecha (sin boton de tema, vive en Configuracion)
        ttk.Label(marco_header,
                  text="Simulador de Intereses y Amortizaciones",
                  style="Titulo.TLabel").pack(side=tk.RIGHT, anchor=tk.E, pady=0)

        # --- Contenido: barra lateral izquierda + vistas a la derecha ---
        marco_contenido = ttk.Frame(marco_principal, style="Fondo.TFrame")
        marco_contenido.pack(fill=tk.BOTH, expand=True)
        marco_contenido.columnconfigure(1, weight=1)
        marco_contenido.rowconfigure(0, weight=1)

        self.barra_lateral = ttk.Frame(marco_contenido, style="Tarjeta.TFrame",
                                       padding=10, relief="solid", borderwidth=1)
        self.barra_lateral.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        self._construir_barra_lateral(self.barra_lateral)

        self.marco_contenido_vistas = ttk.Frame(marco_contenido, style="Fondo.TFrame")
        self.marco_contenido_vistas.grid(row=0, column=1, sticky="nsew")
        self.marco_contenido_vistas.columnconfigure(0, weight=1)
        self.marco_contenido_vistas.rowconfigure(0, weight=1)

        # Vista 1: Area de trabajo (lo que estaba al iniciar: Calcular + Comparar)
        self.marco_vista_area = ttk.Frame(self.marco_contenido_vistas, style="Fondo.TFrame")
        self.marco_vista_area.grid(row=0, column=0, sticky="nsew")
        self.cuaderno_principal = ttk.Notebook(self.marco_vista_area,
                                               style="NavegacionPrincipal.TNotebook")
        self.cuaderno_principal.pack(fill=tk.BOTH, expand=True)

        # Apartado 1: Calcular Tabla (contiene el formulario, tabla y graficas)
        marco_seccion_calculo = ttk.Frame(self.cuaderno_principal, style="Fondo.TFrame", padding=(0, 10, 0, 0))
        self.cuaderno_principal.add(marco_seccion_calculo, text="  Calcular Tabla  ")

        # Apartado 2: Comparar
        self.marco_seccion_comparar = ttk.Frame(self.cuaderno_principal, style="Fondo.TFrame", padding=(0, 10, 0, 0))
        self.cuaderno_principal.add(self.marco_seccion_comparar, text="  Comparar  ")
        self._construir_apartado_comparar(self.marco_seccion_comparar)

        # Vista 2: Historial (fuera del notebook principal)
        self.marco_vista_historial = ttk.Frame(self.marco_contenido_vistas, style="Fondo.TFrame",
                                               padding=(0, 10, 0, 0))
        self._construir_apartado_tres(self.marco_vista_historial)

        # Vista 3: Configuracion (boton de tema vive aqui)
        self.marco_vista_config = ttk.Frame(self.marco_contenido_vistas, style="Fondo.TFrame",
                                            padding=(0, 10, 0, 0))
        self._construir_vista_config(self.marco_vista_config)

        # --- Cuerpo dividido en 2 paneles (dentro del apartado Calcular Tabla) ---
        marco_cuerpo = ttk.Frame(marco_seccion_calculo, style="Fondo.TFrame")
        marco_cuerpo.pack(fill=tk.BOTH, expand=True)
        marco_cuerpo.columnconfigure(1, weight=1)
        marco_cuerpo.rowconfigure(0, weight=1)

        # Panel izquierdo: formulario y resumen
        self._construir_panel_formulario(marco_cuerpo)

        # Panel derecho: visualizacion (pestanas con tabla y graficas)
        self._construir_panel_derecho(marco_cuerpo)

        self._mostrar_vista("area")

    def _construir_barra_lateral(self, marco_padre):
        """Crea los botones verticales de navegacion lateral."""
        ttk.Label(marco_padre, text="Menu",
                  style="Seccion.TLabel").pack(anchor=tk.W, pady=(0, 10))
        for clave, texto in (("area", "⌂  Area de trabajo"),
                             ("historial", "🕓  Historial"),
                             ("config", "⚙  Configuracion")):
            boton = ttk.Button(marco_padre, text=texto, width=20,
                               style="Limpiar.TButton",
                               command=lambda c=clave: self._mostrar_vista(c))
            boton.pack(fill=tk.X, pady=4)
            self.botones_menu[clave] = boton

    def _construir_vista_config(self, marco_padre):
        """Construye la vista de configuracion con tema, letra, formato y exportacion."""
        marco_tarjeta = ttk.Frame(marco_padre, style="Tarjeta.TFrame",
                                  padding=18, relief="solid", borderwidth=1)
        marco_tarjeta.pack(fill=tk.BOTH, expand=True)
        ttk.Label(marco_tarjeta, text="Configuracion",
                  style="Seccion.TLabel").pack(anchor=tk.W, pady=(0, 4))
        ttk.Label(marco_tarjeta, text="Los cambios se guardan en config.json y se aplican al instante.",
                  style="Normal.TLabel").pack(anchor=tk.W, pady=(0, 12))

        # Apariencia: tema + tamano de letra
        ttk.Label(marco_tarjeta, text="Apariencia",
                  style="Seccion.TLabel").pack(anchor=tk.W, pady=(0, 4))
        ttk.Button(marco_tarjeta, textvariable=self.var_texto_tema,
                   style="Tema.TButton",
                   command=self._alternar_tema).pack(anchor=tk.W, pady=(0, 6))
        marco_letra = ttk.Frame(marco_tarjeta, style="Tarjeta.TFrame")
        marco_letra.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(marco_letra, text="Tamano de letra:",
                  style="Normal.TLabel").pack(side=tk.LEFT, padx=(0, 8))
        cmb_letra = ttk.Combobox(marco_letra, textvariable=self.var_tamano_letra,
                                 values=OPCIONES_TAMANO_LETRA, state="readonly", width=12)
        cmb_letra.pack(side=tk.LEFT)
        cmb_letra.bind("<<ComboboxSelected>>", lambda e: self._evento_cambiar_tamano())

        ttk.Separator(marco_tarjeta, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Formato de numeros
        ttk.Label(marco_tarjeta, text="Formato de numeros",
                  style="Seccion.TLabel").pack(anchor=tk.W, pady=(0, 4))
        marco_formato = ttk.Frame(marco_tarjeta, style="Tarjeta.TFrame")
        marco_formato.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(marco_formato, text="Decimales:",
                  style="Normal.TLabel").pack(side=tk.LEFT, padx=(0, 8))
        cmb_dec = ttk.Combobox(marco_formato, textvariable=self.var_decimales,
                               values=[str(v) for v in OPCIONES_DECIMALES],
                               state="readonly", width=6)
        cmb_dec.pack(side=tk.LEFT, padx=(0, 16))
        cmb_dec.bind("<<ComboboxSelected>>", lambda e: self._evento_cambiar_formato())
        ttk.Label(marco_formato, text="Moneda:",
                  style="Normal.TLabel").pack(side=tk.LEFT, padx=(0, 8))
        cmb_mon = ttk.Combobox(marco_formato, textvariable=self.var_moneda,
                               values=OPCIONES_MONEDA, state="readonly", width=8)
        cmb_mon.pack(side=tk.LEFT)
        cmb_mon.bind("<<ComboboxSelected>>", lambda e: self._evento_cambiar_formato())

        ttk.Separator(marco_tarjeta, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Defaults de exportacion
        ttk.Label(marco_tarjeta, text="Exportacion (PDF / Excel)",
                  style="Seccion.TLabel").pack(anchor=tk.W, pady=(0, 4))
        marco_carpeta = ttk.Frame(marco_tarjeta, style="Tarjeta.TFrame")
        marco_carpeta.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(marco_carpeta, text="Carpeta destino:",
                  style="Normal.TLabel").pack(side=tk.LEFT, padx=(0, 8))
        ttk.Entry(marco_carpeta, textvariable=self.var_carpeta_export, width=32).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 8))
        ttk.Button(marco_carpeta, text="Examinar...",
                   style="Limpiar.TButton",
                   command=self._elegir_carpeta_exportacion).pack(side=tk.LEFT)
        ttk.Checkbutton(marco_tarjeta, text="Incluir logo en PDF",
                        variable=self.var_incluir_logo,
                        command=self._evento_cambiar_export).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(marco_tarjeta, text="Incluir pie de pagina en PDF",
                        variable=self.var_incluir_pie,
                        command=self._evento_cambiar_export).pack(anchor=tk.W, pady=2)
        marco_cfg_bot = ttk.Frame(marco_tarjeta, style="Tarjeta.TFrame")
        marco_cfg_bot.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(marco_cfg_bot, text="Restablecer valores",
                   style="Limpiar.TButton",
                   command=self._restablecer_config).pack(side=tk.LEFT)

    def _evento_cambiar_tamano(self):
        """Guarda el tamano de letra y re-aplica estilos."""
        self.dict_config["tamano_letra"] = self.var_tamano_letra.get()
        self._aplicar_configuracion()

    def _evento_cambiar_formato(self):
        """Guarda decimales y moneda y re-formatea tablas y resumenes."""
        try:
            self.dict_config["num_decimales"] = int(self.var_decimales.get())
        except ValueError:
            self.dict_config["num_decimales"] = 2
        self.dict_config["simbolo_moneda"] = self.var_moneda.get()
        self._aplicar_configuracion()

    def _evento_cambiar_export(self):
        """Guarda carpeta y banderas de PDF para las proximas exportaciones."""
        self.dict_config["carpeta_exportacion"] = self.var_carpeta_export.get().strip()
        self.dict_config["incluir_logo_pdf"] = bool(self.var_incluir_logo.get())
        self.dict_config["incluir_pie_pdf"] = bool(self.var_incluir_pie.get())
        self._guardar_config_actual()

    def _elegir_carpeta_exportacion(self):
        """Permite elegir la carpeta destino por defecto para exportar."""
        ruta_elegida = filedialog.askdirectory(title="Elegir carpeta de exportacion")
        if ruta_elegida:
            self.var_carpeta_export.set(ruta_elegida)
            self._evento_cambiar_export()

    def _restablecer_config(self):
        """Vuelve a los valores por defecto y refresca la vista de configuracion."""
        self.dict_config = {"tema": self.modo_tema, "tamano_letra": "Normal",
                            "num_decimales": 2, "simbolo_moneda": "$",
                            "carpeta_exportacion": "",
                            "incluir_logo_pdf": True, "incluir_pie_pdf": True}
        self.var_tamano_letra.set("Normal")
        self.var_decimales.set("2")
        self.var_moneda.set("$")
        self.var_carpeta_export.set("")
        self.var_incluir_logo.set(True)
        self.var_incluir_pie.set(True)
        self._aplicar_configuracion()

    def _carpeta_inicial_export(self) -> str | None:
        """Retorna la carpeta configurada si existe, None para dialogo por defecto."""
        ruta_carpeta = self.dict_config.get("carpeta_exportacion", "").strip()
        if ruta_carpeta and os.path.isdir(ruta_carpeta):
            return ruta_carpeta
        return None

    def _alternar_barra_lateral(self):
        """Muestra u oculta la barra lateral izquierda."""
        if self.barra_lateral_visible:
            self.barra_lateral.grid_remove()
            self.barra_lateral_visible = False
        else:
            self.barra_lateral.grid()
            self.barra_lateral_visible = True

    def _mostrar_vista(self, nombre_vista: str):
        """Conmuta entre area de trabajo, historial y configuracion."""
        self.vista_actual = nombre_vista
        self.marco_vista_area.grid_remove()
        self.marco_vista_historial.grid_remove()
        self.marco_vista_config.grid_remove()
        if nombre_vista == "historial":
            self.marco_vista_historial.grid(row=0, column=0, sticky="nsew")
            self._actualizar_vista_historial()
        elif nombre_vista == "config":
            self.marco_vista_config.grid(row=0, column=0, sticky="nsew")
        else:
            self.marco_vista_area.grid(row=0, column=0, sticky="nsew")
        for clave, boton in self.botones_menu.items():
            boton.state(["pressed"] if clave == nombre_vista else ["!pressed"])

    def _construir_apartado_comparar(self, marco_padre):
        """Construye la vista del apartado Comparar con micro barra Tablas/Grafica."""
        marco_tarjeta = ttk.Frame(marco_padre, style="Tarjeta.TFrame",
                                  padding=12, relief="solid", borderwidth=1)
        marco_tarjeta.pack(fill=tk.BOTH, expand=True)

        # Encabezado con titulo a la izquierda y botones a la derecha y arriba
        marco_encabezado = ttk.Frame(marco_tarjeta, style="Tarjeta.TFrame")
        marco_encabezado.pack(fill=tk.X, pady=(0, 8))
        marco_encabezado.columnconfigure(0, weight=1)

        marco_titulos = ttk.Frame(marco_encabezado, style="Tarjeta.TFrame")
        marco_titulos.grid(row=0, column=0, sticky="nw")
        ttk.Label(marco_titulos, text="Comparar dos calculos distintos",
                  style="Seccion.TLabel").pack(anchor=tk.W, pady=(0, 2))
        ttk.Label(marco_titulos,
                  text="Calcula en 'Calcular Tabla', luego fija el resultado como A o B para verlos en paralelo.",
                  style="Normal.TLabel").pack(anchor=tk.W)

        # Barra de acciones alineada a la derecha y arriba
        marco_acciones = ttk.Frame(marco_encabezado, style="Tarjeta.TFrame")
        marco_acciones.grid(row=0, column=1, sticky="ne", padx=(10, 0))
        ttk.Button(marco_acciones, text="Fijar actual como A",
                   style="Calcular.TButton",
                   command=lambda: self._fijar_escenario_comparar("A")).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(marco_acciones, text="Fijar actual como B",
                   style="Calcular.TButton",
                   command=lambda: self._fijar_escenario_comparar("B")).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(marco_acciones, text="Limpiar comparativa",
                   style="Limpiar.TButton",
                   command=self._limpiar_comparar).pack(side=tk.LEFT, padx=(0, 6))
        boton_exportar_comp = ttk.Menubutton(marco_acciones, text="Exportar a ▾",
                                             style="Limpiar.TButton")
        boton_exportar_comp.pack(side=tk.LEFT)
        menu_exportar_comp = tk.Menu(boton_exportar_comp, tearoff=0)
        menu_exportar_comp.add_command(label="PDF (.pdf)",
                                       command=lambda: self._evento_exportar_comparar("pdf"))
        menu_exportar_comp.add_command(label="Excel (.xlsx)",
                                       command=lambda: self._evento_exportar_comparar("excel"))
        boton_exportar_comp.configure(menu=menu_exportar_comp)

        # Micro barra inferior con vistas Tablas y Grafica
        self.cuaderno_vistas_comparar = ttk.Notebook(marco_tarjeta)
        self.cuaderno_vistas_comparar.pack(fill=tk.BOTH, expand=True)

        # Vista 1: Tablas (lo que ya hay)
        marco_vista_tablas = ttk.Frame(self.cuaderno_vistas_comparar, style="Tarjeta.TFrame", padding=8)
        self.cuaderno_vistas_comparar.add(marco_vista_tablas, text="  Tablas  ")
        self._construir_vista_tablas_paralelas(marco_vista_tablas)

        # Vista 2: Grafica comparativa A vs B
        self.marco_vista_grafica = ttk.Frame(self.cuaderno_vistas_comparar, style="Tarjeta.TFrame", padding=8)
        self.cuaderno_vistas_comparar.add(self.marco_vista_grafica, text="  Grafica  ")
        self._actualizar_grafica_comparar()

        # Resumen de diferencias
        ttk.Label(marco_tarjeta, textvariable=self.var_diferencia,
                  style="Resumen.TLabel").pack(anchor=tk.W, pady=(8, 0))

    def _construir_vista_tablas_paralelas(self, marco_padre):
        """Construye las dos tablas en paralelo dentro de la vista Tablas."""
        marco_paralelo = ttk.Frame(marco_padre, style="Tarjeta.TFrame")
        marco_paralelo.pack(fill=tk.BOTH, expand=True)
        marco_paralelo.columnconfigure(0, weight=1)
        marco_paralelo.columnconfigure(1, weight=1)
        marco_paralelo.rowconfigure(0, weight=1)

        # Escenario A (izquierda)
        marco_a = ttk.Frame(marco_paralelo, style="Tarjeta.TFrame", padding=6)
        marco_a.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ttk.Label(marco_a, textvariable=self.var_titulo_a,
                  style="Resumen.TLabel").pack(anchor=tk.W, pady=(0, 4))
        self.tabla_comparar_a = self._crear_treeview_comparar(marco_a)
        ttk.Label(marco_a, textvariable=self.var_resumen_a,
                  style="Normal.TLabel").pack(anchor=tk.W, pady=(4, 0))

        # Escenario B (derecha)
        marco_b = ttk.Frame(marco_paralelo, style="Tarjeta.TFrame", padding=6)
        marco_b.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        ttk.Label(marco_b, textvariable=self.var_titulo_b,
                  style="Resumen.TLabel").pack(anchor=tk.W, pady=(0, 4))
        self.tabla_comparar_b = self._crear_treeview_comparar(marco_b)
        ttk.Label(marco_b, textvariable=self.var_resumen_b,
                  style="Normal.TLabel").pack(anchor=tk.W, pady=(4, 0))

    def _crear_treeview_comparar(self, marco_padre):
        """Crea un Treeview reutilizable para las tablas paralelas A y B."""
        marco_scroll = ttk.Frame(marco_padre, style="Tarjeta.TFrame")
        marco_scroll.pack(fill=tk.BOTH, expand=True)
        columnas = ("mes", "cuota", "interes", "capital", "saldo")
        tabla = ttk.Treeview(marco_scroll, columns=columnas,
                             show="headings", style="Tabla.Treeview", height=12)
        tabla.heading("mes", text="Mes")
        tabla.heading("cuota", text="Cuota ($)")
        tabla.heading("interes", text="Interes ($)")
        tabla.heading("capital", text="Capital ($)")
        tabla.heading("saldo", text="Saldo ($)")
        tabla.column("mes", width=50, anchor=tk.CENTER)
        tabla.column("cuota", width=100, anchor=tk.E)
        tabla.column("interes", width=100, anchor=tk.E)
        tabla.column("capital", width=100, anchor=tk.E)
        tabla.column("saldo", width=120, anchor=tk.E)
        barra_scroll = ttk.Scrollbar(marco_scroll, orient=tk.VERTICAL, command=tabla.yview)
        tabla.configure(yscrollcommand=barra_scroll.set)
        tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        barra_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        return tabla

    def _fijar_escenario_comparar(self, letra_escenario: str):
        """Guarda el calculo actual como escenario A o B y refresca la vista."""
        if not self.lista_filas_actual:
            self._mostrar_alerta("Primero calcula una tabla en 'Calcular Tabla'.")
            return
        if letra_escenario == "A":
            self.lista_tabla_a = list(self.lista_filas_actual)
            self.dict_params_a = dict(self.dict_params_actual)
        else:
            self.lista_tabla_b = list(self.lista_filas_actual)
            self.dict_params_b = dict(self.dict_params_actual)
        self._actualizar_vista_comparar()

    def _limpiar_comparar(self):
        """Limpia los dos escenarios de la comparativa."""
        self.lista_tabla_a = []
        self.lista_tabla_b = []
        self.dict_params_a = {}
        self.dict_params_b = {}
        self._actualizar_vista_comparar()

    def _fijar_comparativa_abonos(self, lista_base: list[dict], lista_con_abonos: list[dict],
                                  str_sistema: str, val_monto: float, val_tasa: float,
                                  num_meses: int):
        """Fija A sin abonos y B con abonos y muestra el ahorro en el formulario."""
        params_base = {"sistema": str_sistema, "monto": val_monto,
                       "tasa": val_tasa, "meses": num_meses, "abonos": []}
        self.lista_tabla_a = list(lista_base)
        self.dict_params_a = params_base
        self.lista_tabla_b = list(lista_con_abonos)
        self.dict_params_b = dict(self.dict_params_actual)
        self._actualizar_vista_comparar()
        total_base, interes_base = self._calcular_totales_lista(lista_base)
        total_abono, interes_abono = self._calcular_totales_lista(lista_con_abonos)
        ahorro_interes = interes_base - interes_abono
        meses_ahorrados = len(lista_base) - len(lista_con_abonos)
        texto_meses = f" y {meses_ahorrados} meses menos" if meses_ahorrados > 0 else ""
        self.var_ahorro_abonos.set(
            f"Ahorro: {self._formatear_moneda(ahorro_interes)} en intereses{texto_meses} (ver Comparar A/B).")

    def _rellenar_treeview_comparar(self, tabla_destino, lista_filas: list[dict]):
        """Limpia y rellena un Treeview de comparativa con filas calculadas."""
        for item in tabla_destino.get_children():
            tabla_destino.delete(item)
        for fila in lista_filas:
            tabla_destino.insert("", tk.END, values=(
                fila["mes"],
                self._formatear_moneda(fila['cuota']),
                self._formatear_moneda(fila['interes']),
                self._formatear_moneda(fila['capital']),
                self._formatear_moneda(fila['saldo'])
            ))

    def _formatear_titulo_escenario(self, letra_escenario: str, dict_params: dict) -> str:
        """Arma el titulo descriptivo de un escenario con sus parametros."""
        if not dict_params:
            return f"Escenario {letra_escenario}: sin datos"
        num_abonos = len(dict_params.get("abonos", []))
        texto_abonos = f" +{num_abonos} abonos" if num_abonos else " sin abonos"
        return (f"Escenario {letra_escenario}: {dict_params.get('sistema', '')} | "
                f"Monto {self._formatear_moneda(dict_params.get('monto', 0))} | "
                f"Tasa {dict_params.get('tasa', 0)}% | "
                f"{dict_params.get('meses', 0)} meses ({len(self.lista_tabla_a if letra_escenario == 'A' else self.lista_tabla_b)} filas{texto_abonos})")

    def _actualizar_vista_comparar(self):
        """Refresca titulos, tablas, resumenes, diferencias y grafica de la comparativa."""
        self._rellenar_treeview_comparar(self.tabla_comparar_a, self.lista_tabla_a)
        self._rellenar_treeview_comparar(self.tabla_comparar_b, self.lista_tabla_b)
        self.var_titulo_a.set(self._formatear_titulo_escenario("A", self.dict_params_a))
        self.var_titulo_b.set(self._formatear_titulo_escenario("B", self.dict_params_b))

        total_a, interes_a = self._calcular_totales_lista(self.lista_tabla_a)
        total_b, interes_b = self._calcular_totales_lista(self.lista_tabla_b)
        self.var_resumen_a.set(f"Total: {self._formatear_moneda(total_a)} | Intereses: {self._formatear_moneda(interes_a)}")
        self.var_resumen_b.set(f"Total: {self._formatear_moneda(total_b)} | Intereses: {self._formatear_moneda(interes_b)}")

        if self.lista_tabla_a and self.lista_tabla_b:
            dif_total = total_a - total_b
            dif_interes = interes_a - interes_b
            self.var_diferencia.set(
                f"Diferencia A-B: Total {dif_total:+,.2f} | Intereses {dif_interes:+,.2f}"
            )
        else:
            self.var_diferencia.set("Calcula y fija dos escenarios para comparar.")

        self._actualizar_grafica_comparar()

    def _actualizar_grafica_comparar(self):
        """Genera y renderiza la grafica comparativa A vs B en la vista Grafica."""
        figura_escenarios = generar_figura_comparativa_escenarios(
            self.lista_tabla_a, self.lista_tabla_b, "A", "B"
        )
        renderizar_lienzo_en_contenedor(figura_escenarios, self.marco_vista_grafica)

    def _calcular_totales_lista(self, lista_filas: list[dict]):
        """Calcula el total pagado y el total de intereses de una lista de filas."""
        if not lista_filas:
            return 0.0, 0.0
        total_pagado = sum(fila["cuota"] for fila in lista_filas)
        total_interes = sum(fila["interes"] for fila in lista_filas)
        return total_pagado, total_interes

    def _construir_apartado_tres(self, marco_padre):
        """Construye la vista del historial persistente en JSON."""
        marco_tarjeta = ttk.Frame(marco_padre, style="Tarjeta.TFrame",
                                  padding=12, relief="solid", borderwidth=1)
        marco_tarjeta.pack(fill=tk.BOTH, expand=True)

        # Encabezado con contador a la izquierda y limpieza a la derecha
        marco_encabezado = ttk.Frame(marco_tarjeta, style="Tarjeta.TFrame")
        marco_encabezado.pack(fill=tk.X, pady=(0, 8))
        marco_encabezado.columnconfigure(0, weight=1)
        ttk.Label(marco_encabezado, text="Historial de calculos",
                  style="Seccion.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(marco_encabezado, textvariable=self.var_contador_historial,
                  style="Normal.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Button(marco_encabezado, text="Limpiar todo",
                   style="Limpiar.TButton",
                   command=self._limpiar_todo_historial).grid(row=0, column=1, rowspan=2, sticky="ne")

        # Area con scroll para las filas del historial
        marco_scroll = ttk.Frame(marco_tarjeta, style="Tarjeta.TFrame")
        marco_scroll.pack(fill=tk.BOTH, expand=True)
        self.lienzo_historial = tk.Canvas(marco_scroll, bg=self.dict_colores["tarjeta"], highlightthickness=0)
        lienzo_historial = self.lienzo_historial
        barra_historial = ttk.Scrollbar(marco_scroll, orient=tk.VERTICAL, command=lienzo_historial.yview)
        self.marco_filas_historial = ttk.Frame(lienzo_historial, style="Tarjeta.TFrame")
        self.marco_filas_historial.bind(
            "<Configure>",
            lambda evento: lienzo_historial.configure(scrollregion=lienzo_historial.bbox("all"))
        )
        lienzo_historial.create_window((0, 0), window=self.marco_filas_historial, anchor="nw")
        lienzo_historial.configure(yscrollcommand=barra_historial.set)
        lienzo_historial.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        barra_historial.pack(side=tk.RIGHT, fill=tk.Y)

    def _ruta_archivo_historial(self) -> str:
        """Retorna la ruta del archivo JSON del historial."""
        dir_actual = os.path.dirname(os.path.abspath(__file__))
        return os.path.normpath(os.path.join(dir_actual, "..", NOMBRE_ARCHIVO_HISTORIAL))

    def _cargar_historial_desde_json(self):
        """Carga la lista del historial desde el archivo JSON si existe."""
        ruta_archivo = self._ruta_archivo_historial()
        if not os.path.exists(ruta_archivo):
            self.lista_historial = []
            return
        try:
            with open(ruta_archivo, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
            self.lista_historial = datos if isinstance(datos, list) else []
        except Exception:
            self.lista_historial = []

    def _guardar_historial_en_json(self):
        """Guarda la lista del historial en el archivo JSON."""
        try:
            with open(self._ruta_archivo_historial(), "w", encoding="utf-8") as archivo:
                json.dump(self.lista_historial, archivo, indent=2, ensure_ascii=False)
        except Exception as obj_err:
            self._mostrar_alerta(f"No se pudo guardar el historial: {obj_err}")

    def _agregar_actual_a_historial(self, lista_filas: list[dict]):
        """Agrega el calculo actual al historial y lo persiste."""
        total_pagado, total_interes = self._calcular_totales_lista(lista_filas)
        nueva_entrada = {
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "monto": self.dict_params_actual.get("monto", 0.0),
            "tasa": self.dict_params_actual.get("tasa", 0.0),
            "meses": self.dict_params_actual.get("meses", 0),
            "sistema": self.dict_params_actual.get("sistema", ""),
            "abonos": [dict(abono) for abono in self.dict_params_actual.get("abonos", [])],
            "total": total_pagado,
            "interes": total_interes
        }
        self.lista_historial.insert(0, nueva_entrada)
        self.lista_historial = self.lista_historial[:MAX_ENTRADAS_HISTORIAL]
        self._guardar_historial_en_json()
        self._actualizar_vista_historial()

    def _actualizar_vista_historial(self):
        """Reconstruye las filas del historial con boton central y borrar a la derecha."""
        if not hasattr(self, "marco_filas_historial"):
            return
        for widget_hijo in self.marco_filas_historial.winfo_children():
            widget_hijo.destroy()
        self.var_contador_historial.set(f"{len(self.lista_historial)} calculos guardados")
        if not self.lista_historial:
            ttk.Label(self.marco_filas_historial, text="Sin calculos aun. Calcula en 'Calcular Tabla'.",
                      style="Normal.TLabel").pack(anchor=tk.W, pady=8)
            return
        for num_indice, dict_entrada in enumerate(self.lista_historial):
            self._crear_fila_historial(num_indice, dict_entrada)

    def _crear_fila_historial(self, num_indice: int, dict_entrada: dict):
        """Crea una fila del historial con boton al centro-izquierda y borrar a la derecha."""
        marco_fila = ttk.Frame(self.marco_filas_historial, style="Tarjeta.TFrame",
                               padding=6, relief="solid", borderwidth=1)
        marco_fila.pack(fill=tk.X, pady=3, padx=2)
        marco_fila.columnconfigure(0, weight=1)
        str_texto = (f"{self._formatear_moneda(dict_entrada.get('monto', 0))} | {dict_entrada.get('fecha', '')} | "
                     f"{dict_entrada.get('sistema', '')}")
        num_abonos_hist = len(dict_entrada.get("abonos", []))
        if num_abonos_hist:
            str_texto += f" +{num_abonos_hist} abonos"
        ttk.Button(marco_fila, text=str_texto, style="Limpiar.TButton",
                   command=lambda idx=num_indice: self._cargar_historial_en_ventana(idx)).grid(
                       row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(marco_fila, text="Borrar", style="Limpiar.TButton",
                   command=lambda idx=num_indice: self._borrar_entrada_historial(idx)).grid(
                       row=0, column=1, sticky="e")

    def _cargar_historial_en_ventana(self, num_indice: int):
        """Recalcula un historial con C++ y lo muestra sin duplicarlo."""
        try:
            dict_entrada = self.lista_historial[num_indice]
        except IndexError:
            return
        try:
            lista_abonos_hist = [dict(abono) for abono in dict_entrada.get("abonos", [])]
            lista_filas = calcular_amortizacion(
                str(dict_entrada.get("sistema", "Frances")),
                float(dict_entrada.get("monto", 0)),
                float(dict_entrada.get("tasa", 0)),
                int(dict_entrada.get("meses", 0)),
                lista_abonos_hist if lista_abonos_hist else None
            )
        except Exception as obj_err:
            self._mostrar_alerta(f"No se pudo recargar el historial: {obj_err}")
            return
        self.var_monto.set(str(dict_entrada.get("monto", "")))
        self.var_tasa_anual.set(str(dict_entrada.get("tasa", "")))
        self.var_plazo_meses.set(str(dict_entrada.get("meses", "")))
        self.var_sistema.set(str(dict_entrada.get("sistema", "")))
        self.lista_abonos = [dict(abono) for abono in dict_entrada.get("abonos", [])]
        self._refrescar_lista_abonos()
        self.lista_filas_actual = list(lista_filas)
        self.dict_params_actual = {
            "sistema": str(dict_entrada.get("sistema", "")),
            "monto": float(dict_entrada.get("monto", 0)),
            "tasa": float(dict_entrada.get("tasa", 0)),
            "meses": int(dict_entrada.get("meses", 0)),
            "abonos": [dict(abono) for abono in dict_entrada.get("abonos", [])],
        }
        self._actualizar_tabla(lista_filas)
        self._actualizar_resumen(lista_filas, float(dict_entrada.get("tasa", 0)))
        self._actualizar_graficas(lista_filas)
        self._mostrar_vista("area")
        self.cuaderno_principal.select(0)

    def _borrar_entrada_historial(self, num_indice: int):
        """Quita una entrada del historial y actualiza el archivo."""
        if 0 <= num_indice < len(self.lista_historial):
            del self.lista_historial[num_indice]
            self._guardar_historial_en_json()
            self._actualizar_vista_historial()

    def _limpiar_todo_historial(self):
        """Borra todo el historial persistente."""
        if not self.lista_historial:
            return
        if messagebox.askyesno("Historial", "¿Borrar todo el historial guardado?"):
            self.lista_historial = []
            self._guardar_historial_en_json()
            self._actualizar_vista_historial()

    def _construir_panel_formulario(self, marco_padre):
        """Construye el panel izquierdo con scroll para campos, resumen e indicadores."""
        marco_form = ttk.Frame(marco_padre, style="Tarjeta.TFrame",
                               padding=18, relief="solid", borderwidth=1)
        marco_form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        marco_form.columnconfigure(0, weight=1)
        marco_form.rowconfigure(0, weight=1)

        # Lienzo con scroll vertical para que nada quede recortado
        self.lienzo_formulario = tk.Canvas(marco_form, bg=self.dict_colores["tarjeta"],
                                           highlightthickness=0)
        barra_form = ttk.Scrollbar(marco_form, orient=tk.VERTICAL,
                                   command=self.lienzo_formulario.yview)
        marco_interno = ttk.Frame(self.lienzo_formulario, style="Tarjeta.TFrame")
        marco_interno.bind(
            "<Configure>",
            lambda evento: self.lienzo_formulario.configure(
                scrollregion=self.lienzo_formulario.bbox("all"))
        )
        self.lienzo_formulario.create_window((0, 0), window=marco_interno, anchor="nw",
                                               tags="ventana_form")
        self.lienzo_formulario.configure(yscrollcommand=barra_form.set)
        self.lienzo_formulario.bind(
            "<Configure>",
            lambda evento: self.lienzo_formulario.itemconfig(
                "ventana_form", width=evento.width))
        self.lienzo_formulario.grid(row=0, column=0, sticky="nsew")
        barra_form.grid(row=0, column=1, sticky="ns")
        self.lienzo_formulario.bind(
            "<MouseWheel>",
            lambda evento: self.lienzo_formulario.yview_scroll(
                -1 if evento.delta > 0 else 1, "units"))
        marco_form = marco_interno

        # Titulo de seccion
        ttk.Label(marco_form, text="Parametros del Credito",
                  style="Seccion.TLabel").pack(anchor=tk.W, pady=(0, 10))

        # Campos de entrada: monto, tasa, plazo
        self._crear_campo_entrada(marco_form, "Monto del Prestamo ($):", self.var_monto)
        self._crear_campo_entrada(marco_form, "Tasa de Interes Anual (%):", self.var_tasa_anual)
        self._crear_campo_entrada(marco_form, "Plazo en Meses:", self.var_plazo_meses)

        # Selector de sistema de amortizacion
        ttk.Label(marco_form, text="Sistema de Amortizacion:",
                  style="Normal.TLabel").pack(anchor=tk.W, pady=(6, 2))
        cmb_sistema = ttk.Combobox(marco_form, textvariable=self.var_sistema,
                                   values=OPCIONES_SISTEMAS, state="readonly",
                                   font=("Segoe UI", 10))
        cmb_sistema.pack(fill=tk.X, pady=(0, 10))

        # Botones de accion
        marco_botones = ttk.Frame(marco_form, style="Tarjeta.TFrame")
        marco_botones.pack(fill=tk.X, pady=(5, 10))

        ttk.Button(marco_botones, text="Calcular Tabla",
                   style="Calcular.TButton",
                   command=self._evento_calcular).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        ttk.Button(marco_botones, text="Limpiar",
                   style="Limpiar.TButton",
                   command=self._evento_limpiar).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        # Separador visual
        ttk.Separator(marco_form, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Resumen financiero
        ttk.Label(marco_form, text="Resumen Financiero",
                  style="Seccion.TLabel").pack(anchor=tk.W, pady=(0, 8))

        ttk.Label(marco_form, textvariable=self.var_cuota_inicial,
                  style="ResumenVerde.TLabel").pack(anchor=tk.W, pady=2)
        ttk.Label(marco_form, textvariable=self.var_total_interes,
                  style="ResumenRojo.TLabel").pack(anchor=tk.W, pady=2)
        ttk.Label(marco_form, textvariable=self.var_total_pagado,
                  style="Resumen.TLabel").pack(anchor=tk.W, pady=2)

        # Separador visual
        ttk.Separator(marco_form, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Panel de indicadores
        ttk.Label(marco_form, text="Indicadores",
                  style="Seccion.TLabel").pack(anchor=tk.W, pady=(0, 8))

        ttk.Label(marco_form, textvariable=self.var_porc_interes,
                  style="Normal.TLabel").pack(anchor=tk.W, pady=2)
        ttk.Label(marco_form, textvariable=self.var_cuota_rango,
                  style="Normal.TLabel").pack(anchor=tk.W, pady=2)
        ttk.Label(marco_form, textvariable=self.var_mes_cruce,
                  style="Normal.TLabel").pack(anchor=tk.W, pady=2)
        ttk.Label(marco_form, textvariable=self.var_tasa_efectiva,
                  style="Normal.TLabel").pack(anchor=tk.W, pady=2)

        # Separador visual
        ttk.Separator(marco_form, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Abonos extra a capital (idea 2)
        ttk.Label(marco_form, text="Abonos Extra a Capital",
                  style="Seccion.TLabel").pack(anchor=tk.W, pady=(0, 4))
        ttk.Label(marco_form, text="Mes y monto que se suman al capital de esa cuota.",
                  style="Normal.TLabel", wraplength=240).pack(anchor=tk.W, pady=(0, 6))

        marco_abono_campos = ttk.Frame(marco_form, style="Tarjeta.TFrame")
        marco_abono_campos.pack(fill=tk.X)
        marco_abono_campos.columnconfigure(0, weight=1)
        marco_abono_campos.columnconfigure(1, weight=1)
        ttk.Label(marco_abono_campos, text="Mes:",
                  style="Normal.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(marco_abono_campos, text="Monto ($):",
                  style="Normal.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Entry(marco_abono_campos, textvariable=self.var_abono_mes,
                  font=("Segoe UI", 10), width=10).grid(row=1, column=0, sticky="ew", padx=(0, 4))
        ttk.Entry(marco_abono_campos, textvariable=self.var_abono_monto,
                  font=("Segoe UI", 10), width=12).grid(row=1, column=1, sticky="ew", padx=(4, 0))

        marco_abono_botones = ttk.Frame(marco_form, style="Tarjeta.TFrame")
        marco_abono_botones.pack(fill=tk.X, pady=(6, 4))
        ttk.Button(marco_abono_botones, text="Agregar abono",
                   style="Calcular.TButton",
                   command=self._agregar_abono).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        ttk.Button(marco_abono_botones, text="Quitar",
                   style="Limpiar.TButton",
                   command=self._quitar_abono).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        self.lista_widget_abonos = tk.Listbox(marco_form, height=3, font=("Segoe UI", 9))
        self.lista_widget_abonos.pack(fill=tk.X, pady=(0, 4))

        ttk.Label(marco_form, textvariable=self.var_ahorro_abonos,
                  style="ResumenVerde.TLabel", wraplength=240).pack(anchor=tk.W, pady=2)

    def _crear_campo_entrada(self, marco_padre, str_etiqueta, var_texto):
        """Crea un par etiqueta + campo de texto reutilizable."""
        ttk.Label(marco_padre, text=str_etiqueta,
                  style="Normal.TLabel").pack(anchor=tk.W, pady=(6, 2))
        entrada = ttk.Entry(marco_padre, textvariable=var_texto,
                            font=("Segoe UI", 10))
        entrada.pack(fill=tk.X, pady=(0, 4))

    def _agregar_abono(self):
        """Valida y agrega un abono extra a la lista en memoria."""
        try:
            num_mes = int(self.var_abono_mes.get().strip())
            val_monto = float(self.var_abono_monto.get().strip())
        except ValueError:
            self._mostrar_alerta("Mes y monto del abono deben ser numericos.")
            return
        if num_mes <= 0:
            self._mostrar_alerta("El mes del abono debe ser mayor a 0.")
            return
        if val_monto <= 0:
            self._mostrar_alerta("El monto del abono debe ser mayor a 0.")
            return
        try:
            num_plazo = int(self.var_plazo_meses.get().strip())
        except ValueError:
            num_plazo = 0
        if num_plazo > 0 and num_mes > num_plazo:
            self._mostrar_alerta("El mes del abono no puede superar el plazo.")
            return
        self.lista_abonos.append({"mes": num_mes, "monto": val_monto})
        self.lista_abonos.sort(key=lambda abono: abono["mes"])
        self.var_abono_mes.set("")
        self.var_abono_monto.set("")
        self._refrescar_lista_abonos()

    def _quitar_abono(self):
        """Quita el abono seleccionado de la lista en memoria."""
        if not hasattr(self, "lista_widget_abonos"):
            return
        seleccion = self.lista_widget_abonos.curselection()
        if not seleccion:
            self._mostrar_alerta("Selecciona un abono de la lista para quitarlo.")
            return
        del self.lista_abonos[seleccion[0]]
        self._refrescar_lista_abonos()

    def _refrescar_lista_abonos(self):
        """Redibuja el listbox con los abonos en formato mes y monto."""
        if not hasattr(self, "lista_widget_abonos"):
            return
        self.lista_widget_abonos.delete(0, tk.END)
        for abono in self.lista_abonos:
            self.lista_widget_abonos.insert(
                tk.END, f"Mes {abono['mes']}: {self._formatear_moneda(abono['monto'])}")

    def _construir_panel_derecho(self, marco_padre):
        """Construye el panel derecho con pestanas para la tabla y las graficas."""
        marco_derecho = ttk.Frame(marco_padre, style="Tarjeta.TFrame",
                                  padding=10, relief="solid", borderwidth=1)
        marco_derecho.grid(row=0, column=1, sticky="nsew")

        # Cuaderno de pestanas para organizar las vistas
        self.pestanas = ttk.Notebook(marco_derecho)
        self.pestanas.pack(fill=tk.BOTH, expand=True)


        # Pestana 1: Tabla de pagos detallada del sistema seleccionado
        marco_pestana_tabla = ttk.Frame(self.pestanas, style="Tarjeta.TFrame", padding=10)
        self.pestanas.add(marco_pestana_tabla, text="  Tabla de Pagos  ")
        self._construir_contenido_tabla(marco_pestana_tabla)

        # Pestana 2: Relacion interes-capital del sistema seleccionado
        self.marco_pestana_relacion = ttk.Frame(self.pestanas, style="Tarjeta.TFrame", padding=10)
        self.pestanas.add(self.marco_pestana_relacion, text="  Relacion Interes-Capital  ")

        # Inicializacion de lienzo vacio de grafica
        self._limpiar_graficas()

    def _construir_contenido_tabla(self, marco_padre):
        """Construye la vista de la tabla Treeview y su barra de desplazamiento."""
        # Encabezado con titulo a la izquierda y boton Exportar a la derecha
        marco_enc_tabla = ttk.Frame(marco_padre, style="Tarjeta.TFrame")
        marco_enc_tabla.pack(fill=tk.X, pady=(0, 8))
        marco_enc_tabla.columnconfigure(0, weight=1)
        ttk.Label(marco_enc_tabla, text="Tabla de Pagos Detallada (Sistema Seleccionado)",
                  style="Seccion.TLabel").grid(row=0, column=0, sticky="w")
        boton_exportar = ttk.Menubutton(marco_enc_tabla, text="Exportar a ▾",
                                        style="Limpiar.TButton")
        boton_exportar.grid(row=0, column=1, sticky="e", padx=(8, 0))
        menu_exportar = tk.Menu(boton_exportar, tearoff=0)
        menu_exportar.add_command(label="PDF (.pdf)",
                                  command=lambda: self._evento_exportar("pdf"))
        menu_exportar.add_command(label="Excel (.xlsx)",
                                  command=lambda: self._evento_exportar("excel"))
        boton_exportar.configure(menu=menu_exportar)

        # Contenedor de la tabla con scrollbar
        marco_scroll = ttk.Frame(marco_padre, style="Tarjeta.TFrame")
        marco_scroll.pack(fill=tk.BOTH, expand=True)

        columnas = ("mes", "cuota", "interes", "capital", "saldo")
        self.tabla_datos = ttk.Treeview(marco_scroll, columns=columnas,
                                        show="headings", style="Tabla.Treeview")

        # Configuracion de encabezados y anchos de columna
        self.tabla_datos.heading("mes", text="Mes")
        self.tabla_datos.heading("cuota", text="Cuota ($)")
        self.tabla_datos.heading("interes", text="Interes ($)")
        self.tabla_datos.heading("capital", text="Capital ($)")
        self.tabla_datos.heading("saldo", text="Saldo Pendiente ($)")

        self.tabla_datos.column("mes", width=60, anchor=tk.CENTER)
        self.tabla_datos.column("cuota", width=120, anchor=tk.E)
        self.tabla_datos.column("interes", width=120, anchor=tk.E)
        self.tabla_datos.column("capital", width=120, anchor=tk.E)
        self.tabla_datos.column("saldo", width=150, anchor=tk.E)

        # Scrollbar vertical vinculada a la tabla
        barra_scroll = ttk.Scrollbar(marco_scroll, orient=tk.VERTICAL,
                                     command=self.tabla_datos.yview)
        self.tabla_datos.configure(yscrollcommand=barra_scroll.set)

        self.tabla_datos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        barra_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # ==========================================
    # Eventos y Logica de Negocio
    # ==========================================

    def _evento_calcular(self):
        """Valida las entradas del usuario y ejecuta el calculo del sistema seleccionado llamando a C++."""
        try:
            val_monto = float(self.var_monto.get().strip())
            val_tasa = float(self.var_tasa_anual.get().strip())
            num_meses = int(self.var_plazo_meses.get().strip())
            str_sistema = self.var_sistema.get().strip()

            if val_monto <= 0:
                self._mostrar_alerta("El monto del prestamo debe ser mayor a 0.")
                return
            if val_tasa < 0:
                self._mostrar_alerta("La tasa de interes no puede ser negativa.")
                return
            if num_meses <= 0:
                self._mostrar_alerta("El plazo en meses debe ser mayor a 0.")
                return

            # Calculo base sin abonos y con abonos si la lista no esta vacia
            lista_base = calcular_amortizacion(str_sistema, val_monto, val_tasa, num_meses)
            hay_abonos = len(self.lista_abonos) > 0
            lista_filas_seleccionada = calcular_amortizacion(
                str_sistema, val_monto, val_tasa, num_meses,
                list(self.lista_abonos)) if hay_abonos else lista_base
            self.lista_filas_actual = list(lista_filas_seleccionada)
            self.dict_params_actual = {
                "sistema": str_sistema,
                "monto": val_monto,
                "tasa": val_tasa,
                "meses": num_meses,
                "abonos": [dict(abono) for abono in self.lista_abonos],
            }
            self._actualizar_tabla(lista_filas_seleccionada)
            self._actualizar_resumen(lista_filas_seleccionada, val_tasa)
            self._actualizar_graficas(lista_filas_seleccionada)
            if hay_abonos:
                self._fijar_comparativa_abonos(lista_base, lista_filas_seleccionada,
                                               str_sistema, val_monto, val_tasa, num_meses)
            else:
                self.var_ahorro_abonos.set("Sin abonos extra.")
            self._agregar_actual_a_historial(lista_filas_seleccionada)

        except ValueError as obj_err:
            self._mostrar_alerta(f"Entrada numerica invalida: {obj_err}")
        except FileNotFoundError as obj_err:
            self._mostrar_alerta(str(obj_err))
        except Exception as obj_err:
            self._mostrar_alerta(f"Error al calcular: {obj_err}")

    def _actualizar_tabla(self, lista_filas: list[dict]):
        """Limpia y rellena la tabla Treeview con las filas calculadas."""
        # Limpieza de filas anteriores
        for item in self.tabla_datos.get_children():
            self.tabla_datos.delete(item)

        # Insercion de nuevas filas
        for fila in lista_filas:
            self.tabla_datos.insert("", tk.END, values=(
                fila["mes"],
                self._formatear_moneda(fila['cuota']),
                self._formatear_moneda(fila['interes']),
                self._formatear_moneda(fila['capital']),
                self._formatear_moneda(fila['saldo'])
            ))

    def _actualizar_resumen(self, lista_filas: list[dict], val_tasa_anual: float = 0.0):
        """Calcula y muestra totales e indicadores del prestamo."""
        if not lista_filas:
            return

        total_pagado = sum(fila["cuota"] for fila in lista_filas)
        total_interes = sum(fila["interes"] for fila in lista_filas)
        cuota_inicial = lista_filas[0]["cuota"]

        self.var_total_pagado.set(f"Total Pagado: {self._formatear_moneda(total_pagado)}")
        self.var_total_interes.set(f"Total Intereses: {self._formatear_moneda(total_interes)}")
        self.var_cuota_inicial.set(f"Cuota Mes 1: {self._formatear_moneda(cuota_inicial)}")

        dict_ind = calcular_indicadores(lista_filas, val_tasa_anual)
        self.var_porc_interes.set(f"% Interes: {dict_ind['porc_interes']:.1f}% del total")
        self.var_cuota_rango.set(
            f"Cuota min-max: {self._formatear_moneda(dict_ind['cuota_min'])} - {self._formatear_moneda(dict_ind['cuota_max'])}")
        self.var_mes_cruce.set(
            f"Cruce capital>interes: {formatear_mes_cruce(dict_ind['mes_cruce'])}")
        self.var_tasa_efectiva.set(
            f"Tasa efectiva anual: {dict_ind['tasa_efectiva_anual']:.2f}%")

    def _actualizar_graficas(self, lista_filas: list[dict]):
        """Genera y renderiza la figura de relacion interes-capital."""
        figura_relacion = generar_figura_relacion_interes_capital(lista_filas)
        renderizar_lienzo_en_contenedor(figura_relacion, self.marco_pestana_relacion)

    def _limpiar_graficas(self):
        """Restaura el lienzo de la grafica a su estado vacio inicial."""
        figura_vacia = generar_figura_relacion_interes_capital([])
        renderizar_lienzo_en_contenedor(figura_vacia, self.marco_pestana_relacion)

    def _evento_limpiar(self):
        """Restablece los campos de entrada, vacia la tabla y limpia graficas."""
        self.var_monto.set("10000")
        self.var_tasa_anual.set("12.0")
        self.var_plazo_meses.set("12")
        self.var_sistema.set("Frances")

        for item in self.tabla_datos.get_children():
            self.tabla_datos.delete(item)

        self.var_total_pagado.set("Total Pagado: $0.00")
        self.var_total_interes.set("Total Intereses: $0.00")
        self.var_cuota_inicial.set("Cuota Mes 1: $0.00")
        self.var_porc_interes.set("% Interes: 0.0%")
        self.var_cuota_rango.set("Cuota min-max: $0.00 - $0.00")
        self.var_mes_cruce.set("Cruce capital>interes: Sin cruce")
        self.var_tasa_efectiva.set("Tasa efectiva anual: 0.00%")
        self.lista_abonos = []
        self.var_abono_mes.set("")
        self.var_abono_monto.set("")
        self.var_ahorro_abonos.set("Sin abonos extra.")
        self._refrescar_lista_abonos()

        self._limpiar_graficas()

    def _evento_exportar(self, tipo_archivo: str):
        """Exporta la tabla actual a PDF o Excel segun el menu elegido."""
        if not self.lista_filas_actual:
            self._mostrar_alerta("Primero calcula una tabla en 'Calcular Tabla'.")
            return
        dir_inicial = self._carpeta_inicial_export()
        num_dec = self.dict_config.get("num_decimales", 2)
        str_moneda = self.dict_config.get("simbolo_moneda", "$")
        if tipo_archivo == "pdf":
            ruta_destino = filedialog.asksaveasfilename(
                defaultextension=".pdf", filetypes=[("PDF", "*.pdf")],
                initialfile="tabla_amortizacion.pdf", title="Exportar a PDF",
                initialdir=dir_inicial or ".")
            if not ruta_destino:
                return
            try:
                ruta_final = exportar_tabla_pdf(
                    self.lista_filas_actual, self.dict_params_actual, ruta_destino,
                    num_decimales=num_dec, simbolo_moneda=str_moneda,
                    incluir_logo=bool(self.dict_config.get("incluir_logo_pdf", True)),
                    incluir_pie=bool(self.dict_config.get("incluir_pie_pdf", True)))
            except Exception as obj_err:
                self._mostrar_alerta(f"No se pudo exportar a PDF: {obj_err}")
                return
        else:
            ruta_destino = filedialog.asksaveasfilename(
                defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")],
                initialfile="tabla_amortizacion.xlsx", title="Exportar a Excel",
                initialdir=dir_inicial or ".")
            if not ruta_destino:
                return
            try:
                ruta_final = exportar_tabla_excel(
                    self.lista_filas_actual, self.dict_params_actual, ruta_destino,
                    num_decimales=num_dec, simbolo_moneda=str_moneda)
            except Exception as obj_err:
                self._mostrar_alerta(f"No se pudo exportar a Excel: {obj_err}")
                return
        messagebox.showinfo("Exportar", f"Archivo guardado en:\n{ruta_final}")

    def _evento_exportar_comparar(self, tipo_archivo: str):
        """Exporta A + B + grafica comparativa a PDF o Excel en un solo archivo."""
        if not self.lista_tabla_a or not self.lista_tabla_b:
            self._mostrar_alerta("Fija los escenarios A y B antes de exportar.")
            return
        dir_inicial = self._carpeta_inicial_export()
        num_dec = self.dict_config.get("num_decimales", 2)
        str_moneda = self.dict_config.get("simbolo_moneda", "$")
        if tipo_archivo == "pdf":
            ruta_destino = filedialog.asksaveasfilename(
                defaultextension=".pdf", filetypes=[("PDF", "*.pdf")],
                initialfile="comparativa_AB.pdf", title="Exportar comparativa a PDF",
                initialdir=dir_inicial or ".")
            if not ruta_destino:
                return
            try:
                ruta_final = exportar_comparativa_pdf(
                    self.lista_tabla_a, self.dict_params_a,
                    self.lista_tabla_b, self.dict_params_b, ruta_destino,
                    num_decimales=num_dec, simbolo_moneda=str_moneda,
                    incluir_logo=bool(self.dict_config.get("incluir_logo_pdf", True)),
                    incluir_pie=bool(self.dict_config.get("incluir_pie_pdf", True)))
            except Exception as obj_err:
                self._mostrar_alerta(f"No se pudo exportar a PDF: {obj_err}")
                return
        else:
            ruta_destino = filedialog.asksaveasfilename(
                defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")],
                initialfile="comparativa_AB.xlsx", title="Exportar comparativa a Excel",
                initialdir=dir_inicial or ".")
            if not ruta_destino:
                return
            try:
                ruta_final = exportar_comparativa_excel(
                    self.lista_tabla_a, self.dict_params_a,
                    self.lista_tabla_b, self.dict_params_b, ruta_destino,
                    num_decimales=num_dec, simbolo_moneda=str_moneda)
            except Exception as obj_err:
                self._mostrar_alerta(f"No se pudo exportar a Excel: {obj_err}")
                return
        messagebox.showinfo("Exportar", f"Archivo guardado en:\n{ruta_final}")

    def _mostrar_alerta(self, str_mensaje: str):
        """Muestra un dialogo emergente con un mensaje de alerta o error."""
        messagebox.showwarning("Aviso del Sistema", str_mensaje)




# ==========================================
# Funcion de Entrada para tkinter
# ==========================================

def iniciar_app(obj_ventana_raiz: tk.Tk):
    """Inicializa la clase controladora de la interfaz en tkinter."""
    AplicacionSimulador(obj_ventana_raiz)
