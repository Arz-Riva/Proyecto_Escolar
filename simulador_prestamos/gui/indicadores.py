# ==========================================
# Encabezados y Librerias
# ==========================================

# ==========================================
# Declaracion de Constantes
# ==========================================
CLAVE_TOTAL_PAGADO = "total_pagado"
CLAVE_TOTAL_INTERES = "total_interes"
CLAVE_PORC_INTERES = "porc_interes"
CLAVE_CUOTA_MIN = "cuota_min"
CLAVE_CUOTA_MAX = "cuota_max"
CLAVE_MES_CRUCE = "mes_cruce"
CLAVE_TASA_EFECTIVA = "tasa_efectiva_anual"
CLAVE_NUM_MESES = "num_meses"

# ==========================================
# Declaracion de Funciones
# ==========================================

def calcular_indicadores(lista_filas: list[dict], val_tasa_anual: float) -> dict:
    """Calcula los indicadores del prestamo con funciones puras."""
    if not lista_filas:
        return {
            CLAVE_TOTAL_PAGADO: 0.0,
            CLAVE_TOTAL_INTERES: 0.0,
            CLAVE_PORC_INTERES: 0.0,
            CLAVE_CUOTA_MIN: 0.0,
            CLAVE_CUOTA_MAX: 0.0,
            CLAVE_MES_CRUCE: 0,
            CLAVE_TASA_EFECTIVA: 0.0,
            CLAVE_NUM_MESES: 0,
        }
    total_pagado = sum(fila["cuota"] for fila in lista_filas)
    total_interes = sum(fila["interes"] for fila in lista_filas)
    porc_interes = (total_interes / total_pagado * 100.0) if total_pagado > 0 else 0.0
    cuotas = [fila["cuota"] for fila in lista_filas]
    fila_cruce = next((fila for fila in lista_filas if fila["capital"] > fila["interes"]), None)
    mes_cruce = int(fila_cruce["mes"]) if fila_cruce else 0
    tasa_mensual = float(val_tasa_anual) / 100.0 / 12.0
    tasa_efectiva = ((1.0 + tasa_mensual) ** 12 - 1.0) * 100.0 if tasa_mensual >= 0 else 0.0
    return {
        CLAVE_TOTAL_PAGADO: total_pagado,
        CLAVE_TOTAL_INTERES: total_interes,
        CLAVE_PORC_INTERES: porc_interes,
        CLAVE_CUOTA_MIN: min(cuotas),
        CLAVE_CUOTA_MAX: max(cuotas),
        CLAVE_MES_CRUCE: mes_cruce,
        CLAVE_TASA_EFECTIVA: tasa_efectiva,
        CLAVE_NUM_MESES: len(lista_filas),
    }


def formatear_mes_cruce(num_mes: int) -> str:
    """Devuelve el texto legible del mes de cruce capital-interes."""
    if num_mes <= 0:
        return "Sin cruce"
    return f"Mes {num_mes}"
