# ==========================================
# Encabezados y Librerias
# ==========================================
import os
import json

# ==========================================
# Declaracion de Constantes
# ==========================================
NOMBRE_ARCHIVO_CONFIG = "config.json"
OPCIONES_TAMANO_LETRA = ["Pequeña", "Normal", "Grande"]
OPCIONES_DECIMALES = [0, 1, 2]
OPCIONES_MONEDA = ["$", "MXN ", "USD "]
FUENTES_DISPONIBLES = ["Segoe UI", "Arial", "Calibri", "Consolas", "Verdana"]
ESQUEMAS_GRAFICAS = {
    "Intresta": "#64B5F6",
    "Azul": "#1976D2",
    "Verde": "#2E7D32",
    "Naranja": "#EF6C00",
    "Morado": "#9C27B0",
    "Personalizado": "#64B5F6",
}
FUENTES_PDF = ["Segoe UI", "Arial", "Helvetica"]
COLORES_DISPONIBLES = {
    "Verde": "#66BB6A",
    "Rojo": "#EF5350",
    "Amarillo": "#E5DE4B",
    "Azul": "#64B5F6",
    "Rosa": "#EC407A",
    "Morado": "#AB47BC",
    "Naranja": "#FF7043",
    "Cian": "#26C6DA",
    "Blanco": "#FFFFFF",
    "Gris": "#9E9E9E",
    "Lima": "#AED581",
    "Magenta": "#FF4081",
}
COLORES_GRAFICAS_DEFECTO = {
    "ingresos": "Verde",
    "egresos": "Rojo",
    "creditos": "Amarillo",
    "saldo": "Azul",
    "intereses": "Rojo",
    "capital": "Verde",
}

CONFIG_POR_DEFECTO = {
    "tema": "oscuro",
    "tamano_letra": "Normal",
    "num_decimales": 2,
    "simbolo_moneda": "$",
    "carpeta_exportacion": "",
    "incluir_logo_pdf": True,
    "incluir_pie_pdf": True,
    "api_key": "",
    "fuente_app": "Segoe UI",
    "color_graficas": "Intresta",
    "decimales_pdf": 2,
    "fuente_pdf": "Segoe UI",
    "color_graficas_pdf": "Intresta",
    "color_ingresos": "Verde",
    "color_egresos": "Rojo",
    "color_creditos": "Amarillo",
    "color_saldo": "Azul",
    "color_intereses": "Rojo",
    "color_capital": "Verde",
}

MAPEO_AJUSTE_FUENTE = {
    "Pequeña": -2,
    "Normal": 0,
    "Grande": 2,
}

# ==========================================
# Declaracion de Funciones
# ==========================================

def _ruta_archivo_config() -> str:
    """Retorna la ruta del JSON de configuracion junto a simulador_prestamos."""
    dir_actual = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(dir_actual, "..", NOMBRE_ARCHIVO_CONFIG))


def cargar_configuracion() -> dict:
    """Lee el JSON de configuracion y mezcla con valores por defecto."""
    dict_config = dict(CONFIG_POR_DEFECTO)
    ruta_archivo = _ruta_archivo_config()
    if not os.path.exists(ruta_archivo):
        return dict_config
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        if isinstance(datos, dict):
            for clave, valor_defecto in CONFIG_POR_DEFECTO.items():
                if clave in datos:
                    dict_config[clave] = datos[clave]
    except Exception:
        pass
    # Normaliza opciones invalidas a valores por defecto
    if dict_config.get("tamano_letra") not in OPCIONES_TAMANO_LETRA:
        dict_config["tamano_letra"] = "Normal"
    if dict_config.get("num_decimales") not in OPCIONES_DECIMALES:
        dict_config["num_decimales"] = 2
    if dict_config.get("simbolo_moneda") not in OPCIONES_MONEDA:
        dict_config["simbolo_moneda"] = "$"
    if dict_config.get("tema") not in ("claro", "oscuro"):
        dict_config["tema"] = "oscuro"
    if dict_config.get("fuente_app") not in FUENTES_DISPONIBLES:
        dict_config["fuente_app"] = "Segoe UI"
    if dict_config.get("color_graficas") not in ESQUEMAS_GRAFICAS:
        dict_config["color_graficas"] = "Intresta"
    if dict_config.get("decimales_pdf") not in OPCIONES_DECIMALES:
        dict_config["decimales_pdf"] = 2
    if dict_config.get("fuente_pdf") not in FUENTES_PDF:
        dict_config["fuente_pdf"] = "Segoe UI"
    if dict_config.get("color_graficas_pdf") not in ESQUEMAS_GRAFICAS:
        dict_config["color_graficas_pdf"] = "Intresta"
    for clave, valor_defecto in COLORES_GRAFICAS_DEFECTO.items():
        clave_config = f"color_{clave}"
        if dict_config.get(clave_config) not in COLORES_DISPONIBLES:
            dict_config[clave_config] = valor_defecto
    return dict_config


def obtener_color_esquema(str_esquema: str) -> str:
    """Retorna el color hexadecimal asociado a un esquema de gráficas."""
    return ESQUEMAS_GRAFICAS.get(str_esquema, ESQUEMAS_GRAFICAS["Intresta"])


def obtener_color_nombre(str_nombre: str) -> str:
    """Retorna el hexadecimal de un color elegido por el usuario."""
    return COLORES_DISPONIBLES.get(str_nombre, COLORES_DISPONIBLES["Azul"])


def guardar_configuracion(dict_config: dict) -> str:
    """Guarda el diccionario de configuracion en JSON y retorna la ruta."""
    ruta_archivo = _ruta_archivo_config()

    # Cargar configuracion actual para no sobrescribir claves existentes como api_key
    datos_actuales = {}
    if os.path.exists(ruta_archivo):
        try:
            with open(ruta_archivo, "r", encoding="utf-8") as archivo:
                contenido = json.load(archivo)
                if isinstance(contenido, dict):
                    datos_actuales = contenido
        except Exception:
            datos_actuales = {}

    datos_limpios = dict(CONFIG_POR_DEFECTO)
    datos_limpios.update(datos_actuales)

    for clave, valor in dict_config.items():
        if clave in CONFIG_POR_DEFECTO:
            # Si se pasa una clave valida, se actualiza respetando la clave si no es vacia
            if clave != "api_key" or (clave == "api_key" and valor):
                datos_limpios[clave] = valor

    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
        json.dump(datos_limpios, archivo, indent=2, ensure_ascii=False)
    return os.path.abspath(ruta_archivo)


def obtener_ajuste_fuente(tamano_letra: str) -> int:
    """Retorna el ajuste en puntos para el tamano de letra elegido."""
    return MAPEO_AJUSTE_FUENTE.get(tamano_letra, 0)


def formatear_moneda(val_monto: float, num_decimales: int, simbolo_moneda: str) -> str:
    """Formatea un monto con simbolo y decimales configurados."""
    try:
        num_dec = int(num_decimales)
    except (TypeError, ValueError):
        num_dec = 2
    if num_dec not in OPCIONES_DECIMALES:
        num_dec = 2
    formato = f",.{num_dec}f" if num_dec > 0 else ",.0f"
    return f"{simbolo_moneda}{val_monto:{formato}}"
