# Explicación del archivo: ventana.py

## Propósito y Rol en la Arquitectura
Este archivo es el **Orquestador Principal de la Interfaz Gráfica de Usuario (GUI)** en Python. Se encarga de la interacción visual con el usuario, la recolección de entradas, la invocación del binario en C++ mediante subprocesos y la presentación de resultados.

## Responsabilidades
1. **Formulario de Entrada de Datos:**
   - Campos interactivos para capturar: Monto del préstamo, Tasa de interés anual, Plazo en meses y Sistema de amortización (Francés, Alemán, Americano).
2. **Comunicación con el Trabajador C++:**
   - Función `calcular_amortizacion(sistema, monto, tasa, meses)` que invoca al ejecutable compilado mediante `subprocess.run`, capturando la salida JSON producida por C++.
3. **Presentación de la Tabla:**
   - Despliegue de los datos calculados (mes a mes con cuota, interés, capital y saldo) en una tabla o Treeview interactivo.
4. **Integración de Componentes:**
   - Embeber las gráficas generadas por `graficas.py`.
   - Conectar los eventos y botones del panel de IA definidos en `ia.py`.

## Principios Aplicados
- **Patrón Orquestador-Trabajador:** La GUI no calcula fórmulas financieras; delega el cómputo al ejecutable C++ y orquesta las vistas y llamadas a la IA.
