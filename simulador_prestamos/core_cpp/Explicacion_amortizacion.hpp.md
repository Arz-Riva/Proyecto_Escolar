# Explicación del archivo: amortizacion.hpp

## Propósito y Rol en la Arquitectura
Este archivo de cabecera (`.hpp`) pertenece al **Trabajador en C++** (`core_cpp`). Su objetivo es centralizar y declarar los contratos de datos (estructuras) y las firmas de las funciones puras encargadas de los cálculos de amortización.

## Contenido Planificado
1. **Estructuras de Datos:**
   - Declaración de la estructura `Fila`, que representa una fila en la tabla de amortización con los siguientes campos:
     - `mes`: Número de período/mes.
     - `cuota`: Monto total a pagar en el período.
     - `interes`: Parte de la cuota correspondiente a intereses.
     - `capital`: Parte de la cuota destinada a la amortización de capital.
     - `saldo`: Deuda remanente luego del pago.

2. **Firmas de Funciones Puras:**
   - Declaración de funciones de cálculo para cada sistema:
     - **Sistema Francés** (cuotas constantes).
     - **Sistema Alemán** (amortización de capital constante).
     - **Sistema Americano** (pago exclusivo de intereses y devolución del capital al vencimiento).

## Principios Aplicados
- **Programación Funcional:** Funciones sin efectos secundarios ni mutación de estado global.
- **Modularidad:** Separación limpia entre declaraciones (`.hpp`) e implementaciones (`.cpp`).
