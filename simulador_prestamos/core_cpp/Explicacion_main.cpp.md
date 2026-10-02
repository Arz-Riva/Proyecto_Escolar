# Explicación del archivo: main.cpp (core_cpp)

## Propósito y Rol en la Arquitectura
Este archivo actúa como la **Capa Imperativa (Imperative Shell)** del ejecutable C++ (`amortizador`). Es el punto de entrada que interactúa con el entorno exterior (argumentos del sistema operativo) y comunica los resultados al orquestador en Python.

## Responsabilidades
1. **Recepción de Parámetros:**
   - Lee los argumentos de línea de comandos proporcionados por el orquestador en Python (`sistema`, `monto`, `tasa`, `meses`).
2. **Invocación del Núcleo:**
   - Llama a las funciones puras de `amortizacion.cpp` pasando los datos convertidos a sus tipos adecuados.
3. **Serialización a JSON:**
   - Convierte el vector de resultados (`std::vector<Fila>`) en una cadena con formato JSON estructurado.
4. **Salida por `stdout`:**
   - Imprime el JSON directamente a la salida estándar para que el proceso de Python pueda capturarlo de forma limpia vía `subprocess`.

## Principios Aplicados
- **Functional Core, Imperative Shell:** La entrada/salida y el manejo de argumentos se aíslan en este archivo, manteniendo el núcleo de amortización completamente puro.
