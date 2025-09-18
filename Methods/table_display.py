# table_display.py
"""
Módulo para la visualización y formateo de tablas del método Simplex.
Contiene todas las funciones relacionadas con la presentación visual de datos.
"""

import numpy as np
from rich.console import Console
from rich.table import Table

console = Console()

def formatear_expresion(coefs):
    """Devuelve una cadena como '3x1 - 2x2 + 5x3' a partir de coeficientes.
    Muestra correctamente los signos y omite el '+' inicial."""
    terminos = []
    for i, a in enumerate(coefs):
        if a == 0:
            continue
        nombre = f"x{i+1}"
        signo = "-" if a < 0 else "+"
        mag = abs(a)
        # Evitar mostrar 1 como coeficiente (opcional). Aquí lo mostramos siempre para claridad.
        termino = f"{mag} {nombre}"
        terminos.append((signo, termino))
    if not terminos:
        return "0"
    # Primer término sin signo '+' inicial
    s0, t0 = terminos[0]
    s = ("- " if s0 == "-" else "") + t0
    for sgn, t in terminos[1:]:
        s += f" {sgn} {t}"
    # Compactar espacios alrededor de variables: '3 x1' -> '3x1'
    return s.replace(" ", "").replace("-", "- ").replace("+", "+ ").replace("  ", " ")

def fmt_num(x, ndigits=4, eps=5e-5):
    """Formatea números evitando '-0.0000'. Aplica redondeo a ndigits.
    Si |x| < eps, devuelve '0.0000'."""
    if abs(x) < eps:
        return f"{0.0:.{ndigits}f}"
    s = f"{x:.{ndigits}f}"
    # Evitar '-0.0000' tras formateo
    if s.startswith("-"):
        try:
            if abs(float(s)) < eps:
                return f"{0.0:.{ndigits}f}"
        except Exception:
            pass
    return s

def show_simplex_table(tabla, iteracion=1, variables_basicas=None):
    """Muestra una tabla del método Simplex con formato profesional."""
    console.print(f"\n[bold underline]📊 Iteración {iteracion}[/bold underline]\n")

    tabla_rich = Table(
        title="Tabla Simplex",
        title_style="bold magenta",
        border_style="blue",
        header_style="bold cyan on black",
        show_lines=True  # Muestra líneas entre filas (opcional, pero útil)
    )

    # Suponemos que la primera fila es el encabezado: VB + variables + LD
    if not variables_basicas:
        variables_basicas = ["Z"] + [f"x{i+1}" for i in range(len(tabla[0]) - 2)] + ["LD"]

    # Agregar columnas
    for var in variables_basicas:
        tabla_rich.add_column(var, justify="center", style="white")

    # Agregar filas
    # Calcular nombres de variables básicas por fila (columna identidad)
    vb_labels = ["Z"]
    if variables_basicas and len(variables_basicas) >= 3:
        var_names = variables_basicas[1:-1]  # nombres de columnas numéricas
        num_rows = len(tabla) - 1
        num_cols = len(var_names)
        for r in range(num_rows):
            # revisar cada columna j si es identidad con 1 en fila r (considerando offset +1 por Z en top)
            vb_name = ""
            for j in range(num_cols):
                col_vec = [tabla[row_idx][j] for row_idx in range(len(tabla))]
                # ignorar fila Z (index 0); identidad en filas 1..n
                col_body = col_vec[1:-1] if len(col_vec) > 1 else []
                # Para fila de datos r, en tabla la fila es r+1
                if len(col_body) == num_rows and col_body.count(0) == num_rows - 1 and abs(col_body[r] - 1.0) < 1e-9:
                    vb_name = var_names[j]
                    break
            vb_labels.append(vb_name if vb_name else f"fila{r+1}")
    else:
        vb_labels = ["Z"] + [f"x{i+1}" for i in range(len(tabla) - 1)]

    for i, fila in enumerate(tabla):
        celdas = [vb_labels[i]] + [fmt_num(x) for x in fila]
        tabla_rich.add_row(*celdas)

    console.print(tabla_rich)
    console.print("")  # espacio extra

def preparar_tabla_para_mostrar(tabla_np):
    """Devuelve una copia de la tabla con la fila Z (última fila) al inicio para visualización."""
    # Convertir a lista de listas para show_simplex_table
    if isinstance(tabla_np, np.ndarray):
        tabla = tabla_np.tolist()
    else:
        tabla = [list(f) for f in tabla_np]
    if not tabla:
        return tabla
    # Mover la última fila (Z) al inicio
    z = tabla[-1]
    resto = tabla[:-1]
    return [z] + resto

def ajustar_visual_minimizacion(tabla_list, es_minimizacion=False):
    """Para problemas de minimización, invierte el signo de toda la fila Z
    (coeficientes y LD) para que la visualización coincida con la FO ingresada
    y el valor Z* mostrado. Solo afecta a la visualización."""
    if not es_minimizacion:
        return tabla_list
    if not tabla_list:
        return tabla_list
    # Copiar para no modificar original
    tabla = [row[:] for row in tabla_list]
    # Fila 0 es Z tras preparar_tabla_para_mostrar
    tabla[0] = [-v for v in tabla[0]]
    return tabla
