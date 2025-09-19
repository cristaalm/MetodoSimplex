import questionary
from rich.console import Console
from rich.table import Table
from copy import deepcopy
from pyfiglet import Figlet

console = Console()

# Función para imprimir una tabla simplex y esperar a que el usuario presione enter
def print_table(headers, rows, title="Tabla Simplex"):
    table = Table(title=title)

    # Primera columna fija: "VB" (Variable Básica)
    table.add_column("VB", justify="center", style="bold cyan")

    # Luego, las cabeceras reales (variables + R)
    for header in headers:
        table.add_column(header, justify="center")

    # Ahora, cada fila: primer elemento es la VB, el resto son los valores
    for row in rows:
        # row[0] = nombre de la variable básica ("Z", "x1", etc.)
        # row[1:] = valores numéricos alineados con las cabeceras
        table.add_row(row[0], *[str(cell) for cell in row[1:]])

    console.print(table)

    # agregamos el que significa a, e y s
    console.print("\n")
    console.print("[bold]Significado de las variables:[/bold]")
    console.print("a: artificial")
    console.print("e: exceso")
    console.print("s: holgura")

    console.print("[dim]Presione ENTER para continuar...[/dim]")
    input()

# Función para encontrar la columna pivote (máximo coeficiente negativo en Z, para maximización)
def find_pivot_column(tableau, var_names, is_maximize):
    z_row = tableau[0][:-1]
    candidates = []

    for j in range(len(z_row)):
        vn = var_names[j]
        if vn.startswith('a'):  # Ignorar artificiales y exceso
            continue
        candidates.append((z_row[j], j))

    if not candidates:
        return -1

    if is_maximize:
        min_val, min_col = min(candidates, key=lambda x: x[0])
        if min_val >= -1e-8:
            return -1
        return min_col
    else:
        max_val, max_col = max(candidates, key=lambda x: x[0])
        if max_val <= 1e-8:
            return -1
        return max_col

def format_restriccion(coeficientes, tipo, r, n_vars):
    partes = []
    for i in range(n_vars):
        c = coeficientes[i]
        if c == 0:
            continue
        # Mostrar sin decimales si es entero
        if c == int(c):
            c_str = str(int(c))
        else:
            c_str = f"{c:.4f}".rstrip('0').rstrip('.')  # Elimina ceros innecesarios

        var = f"x{i+1}"
        if c == 1:
            partes.append(f"+ {var}" if partes else var)
        elif c == -1:
            partes.append(f"- {var}")
        elif c > 0:
            partes.append(f"+ {c_str}{var}" if partes else f"{c_str}{var}")
        else:  # c < 0
            partes.append(f"- {abs(float(c_str))}{var}")

    # Si no hay términos, poner 0
    if not partes:
        partes = ["0"]

    # Formatear R
    if r == int(r):
        r_str = str(int(r))
    else:
        r_str = f"{r:.4f}".rstrip('0').rstrip('.')

    return f"{' '.join(partes)} {tipo} {r_str}"

def format_expression(coeficientes, n_vars, is_objective=False):
    """
    Formatea una expresión matemática (objetivo o restricción) de forma legible.
    Ej: [4, 1] → "4x₁ + x₂"
    """
    partes = []
    for i in range(n_vars):
        c = coeficientes[i]
        if c == 0:
            continue

        # Mostrar enteros sin decimales
        if isinstance(c, float) and c.is_integer():
            c_display = int(c)
        else:
            c_display = c

        # Formato del número
        if isinstance(c_display, float):
            c_str = f"{c_display:.6f}".rstrip('0').rstrip('.')
        else:
            c_str = str(c_display)

        var = f"x{i+1}"

        if c > 0:
            if c == 1 and not is_objective:
                term = f"+ {var}" if partes else var
            elif c == 1:
                term = f"{var}" if not partes else f"+ {var}"
            else:
                term = f"+ {c_str}{var}" if partes else f"{c_str}{var}"
        else:  # c < 0
            abs_c = abs(c_display)
            if abs_c == 1:
                term = f"- {var}"
            else:
                term = f"- {abs_c}{var}" if isinstance(abs_c, int) else f"- {abs_c:.6f}".rstrip('0').rstrip('.') + f"{var}"
        partes.append(term)

    if not partes:
        return "0"

    return ' '.join(partes)

# Función para encontrar la fila pivote (mínima razón no negativa)
def find_pivot_row(tableau, pivot_col):
    ratios = []
    for i in range(1, len(tableau)):
        if tableau[i][pivot_col] > 0:
            ratio = tableau[i][-1] / tableau[i][pivot_col]
            ratios.append((ratio, i))
        else:
            ratios.append((float('inf'), i))
    if not ratios or all(r[0] == float('inf') for r in ratios):
        return -1  # Problema no acotado
    min_ratio = min(ratios, key=lambda x: x[0])
    return min_ratio[1]

# Función para realizar la operación de pivoteo
def pivot(tableau, pivot_row, pivot_col):
    # Hacer 1 el elemento pivote
    divisor = tableau[pivot_row][pivot_col]
    for j in range(len(tableau[pivot_row])):
        tableau[pivot_row][j] /= divisor

    # Hacer 0 los demás elementos de la columna pivote
    for i in range(len(tableau)):
        if i != pivot_row:
            factor = tableau[i][pivot_col]
            for j in range(len(tableau[i])):
                tableau[i][j] -= factor * tableau[pivot_row][j]

# Función principal del método Big M
def big_m():
    console.clear()
    f = Figlet(font='big')
    console.print(f.renderText('Metodo Big M'), style="bold blue")
    console.print("[bold green]🚀 Método Big M para Programación Lineal[/bold green]\n")

    # Preguntar objetivo
    objetivo = questionary.select(
        "¿Qué deseas hacer?",
        choices=["Maximizar", "Minimizar"]
    ).ask()

    is_maximize = objetivo == "Maximizar"

    # Número de variables
    n_vars = int(questionary.text("Número de variables de decisión:").ask())

    # Coeficientes de la función objetivo
    coef_obj = []
    coef_obj_original = []
    for i in range(n_vars):
        coef = float(questionary.text(f"Coeficiente de x{i+1} en Z:").ask())
        coef_obj_original.append(coef) 
        coef_obj.append(coef if is_maximize else -coef)  # Convertimos si es minimizar
    
    console.print(f"[bold green]→ {'Maximizar' if is_maximize else 'Minimizar'} Z = {format_expression(coef_obj_original, n_vars, is_objective=True)}[/bold green] \n")

    # Número de restricciones
    n_restricciones = int(questionary.text("Número de restricciones:").ask())

    restricciones = []
    tipos = []
    r = []

    for i in range(n_restricciones):
        console.print(f"\n[bold]Restricción {i+1}[/bold]")
        coef_restriccion = []
        for j in range(n_vars):
            c = float(questionary.text(f"Coeficiente de x{j+1}:").ask())
            coef_restriccion.append(c)
        tipo = questionary.select(
            "Tipo de restricción:",
            choices=["≤", "≥", "="]
        ).ask()
        b = float(questionary.text("Valor del lado derecho (R):").ask())
        
        restriccion_str = format_restriccion(coef_restriccion, tipo, b, n_vars)
        console.print(f"[green]→ {restriccion_str}[/green]")

        restricciones.append(coef_restriccion)
        tipos.append(tipo)
        r.append(b)

    # MOSTRAR RESUMEN DEL PROBLEMA
    console.print("\n" + "═" * 60)
    console.print(f"[bold blue]📋 PROBLEMA INGRESADO[/bold blue]")
    console.print("═" * 60)

    # Función objetivo
    obj_expr = format_expression(coef_obj_original, n_vars, is_objective=True)
    console.print(f"[bold green]{'Maximizar' if is_maximize else 'Minimizar'} Z = {obj_expr}[/bold green]")

    # Restricciones
    console.print(f"\n[bold]Restricciones:[/bold]")
    for i in range(n_restricciones):
        restr_expr = format_expression(restricciones[i], n_vars)
        console.print(f" {restr_expr} {tipos[i]} {int(r[i]) if r[i].is_integer() else r[i]:.6f}".rstrip('0').rstrip('.'))
    
    console.print("═" * 60 + "\n")

    # Construir la tabla inicial (tableau)
    # Variables: x1, x2, ..., xn, s1, s2, ..., a1, a2, ...
    M = 1e6  # Valor grande para Big M

    # Contar variables de holgura, exceso y artificiales
    n_holgura = 0
    n_exceso = 0
    n_artificial = 0

    var_names = [f"x{i+1}" for i in range(n_vars)]
    basic_vars = []  # Variables básicas actuales

    # Primera pasada: contar variables a añadir
    for tipo in tipos:
        if tipo == "≤":
            n_holgura += 1
        elif tipo == "≥":
            n_exceso += 1
            n_artificial += 1
        elif tipo == "=":
            n_artificial += 1

    # Añadir nombres de variables
    for i in range(n_holgura):
        var_names.append(f"s{i+1}")
    for i in range(n_exceso):
        var_names.append(f"e{i+1}")
    for i in range(n_artificial):
        var_names.append(f"a{i+1}")

    # Construir el tableau
    n_total_vars = len(var_names)
    n_rows = n_restricciones + 1  # +1 para la fila Z
    tableau = [[0.0] * (n_total_vars + 1) for _ in range(n_rows)]  # +1 para R

    # Llenar fila Z original: coeficientes de -Z (porque en tableau se escribe Z - c1x1 - c2x2 ... = 0)
    # Recordar: si es minimización, convertimos a maximizar -Z, así que los coeficientes en Z son los originales
    for i in range(n_vars):
        tableau[0][i] = -coef_obj[i]   # ¡OJO! Aquí va el coeficiente tal cual para -Z

    # Variables de holgura/exceso/artificiales empiezan en 0 en la fila Z (por ahora)
    # Llenar restricciones y definir variables básicas
    slack_idx = n_vars
    excess_idx = n_vars + n_holgura
    artificial_idx = n_vars + n_holgura + n_exceso

    slack_counter = 0
    excess_counter = 0
    artificial_counter = 0

    for i in range(n_restricciones):
        # Copiar coeficientes de variables de decisión
        for j in range(n_vars):
            tableau[i+1][j] = restricciones[i][j]

        # Añadir variables según tipo
        if tipos[i] == "≤":
            tableau[i+1][slack_idx + slack_counter] = 1.0
            basic_vars.append(f"s{slack_counter+1}")
            slack_counter += 1
        elif tipos[i] == "≥":
            tableau[i+1][excess_idx + excess_counter] = -1.0
            tableau[i+1][artificial_idx + artificial_counter] = 1.0
            basic_vars.append(f"a{artificial_counter+1}")
            excess_counter += 1
            artificial_counter += 1
        elif tipos[i] == "=":
            tableau[i+1][artificial_idx + artificial_counter] = 1.0
            basic_vars.append(f"a{artificial_counter+1}")
            artificial_counter += 1

        # R
        tableau[i+1][-1] = r[i]

    # Por cada restricción con variable artificial, RESTAMOS M * (esa fila) de la fila Z
    # Porque: Z = original - M * (suma de artificiales), y artificial = R - ... → sustituimos

    for i in range(n_restricciones):
        if tipos[i] in ["≥", "="]:
            # Encontrar la columna de la variable artificial en esta fila
            found = False
            for a_col in range(artificial_idx, n_total_vars):
                if abs(tableau[i+1][a_col] - 1.0) < 1e-8:  # Encontramos la artificial
                    # Restamos M veces esta fila entera de la fila Z
                    for j in range(n_total_vars + 1):
                        tableau[0][j] -= M * tableau[i+1][j]
                    found = True
                    break
            if not found:
                console.print(f"[red]❌ No se encontró variable artificial en restricción {i+1}[/red]")

    # Mostrar tabla inicial
    console.print(f"\n[bold cyan]Tabla Inicial (Big M)[/bold cyan]")
    headers = var_names + ["R"]
    rows = []
    for i in range(1, len(tableau)):
        rows.append([basic_vars[i-1]] + [f"{val:.4f}" for val in tableau[i]])
    rows.append(["Z"] + [f"{val:.4f}" for val in tableau[0]])
    print_table(headers, rows, "Iteración 0")

    iteracion = 1
    while True:
        # Encontrar columna pivote
        pivot_col = find_pivot_column(tableau, var_names, True)  # Siempre maximizando internamente
        if pivot_col == -1:
            console.print("\n[green bold]✅ ¡Solución óptima encontrada![/green bold]")
            break

        # Encontrar fila pivote
        pivot_row = find_pivot_row(tableau, pivot_col)
        if pivot_row == -1:
            console.print("\n[red bold]❌ Problema no acotado[/red bold]")
            return

        # Actualizar variable básica
        entering_var = var_names[pivot_col]
        leaving_var = basic_vars[pivot_row - 1]
        basic_vars[pivot_row - 1] = entering_var

        console.print(f"\n[bold yellow]Iteración {iteracion}[/bold yellow]")
        console.print(f"Variable entrante: {entering_var}, Variable saliente: {leaving_var}, Elemento pivote: ({pivot_row}, {pivot_col})")

        # Pivoteo
        pivot(tableau, pivot_row, pivot_col)

        # Mostrar tabla actual
        rows = []
        for i in range(1, len(tableau)):
            rows.append([basic_vars[i-1]] + [f"{val:.4f}" for val in tableau[i]])
        rows.append(["Z"] + [f"{val:.4f}" for val in tableau[0]])
        print_table(headers, rows, f"Iteración {iteracion}")

        iteracion += 1
        
    # Mostrar solución
    # Verificar si hay variables artificiales en la solución final con valor > 0 (infactibilidad)
    for i, bv in enumerate(basic_vars):
        if bv.startswith('a') and abs(tableau[i+1][-1]) > 1e-5:
            console.print("\n[red bold]❌ SOLUCIÓN INFACTIBLE: Variable artificial en base con valor positivo.[/red bold]")
            return

    console.print("\n[bold green]📈 SOLUCIÓN ÓPTIMA[/bold green]")
    solution = {var: 0.0 for var in var_names}
    for i in range(len(basic_vars)):
        solution[basic_vars[i]] = tableau[i+1][-1]

    console.print("Valores de las variables:")
    for var in var_names[:n_vars]:  # Solo variables de decisión originales
        console.print(f"  {var} = {solution[var]:.4f}")

    optimal_value = tableau[0][-1] if is_maximize else -tableau[0][-1]
    console.print(f"\n[bold]Valor óptimo de Z: {optimal_value:.4f}[/bold]")
    console.print("Presione ENTER para continuar...")
    input()

    # Verificar si hay variables artificiales en la solución con valor > 0
    for i in range(n_vars + n_holgura + n_exceso, n_total_vars):
        if solution[var_names[i]] > 1e-5:
            console.print("[red]⚠️  ATENCIÓN: Variable artificial en solución final. El problema original es infactible.[/red]")