# ==========================================
# Encabezados y Librerias
# ==========================================
import os
import json
import subprocess
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

try:
    from gui.graficas import (
        generar_figura_relacion_interes_capital,
        generar_figura_comparativa_escenarios,
        renderizar_lienzo_en_contenedor
    )
except ImportError:
    from graficas import (
        generar_figura_relacion_interes_capital,
        generar_figura_comparativa_escenarios,
        renderizar_lienzo_en_contenedor
    )



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

# Colores para estilizar la interfaz
COLOR_FONDO = "#380057" #Color de Fondo
COLOR_PRIMARIO = "#380057" #Color Prestamo de credito
COLOR_SECUNDARIO = "#CFCC27" #Color letras tabla
COLOR_FONDO_TARJETA = "#CFCFCF" #Fondo de la tabla
COLOR_ROJO = "#C62828"
COLOR_VERDE = "#2E7D32"


def calcular_amortizacion(str_sistema: str, val_monto: float, val_tasa_anual: float, num_meses: int) -> list[dict]:
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
        self._configurar_ventana()
        self._configurar_estilos()
        self._crear_componentes()
        self._construir_disposicion()
        self._cargar_historial_desde_json()
        self._actualizar_vista_historial()

    def _configurar_ventana(self):
        """Ajusta las propiedades globales, iconos y titulo de la ventana."""
        self.raiz.title(TITULO_APLICACION)
        self.raiz.geometry(f"{ANCHO_VENTANA}x{ALTO_VENTANA}")
        self.raiz.minsize(ANCHO_MINIMO, ALTO_MINIMO)
        self.raiz.configure(bg=COLOR_FONDO)

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

        """Configura los estilos de ttk para una apariencia uniforme."""
        self.estilo = ttk.Style()
        self.estilo.theme_use("clam")

        # Estilo general de los frames
        self.estilo.configure("Tarjeta.TFrame", background=COLOR_FONDO_TARJETA)
        self.estilo.configure("Fondo.TFrame", background=COLOR_FONDO)

        # Etiquetas
        self.estilo.configure("Titulo.TLabel",
                              background=COLOR_FONDO,
                              foreground=COLOR_SECUNDARIO,
                              font=("Segoe UI", 16, "bold"))
        self.estilo.configure("Subtitulo.TLabel",
                              background=COLOR_FONDO,
                              foreground="#546E7A",
                              font=("Segoe UI", 9))
        self.estilo.configure("Seccion.TLabel",
                              background=COLOR_FONDO_TARJETA,
                              foreground=COLOR_PRIMARIO,
                              font=("Segoe UI", 12, "bold"))
        self.estilo.configure("Normal.TLabel",
                              background=COLOR_FONDO_TARJETA,
                              font=("Segoe UI", 10))
        self.estilo.configure("Resumen.TLabel",
                              background=COLOR_FONDO_TARJETA,
                              font=("Segoe UI", 11, "bold"))
        self.estilo.configure("ResumenRojo.TLabel",
                              background=COLOR_FONDO_TARJETA,
                              foreground=COLOR_ROJO,
                              font=("Segoe UI", 11, "bold"))
        self.estilo.configure("ResumenVerde.TLabel",
                              background=COLOR_FONDO_TARJETA,
                              foreground=COLOR_VERDE,
                              font=("Segoe UI", 11, "bold"))

        # Botones
        self.estilo.configure("Calcular.TButton",
                              font=("Segoe UI", 10, "bold"),
                              padding=8)
        self.estilo.configure("Limpiar.TButton",
                              font=("Segoe UI", 10),
                              padding=8)

        # Pestanas (Notebook)
        self.estilo.configure("TNotebook", background=COLOR_FONDO_TARJETA)
        self.estilo.configure("TNotebook.Tab",
                              font=("Segoe UI", 10, "bold"),
                              padding=[12, 6])

        # Pestanas de navegacion principal
        self.estilo.configure("NavegacionPrincipal.TNotebook", background=COLOR_FONDO)
        self.estilo.configure("NavegacionPrincipal.TNotebook.Tab",
                              font=("Segoe UI", 10, "bold"),
                              padding=[16, 6])

        # Treeview (tabla de datos)
        self.estilo.configure("Tabla.Treeview",
                              font=("Segoe UI", 10),
                              rowheight=28)
        self.estilo.configure("Tabla.Treeview.Heading",
                              font=("Segoe UI", 10, "bold"),
                              foreground=COLOR_SECUNDARIO)


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

    def _construir_disposicion(self):
        """Organiza los componentes en la pantalla usando frames y grid."""
        # Marco principal con padding
        marco_principal = ttk.Frame(self.raiz, style="Fondo.TFrame", padding=15)
        marco_principal.pack(fill=tk.BOTH, expand=True)

        # --- Encabezado ---
        marco_header = ttk.Frame(marco_principal, style="Fondo.TFrame")
        marco_header.pack(fill=tk.X, pady=(0, 10))

        # Cargar logo de la aplicacion en el encabezado si existe (alineado a la izquierda)
        dir_img = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Img")
        ruta_logo = os.path.join(dir_img, "intresta-logo-horizontal.png")

        if os.path.exists(ruta_logo):
            try:
                self.img_logo_encabezado = tk.PhotoImage(file=ruta_logo)
                lbl_logo = tk.Label(marco_header, image=self.img_logo_encabezado,
                                    bg=COLOR_FONDO, borderwidth=0, highlightthickness=0)
                lbl_logo.pack(side=tk.LEFT, anchor=tk.W)
            except Exception:
                pass

        # Titulo centrado verticalmente a la derecha
        ttk.Label(marco_header,
                  text="Simulador de Intereses y Amortizaciones",
                  style="Titulo.TLabel").pack(side=tk.RIGHT, anchor=tk.E, pady=0)


        # --- Barra de navegacion principal (tres apartados) ---
        self.cuaderno_principal = ttk.Notebook(marco_principal, style="NavegacionPrincipal.TNotebook")
        self.cuaderno_principal.pack(fill=tk.BOTH, expand=True)

        # Apartado 1: Calcular Tabla (contiene el formulario, tabla y graficas)
        marco_seccion_calculo = ttk.Frame(self.cuaderno_principal, style="Fondo.TFrame", padding=(0, 10, 0, 0))
        self.cuaderno_principal.add(marco_seccion_calculo, text="  Calcular Tabla  ")

        # Apartado 2: Comparar
        self.marco_seccion_comparar = ttk.Frame(self.cuaderno_principal, style="Fondo.TFrame", padding=(0, 10, 0, 0))
        self.cuaderno_principal.add(self.marco_seccion_comparar, text="  Comparar  ")
        self._construir_apartado_comparar(self.marco_seccion_comparar)

        # Apartado 3: Historial
        self.marco_seccion_apartado3 = ttk.Frame(self.cuaderno_principal, style="Fondo.TFrame", padding=(0, 10, 0, 0))
        self.cuaderno_principal.add(self.marco_seccion_apartado3, text="  Historial  ")
        self._construir_apartado_tres(self.marco_seccion_apartado3)

        # --- Cuerpo dividido en 2 paneles (dentro del apartado Calcular Tabla) ---
        marco_cuerpo = ttk.Frame(marco_seccion_calculo, style="Fondo.TFrame")
        marco_cuerpo.pack(fill=tk.BOTH, expand=True)
        marco_cuerpo.columnconfigure(1, weight=1)
        marco_cuerpo.rowconfigure(0, weight=1)

        # Panel izquierdo: formulario y resumen
        self._construir_panel_formulario(marco_cuerpo)

        # Panel derecho: visualizacion (pestanas con tabla y graficas)
        self._construir_panel_derecho(marco_cuerpo)

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
                   command=self._limpiar_comparar).pack(side=tk.LEFT)

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

    def _rellenar_treeview_comparar(self, tabla_destino, lista_filas: list[dict]):
        """Limpia y rellena un Treeview de comparativa con filas calculadas."""
        for item in tabla_destino.get_children():
            tabla_destino.delete(item)
        for fila in lista_filas:
            tabla_destino.insert("", tk.END, values=(
                fila["mes"],
                f"${fila['cuota']:,.2f}",
                f"${fila['interes']:,.2f}",
                f"${fila['capital']:,.2f}",
                f"${fila['saldo']:,.2f}"
            ))

    def _formatear_titulo_escenario(self, letra_escenario: str, dict_params: dict) -> str:
        """Arma el titulo descriptivo de un escenario con sus parametros."""
        if not dict_params:
            return f"Escenario {letra_escenario}: sin datos"
        return (f"Escenario {letra_escenario}: {dict_params.get('sistema', '')} | "
                f"Monto ${dict_params.get('monto', 0):,.2f} | "
                f"Tasa {dict_params.get('tasa', 0)}% | "
                f"{dict_params.get('meses', 0)} meses ({len(self.lista_tabla_a if letra_escenario == 'A' else self.lista_tabla_b)} filas)")

    def _actualizar_vista_comparar(self):
        """Refresca titulos, tablas, resumenes, diferencias y grafica de la comparativa."""
        self._rellenar_treeview_comparar(self.tabla_comparar_a, self.lista_tabla_a)
        self._rellenar_treeview_comparar(self.tabla_comparar_b, self.lista_tabla_b)
        self.var_titulo_a.set(self._formatear_titulo_escenario("A", self.dict_params_a))
        self.var_titulo_b.set(self._formatear_titulo_escenario("B", self.dict_params_b))

        total_a, interes_a = self._calcular_totales_lista(self.lista_tabla_a)
        total_b, interes_b = self._calcular_totales_lista(self.lista_tabla_b)
        self.var_resumen_a.set(f"Total: ${total_a:,.2f} | Intereses: ${interes_a:,.2f}")
        self.var_resumen_b.set(f"Total: ${total_b:,.2f} | Intereses: ${interes_b:,.2f}")

        if self.lista_tabla_a and self.lista_tabla_b:
            dif_total = total_a - total_b
            dif_interes = interes_a - interes_b
            self.var_diferencia.set(
                f"Diferencia A-B: Total ${dif_total:+,.2f} | Intereses ${dif_interes:+,.2f}"
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
        lienzo_historial = tk.Canvas(marco_scroll, bg="#CFCFCF", highlightthickness=0)
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
        str_texto = (f"${dict_entrada.get('monto', 0):,.2f} | {dict_entrada.get('fecha', '')} | "
                     f"{dict_entrada.get('sistema', '')}")
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
            lista_filas = calcular_amortizacion(
                str(dict_entrada.get("sistema", "Frances")),
                float(dict_entrada.get("monto", 0)),
                float(dict_entrada.get("tasa", 0)),
                int(dict_entrada.get("meses", 0))
            )
        except Exception as obj_err:
            self._mostrar_alerta(f"No se pudo recargar el historial: {obj_err}")
            return
        self.var_monto.set(str(dict_entrada.get("monto", "")))
        self.var_tasa_anual.set(str(dict_entrada.get("tasa", "")))
        self.var_plazo_meses.set(str(dict_entrada.get("meses", "")))
        self.var_sistema.set(str(dict_entrada.get("sistema", "")))
        self.lista_filas_actual = list(lista_filas)
        self.dict_params_actual = {
            "sistema": str(dict_entrada.get("sistema", "")),
            "monto": float(dict_entrada.get("monto", 0)),
            "tasa": float(dict_entrada.get("tasa", 0)),
            "meses": int(dict_entrada.get("meses", 0))
        }
        self._actualizar_tabla(lista_filas)
        self._actualizar_resumen(lista_filas)
        self._actualizar_graficas(lista_filas)
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
        """Construye el panel izquierdo con campos de entrada y resumen."""
        marco_form = ttk.Frame(marco_padre, style="Tarjeta.TFrame",
                               padding=18, relief="solid", borderwidth=1)
        marco_form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

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

    def _crear_campo_entrada(self, marco_padre, str_etiqueta, var_texto):
        """Crea un par etiqueta + campo de texto reutilizable."""
        ttk.Label(marco_padre, text=str_etiqueta,
                  style="Normal.TLabel").pack(anchor=tk.W, pady=(6, 2))
        entrada = ttk.Entry(marco_padre, textvariable=var_texto,
                            font=("Segoe UI", 10))
        entrada.pack(fill=tk.X, pady=(0, 4))

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
        # Titulo de seccion
        ttk.Label(marco_padre, text="Tabla de Pagos Detallada (Sistema Seleccionado)",
                  style="Seccion.TLabel").pack(anchor=tk.W, pady=(0, 8))

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

            # Calculo del sistema seleccionado para la tabla de amortizacion
            lista_filas_seleccionada = calcular_amortizacion(str_sistema, val_monto, val_tasa, num_meses)
            self.lista_filas_actual = list(lista_filas_seleccionada)
            self.dict_params_actual = {
                "sistema": str_sistema,
                "monto": val_monto,
                "tasa": val_tasa,
                "meses": num_meses
            }
            self._actualizar_tabla(lista_filas_seleccionada)
            self._actualizar_resumen(lista_filas_seleccionada)
            self._actualizar_graficas(lista_filas_seleccionada)
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
                f"${fila['cuota']:,.2f}",
                f"${fila['interes']:,.2f}",
                f"${fila['capital']:,.2f}",
                f"${fila['saldo']:,.2f}"
            ))

    def _actualizar_resumen(self, lista_filas: list[dict]):
        """Calcula y muestra los totales financieros acumulados."""
        if not lista_filas:
            return

        total_pagado = sum(fila["cuota"] for fila in lista_filas)
        total_interes = sum(fila["interes"] for fila in lista_filas)
        cuota_inicial = lista_filas[0]["cuota"]

        self.var_total_pagado.set(f"Total Pagado: ${total_pagado:,.2f}")
        self.var_total_interes.set(f"Total Intereses: ${total_interes:,.2f}")
        self.var_cuota_inicial.set(f"Cuota Mes 1: ${cuota_inicial:,.2f}")

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

        self._limpiar_graficas()

    def _mostrar_alerta(self, str_mensaje: str):
        """Muestra un dialogo emergente con un mensaje de alerta o error."""
        messagebox.showwarning("Aviso del Sistema", str_mensaje)




# ==========================================
# Funcion de Entrada para tkinter
# ==========================================

def iniciar_app(obj_ventana_raiz: tk.Tk):
    """Inicializa la clase controladora de la interfaz en tkinter."""
    AplicacionSimulador(obj_ventana_raiz)
