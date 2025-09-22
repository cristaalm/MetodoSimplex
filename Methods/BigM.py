import questionary
from rich.console import Console
from rich.table import Table
from copy import deepcopy
from pyfiglet import Figlet
from .Simplex import construir_tabla_big_m
from .table_display import fmt_num

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

# Formateador opcional para mostrar términos con M (solo visual)
def fmt_with_M(value, M=1e6, ndigits=4):
    try:
        if M <= 0:
            return fmt_num(value, ndigits)
        k = round(value / M)
        remainder = value - k * M
        # Si es prácticamente múltiplo de M
        if abs(remainder) < max(1e-8 * max(1.0, abs(value)), 1e-6):
            if k == 0:
                return "0"
            if k == 1:
                return "M"
            if k == -1:
                return "-M"
            return f"{k}M"
        # Si contiene un término M dominante y un residual pequeño
        if abs(k) >= 1:
            rem_str = fmt_intsmart(remainder, ndigits)
            if k == 1:
                sign = "+" if remainder >= 0 else "-"
                return f"M {sign} {rem_str.lstrip('-')}"
            elif k == -1:
                sign = "+" if remainder >= 0 else "-"
                return f"-M {sign} {rem_str.lstrip('-')}"
            else:
                sign = "+" if remainder >= 0 else "-"
                return f"{k}M {sign} {rem_str.lstrip('-')}"
        # De lo contrario, mostrar número normal
        return fmt_intsmart(value, ndigits)
    except Exception:
        return fmt_intsmart(value, ndigits)

# Formateador que muestra enteros sin decimales y decimales con 4 dígitos; clamp a 0 cercano
def fmt_intsmart(x, ndigits=4, eps=5e-5):
    try:
        if abs(x) < eps:
            return f"{0}"
        rx = round(x)
        if abs(x - rx) < eps:
            return f"{int(rx)}"
        return f"{x:.{ndigits}f}"
    except Exception:
        return f"{x}"

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

    # Construcción del tableau usando la implementación validada en Simplex.py
    # Mapear operadores unicode a ASCII requeridos por construir_tabla_big_m
    op_map = {"≤": "<=", "≥": ">=", "=": "="}
    ops_ascii = [op_map[t] for t in tipos]

    # construir_tabla_big_m asume maximización; ya ajustamos coef_obj para minimizar si aplica
    M = 1e6
    tabla_np, col_names = construir_tabla_big_m(coef_obj, restricciones, r, ops_ascii, M=M)

    # Convertir a listas y mover la fila Z (última) al inicio para nuestro ciclo de pivoteo
    tabla_list = tabla_np.tolist()
    tableau = [tabla_list[-1]] + tabla_list[:-1]

    # Nombres de variables de columnas (sin el término independiente LD/R)
    var_names = col_names[:-1]

    # Detectar variables básicas automáticamente por columna identidad en las filas de restricciones
    num_rows = len(tableau) - 1  # sin la fila Z
    num_cols = len(var_names)
    basic_vars = []
    for r_idx in range(1, num_rows + 1):
        vb = ""
        for c_idx in range(num_cols):
            col_vec = [tableau[row][c_idx] for row in range(1, num_rows + 1)]
            if col_vec.count(0.0) == num_rows - 1 and abs(col_vec[r_idx - 1] - 1.0) < 1e-8:
                vb = var_names[c_idx]
                break
        basic_vars.append(vb if vb else f"fila{r_idx}")

    # Construir mapeo de nombres para variables agregadas en el orden de las restricciones:
    # Por cada fila de restricción i, si hay holgura (h*) con coef 1 o exceso (e*) con coef -1,
    # se les asigna nombres S1, S2, S3... en ese mismo orden. Artificiales (a*) se mantienen.
    added_order = []  # lista de (col_idx, name) en orden de restricción
    for i_row in range(1, num_rows + 1):
        # Buscar holgura con 1.0
        for j in range(num_cols):
            name = var_names[j]
            val = tableau[i_row][j]
            if isinstance(name, str) and name.startswith('h') and abs(val - 1.0) < 1e-8:
                added_order.append((j, name))
                break  # solo una agregada por restricción (para <=)
        # Buscar exceso con -1.0 (para >=)
        for j in range(num_cols):
            name = var_names[j]
            val = tableau[i_row][j]
            if isinstance(name, str) and name.startswith('e') and abs(val + 1.0) < 1e-8:
                added_order.append((j, name))
                break

    name_map = {name: name for name in var_names}
    s_counter = 1
    for col_idx, orig_name in added_order:
        name_map[orig_name] = f"S{s_counter}"
        s_counter += 1

    # Función de mapeo general para headers/VB
    def map_var(name: str) -> str:
        if not isinstance(name, str):
            return name
        if name in name_map:
            return name_map[name]
        return name

    # Mostrar tabla inicial (ajuste visual: si es minimización, invertimos la fila Z solo para mostrar)
    console.print(f"\n[bold cyan]Tabla Inicial (Big M)[/bold cyan]")
    # Construir orden de columnas para visualización: x's, luego S1,S2,S3..., luego artificiales
    x_indices = [j for j, nm in enumerate(var_names) if isinstance(nm, str) and nm.startswith('x')]
    s_index_pairs = []  # (S_num, col_index)
    other_indices = []
    for j, nm in enumerate(var_names):
        disp = map_var(nm)
        if isinstance(disp, str) and disp.startswith('S') and disp[1:].isdigit():
            s_index_pairs.append((int(disp[1:]), j))
        elif not (isinstance(nm, str) and nm.startswith('x')):
            other_indices.append(j)
    s_indices_sorted = [j for _, j in sorted(s_index_pairs, key=lambda t: t[0])]
    display_cols = x_indices + s_indices_sorted + other_indices

    headers = [map_var(var_names[j]) for j in display_cols] + ["R"]
    rows = []

    # Determinar pivote de la iteración 0 para resaltar (antes de pivotear)
    pivot_col0 = find_pivot_column(tableau, var_names, True)
    pivot_row0 = find_pivot_row(tableau, pivot_col0) if pivot_col0 != -1 else -1
    disp_pivot_col0 = display_cols.index(pivot_col0) if pivot_col0 != -1 and pivot_col0 in display_cols else -1

    for i in range(1, len(tableau)):
        vb_disp = map_var(basic_vars[i-1])
        row_vals = []
        for k, j in enumerate(display_cols):
            val_str = fmt_intsmart(tableau[i][j])
            row_vals.append(val_str)
        row_vals.append(fmt_intsmart(tableau[i][-1]))
        rows.append([vb_disp] + row_vals)
    z_display = tableau[0][:]
    if not is_maximize:
        z_display = [-v for v in z_display]
    z_vals = [fmt_with_M(z_display[j], M) for j in display_cols] + [fmt_with_M(z_display[-1], M)]
    rows.append(["Z"] + z_vals)
    print_table(headers, rows, "Tabla Inicial")

    iteracion = 1
    while True:
        # Encontrar columna pivote en el estado ACTUAL de la tabla (antes de pivotear)
        pivot_col = find_pivot_column(tableau, var_names, True)
        if pivot_col == -1:
            # Mostrar tabla final sin resaltar pivote y con el LD de Z resaltado
            rows = []
            for i in range(1, len(tableau)):
                vb_disp = map_var(basic_vars[i-1])
                row_vals = [fmt_intsmart(tableau[i][j]) for j in display_cols] + [fmt_intsmart(tableau[i][-1])]
                rows.append([vb_disp] + row_vals)
            z_display = tableau[0][:]
            if not is_maximize:
                z_display = [-v for v in z_display]
            z_vals = [fmt_with_M(z_display[j], M) for j in display_cols] + [fmt_with_M(z_display[-1], M)]
            # Resaltar valor óptimo en LD
            z_vals[-1] = f"[black on bright_cyan]{z_vals[-1]}[/]"
            console.print(f"\n[bold yellow]Iteración FINAL[/bold yellow]")
            print_table([map_var(var_names[j]) for j in display_cols] + ["R"], rows + [["Z"] + z_vals], "FINAL")
            console.print("\n[green bold]✅ ¡Solución óptima encontrada![/green bold]")
            break

        # Encontrar fila pivote
        pivot_row = find_pivot_row(tableau, pivot_col)
        if pivot_row == -1:
            console.print("\n[red bold]❌ Problema no acotado[/red bold]")
            return

        # Variables entrante/saliente (con nombres visuales)
        entering_var = var_names[pivot_col]
        leaving_var = basic_vars[pivot_row - 1]

        console.print(f"\n[bold yellow]Iteración {iteracion}[/bold yellow]")
        # Mostrar SOLO el valor del elemento pivote como pediste
        pivot_val_disp = fmt_intsmart(tableau[pivot_row][pivot_col])
        console.print(f"Variable entrante: {map_var(entering_var)}, Variable saliente: {map_var(leaving_var)}, Elemento pivote: ({pivot_val_disp})")

        # Mostrar tabla actual destacando el pivote (ANTES de pivotear)
        rows = []
        disp_pivot_col = display_cols.index(pivot_col) if pivot_col in display_cols else -1
        for i in range(1, len(tableau)):
            vb_disp = map_var(basic_vars[i-1])
            row_vals = []
            for k, j in enumerate(display_cols):
                val_str = fmt_intsmart(tableau[i][j])
                if i == pivot_row and k == disp_pivot_col:
                    val_str = f"[black on bright_yellow]{val_str}[/]"
                row_vals.append(val_str)
            row_vals.append(fmt_intsmart(tableau[i][-1]))
            rows.append([vb_disp] + row_vals)
        z_display = tableau[0][:]
        if not is_maximize:
            z_display = [-v for v in z_display]
        z_vals = [fmt_with_M(z_display[j], M) for j in display_cols] + [fmt_with_M(z_display[-1], M)]
        rows.append(["Z"] + z_vals)
        print_table(headers, rows, f"Iteración {iteracion}")

        # Ahora sí, aplicar el pivote y actualizar la base
        basic_vars[pivot_row - 1] = entering_var
        pivot(tableau, pivot_row, pivot_col)

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
        console.print(f"  {var} = {fmt_num(solution[var])}")

    optimal_value = tableau[0][-1] if is_maximize else -tableau[0][-1]
    console.print(f"\n[bold]Valor óptimo de Z: {fmt_num(optimal_value)}[/bold]")
    console.print("Presione ENTER para continuar...")
    input()

    # Verificar si hay variables artificiales en la solución con valor > 0 (usando nombres)
    for name in var_names:
        if isinstance(name, str) and name.startswith('a'):
            if solution.get(name, 0.0) > 1e-5:
                console.print("[red]⚠️  ATENCIÓN: Variable artificial en solución final. El problema original es infactible.[/red]")