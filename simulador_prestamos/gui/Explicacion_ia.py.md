# Explicación del archivo: ia.py

## Propósito y Rol en la Arquitectura
Este archivo implementa la **Capa de Inteligencia Artificial** dentro del orquestador en Python. Se encarga de construir prompts enriquecidos con datos previamente calculados por C++ y comunicarse con la API de IA para generar interpretaciones y comparaciones en lenguaje natural.

## Responsabilidades
1. **Interpretación de Amortización (`explicar_tabla_amortizacion`):**
   - Recibe la tabla generada y los parámetros iniciales del préstamo.
   - Genera una explicación accesible del costo financiero, total de intereses y evolución de las cuotas.
2. **Comparativa Multimodelo (`comparar_sistemas`):**
   - Recibe los resúmenes financieros de los tres sistemas (Francés, Alemán, Americano).
   - Genera una comparativa detallada y sugiere la mejor opción según el objetivo del usuario (menor pago inicial, menor costo financiero total o estabilidad de cuota).
3. **Escenarios Personalizados (`simular_escenario_personalizado`):**
   - Responde preguntas personalizadas formuladas por el usuario, analizando el contexto de un escenario recalculado por el núcleo C++.
4. **Comunicación Segura con la API:**
   - Manejo de llaves de API, gestión de errores de red y configuración de parámetros del modelo.

## Principios Aplicados
- **La IA como Intérprete, no como Calculadora:** La IA nunca calcula las fórmulas matemáticas; opera únicamente sobre los datos exactos provistos por el trabajador funcional en C++.
