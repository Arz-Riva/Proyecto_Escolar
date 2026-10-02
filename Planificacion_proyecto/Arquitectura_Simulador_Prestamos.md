# Arquitectura del Proyecto: Simulador de Préstamos / Amortización

Aplicación con GUI, programación funcional, IA vía API y los lenguajes Python y C++.

---

## 1. Objetivo del proyecto

Simular el pago de un préstamo bajo distintos sistemas de amortización (francés, alemán, americano), mostrando la tabla de pagos, gráficas de evolución, y utilizando IA para explicar e interpretar los resultados en lenguaje natural.

## 2. Requisitos cumplidos

- **GUI** (no CLI): formulario de entrada + tabla + gráficas.
- **Programación funcional**: todo el cálculo de amortización son funciones puras encadenadas.
- **Multi-lenguaje**: Python y C++, cada uno con un rol específico.
- **IA implementada vía API**: interpretación y comparación de resultados.

## 3. Patrón arquitectónico general: Orquestador-Trabajador

La aplicación sigue un patrón **orquestador-trabajador** (similar a interfaces gráficas que invocan herramientas externas, como Git GUIs llamando a `git.exe`):

- **Orquestador (Python):** GUI, captura de datos del usuario, invoca al trabajador compilado, arma llamadas a la API de IA, muestra resultados.
- **Trabajador (C++):** binario compilado independiente, sin estado, que recibe datos y devuelve resultados calculados. Aquí vive el **núcleo funcional puro**.

```
Usuario → GUI (Python) → subprocess → Trabajador (C++) → resultado (JSON) → GUI
                        → API de IA  → interpretación en texto           → GUI
```

Dentro del trabajador se aplica además el patrón **Functional Core, Imperative Shell**: el núcleo de cálculo es puro (sin estado), y solo la capa de entrada/salida del binario (leer argumentos, imprimir resultado) es imperativa.

## 4. Estructura de carpetas

```
simulador_prestamos/
├── core_cpp/                  <- Trabajador: sistemas de amortización (francés, alemán, americano)
│   ├── amortizacion.hpp       <- definiciones y estructuras
│   ├── amortizacion.cpp       <- funciones puras de cálculo
│   └── main.cpp               <- lee argumentos (CLI/JSON), llama al core, imprime JSON
├── gui/                       <- Orquestador
│   ├── ventana.py             <- captura inputs, invoca subprocess, muestra tabla/gráficas
│   ├── ia.py                  <- funciones que arman prompts y llaman a la API
│   └── graficas.py            <- generación de gráficas con matplotlib
└── main.py                    <- inicia la ventana
```

## 5. Núcleo funcional (Trabajador en C++)

Cada sistema de amortización se modela mediante funciones puras que calculan el estado del préstamo mes a mes sin mutar estructuras globales. La tabla se construye acumulando resultados.

### 5.1 Estructuras y cálculo del Sistema Francés (C++)

```cpp
struct Fila { 
    int mes; 
    double cuota;
    double interes; 
    double capital; 
    double saldo; 
};

Fila calcularFilaFrances(double saldo, double tasaMensual, double cuota) {
    double interes = saldo * tasaMensual;
    double capital = cuota - interes;
    double nuevoSaldo = saldo - capital;
    return {0, cuota, interes, capital, nuevoSaldo};
}

std::vector<Fila> generarTablaFrances(double monto, double tasaMensual, int meses, double cuota) {
    std::vector<Fila> tabla;
    tabla.reserve(meses);
    double saldo = monto;
    for (int i = 1; i <= meses; ++i) {
        Fila fila = calcularFilaFrances(saldo, tasaMensual, cuota);
        fila.mes = i;
        tabla.push_back(fila);
        saldo = fila.saldo;
    }
    return tabla;
}
```

### 5.2 Sistema Alemán (C++)

```cpp
Fila calcularFilaAleman(double saldo, double tasaMensual, double capitalFijo) {
    double interes = saldo * tasaMensual;
    double cuota = capitalFijo + interes;
    double nuevoSaldo = saldo - capitalFijo;
    return {0, cuota, interes, capitalFijo, nuevoSaldo};
}

std::vector<Fila> generarTablaAleman(double monto, double tasaMensual, int meses) {
    std::vector<Fila> tabla;
    tabla.reserve(meses);
    double capitalFijo = monto / meses;
    double saldo = monto;
    for (int i = 1; i <= meses; ++i) {
        Fila fila = calcularFilaAleman(saldo, tasaMensual, capitalFijo);
        fila.mes = i;
        tabla.push_back(fila);
        saldo = fila.saldo;
    }
    return tabla;
}
```

### 5.3 Comunicación con el orquestador

El binario de C++ recibe los parámetros como argumentos de línea de comandos (o JSON por `stdin`) y devuelve la tabla como **JSON por `stdout`**, permitiendo que Python la consuma directamente:

```python
# gui/ventana.py
import subprocess, json

def calcular_amortizacion(sistema: str, monto: float, tasa: float, meses: int):
    resultado = subprocess.run(
        ["./core_cpp/amortizador", sistema, str(monto), str(tasa), str(meses)],
        capture_output=True, text=True, check=True
    )
    return json.loads(resultado.stdout)
```

## 6. Capa de IA (Orquestador)

Tres funciones que consumen la API, siempre operando sobre datos **ya calculados** por el núcleo funcional de C++ (la IA nunca realiza el cálculo financiero numérico, solo lo interpreta):

| Función | Entrada | Salida |
|---|---|---|
| `explicar_tabla_amortizacion(tabla, datos_prestamo)` | Tabla calculada + datos del préstamo | Explicación en lenguaje simple del total pagado, interés total y punto de cruce |
| `comparar_sistemas(resumen_frances, resumen_aleman, resumen_americano)` | Resúmenes de las 3 tablas | Recomendación de cuál sistema conviene según el objetivo del usuario |
| `simular_escenario_personalizado(pregunta_usuario, datos_prestamo, nueva_tabla)` | Pregunta libre del usuario + nuevo escenario ya recalculado por el núcleo | Respuesta directa a la pregunta del usuario |

```python
# gui/ia.py
def explicar_tabla_amortizacion(tabla: list[dict], monto: float, tasa: float, meses: int) -> str:
    prompt = f"""Explica en lenguaje sencillo este préstamo:
    Monto: {monto}, Tasa anual: {tasa}%, Plazo: {meses} meses.
    Total pagado: {tabla[-1]['acumulado']}
    Total de interés: {sum(f['interes'] for f in tabla)}
    """
    return llamar_api(prompt)
```

## 7. Capa de presentación (GUI)

| Elemento | Descripción |
|---|---|
| Formulario | Monto, tasa anual, plazo, sistema de amortización (combobox) |
| Tabla de resultados | Mes, cuota, interés, capital, saldo — generada por el trabajador de C++ |
| Gráfica | Línea de saldo decreciente + barras apiladas interés/capital por mes (matplotlib embebido) |
| Panel de IA | Botón "Explicar" (función 1), botón "Comparar sistemas" (función 2), campo de pregunta libre (función 3) |

## 8. Rol de cada lenguaje — resumen

| Lenguaje | Rol | Justificación |
|---|---|---|
| **C++** | Trabajador — cálculo de todos los sistemas de amortización (francés, alemán, americano) y alto rendimiento | Control de bajo nivel, alto rendimiento en cálculos masivos y compilación a binario nativo independiente |
| **Python** | Orquestador — GUI, llamadas a la API, gráficas | Librería estándar para GUI (tkinter / ttk) y ecosistema simple para integración de APIs de IA |

## 9. Flujo completo de una interacción

1. El usuario llena el formulario y elige "sistema francés".
2. La GUI (Python) invoca al binario de C++ vía `subprocess`, pasando sistema, monto, tasa y meses.
3. C++ calcula la tabla completa con funciones puras y la devuelve como JSON en stdout.
4. Python recibe el JSON, lo muestra en la tabla y grafica la evolución del saldo.
5. El usuario presiona "Explicar resultado" → Python arma el prompt con la tabla ya calculada y llama a la API de IA.
6. La respuesta de la IA se muestra en un panel de texto junto a la tabla.

## 10. Conclusión

La arquitectura mantiene una separación estricta entre **cálculo financiero** (funciones puras en C++, sin estado, ejecutadas como un trabajador independiente de alto rendimiento) y **orquestación/presentación** (Python, con estado, maneja la GUI y las llamadas a la API de IA). La IA se integra como una capa de interpretación sobre datos ya calculados, nunca reemplazando la lógica funcional del núcleo.
