# ==========================================
# Encabezados y Librerias
# ==========================================
import sys
import os

# Asegurar que el directorio de simulador_prestamos este en el sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.interfaz_flet import iniciar_interfaz_flet

# ==========================================
# Proceso Principal
# ==========================================

def main():
    """
    Punto de entrada de la aplicacion de simulacion de amortizaciones.
    Lanza la aplicacion de escritorio reactiva desarrollada con Flet.
    """
    iniciar_interfaz_flet()

# ==========================================
# Ejecucion del Script
# ==========================================

if __name__ == "__main__":
    main()

