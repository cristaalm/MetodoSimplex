# metodo_simplex.py
from rich.console import Console
from rich.table import Table
from rich.text import Text
from pyfiglet import Figlet

console = Console()

def show_simplex_table(tabla, iteracion=1, variables_basicas=None):
    """Muestra una tabla del método Simplex con formato profesional."""
    console.print(f"\n[bold underline]📊 Iteración {iteracion}[/bold underline]\n")

    tabla_rich = Table(
        title="Tabla Simplex",
        title_style="bold magenta",
        border_style="blue",
        header_style="bold cyan on black",
        row_styles=["", "dim"],  # Alterna colores para mejor legibilidad
        show_lines=True  # Muestra líneas entre filas (opcional, pero útil)
    )

    # Suponemos que la primera fila es el encabezado: VB + variables + LD
    if not variables_basicas:
        variables_basicas = ["Z"] + [f"x{i+1}" for i in range(len(tabla[0]) - 2)] + ["LD"]

    # Agregar columnas
    for var in variables_basicas:
        tabla_rich.add_column(var, justify="center", style="green")

    # Agregar filas
    nombres_filas = ["Z"] + [f"x{i+1}" for i in range(len(tabla) - 1)]
    for i, fila in enumerate(tabla):
        # Resaltar fila pivote en iteraciones (opcional)
        estilo_fila = "bold yellow on black" if i == 1 else None  # ejemplo: resaltar x1
        celdas = [nombres_filas[i]] + [str(round(x, 4)) for x in fila]  # redondear para limpieza
        tabla_rich.add_row(*celdas, style=estilo_fila)

    console.print(tabla_rich)
    console.print("")  # espacio extra

def simplex():
    console.clear()
    f = Figlet(font='big')
    console.print(f.renderText('Metodo Simplex'), style="bold blue")
    console.print("Resuelve problemas de programación lineal con cualquier número de variables.", style="italic")

    ## LOGICA DEL METODO ##

    # 1. Pedir al usuario la función objetivo (max o min) y sus coeficientes.
    # 2. Pedir el número de restricciones y, para cada una:
    #    - Coeficientes de las variables
    #    - Tipo de desigualdad (<=, >=, =)
    #    - Lado derecho (LD)
    # 3. Convertir el problema a forma estándar:
    #    - Agregar variables de holgura para <=.
    #    - Agregar variables de exceso + artificiales para >=.
    #    - Agregar variables artificiales para =.
    # 4. Construir la tabla inicial del Simplex (matriz aumentada).
    # 5. Mostrar la tabla inicial con rich.Table.
    # 6. Iterar hasta encontrar la solución óptima:
    #    a. Identificar variable entrante (coeficiente más negativo en Z para max).
    #    b. Identificar variable saliente (mínima razón LD/columna entrante, >0).
    #    c. Calcular elemento pivote y actualizar la tabla.
    #    d. Mostrar la nueva tabla en cada iteración.
    # 7. Verificar optimalidad (todos coeficientes en Z >= 0 para max).
    # 8. Extraer y mostrar la solución óptima:
    #    - Valores de variables básicas.
    #    - Valor de Z.
    #    - Variables no básicas = 0.
    # 9. Opcional: Mostrar análisis de sensibilidad o precios sombra.

    # ==============================================
    # EJEMPLO DE SIMPLEX
    # ==============================================

    # ==============================================
    # 🧮 SIMULACIÓN DE LÓGICA DEL MÉTODO SIMPLEX
    # (Reemplaza esto con tu lógica real)
    # ==============================================

    # Ejemplo: Tabla inicial (Max Z = 3x1 + 5x2)
    # Sujeto a:
    #   x1 <= 4
    #   2x2 <= 12
    #   3x1 + 2x2 <= 18

    # Tabla inicial Simplex (con variables de holgura)
    tabla_iteracion_1 = [
        [1, -3, -5, 0, 0, 0, 0],      # Fila Z
        [0, 1, 0, 1, 0, 0, 4],        # x3 (h1)
        [0, 0, 2, 0, 1, 0, 12],       # x4 (h2)
        [0, 3, 2, 0, 0, 1, 18]        # x5 (h3)
    ]

    show_simplex_table(tabla_iteracion_1, iteracion=1, variables_basicas=["VB", "x1", "x2", "h1", "h2", "h3", "LD"])

    console.input("\n[bold cyan]➡️  Presiona Enter para ver la siguiente iteración...[/bold cyan]")

    # Tabla después de una iteración (pivotando en x2)
    tabla_iteracion_2 = [
        [1, -3, 0, 0, 2.5, 0, 30],    # Z actualizada
        [0, 1, 0, 1, 0, 0, 4],
        [0, 0, 1, 0, 0.5, 0, 6],      # x2 entra
        [0, 3, 0, 0, -1, 1, 6]
    ]

    show_simplex_table(tabla_iteracion_2, iteracion=2, variables_basicas=["VB", "x1", "x2", "h1", "h2", "h3", "LD"])

    console.input("\n[bold cyan]➡️  Presiona Enter para ver la solución final...[/bold cyan]")

    # Tabla final (óptima)
    tabla_final = [
        [1, 0, 0, 0, 1.5, 1, 36],     # Z*
        [0, 1, 0, 1, 0, 0, 4],        # x1
        [0, 0, 1, 0, 0.5, 0, 6],      # x2
        [0, 0, 0, -3, 0.5, 1, 6]      # h3
    ]

    show_simplex_table(tabla_final, iteracion="FINAL", variables_basicas=["VB", "x1", "x2", "h1", "h2", "h3", "LD"])

    console.print("\n[bold green]✅ SOLUCIÓN ÓPTIMA ENCONTRADA[/bold green]")
    console.print("Z* = 36, x1 = 4, x2 = 6", style="bold yellow")

    console.input("\n[bold cyan]Presiona Enter para volver al menú...[/bold cyan]")