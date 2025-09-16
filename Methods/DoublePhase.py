# metodo_dos_fases.py
from rich.console import Console
from rich.table import Table
from pyfiglet import Figlet
import numpy as np

console = Console()

def show_simplex_table(tabla, iteracion=1, variables_basicas=None, titulo="Tabla Simplex", fase=None):
    """Muestra una tabla del método Simplex con formato profesional."""
    if fase:
        console.print(f"\n[bold underline]📊 {titulo} - Fase {fase} - Iteración {iteracion}[/bold underline]\n")
    else:
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
        variables_basicas = ["VB"] + [f"x{i}" for i in range(1, len(tabla[0]))]

    for var in variables_basicas:
        tabla_rich.add_column(var, justify="center", style="green")

    nombres_filas = ["W" if fase == 1 else "Z"] + [f"A{i}" if "A" in var else var for i, var in enumerate(variables_basicas[1:], 1) if i <= len(tabla)-1]
    # Ajustamos nombres de filas según variables básicas actuales
    nombres_filas = [nombres_filas[0]]  # Primero la función objetivo
    for i in range(1, len(tabla)):
        # Buscar qué variable está en esa fila (por posición en VB)
        if i < len(variables_basicas):
            nombres_filas.append(variables_basicas[i])
        else:
            nombres_filas.append(f"F{i}")

    for i, fila in enumerate(tabla):
        estilo_fila = "bold yellow on black" if i == 1 else None
        celdas = [nombres_filas[i]] + [f"{x:.4g}" if isinstance(x, float) else str(x) for x in fila]
        tabla_rich.add_row(*celdas, style=estilo_fila)

    console.print(tabla_rich)
    console.print("")

def double_phase():
    console.clear()
    f = Figlet(font='big')
    console.print(f.renderText('Dos Fases'), style="bold blue")
    console.print("Resuelve PL con variables artificiales en dos etapas: encontrar solución factible y luego optimizar.", style="italic")


    ## LOGICA DEL METODO ##

    # FASE 1:
    # 1. Pedir función objetivo y restricciones (igual que Simplex).
    # 2. Agregar variables artificiales donde sea necesario (>= o =).
    # 3. Crear una NUEVA función objetivo: W = suma de todas las variables artificiales.
    # 4. Construir tabla inicial con W como función objetivo.
    # 5. Aplicar Simplex para minimizar W:
    #    - Variable entrante: columna con coeficiente positivo más grande en W.
    #    - Variable saliente: mínima razón >0.
    #    - Pivoteo normal.
    #    - Mostrar cada tabla.
    # 6. Si el valor óptimo de W > 0 → problema original infactible → terminar.
    # 7. Si W = 0 → eliminar columnas de variables artificiales y pasar a Fase 2.

    # FASE 2:
    # 8. Tomar la tabla final de Fase 1 (sin columnas de artificiales).
    # 9. Reescribir la fila Z original (del problema del usuario) en términos de las variables no básicas actuales.
    #    - Usar sustitución algebraica o operaciones de fila.
    # 10. Aplicar Simplex normal con la nueva Z:
    #     - Variable entrante: coeficiente negativo más grande (para minimización).
    #     - Pivoteo hasta optimalidad.
    #     - Mostrar tablas en cada iteración.
    # 11. Mostrar solución óptima final:
    #     - Valores de variables de decisión.
    #     - Valor de Z.
    #     - Estado de variables de holgura/exceso.

    # NOTA: Si en Fase 2 alguna variable artificial permanece en la base con valor 0,
    #       se puede eliminar o mantener como variable básica degenerada.

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

    console.print("\n[bold yellow]🛠️  Paso 1: Forma estándar[/bold yellow]")
    console.print("→ Agregamos variable de holgura h₁ en (1)")
    console.print("→ Agregamos exceso e₂ y artificial A₂ en (2)")
    console.print("→ Agregamos artificial A₃ en (3)")

    console.input("\n[bold cyan]➡️  Presiona Enter para comenzar Fase 1...[/bold cyan]")

    # =============================================
    # 🧮 FASE 1: Minimizar W = A₂ + A₃
    # Variables: [x1, x2, h1, e2, A2, A3, LD]
    # =============================================

    # Tabla Fase 1 inicial
    # W = A2 + A3 → expresamos en términos de no básicas
    # A2 = 20 - x1 - 3x2 + e2
    # A3 = 10 - x1 - x2
    # W = (20 - x1 - 3x2 + e2) + (10 - x1 - x2) = 30 - 2x1 - 4x2 + e2
    # → W + 2x1 + 4x2 - e2 = 30

    tabla_f1_inicial = [
        [1, 2, 4, 0, -1, 0, 0, 30],   # W (coeficientes: W + 2x1 + 4x2 - e2 + 0h1 + 0A2 + 0A3 = 30)
        [0, 0.5, 0.25, 1, 0, 0, 0, 4], # h1
        [0, 1, 3, 0, -1, 1, 0, 20],    # A2
        [0, 1, 1, 0, 0, 0, 1, 10]      # A3
    ]

    vars_f1 = ["VB", "x₁", "x₂", "h₁", "e₂", "A₂", "A₃", "LD"]
    show_simplex_table(tabla_f1_inicial, iteracion=1, variables_basicas=vars_f1, titulo="Fase 1 - Inicial", fase=1)

    console.input("\n[bold cyan]➡️  Presiona Enter para siguiente iteración (Fase 1)...[/bold cyan]")

    # =============================================
    # 🔄 Fase 1 - Iteración 1: Entra x2 (coef más positivo en W: 4), sale A2 (min{4/0.25=16, 20/3≈6.67, 10/1=10})
    # Pivote: fila A2, columna x2 → 3
    # =============================================

    # Nueva fila x2 = fila A2 / 3
    # Actualizar W, h1, A3

    tabla_f1_iter2 = [
        [1, 2/3, 0, 0, 1/3, -4/3, 0, 10/3],  # W actualizada
        [0, 5/12, 0, 1, 1/12, -1/12, 0, 7/3], # h1
        [0, 1/3, 1, 0, -1/3, 1/3, 0, 20/3],   # x2
        [0, 2/3, 0, 0, 1/3, -1/3, 1, 10/3]    # A3
    ]

    show_simplex_table(tabla_f1_iter2, iteracion=2, variables_basicas=vars_f1, titulo="Fase 1 - Iteración 1", fase=1)

    console.input("\n[bold cyan]➡️  Presiona Enter para siguiente iteración (Fase 1)...[/bold cyan]")

    # =============================================
    # 🔄 Fase 1 - Iteración 2: Entra x1 (coef 2/3), sale A3 (min{ (7/3)/(5/12)=5.6, (20/3)/(1/3)=20, (10/3)/(2/3)=5 })
    # Pivote: fila A3, columna x1 → 2/3
    # =============================================

    # Nueva fila x1 = fila A3 * 3/2
    # Actualizar W, h1, x2

    tabla_f1_final = [
        [1, 0, 0, 0, 0, -1, -1, 0],   # ¡W = 0! → Solución factible encontrada
        [0, 0, 0, 1, -0.25, 0.25, -0.75, 0.5], # h1
        [0, 0, 1, 0, -0.5, 0.5, -0.5, 5],      # x2
        [0, 1, 0, 0, 0.5, -0.5, 1.5, 5]        # x1
    ]

    show_simplex_table(tabla_f1_final, iteracion="FINAL", variables_basicas=vars_f1, titulo="Fase 1 - Final", fase=1)

    console.print("\n[bold green]✅ FASE 1 COMPLETADA: W = 0 → Solución factible encontrada.[/bold green]")
    console.print("[bold blue]Variables básicas iniciales para Fase 2: x₁, x₂, h₁[/bold blue]")

    console.input("\n[bold cyan]➡️  Presiona Enter para comenzar Fase 2...[/bold cyan]")

    # =============================================
    # 🎯 FASE 2: Resolver problema original
    # Z = 2x1 + 3x2
    # Usamos la tabla final de Fase 1, pero eliminamos columnas de artificiales y reescribimos Z
    # =============================================

    # Nueva tabla sin A2 y A3
    # Variables: [x1, x2, h1, e2, LD]
    # Pero Z debe expresarse en términos de no básicas (e2 en este caso)

    # De la tabla anterior:
    # x1 = 5 - 0.5 e2
    # x2 = 5 + 0.5 e2
    # → Z = 2(5 - 0.5 e2) + 3(5 + 0.5 e2) = 10 - e2 + 15 + 1.5 e2 = 25 + 0.5 e2
    # → Z - 0.5 e2 = 25

    tabla_f2_inicial = [
        [1, 0, 0, 0, -0.5, 25],  # Z (coeficientes: Z - 0.5 e2 = 25)
        [0, 0, 0, 1, -0.25, 0.5], # h1
        [0, 0, 1, 0, -0.5, 5],    # x2
        [0, 1, 0, 0, 0.5, 5]      # x1
    ]

    vars_f2 = ["VB", "x₁", "x₂", "h₁", "e₂", "LD"]
    show_simplex_table(tabla_f2_inicial, iteracion=1, variables_basicas=vars_f2, titulo="Fase 2 - Inicial", fase=2)

    console.print("\n[bold green]🔍 En Fase 2, todos los coeficientes en Z son no negativos (minimización) → ¡Solución óptima![/bold green]")

    console.print("\n[bold green]✅ SOLUCIÓN ÓPTIMA:[/bold green]")
    console.print("x₁ = 5, x₂ = 5, Z = 25")
    console.print("h₁ = 0.5 (hay holgura en primera restricción)")
    console.print("e₂ = 0 (no hay exceso en segunda restricción)")

    console.input("\n[bold cyan]Presiona Enter para volver al menú...[/bold cyan]")