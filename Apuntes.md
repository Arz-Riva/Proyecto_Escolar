# Apuntes del Proyecto: Simulador de Préstamos

## Vinculación con los Objetivos de la Materia (Plan de Materia)

### Fecha: 18 de septiembre de 2026

#### 1. Creación de la Estructura Modular del Proyecto
- **Unidad I & II:** *Fundamentos del paradigma funcional, módulos y organización de código (2.1.7 Módulos y Organización)*.
- Se definió y estructuró el espacio de trabajo en base al patrón **Orquestador-Trabajador** y **Functional Core, Imperative Shell**:
  - `simulador_prestamos/core_cpp/`: Núcleo de cálculo funcional puro en C++ (`amortizacion.hpp`, `amortizacion.cpp`) y su interfaz imperativa/CLI (`main.cpp`).
  - `simulador_prestamos/gui/`: Orquestador de la interfaz gráfica y cliente de IA en Python (`ventana.py`, `ia.py`, `graficas.py`).
  - `simulador_prestamos/main.py`: Punto de entrada principal.
- Para cada componente se generaron sus respectivos archivos de especificación y explicación (`Explicacion_*.md`), preparando el terreno para la implementación de funciones puras, inmutabilidad de datos y pruebas.

---

### Fecha: 22 de septiembre de 2026

**Prompts:**
- *"si, solo la implementacion primero."*
- *"Analiza los archivos .cpp y dime porque me marca error en el IDE"*
- *"entonce dime, ya esta todo la logica? en .cpp? si es asi, podemos pasar a hacer el GUI?"*

**Archivos involucrados:**
- `simulador_prestamos/core_cpp/amortizacion.hpp`
- `simulador_prestamos/core_cpp/amortizacion.cpp`
- `simulador_prestamos/core_cpp/main.cpp`

#### 2. Implementación del Núcleo Funcional Puro en C++
- **Unidad I & II:** *Funciones Puras, Inmutabilidad, Transparencia Referencial y Patrón Functional Core, Imperative Shell*.
- **Descripción de lo que hace el código:**
  - **`amortizacion.hpp`:** Declara la estructura inmutable `FilaTabla` (`num_mes`, `val_cuota`, `val_interes`, `val_capital`, `val_saldo`) y las firmas de las funciones puras de cálculo.
  - **`amortizacion.cpp`:**
    - Implementa funciones puras de cálculo financiero para los 3 sistemas de amortización:
      - **Sistema Francés:** `calcular_cuota_fija_frances()`, `calcular_fila_frances()`, `generar_tabla_frances()`.
      - **Sistema Alemán:** `calcular_fila_aleman()`, `generar_tabla_aleman()`.
      - **Sistema Americano:** `calcular_fila_americano()`, `generar_tabla_americano()`.
    - Todas las funciones son **deterministas y sin efectos secundarios** (dada la misma entrada, producen exactamente la misma salida sin mutar variables externas).
    - Incluye la función `serializar_tabla_json()` que formatea los datos calculados en un arreglo estándar JSON.
  - **`main.cpp` (Imperative Shell):**
    - Actúa como la capa externa imperativa que recibe argumentos por línea de comandos (`<sistema> <monto> <tasa_anual> <meses>`), valida las entradas, delega el cálculo a las funciones puras y escribe la salida JSON en `stdout`.
  - **Compilación y Pruebas:**
    - Se compiló con `g++ -Wall -Wextra -O2 amortizacion.cpp main.cpp -o amortizador.exe` generando el binario ejecutable `amortizador.exe`.
    - Se validó el cálculo y formato JSON en terminal con pruebas de los tres sistemas (`frances`, `aleman`, `americano`).

---

### Fecha: 22 de septiembre de 2026

**Prompts:**
- *"ok, procedamos con el entorno GUI, nadamas necesito por el momento que hagas las ventanas, ojo, no ocupo que hagas algo por el moemnto de IA o graficas"*

**Archivos involucrados:**
- `simulador_prestamos/gui/ventana.py`
- `simulador_prestamos/main.py`

#### 3. Implementación de la Interfaz Gráfica (GUI) y Conexión Multi-lenguaje
- **Unidad I & II:** *Integración de módulos, separación de responsabilidades y patrón Orquestador-Trabajador*.
- **Descripción de lo que hace el código:**
  - **`ventana.py`:**
    - Define la función `calcular_amortizacion(str_sistema, val_monto, val_tasa_anual, num_meses)` que invoca mediante `subprocess.run` el binario compilado `amortizador.exe` de C++, pasando los argumentos y deserializando el resultado JSON devuelto en `stdout`.
    - Implementa la clase `VentanaPrincipal(tk.Tk)` con `tkinter` y `ttk`:
      - **Panel de Formulario:** Campos de entrada para Monto del préstamo, Tasa de interés anual porcentual, Plazo en meses y selector desplegable del Sistema de amortización (Francés, Alemán, Americano).
      - **Panel de Tabla (`Treeview`):** Muestra de forma tabular las columnas calculadas (Mes, Cuota, Interés, Capital y Saldo pendiente) con formato de moneda y scrollbar vertical.
      - **Panel de Resumen Financiero:** Tarjeta con cálculo automático de Total Pagado acumulado, Total de Intereses generados y Cuota del primer mes.
      - Botones de acción: *Calcular Tabla* y *Limpiar*.
  - **`main.py`:**
    - Punto de entrada principal que inicializa la aplicación y arranca el ciclo principal de eventos `mainloop()`.

---

### Fecha: 22 de septiembre de 2026

**Prompts:**
- *"dime, hay mucho problema si cambiamos la libreria de tkinter a flet?"*
- *"listo ya descarge la libreria, ahora por favor implemntala en el proyecto, por cierto, no olvides leer los archivos de la carpeta "Roles_and_skills" y al editar los archivos haslo segun lo que este escrito"*

**Archivos involucrados:**
- `simulador_prestamos/gui/ventana.py`
- `simulador_prestamos/main.py`
- `Planificacion_proyecto/Arquitectura_Simulador_Prestamos.md`

#### 4. Migración e Implementación de la Interfaz Gráfica Moderna con Flet
- **Unidad I & II:** *Desarrollo de interfaces declarativas reactivas, desacoplamiento y patrón Orquestador-Trabajador*.
- **Descripción de lo que hace el código:**
  - **`ventana.py` (Flet):**
    - Mantiene intacta la función pura de invocación `calcular_amortizacion(str_sistema, val_monto, val_tasa_anual, num_meses)` vía `subprocess.run` contra `amortizador.exe` de C++.
    - Implementa la clase `AplicacionSimulador` con componentes declarativos de Flet (Flutter para Python):
      - **Panel de Formulario (Columna Izquierda):** Campos de texto reactivos con iconos (`ft.TextField` para monto, tasa anual, plazo) y selector `ft.Dropdown` de sistemas de amortización.
      - **Botones de Acción:** `ft.ElevatedButton` (Calcular Tabla) con estilos modernos y `ft.OutlinedButton` (Limpiar).
      - **Tarjeta de Resumen Financiero:** Muestra dinámica del total pagado, total de intereses y cuota inicial.
      - **Tabla de Resultados (`ft.DataTable` + `ft.ListView`):** Visualización de las filas de amortización (Mes, Cuota, Interés, Capital y Saldo) con soporte para scroll vertical fluido y diseño Material Design 3.
      - **Diálogo de Alerta:** Manejo de validaciones numéricas con ventanas emergentes `ft.AlertDialog`.
  - **`main.py`:**
    - Inicializa la aplicación de escritorio nativa mediante `ft.app(target=iniciar_app_flet)`.

---

### Fecha: 22 de septiembre de 2026

**Prompts:**
- *"resolver el GUI de flet a tkinter"*

**Archivos involucrados:**
- `simulador_prestamos/gui/ventana.py`
- `simulador_prestamos/main.py`

#### 5. Migración de la Interfaz Gráfica de Flet a tkinter
- **Motivo:** La librería Flet presentaba problemas de instalación y no permitía ejecutar la aplicación correctamente.
- **Descripción de lo que hace el código:**
  - **`ventana.py` (tkinter):**
    - Se conserva **idéntica** la función `calcular_amortizacion()` que invoca vía `subprocess.run` al binario compilado `amortizador.exe` de C++.
    - Se reimplementa la clase `AplicacionSimulador` usando `tkinter` y `ttk` (incluidos con Python, sin dependencias externas):
      - **Panel de Formulario (Izquierda):** Campos `ttk.Entry` con `tk.StringVar` para monto, tasa y plazo. Selector `ttk.Combobox` de sistema de amortización (Francés, Alemán, Americano).
      - **Botones de Acción:** `ttk.Button` (Calcular Tabla y Limpiar) con estilos personalizados vía `ttk.Style`.
      - **Resumen Financiero:** Etiquetas `ttk.Label` vinculadas a `StringVar` que muestran Total Pagado, Total Intereses y Cuota Mes 1 con formato de moneda.
      - **Tabla de Resultados (`ttk.Treeview`):** Columnas Mes, Cuota, Interés, Capital y Saldo con `ttk.Scrollbar` vertical.
      - **Alertas:** Se usa `messagebox.showwarning()` para validaciones.
    - Se utiliza `ttk.Style` con tema "clam" para estilizar la interfaz con colores consistentes y tipografía "Segoe UI".
    - La función de entrada se renombra de `iniciar_app_flet` a `iniciar_app`.
  - **`main.py`:**
    - Se reemplaza `flet` por `tkinter`. Se crea la ventana raíz con `tk.Tk()`, se pasa a `iniciar_app()` y se inicia el ciclo de eventos con `mainloop()`.

---

### Fecha: 24 de septiembre de 2026

**Prompts:**
- *"hola gemini, si sabes como estomos en el proyecto? si es así entonces procedamos con el apartado de gráficas que quiero implementar. (recuerda leer los archivo de la carpeta "Roles_and_skills""*
- *"si"*

**Archivos involucrados:**
- `simulador_prestamos/gui/graficas.py`
- `simulador_prestamos/gui/ventana.py`
- `simulador_prestamos/gui/Explicacion_graficas.py.md`

#### 6. Implementación del Módulo de Visualizaciones Gráficas e Integración en GUI
- **Unidad I & II:** *Modularidad, Organización de Código (2.1.7) e Integración Funcional Desacoplada*.
- **Descripción de lo que hace el código:**
  - **`graficas.py`:**
    - Implementa funciones puras desacopladas que reciben la estructura inmutable generada por el trabajador de C++ (`lista_filas`) y construyen figuras de visualización financiera con `matplotlib`:
      - `generar_figura_saldo(lista_filas, val_monto_inicial)`: Traza la curva continua y decreciente del saldo deudor desde el momento del desembolso (mes 0) hasta la liquidación del préstamo (mes $N$).
      - `generar_figura_composicion(lista_filas)`: Construye un gráfico de barras apiladas donde cada mensualidad desglosa de manera transparente el capital amortizado frente a los intereses devengados.
      - `renderizar_lienzo_en_contenedor(figura, obj_contenedor)`: Gestiona de forma limpia y reactiva el ciclo de vida del lienzo `FigureCanvasTkAgg` dentro de la interfaz gráfica.
  - **`ventana.py`:**
    - Se actualiza la arquitectura de la ventana derecha sustituyendo el contenedor estático por un componente de pestañas (`ttk.Notebook`) con estilos unificados.
    - Se añaden tres pestañas interactivas:
      1. **Tabla de Pagos:** Vista tabular clásica (`Treeview`).
      2. **Evolución del Saldo:** Visualización gráfica de la amortización acumulada.
      3. **Composición de Cuota:** Visualización gráfica del balance capital/interés.
    - Se conectan los controladores de eventos `_evento_calcular()` y `_evento_limpiar()` para generar o limpiar automáticamente las figuras al realizar simulaciones o restablecer valores.

---

### Fecha: 24 de septiembre de 2026 - 20:10:39

**Prompts:**
- *"ok, pero quiero que las graficas se comparen entre si (los tipos de amortizacion americano, frances e aleman) no olvides leer Roles_and_skills"*
- *"si"*

**Archivos involucrados:**
- `simulador_prestamos/gui/graficas.py`
- `simulador_prestamos/gui/ventana.py`
- `simulador_prestamos/gui/Explicacion_graficas.py.md`

#### 7. Implementación de Gráficas Comparativas Multi-Sistema (Francés, Alemán y Americano)
- **Unidad I & II:** *Evaluación y Análisis Comparativo de Algoritmos Funcionales, Inmutabilidad y Visualización Declarativa*.
- **Descripción de lo que hace el código:**
  - **`graficas.py`:**
    - Se refactoriza para operar de forma polimórfica y comparativa recibiendo un diccionario con los resultados de los tres sistemas (`dict_tablas`):
      - `generar_figura_comparativa_saldos(dict_tablas, val_monto_inicial)`: Superpone en un único plano cartesiano la curva convexa del sistema Francés (amortización creciente de capital), la recta diagonal del sistema Alemán (amortización uniforme constante) y la línea plana horizontal del sistema Americano (liquidación total del principal en la última cuota).
      - `generar_figura_comparativa_cuotas(dict_tablas)`: Contrasta la evolución temporal del flujo de pagos mensual (cuota fija francesa, cuota escalonada decreciente alemana y cuota reducida de solo intereses americana con desembolso final de capital).
      - `generar_figura_comparativa_costos(dict_tablas)`: Genera un gráfico de barras comparativo del interés total pagado, mostrando visual y numéricamente cuál sistema minimiza o maximiza el costo financiero del crédito.
  - **`ventana.py`:**
    - Al presionar *"Calcular Tabla"*, se orquesta de forma transparente y simultánea la llamada a C++ para los tres modelos de amortización.
    - Se incorporan 4 pestañas interactivas en `ttk.Notebook`:
      1. **Tabla de Pagos:** Detalle numérico del sistema seleccionado.
      2. **Comparativa Saldos:** Trayectoria superpuesta de liquidación de saldo.
      3. **Comparativa Cuotas:** Trayectoria de las cuotas mes a mes.
      4. **Comparativa Intereses:** Comparativa de costo total en intereses entre los 3 sistemas.

---

### Fecha: 24 de septiembre de 2026 - 20:22:56

**Prompts:**
- *"ok, algo rapido, modifica los iconos de las ventans de tk y usa los archivos que estan en la carpeta "img" el .icon usalo para la barra de tareas y el -logo para la parte superior de la ventana"*
- *"intenta de nuevo"*

**Archivos involucrados:**
- `simulador_prestamos/gui/Img/generar_recursos.py`
- `simulador_prestamos/gui/Img/intresta-icon.ico`
- `simulador_prestamos/gui/Img/intresta-icon.png`
- `simulador_prestamos/gui/Img/intresta-logo-horizontal.png`
- `simulador_prestamos/gui/ventana.py`

#### 8. Personalización de Identidad Visual (Iconos de Ventana, Barra de Tareas y Logo)
- **Unidad I & II:** *Presentación Gráfica, Integración de Recursos Multimedia e Interoperabilidad con el Sistema Operativo*.
- **Descripción de lo que hace el código:**
  - **`generar_recursos.py`:**
    - Script utilitario que convierte y renderiza los vectores SVG originales (`intresta-icon.svg` e `intresta-logo-horizontal.svg`) a formatos matriciales nativos de alta fidelidad (`.ico` y `.png`) compatibles con el motor Tkinter y la shell de Windows.
  - **`ventana.py`:**
    - Invoca a través de `ctypes` la función del API de Windows `SetCurrentProcessExplicitAppUserModelID` para registrar un App ID explícito, permitiendo que Windows asigne a la ventana su icono propio en la **barra de tareas** en lugar del icono predeterminado del intérprete de Python.
    - Carga `intresta-icon.ico` (y `intresta-icon.png`) asignándolos con `iconbitmap()` e `iconphoto()`.
    - Integra en el contenedor de cabecera (`marco_header`) el isotipo y tipografía corporativa `intresta-logo-horizontal.png`.

---

### Fecha: 26 de septiembre de 2026 - 20:28:14

**Prompts:**
- *"ok, veras quiero que me ayudes a mover el texto "Simluador de intereses y amortizaciones" a la esquina superior derecha y el texto que dice "Hecho con python y c++" quitalo."*
- *"si"*

**Archivos involucrados:**
- `simulador_prestamos/gui/ventana.py`

#### 9. Ajuste de Maquetación y Distribución del Encabezado (Header Layout)
- **Unidad I & II:** *Diseño de Interfaces Gráficas de Usuario (GUI), jerarquía visual y distribución de componentes espaciales mediante gestores geométricos (`pack`).*
- **Descripción de lo que hace el código:**
  - **`ventana.py`:**
    - Se reestructura el contenedor del encabezado (`marco_header`) para distribuir los elementos visuales en los extremos opuestos.
    - El logotipo corporativo (`lbl_logo`) se fija con `side=tk.LEFT, anchor=tk.W` manteniendo su anclaje en el borde izquierdo.
    - Se mueve el título principal de la aplicación (`ttk.Label` con estilo `Titulo.TLabel`) hacia la esquina superior derecha mediante `side=tk.RIGHT, anchor=tk.NE, pady=(4, 0)`.
    - Se elimina la etiqueta de subtítulo descriptivo (`Subtitulo.TLabel`) para limpiar la interfaz y darle un aspecto más minimalista y profesional.

---

### Fecha: 26 de septiembre de 2026 - 20:37:40

**Prompts:**
- *"Ahora debajo de el logo de Intresta y el texto que moviste, pon una barra que tengatres apartados "calcular tabla" y ahí estara lo que ya hay, otro apartado que diga "Comparar". Por el momento asi hasle despues te dire que hacer"*
- *"si"*

**Archivos involucrados:**
- `simulador_prestamos/gui/ventana.py`

#### 10. Implementación de Barra de Navegación Principal Multinivel (Main Navigation Tabs)
- **Unidad I & II:** *Diseño de Interfaces Gráficas de Usuario (GUI), arquitectura modular de vistas y control de navegación mediante contenedores jerárquicos (`ttk.Notebook`).*
- **Descripción de lo que hace el código:**
  - **`ventana.py`:**
    - Se añade un contenedor `ttk.Notebook` principal (`self.cuaderno_principal`) debajo del encabezado institucional.
    - Se configuran tres apartados principales:
      1. **"Calcular Tabla":** Encapsula el diseño previo de dos paneles (panel izquierdo de formulario y resumen financiero, y panel derecho con la tabla y gráficas comparativas).
      2. **"Comparar":** Contenedor modular independiente preparado para funcionalidades analíticas comparativas adicionales.
      3. **"Apartado 3":** Contenedor reservado para futuras herramientas del simulador.
    - Se establecen estilos visuales dedicados (`NavegacionPrincipal.TNotebook` y `NavegacionPrincipal.TNotebook.Tab`) para diferenciar la barra de navegación superior de las pestañas internas de visualización.

---

### Fecha: 28 de septiembre de 2026

**Prompts:**
- *"ok, creo que ya sabes el contexto necesario. Bien, quiero que me ayudes a que la pestaña numero 2 de el apartado GUI me compare las tablas calculadas en paralelo"*
- *"no, quiero comparar dos tablas de diferentes calculos no de distintos tipos de amortizacion."*
- *"Sí, ejecútalo"*

**Archivos involucrados:**
- `simulador_prestamos/gui/ventana.py`

**Archivos usados de Planificacion_proyecto y Roles_and_skills:**
- `Planificacion_proyecto/Arquitectura_Simulador_Prestamos.md` (patrón Orquestador-Trabajador, GUI en Python)
- `Planificacion_proyecto/bitacora.md` (registro del prompt)
- `Roles_and_skills/rules.md` (reglas de proceso, escritura snake_case, métodos privados con _, y formato)
- `Roles_and_skills/skills.md` (rol Programador: describir proceso y esperar Sí)

#### 11. Comparativa en Paralelo de Dos Cálculos Distintos (Pestaña Comparar)
- **Unidad II (2.1.7 Módulos y Organización) y Unidad III (3.1 Funciones de alto orden, map/filter/sum):** *Reutilización modular, funciones puras de resumen con `sum()` y separación Orquestador-Trabajador sin tocar el núcleo C++.*
- **Descripción de lo que hace el código:**
  - **`ventana.py`:**
    - Guarda el último cálculo de `_evento_calcular()` en memoria (`lista_filas_actual`, `dict_params_actual`) sin base de datos, reutilizando `calcular_amortizacion()` que invoca al binario C++.
    - `_construir_apartado_comparar()` ahora muestra dos `Treeview` lado a lado (Escenario A y B) con botones `Fijar actual como A/B`, `Intercambiar A/B` y `Limpiar comparativa`.
    - `_fijar_escenario_comparar()`, `_intercambiar_escenarios()`, `_limpiar_comparar()` y `_actualizar_vista_comparar()` gestionan el estado en memoria y refrescan títulos, resúmenes y diferencia `A-B` en totales e intereses.
    - `_crear_treeview_comparar()`, `_rellenar_treeview_comparar()`, `_formatear_titulo_escenario()` y `_calcular_totales_lista()` son funciones reutilizables en snake_case que evitan duplicar lógica de tabla.

---

### Fecha: 28 de septiembre de 2026

**Prompts:**
- *"ok, ahora por favor, el apartado de la pestaña 1 "calcular tabla" tiene mas apartados que son "Comparativa de saldos y comparativas de cuotas" esas dos quitalas y la "Comparativa de intereses" modificala para que muestre la relacion inerese-capital no los intereses de distintos metodos"*
- *"Sí, ejecútalo"*

**Archivos involucrados:**
- `simulador_prestamos/gui/ventana.py`
- `simulador_prestamos/gui/graficas.py`

**Archivos usados de Planificacion_proyecto y Roles_and_skills:**
- `Planificacion_proyecto/Arquitectura_Simulador_Prestamos.md` (orquestador Python, trabajador C++)
- `Planificacion_proyecto/bitacora.md` (registro del prompt)
- `Roles_and_skills/rules.md` (snake_case, constantes en mayúsculas, métodos privados con _, formato headers/funciones/proceso)
- `Roles_and_skills/skills.md` (rol Programador: describir proceso y esperar Sí)

#### 12. Simplificación de Pestañas y Relación Interés-Capital (Calcular Tabla)
- **Unidad II (2.1.7 Módulos y Organización) y Unidad III (3.1 map/filter/sum):** *Modularidad visual aislada en `graficas.py` y cálculo funcional con `sum()` sobre datos inmutables del trabajador C++.*
- **Descripción de lo que hace el código:**
  - **`graficas.py`:**
    - Nueva función pura `generar_figura_relacion_interes_capital(lista_filas)` que suma capital e interés del sistema seleccionado y grafica dos barras (Capital vs Interés) con el porcentaje de interés en el título.
  - **`ventana.py`:**
    - `_construir_panel_derecho()` deja solo `Tabla de Pagos` y `Relacion Interes-Capital`; elimina `marco_pestana_saldos` y `marco_pestana_cuotas`.
    - `_evento_calcular()` solo calcula el sistema seleccionado y guarda `lista_filas_actual` para la pestaña Comparar; ya no calcula los 3 sistemas.
    - `_actualizar_graficas()` y `_limpiar_graficas()` solo usan la nueva figura de relación.

---

### Fecha: 28 de septiembre de 2026

**Prompts:**
- *"ok, esta bien, ahora en el apartado de la pestaña dos "comparar" quita el boton intercambiar y despues, pon abajo una micro barra donde esten dos botones "Tablas" y otra "grafica" y en la cual, la primera es totalmente lo que ya hay pero la otra, mostrara una grafica mostrando la comparativa de las dos tablas A y B"*
- *"Sí, ejecútalo"*

**Archivos involucrados:**
- `simulador_prestamos/gui/ventana.py`
- `simulador_prestamos/gui/graficas.py`

**Archivos usados de Planificacion_proyecto y Roles_and_skills:**
- `Planificacion_proyecto/Arquitectura_Simulador_Prestamos.md` (orquestador Python, trabajador C++)
- `Planificacion_proyecto/bitacora.md` (registro del prompt)
- `Roles_and_skills/rules.md` (snake_case, constantes en mayúsculas, métodos privados con _, formato headers/funciones/proceso)
- `Roles_and_skills/skills.md` (rol Programador: describir proceso y esperar Sí)

#### 13. Micro Barra Tablas/Grafica en Comparar (Sin Intercambiar)
- **Unidad II (2.1.7 Módulos y Organización) y Unidad III (3.1 sum/zip):** *Vista modular con `ttk.Notebook` anidado y funciones puras de agregación para comparar dos cálculos distintos en memoria.*
- **Descripción de lo que hace el código:**
  - **`graficas.py`:**
    - Nueva función pura `generar_figura_comparativa_escenarios(lista_a, lista_b)` con dos paneles: barras agrupadas Capital/Interés A vs B y líneas de evolución de saldo A vs B.
  - **`ventana.py`:**
    - `_construir_apartado_comparar()` quita el botón `Intercambiar A/B` y crea `cuaderno_vistas_comparar` con `Tablas` (tablas paralelas existentes vía `_construir_vista_tablas_paralelas()`) y `Grafica` (`marco_vista_grafica`).
    - `_actualizar_vista_comparar()` ahora también llama a `_actualizar_grafica_comparar()` que renderiza la figura A vs B.
    - Se elimina `_intercambiar_escenarios()`.

---

### Fecha: 28 de septiembre de 2026

**Prompts:**
- *"ok, todo bien, ahora mueve los botones de "fijar tabla A y B" y "Limpiar comparativa" a la derecha y hacia arriba, despues ajusta un poco las graficas osea, que no se vean mal ni deformes"*
- *"Sí, ejecútalo"*

**Archivos involucrados:**
- `simulador_prestamos/gui/ventana.py`
- `simulador_prestamos/gui/graficas.py`

**Archivos usados de Planificacion_proyecto y Roles_and_skills:**
- `Planificacion_proyecto/bitacora.md` (registro del prompt)
- `Roles_and_skills/rules.md` (snake_case, métodos privados con _, formato headers/funciones/proceso)
- `Roles_and_skills/skills.md` (rol Programador: describir proceso y esperar Sí)

#### 14. Botones a la Derecha y Ajuste de Proporción de Gráficas
- **Unidad II (2.1.7 Módulos y Organización):** *Maquetación con `grid(sticky=ne)` y visualización con proporción fija para evitar deformación en `FigureCanvasTkAgg`.*
- **Descripción de lo que hace el código:**
  - **`ventana.py`:**
    - `_construir_apartado_comparar()` crea `marco_encabezado` con `columnconfigure(0, weight=1)`; títulos a la izquierda (`sticky=nw`) y `marco_acciones` a la derecha y arriba (`sticky=ne`).
  - **`graficas.py`:**
    - `generar_figura_relacion_interes_capital()` pasa a `figsize=(6.2, 3.8)`, `tight_layout(pad=2.0)`, fuentes 11/9/8 y `ylim max*1.25`.
    - `generar_figura_comparativa_escenarios()` pasa a `figsize=(8.0, 3.8)`, `subplots_adjust(wspace=0.35, left=0.08, right=0.97, top=0.88, bottom=0.15)`, fuentes 10/8/7 y `ylim max*1.3`.

---

### Fecha: 28 de septiembre de 2026

**Prompts:**
- *"Hagamos un pequeño histrorial. Cada calculo se guardara en un tipo de boton o barra que diga el monto y fecha junto al tipo de amortizacion, eso del extremo izquierdo hacia el centro, al otro lado un boton que diga borrar y ese calculo se quite del historia. Ojo, si esto requieere base de datos no hagas nada y consulatame que hacer"*
- *"dime antes de eso, si se cierra la ventana o proframa se borrara?"*
- *"dame mas informacion del .json"*
- *"ok, hagamoslo asi"*

**Archivos involucrados:**
- `simulador_prestamos/gui/ventana.py`
- `simulador_prestamos/historial.json` (se crea al guardar)

**Archivos usados de Planificacion_proyecto y Roles_and_skills:**
- `Planificacion_proyecto/bitacora.md` (registro del prompt)
- `Roles_and_skills/rules.md` (snake_case, constantes en mayúsculas, métodos privados con _, formato headers/funciones/proceso)
- `Roles_and_skills/skills.md` (rol Programador: describir proceso y esperar Sí)

#### 15. Historial Persistente en JSON (Apartado 3)
- **Unidad II (2.1.7 Módulos y Organización, 2.1.8 Pruebas) y Unidad III (3.1 sum):** *Persistencia ligera en archivo JSON con recálculo funcional vía trabajador C++ y lista en memoria.*
- **Descripción de lo que hace el código:**
  - **`ventana.py`:**
    - Constantes `NOMBRE_ARCHIVO_HISTORIAL` y `MAX_ENTRADAS_HISTORIAL`; estado `lista_historial` y `var_contador_historial`.
    - `_ruta_archivo_historial()`, `_cargar_historial_desde_json()` y `_guardar_historial_en_json()` gestionan `simulador_prestamos/historial.json` con solo resumen + parámetros.
    - `_evento_calcular()` llama a `_agregar_actual_a_historial()` tras calcular; `_cargar_historial_en_ventana()` recalcula con C++ sin duplicar y salta a `Calcular Tabla`.
    - `_construir_apartado_tres()` muestra filas con botón central-izquierdo (`monto | fecha | sistema`) y `Borrar` a la derecha, con scroll y `Limpiar todo`.
    - `_borrar_entrada_historial()` y `_limpiar_todo_historial()` actualizan archivo y vista.

---

### Fecha: 28 de septiembre de 2026

**Prompts:**
- *"Ahora, la pestaña 3 "aaprtado 3" ponle el nombre de "Historial""*

**Archivos involucrados:**
- `simulador_prestamos/gui/ventana.py`

#### 15.1 Renombrar Pestaña a Historial
- **Descripción:** `cuaderno_principal.add(..., text="  Historial  ")` en `ventana.py:276`.

---

### Fecha: 28 de septiembre de 2026

**Prompts:**
- *"ok, ahora hagamos lo siguiente, el texto que aparece en la parte suprior de la ventana "Simulador de Intereses y Amortizaciones" quiero que lo centres mas en terminos verticales"*

**Archivos involucrados:**
- `simulador_prestamos/gui/ventana.py`

#### 15.2 Centrado Vertical del Título del Encabezado
- **Descripción:** Título pasa de `anchor=NE, pady=(4,0)` a `anchor=E, pady=0` para centrado vertical a la derecha; logo ya estaba en `anchor=W` (centrado vertical izquierdo).

---

### Fecha: 28 de septiembre de 2026

**Prompts:**
- *"ok, dime solamente dime, puedes saber la fuente (tipo de letra) que tiene la imagen de Intresta?"*
- *"puedes implementar esa fuente en todos los textos? osea las pestañas y todo qque tenga letra? solo dime si o no, después te dire si lo haces"*
- *"ok, haslo"*

**Archivos involucrados:**
- `simulador_prestamos/gui/ventana.py`
- `simulador_prestamos/gui/graficas.py`

#### 15.3 Fuente Corporativa Segoe UI en Todos los Textos
- **Unidad II (2.1.7 Módulos y Organización):** *Unificación tipográfica con la fuente del logo (`segoeuib.ttf` / Segoe UI).*
- **Descripción de lo que hace el código:**
  - **`ventana.py`:**
    - `_configurar_estilos()` agrega `option_add("*Font", "Segoe UI 10")`; todos los estilos ttk ya usaban `Segoe UI`.
  - **`graficas.py`:**
    - Constante `FUENTE_PRINCIPAL` y `matplotlib.rcParams["font.family"] = ["Segoe UI", "Arial", "DejaVu Sans"]` para títulos, ejes y leyendas.

---

### Fecha: 28 de septiembre de 2026

**Prompts:**
- *"ok, hay un error al ejecutar el main.py ya no me muestra la ventana, analizalo porfavor y si hay un problema con la fuente, simplemente deshaz lo que te solicite anteriormente"*

**Archivos involucrados:**
- `simulador_prestamos/gui/ventana.py`
- `simulador_prestamos/gui/graficas.py`

#### 15.4 Reversión de Fuente Global por Error Tcl
- **Causa:** `option_add("*Font", "Segoe UI 10")` sin llaves provoca `_tkinter.TclError: expected integer but got "UI"` al crear `ttk.Label` en `_construir_disposicion()`.
- **Acción:** Se eliminó `option_add` y se revirtió `matplotlib.rcParams` + `FUENTE_PRINCIPAL`; se conserva `Segoe UI` solo en estilos ttk puntuales. Verificado: `main.py` ya abre ventana (timeout sin traceback).

---

### Fecha: 01 de octubre de 2026

**Prompt:**
- *"Ponte en el modo de un profesor y lee Roles_and_skills y analiza el apartado de Unidad 1 y 2 y de el archivo plan_materia.md y explica esas unidades... crea un archivo llamado Guia_de_estudio.md que explique esos temas, ojo debes de explicarlo de forma tan sencilla que lo entienda alguien que no sabe nada de programacion"*

**Archivos involucrados:**
- `Guia_de_estudio.md` (nuevo, en carpeta general Proyecto_Walter)
- `plan_materia (1).md` (Unidades I y II)
- `Roles_and_skills/skills.md`, `Roles_and_skills/rules.md`
- `Planificacion_proyecto/bitacora.md` (registro)

**Archivos usados de Planificacion_proyecto y Roles_and_skills:**
- `Planificacion_proyecto/Arquitectura_Simulador_Prestamos.md` (contexto Orquestador-Trabajador)
- `Roles_and_skills/skills.md` (Plan de estudio: apegado al plan + ejemplos en .md)
- `Roles_and_skills/rules.md` (Reglas de Proceso 1 y 2)

#### 16. Guia de estudio Unidades I y II en lenguaje sencillo
- **Unidad I y II:** *1.1 Que es PF, paradigma, funciones matematicas, cambios de estado, POO vs PF / 1.2 Comparacion estructurada-POO-funcional / 1.3 Tipos, operadores, list-dict-set-tuple, if-match, for-while / 2.1 def-return, parametros, *args-**kwargs, lambda, recursion, docstrings, modulos, assert*.
- **Descripcion de lo que hace el documento:**
  - `Guia_de_estudio.md` explica cada tema del plan sin asumir saber programar, con analogias (calculadora, receta, cajas) y ejemplos Python cortos comentados linea por linea.
  - Incluye glosario de una linea, 10 preguntas tipo examen 01/10/2026 y conexion con el proyecto (`amortizacion.cpp` como funciones puras, `graficas.py` con `sum`, `ventana.py` como POO + funcional).

---


