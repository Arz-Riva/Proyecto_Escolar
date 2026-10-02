# ==========================================
# Encabezados y Librerias
# ==========================================
import sys
import os
import tkinter as tk

# Asegurar que el directorio de simulador_prestamos este en el sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.ventana import iniciar_app

# ==========================================
# Proceso Principal
# ==========================================

def main():
    """
    Punto de entrada de la aplicacion de simulacion de amortizaciones.
    Lanza la ventana de escritorio nativa mediante tkinter.
    """
    ventana_raiz = tk.Tk()
    iniciar_app(ventana_raiz)
    ventana_raiz.mainloop()

# ==========================================
# Ejecucion del Script
# ==========================================

if __name__ == "__main__":
    main()
