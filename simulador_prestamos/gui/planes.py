# ==========================================
# Encabezados y Librerias
# ==========================================
import os
import json

# ==========================================
# Declaracion de Constantes
# ==========================================
NOMBRE_ARCHIVO_PLANES = "planes.json"
MAX_PLANES = 50
SISTEMAS_VALIDOS = ("Frances", "Aleman", "Americano")

# ==========================================
# Declaracion de Funciones de Apoyo
# ==========================================

def _ruta_archivo_planes() -> str:
    """Retorna la ruta absoluta del archivo planes.json."""
    dir_actual = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(dir_actual, "..", NOMBRE_ARCHIVO_PLANES))


def valor_fijo_en_mes(historial, num_mes: int) -> float:
    """Devuelve el monto fijo vigente en un mes según su historial de cambios."""
    if isinstance(historial, list):
        aplicables = [
            entrada for entrada in historial
            if isinstance(entrada, dict)
            and int(entrada.get("desde_mes", 1)) <= num_mes
        ]
        if aplicables:
            vigente = max(aplicables, key=lambda item: int(item.get("desde_mes", 1)))
            return convertir_a_numero(vigente.get("monto", 0))
        return 0.0
    return convertir_a_numero(historial)


def sumar_grupo_movimientos(valor) -> float:
    """Suma un grupo de movimientos (lista de conceptos o un monto simple)."""
    if isinstance(valor, list):
        return sum(
            convertir_a_numero(item.get("monto", 0))
            for item in valor if isinstance(item, dict)
        )
    return convertir_a_numero(valor)


def convertir_a_numero(cadena: str, num_defecto: float = 0.0) -> float:
    """Convierte una cadena con separadores a numero flotante."""
    try:
        return float(str(cadena).replace(",", "").strip())
    except (TypeError, ValueError):
        return num_defecto


def cargar_planes() -> list[dict]:
    """Lee planes.json y devuelve la lista de planes guardados."""
    ruta_archivo = _ruta_archivo_planes()
    if not os.path.exists(ruta_archivo):
        return []
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        lista = datos if isinstance(datos, list) else []
        for plan in lista:
            if not isinstance(plan, dict):
                continue
            if not plan.get("duracion_meses"):
                plazos = []
                for credito in plan.get("creditos", []):
                    try:
                        plazos.append(int(credito.get("meses", 0)))
                    except (TypeError, ValueError):
                        pass
                plan["duracion_meses"] = max([12] + plazos)
            for movimiento in plan.get("movimientos", []):
                for clave, etiqueta in (("ingresos", "Ingreso"), ("egresos", "Gasto")):
                    valor_actual = movimiento.get(clave)
                    if not isinstance(valor_actual, list):
                        numero = convertir_a_numero(valor_actual)
                        movimiento[clave] = (
                            [{"concepto": etiqueta, "monto": numero}] if numero else []
                        )
            plan.setdefault("ingreso_fijo", 0.0)
            plan.setdefault("egreso_fijo", 0.0)
            for clave, clave_historial in (
                ("ingreso_fijo", "ingresos_fijos_historial"),
                ("egreso_fijo", "egresos_fijos_historial"),
            ):
                if not isinstance(plan.get(clave_historial), list):
                    valor_actual = convertir_a_numero(plan.get(clave, 0))
                    plan[clave_historial] = (
                        [{"monto": valor_actual, "desde_mes": 1}] if valor_actual else []
                    )
                plan[clave] = valor_fijo_en_mes(
                    plan[clave_historial], int(plan.get("duracion_meses", 12))
                )
            meses_editados = [
                int(item.get("mes", 0))
                for item in plan.get("movimientos", [])
                if item.get("ingresos") or item.get("egresos")
            ]
            plan["ultimo_mes_editado"] = max(meses_editados) if meses_editados else 0
        return lista
    except Exception:
        return []


def guardar_planes(lista_planes: list[dict]) -> str:
    """Escribe la lista de planes en planes.json y retorna la ruta."""
    ruta_archivo = _ruta_archivo_planes()
    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
        json.dump(lista_planes, archivo, indent=2, ensure_ascii=False)
    return os.path.abspath(ruta_archivo)


def calcular_credito(dict_credito: dict) -> dict:
    """
    Calcula la cuota inicial, el total a pagar y los intereses de un credito.
    Usa las mismas formulas de los sistemas Frances, Aleman y Americano.
    """
    val_monto = max(0.0, convertir_a_numero(dict_credito.get("monto", 0)))
    val_tasa = max(0.0, convertir_a_numero(dict_credito.get("tasa_anual", 0)))
    try:
        num_meses = max(1, int(dict_credito.get("meses", 1)))
    except (TypeError, ValueError):
        num_meses = 1
    str_sistema = str(dict_credito.get("sistema", "Frances"))
    if str_sistema not in SISTEMAS_VALIDOS:
        str_sistema = "Frances"

    tasa_mensual = val_tasa / 100.0 / 12.0

    if str_sistema == "Aleman":
        # Capital constante y cuota decreciente: se reporta la primera cuota.
        cuota_mensual = (val_monto / num_meses) + (val_monto * tasa_mensual)
        total_interes = val_monto * tasa_mensual * (num_meses + 1) / 2.0
        tipo_cuota = "Primera cuota"
    elif str_sistema == "Americano":
        # Solo se pagan intereses cada mes y el capital al final.
        cuota_mensual = val_monto * tasa_mensual
        total_interes = val_monto * tasa_mensual * num_meses
        tipo_cuota = "Interés mensual"
    else:
        if tasa_mensual > 0:
            factor = tasa_mensual / (1.0 - (1.0 + tasa_mensual) ** (-num_meses))
            cuota_mensual = val_monto * factor
        else:
            cuota_mensual = val_monto / num_meses
        total_interes = (cuota_mensual * num_meses) - val_monto
        tipo_cuota = "Cuota fija"

    total_pagar = val_monto + total_interes
    return {
        "concepto": str(dict_credito.get("concepto", "Crédito")).strip() or "Crédito",
        "sistema": str_sistema,
        "monto": round(val_monto, 2),
        "tasa_anual": round(val_tasa, 4),
        "meses": num_meses,
        "cuota_mensual": round(cuota_mensual, 2),
        "total_interes": round(max(0.0, total_interes), 2),
        "total_pagar": round(total_pagar, 2),
        "tipo_cuota": tipo_cuota,
    }


def calcular_resumen_plan(dict_plan: dict) -> dict:
    """Suma ingresos, gastos y cuotas para calcular el balance y el endeudamiento."""
    try:
        num_duracion = max(1, int(dict_plan.get("duracion_meses", 12)))
    except (TypeError, ValueError):
        num_duracion = 12
    historial_ingresos = dict_plan.get("ingresos_fijos_historial", dict_plan.get("ingreso_fijo", 0))
    historial_gastos = dict_plan.get("egresos_fijos_historial", dict_plan.get("egreso_fijo", 0))
    total_ingreso_fijo = sum(
        valor_fijo_en_mes(historial_ingresos, num_mes)
        for num_mes in range(1, num_duracion + 1)
    )
    total_gasto_fijo = sum(
        valor_fijo_en_mes(historial_gastos, num_mes)
        for num_mes in range(1, num_duracion + 1)
    )
    movimientos = dict_plan.get("movimientos") or []
    if movimientos:
        total_ingresos = total_ingreso_fijo + sum(
            sumar_grupo_movimientos(item.get("ingresos", 0)) for item in movimientos
        )
        total_gastos = total_gasto_fijo + sum(
            sumar_grupo_movimientos(item.get("egresos", 0)) for item in movimientos
        )
    else:
        total_ingresos = total_ingreso_fijo + sum(
            convertir_a_numero(item.get("monto", 0)) for item in dict_plan.get("ingresos", [])
        )
        total_gastos = total_gasto_fijo + sum(
            convertir_a_numero(item.get("monto", 0)) for item in dict_plan.get("gastos", [])
        )

    lista_creditos = []
    for dict_credito in dict_plan.get("creditos", []):
        if "cuota_mensual" in dict_credito:
            lista_creditos.append(dict_credito)
        else:
            lista_creditos.append(calcular_credito(dict_credito))

    # Las cuotas se totalizan mes por mes para que usen la misma unidad que
    # ingresos y gastos (que ya son acumulados durante toda la duración).
    evolucion_creditos = {
        int(fila["mes"]): fila
        for fila in calcular_evolucion_plan(lista_creditos)
    }
    total_cuotas = sum(
        float(evolucion_creditos[num_mes]["pago_total"])
        for num_mes in range(1, num_duracion + 1)
        if num_mes in evolucion_creditos
    )
    total_intereses = sum(float(credito.get("total_interes", 0)) for credito in lista_creditos)
    total_deuda = sum(float(credito.get("monto", 0)) for credito in lista_creditos)
    balance_total = total_ingresos - total_gastos - total_cuotas
    ratio_endeudamiento = (total_cuotas / total_ingresos * 100.0) if total_ingresos > 0 else 0.0

    return {
        "total_ingresos": round(total_ingresos, 2),
        "total_gastos": round(total_gastos, 2),
        "total_cuotas": round(total_cuotas, 2),
        "total_intereses": round(total_intereses, 2),
        "total_deuda": round(total_deuda, 2),
        "balance_total": round(balance_total, 2),
        "balance_mensual": round(balance_total / num_duracion, 2),
        "ratio_endeudamiento": round(ratio_endeudamiento, 2),
        "num_creditos": len(lista_creditos),
    }


def nivel_endeudamiento(val_ratio: float, val_ingresos: float) -> str:
    """Clasifica la carga de los creditos respecto al ingreso mensual."""
    if val_ingresos <= 0:
        return "sin_ingresos"
    if val_ratio <= 30:
        return "saludable"
    if val_ratio <= 40:
        return "moderado"
    return "alto"


def crear_plan(str_nombre: str, lista_ingresos: list[dict],
               lista_gastos: list[dict], lista_creditos: list[dict],
               num_duracion_meses: int = 12) -> dict:
    """Construye un plan financiero con sus creditos calculados y su resumen."""
    try:
        num_duracion = max(1, int(num_duracion_meses))
    except (TypeError, ValueError):
        num_duracion = 12
    dict_plan = {
        "nombre": str_nombre.strip(),
        "duracion_meses": num_duracion,
        "ingreso_fijo": 0.0,
        "egreso_fijo": 0.0,
        "ingresos_fijos_historial": [],
        "egresos_fijos_historial": [],
        "ultimo_mes_editado": 0,
        "ingresos": [dict(item) for item in lista_ingresos],
        "gastos": [dict(item) for item in lista_gastos],
        "creditos": [calcular_credito(credito) for credito in lista_creditos],
        "movimientos": [
            {"mes": num_mes, "ingresos": [], "egresos": []}
            for num_mes in range(1, num_duracion + 1)
        ],
    }
    dict_plan["resumen"] = calcular_resumen_plan(dict_plan)
    return dict_plan


def generar_tabla_credito(dict_credito: dict) -> list[dict]:
    """
    Genera la tabla mes a mes de un credito con cuota, interes, capital y saldo.
    Se usa para la grafica de evolucion mensual del plan.
    """
    val_monto = max(0.0, convertir_a_numero(dict_credito.get("monto", 0)))
    val_tasa = max(0.0, convertir_a_numero(dict_credito.get("tasa_anual", 0)))
    try:
        num_meses = max(1, int(dict_credito.get("meses", 1)))
    except (TypeError, ValueError):
        num_meses = 1
    str_sistema = str(dict_credito.get("sistema", "Frances"))
    if str_sistema not in SISTEMAS_VALIDOS:
        str_sistema = "Frances"
    tasa_mensual = val_tasa / 100.0 / 12.0

    filas: list[dict] = []
    saldo = val_monto

    if str_sistema == "Aleman":
        capital_fijo = val_monto / num_meses
        for num_mes in range(1, num_meses + 1):
            interes = saldo * tasa_mensual
            capital = capital_fijo if num_mes < num_meses else saldo
            saldo = max(0.0, saldo - capital)
            filas.append({
                "mes": num_mes,
                "cuota": capital + interes,
                "interes": interes,
                "capital": capital,
                "saldo": saldo,
            })

    elif str_sistema == "Americano":
        for num_mes in range(1, num_meses + 1):
            interes = val_monto * tasa_mensual
            capital = val_monto if num_mes == num_meses else 0.0
            saldo = 0.0 if num_mes == num_meses else val_monto
            filas.append({
                "mes": num_mes,
                "cuota": interes + capital,
                "interes": interes,
                "capital": capital,
                "saldo": saldo,
            })

    else:
        if tasa_mensual > 0:
            factor = tasa_mensual / (1.0 - (1.0 + tasa_mensual) ** (-num_meses))
            cuota_fija = val_monto * factor
        else:
            cuota_fija = val_monto / num_meses
        for num_mes in range(1, num_meses + 1):
            interes = saldo * tasa_mensual
            capital = saldo if num_mes == num_meses else cuota_fija - interes
            saldo = max(0.0, saldo - capital)
            filas.append({
                "mes": num_mes,
                "cuota": capital + interes,
                "interes": interes,
                "capital": capital,
                "saldo": saldo,
            })

    for fila in filas:
        for clave in ("cuota", "interes", "capital", "saldo"):
            fila[clave] = round(fila[clave], 2)
    return filas


def calcular_evolucion_plan(lista_creditos: list[dict]) -> list[dict]:
    """
    Suma mes a mes el pago, los intereses, el capital y el saldo de todos los
    creditos del plan para construir la serie de evolucion mensual.
    """
    tablas = [generar_tabla_credito(credito) for credito in lista_creditos]
    tablas = [tabla for tabla in tablas if tabla]
    if not tablas:
        return []

    max_meses = max(len(tabla) for tabla in tablas)
    filas: list[dict] = []
    for num_mes in range(1, max_meses + 1):
        pago_total = 0.0
        interes_total = 0.0
        capital_total = 0.0
        saldo_total = 0.0
        for tabla in tablas:
            if num_mes <= len(tabla):
                fila = tabla[num_mes - 1]
                pago_total += float(fila["cuota"])
                interes_total += float(fila["interes"])
                capital_total += float(fila["capital"])
                saldo_total += float(fila["saldo"])
        filas.append({
            "mes": num_mes,
            "pago_total": round(pago_total, 2),
            "interes_total": round(interes_total, 2),
            "capital_total": round(capital_total, 2),
            "saldo_total": round(saldo_total, 2),
        })
    return filas


def calcular_flujo_plan(dict_plan: dict) -> list[dict]:
    """
    Construye el flujo mensual del plan durante su duracion: ingresos, egresos,
    pago del credito, intereses, capital y saldos netos y del credito.
    """
    try:
        num_duracion = max(1, int(dict_plan.get("duracion_meses", 12)))
    except (TypeError, ValueError):
        num_duracion = 12

    resumen = dict_plan.get("resumen") or calcular_resumen_plan(dict_plan)
    historial_ingresos = dict_plan.get("ingresos_fijos_historial", dict_plan.get("ingreso_fijo", 0))
    historial_gastos = dict_plan.get("egresos_fijos_historial", dict_plan.get("egreso_fijo", 0))
    movimientos = {
        int(item["mes"]): item for item in (dict_plan.get("movimientos") or [])
        if "mes" in item
    }
    evolucion_credito = {
        int(fila["mes"]): fila for fila in calcular_evolucion_plan(dict_plan.get("creditos", []))
    }

    filas: list[dict] = []
    saldo_neto_acumulado = 0.0
    for num_mes in range(1, num_duracion + 1):
        fila_credito = evolucion_credito.get(num_mes, {})
        pago_credito = float(fila_credito.get("pago_total", 0))
        movimiento = movimientos.get(num_mes)
        if movimiento is not None:
            val_ingresos_mes = valor_fijo_en_mes(historial_ingresos, num_mes) + sumar_grupo_movimientos(
                movimiento.get("ingresos", 0)
            )
            val_egresos_mes = valor_fijo_en_mes(historial_gastos, num_mes) + sumar_grupo_movimientos(
                movimiento.get("egresos", 0)
            )
        else:
            val_ingresos_mes = float(resumen.get("total_ingresos", 0))
            val_egresos_mes = float(resumen.get("total_gastos", 0))
        saldo_neto = val_ingresos_mes - val_egresos_mes - pago_credito
        saldo_neto_acumulado += saldo_neto
        lista_ingresos_detalle = (
            [dict(item) for item in movimiento.get("ingresos", [])]
            if isinstance(movimiento, dict) and isinstance(movimiento.get("ingresos"), list) else []
        )
        lista_egresos_detalle = (
            [dict(item) for item in movimiento.get("egresos", [])]
            if isinstance(movimiento, dict) and isinstance(movimiento.get("egresos"), list) else []
        )
        filas.append({
            "mes": num_mes,
            "anio": (num_mes - 1) // 12 + 1,
            "ingresos": round(val_ingresos_mes, 2),
            "egresos": round(val_egresos_mes, 2),
            "pago_credito": round(pago_credito, 2),
            "intereses": round(float(fila_credito.get("interes_total", 0)), 2),
            "capital": round(float(fila_credito.get("capital_total", 0)), 2),
            "saldo_neto": round(saldo_neto, 2),
            "saldo_neto_acumulado": round(saldo_neto_acumulado, 2),
            "saldo_credito": round(float(fila_credito.get("saldo_total", 0)), 2),
            "ingresos_detalle": lista_ingresos_detalle,
            "egresos_detalle": lista_egresos_detalle,
        })
    return filas


def calcular_resumen_anual(lista_filas: list[dict]) -> list[dict]:
    """Agrupa por anio el flujo mensual del plan para mostrar totales anuales."""
    anios: dict[int, dict] = {}
    for fila in lista_filas:
        num_anio = int(fila.get("anio", 1))
        if num_anio not in anios:
            anios[num_anio] = {
                "anio": num_anio,
                "ingresos": 0.0,
                "egresos": 0.0,
                "pago_credito": 0.0,
                "intereses": 0.0,
                "capital": 0.0,
                "saldo_neto": 0.0,
                "saldo_credito": 0.0,
            }
        acumulado = anios[num_anio]
        for clave in ("ingresos", "egresos", "pago_credito", "intereses",
                      "capital", "saldo_neto"):
            acumulado[clave] += float(fila.get(clave, 0))
        acumulado["saldo_credito"] = float(fila.get("saldo_credito", 0))

    filas_anuales = []
    for num_anio in sorted(anios):
        fila = anios[num_anio]
        for clave in ("ingresos", "egresos", "pago_credito", "intereses",
                      "capital", "saldo_neto", "saldo_credito"):
            fila[clave] = round(fila[clave], 2)
        filas_anuales.append(fila)
    return filas_anuales
