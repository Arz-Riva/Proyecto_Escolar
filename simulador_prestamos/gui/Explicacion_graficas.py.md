# Explicación del archivo: graficas.py

## Propósito y Rol en la Arquitectura
Este archivo encapsula la **Generación y Renderizado de Visualizaciones Gráficas** utilizando la librería `matplotlib`. Proporciona representaciones visuales claras de las proyecciones financieras para ser embebidas directamente en la GUI.

## Responsabilidades
1. **Comparativa de Saldo Deudor:**
   - Superpone en una sola gráfica la trayectoria del saldo para los sistemas Francés, Alemán y Americano, evidenciando las diferencias en la velocidad de amortización.
2. **Comparativa de Cuotas Mensuales:**
   - Contrasta la evolución de las cuotas a lo largo de los meses (cuota fija en el Francés, decreciente en el Alemán y reducida con pago final en el Americano).
3. **Comparativa de Costo Total (Intereses):**
   - Gráfico de barras que compara el monto total de intereses generados por cada sistema, identificando cuál resulta más económico y cuál más costoso.
4. **Integración con Tkinter:**
   - Embebe dinámicamente las figuras de `matplotlib` en contenedores de pestañas (`FigureCanvasTkAgg`).

## Funciones Implementadas
- `generar_figura_comparativa_saldos(dict_tablas, val_monto_inicial)`: Construye las 3 curvas superpuestas de saldo pendiente.
- `generar_figura_comparativa_cuotas(dict_tablas)`: Traza las 3 series de cuotas mensuales a través del plazo.
- `generar_figura_comparativa_costos(dict_tablas)`: Genera el gráfico de barras comparando los intereses totales con anotaciones numéricas en cada barra.
- `renderizar_lienzo_en_contenedor(figura, obj_contenedor)`: Limpia el contenedor Tkinter e incrusta el `FigureCanvasTkAgg` de forma reactiva.

## Principios Aplicados
- **Modularidad Visual:** Toda la configuración estética, estilos y renderizado de gráficos quedan aislados de la lógica de ventanas y de la lógica de negocio.
- **Transparencia Funcional:** Las funciones reciben diccionarios de datos inmutables y devuelven nuevas instancias de figuras sin efectos colaterales.

