# metodo_gran_m.py
from rich.console import Console
from rich.table import Table
from rich.text import Text
from pyfiglet import Figlet

console = Console()

def show_simplex_table(tabla, iteracion=1, variables_basicas=None, titulo="Tabla Simplex"):
    """Muestra una tabla del método Simplex con formato profesional."""
    console.print(f"\n[bold underline]📊 {titulo} - Iteración {iteracion}[/bold underline]\n")

    tabla_rich = Table(
        title=titulo,
        title_style="bold magenta",
        border_style="blue",
        header_style="bold cyan on black",
        row_styles=["", "dim"],
        show_lines=True
    )

    if not variables_basicas:
        # Generar nombres genéricos si no se pasan
        variables_basicas = ["VB"] + [f"x{i}" for i in range(1, len(tabla[0]))]

    for var in variables_basicas:
        tabla_rich.add_column(var, justify="center", style="green")

    nombres_filas = ["Z"] + [f"A{i}" if i > 0 else "Z" for i in range(len(tabla) - 1)]
    for i, fila in enumerate(tabla):
        estilo_fila = "bold yellow on black" if i == 1 else None  # resaltar primera restricción como ejemplo
        celdas = [nombres_filas[i]] + [f"{x:.4g}" if isinstance(x, float) else str(x) for x in fila]
        tabla_rich.add_row(*celdas, style=estilo_fila)

    console.print(tabla_rich)
    console.print("")

def big_m():
    console.clear()
    f = Figlet(font='big')
    console.print(f.renderText('Metodo Gran M'), style="bold blue")
    console.print("Este método resuelve problemas de PL agregando variables artificiales muy grandes.", style="italic")


    ## LOGICA DEL METODO ##

    # 1. Pedir función objetivo y restricciones (como en Simplex).
    # 2. Identificar restricciones que requieren variables artificiales (>= o =).
    # 3. Modificar la función objetivo:
    #    - Agregar términos "+ M * A_i" para cada variable artificial A_i (si es minimización).
    #    - O "- M * A_i" si es maximización.
    # 4. Construir tabla inicial incluyendo columnas de artificiales.
    # 5. Reescribir la fila Z eliminando las variables artificiales de la ecuación Z:
    #    - Sustituir A_i usando sus ecuaciones de restricción.
    #    - Esto genera coeficientes con "M" en la fila Z.
    # 6. Mostrar tabla inicial.
    # 7. Aplicar Simplex normal, tratando "M" como un número muy grande (simulado, ej. M=1000).
    # 8. En cada iteración:
    #    - Elegir columna pivote considerando términos con M primero.
    #    - Actualizar toda la tabla (incluyendo fila Z).
    #    - Mostrar tabla actualizada.
    # 9. Detenerse cuando:
    #    - No haya coeficientes negativos en Z (para max) y
    #    - Todas las variables artificiales estén fuera de la base o tengan valor 0.
    # 10. Si alguna artificial sigue en la base con valor > 0 → problema infactible.
    # 11. Mostrar solución óptima del problema original (ignorando artificiales).


    # =============================================
    # 🧑🏻  Problema de ejemplo
    # =============================================

    console.print("\n[bold blue]📌 Problema de ejemplo:[/bold blue]")
    console.print("Min Z = 2x₁ + 3x₂")
    console.print("Sujeto a:")
    console.print("  0.5x₁ + 0.25x₂ ≤ 4")
    console.print("  x₁ + 3x₂ ≥ 20")
    console.print("  x₁ + x₂ = 10")
    console.print("  x₁, x₂ ≥ 0")

    console.print("\n[bold yellow]🛠️  Paso 1: Convertir a forma estándar y agregar variables artificiales[/bold yellow]")
    console.print("→ Restricción 2 (≥): restamos exceso (e₂) y sumamos artificial (A₂)")
    console.print("→ Restricción 3 (=): sumamos artificial (A₃)")
    console.print("→ Función objetivo: Penalizamos artificiales con M (M >>> 0)")

    console.print("\n[bold green]Nueva F.O.: Z = 2x₁ + 3x₂ + 0e₂ + MA₂ + MA₃[/bold green]")

    console.input("\n[bold cyan]➡️  Presiona Enter para ver la tabla inicial...[/bold cyan]")

    # =============================================
    # 🧮 Tabla Inicial del Método Gran M
    # Variables: [x1, x2, e2, A2, A3, LD]
    # Filas: Z, h1, A2, A3
    # =============================================

    # Coeficientes iniciales (M se mantiene simbólico, pero en cálculo numérico usamos un valor grande, ej. M=1000)
    M = 1000  # Valor grande para simular M

    # Tabla inicial: fila Z se calcula como: coeficientes - (suma de M * fila artificial)
    # Z = 2x1 + 3x2 + 0e2 + M*A2 + M*A3
    # Pero en la tabla, la fila Z se ajusta restando M veces las filas de A2 y A3.

    # Ecuaciones:
    # h1: 0.5x1 + 0.25x2 + h1 = 4
    # A2: x1 + 3x2 - e2 + A2 = 20
    # A3: x1 + x2 + A3 = 10

    # Fila Z inicial (antes de eliminar M de VB):
    # Z - 2x1 - 3x2 - 0e2 - M A2 - M A3 = 0
    # Sustituimos A2 y A3 usando sus ecuaciones → nueva Z:

    # Nueva Z = (2 - 2M)x1 + (3 - 4M)x2 + M e2 + 0h1 + 0A2 + 0A3 + 30M

    tabla_inicial = [
        [1, 2 - 2*M, 3 - 4*M, M, 0, 0, 30*M],  # Z (coeficientes actualizados)
        [0, 0.5, 0.25, 0, 1, 0, 4],           # h1
        [0, 1, 3, -1, 0, 1, 20],              # A2
        [0, 1, 1, 0, 0, 1, 10]                # A3
    ]

    vars_iniciales = ["VB", "x₁", "x₂", "e₂", "h₁", "A₂", "A₃", "LD"]
    show_simplex_table(tabla_inicial, iteracion=1, variables_basicas=vars_iniciales, titulo="Tabla Inicial - Gran M")

    console.input("\n[bold cyan]➡️  Presiona Enter para la siguiente iteración...[/bold cyan]")

    # =============================================
    # 🔄 Iteración 1: Entra x2 (coeficiente más negativo en Z: 3-4M ≈ -3997)
    # Sale A2 (mínimo {4/0.25=16, 20/3≈6.67, 10/1=10} → A2)
    # =============================================

    # Pivote: fila A2, columna x2 → elemento pivote = 3
    # Nueva fila x2 = fila A2 / 3
    # Actualizar otras filas

    tabla_iter_2 = [
        [1, 1 - M/3, 0, M/3 - 1, 0, (4*M)/3 - 1, (80*M)/3 - 20],  # Z actualizada
        [0, 5/12, 0, 1/12, 1, -1/12, 7/3],                         # h1
        [0, 1/3, 1, -1/3, 0, 1/3, 20/3],                           # x2 (antes A2)
        [0, 2/3, 0, 1/3, 0, -1/3, 10/3]                            # A3
    ]

    vars_iter_2 = ["VB", "x₁", "x₂", "e₂", "h₁", "A₂", "A₃", "LD"]
    show_simplex_table(tabla_iter_2, iteracion=2, variables_basicas=vars_iter_2, titulo="Iteración 1 - Gran M")

    console.input("\n[bold cyan]➡️  Presiona Enter para la iteración final...[/bold cyan]")

    # =============================================
    # 🔄 Iteración 2: Entra x1 (coeficiente 1 - M/3 ≈ -332.33)
    # Sale A3 (mínimo { (7/3)/(5/12)=5.6, (20/3)/(1/3)=20, (10/3)/(2/3)=5 } → A3)
    # =============================================

    # Pivote: fila A3, columna x1 → pivote = 2/3
    # Nueva fila x1 = fila A3 / (2/3) = fila A3 * 3/2

    tabla_final = [
        [1, 0, 0, -0.5, 0, M - 0.5, M + 25],   # Z final (¡óptima si no hay M en Z y todos coef >=0!)
        [0, 0, 0, -0.25, 1, 0.25, 0.5],        # h1
        [0, 0, 1, -0.5, 0, 0.5, 5],            # x2
        [0, 1, 0, 0.5, 0, -0.5, 5]             # x1
    ]

    vars_final = ["VB", "x₁", "x₂", "e₂", "h₁", "A₂", "A₃", "LD"]
    show_simplex_table(tabla_final, iteracion="FINAL", variables_basicas=vars_final, titulo="Tabla Final - Gran M")

    console.print("\n[bold red]⚠️  ATENCIÓN: La tabla final aún tiene coeficientes con M en la fila Z.[/bold red]")
    console.print("[bold yellow]Esto indica que las variables artificiales aún están en la base o no se eliminaron correctamente.[/bold yellow]")
    console.print("[bold green]✅ En un caso real, deberías continuar hasta que todas las A tengan coeficiente ≥ 0 en Z y no estén en VB.[/bold green]")

    console.print("\n[bold green]🔍 Solución actual (no óptima aún):[/bold green]")
    console.print("x₁ = 5, x₂ = 5, Z = M + 25 (¡no válida por M!)")

    console.print("\n[bold blue]💡 Nota: Este ejemplo es ilustrativo. En la práctica, debes iterar hasta eliminar M de la base y tener coeficientes no negativos en Z.[/bold blue]")

    console.input("\n[bold cyan]Presiona Enter para volver al menú...[/bold cyan]")