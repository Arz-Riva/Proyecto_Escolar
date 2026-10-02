# Explicación del archivo: main.py (simulador_prestamos)

## Propósito y Rol en la Arquitectura
Este archivo es el **Punto de Entrada Principal** de la aplicación completa del simulador de préstamos. Se encarga de instanciar y ejecutar el ciclo de vida de la aplicación.

## Responsabilidades
1. **Arranque de la Aplicación:**
   - Configura el entorno inicial si es necesario.
   - Instancia la ventana principal desde el módulo `gui.ventana`.
2. **Ejecución del Main Loop:**
   - Lanza el bucle de eventos (`mainloop`) de la interfaz gráfica para mantener la aplicación en escucha de interacciones del usuario.

## Principios Aplicados
- **Simplicidad:** Mantiene el punto de entrada limpio y desacoplado, delegando toda la construcción de componentes a sus respectivos submódulos.
