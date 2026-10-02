# Explicación del archivo: amortizacion.cpp

## Propósito y Rol en la Arquitectura
Este archivo implementa el **Núcleo Funcional Puro (Functional Core)** del trabajador en C++. Contiene los algoritmos matemáticos y financieros de los distintos sistemas de amortización sin depender de entradas/salidas directas ni de estado mutable global.

## Responsabilidades
1. **Cálculo de Filas Individuales:**
   - Funciones puras que reciben saldo actual, tasa de interés y parámetros correspondientes, devolviendo una nueva estructura `Fila`.
2. **Generación de Tablas Completas:**
   - Funciones que acumulan las filas mes a mes hasta completar el plazo del préstamo, devolviendo un vector (`std::vector<Fila>`).
3. **Sistemas Soportados:**
   - **Francés:** Cuota fija, interés decreciente y amortización de capital creciente.
   - **Alemán:** Amortización de capital constante, cuota e interés decrecientes.
   - **Americano:** Cuota solo cubre intereses durante el plazo; el capital total se abona en la última cuota.

## Principios Aplicados
- **Inmutabilidad y Pureza Funcional:** Cada cálculo genera nuevos valores sin modificar estructuras previas de forma destructiva.
- **Alto Rendimiento:** Procesamiento veloz en código nativo para permitir recálculos instantáneos.
