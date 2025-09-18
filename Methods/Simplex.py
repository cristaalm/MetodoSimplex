# metodo_simplex.py
import numpy as np
from rich.console import Console
from pyfiglet import Figlet
import questionary
from .table_display import (
    formatear_expresion, 
    fmt_num, 
    show_simplex_table, 
    preparar_tabla_para_mostrar, 
    ajustar_visual_minimizacion
)

console = Console()

def validar_numero(x):
    """Valida que el input sea un número válido (entero o decimal, positivo o negativo)"""
    try:
        float(x)
        return True
    except ValueError:
        return False

# ==============================
# FUNCIONES DEL MÉTODO SIMPLEX
# ==============================

def crear_tabla(c, A, b):
    """
    Crea la tabla inicial del método simplex.
    c: coeficientes de la función objetivo (lista)
    A: coeficientes de las restricciones (matriz)
    b: términos independientes de las restricciones (lista)
    """
    filas = len(A)
    columnas = len(A[0]) + filas + 1  # variables + holgura + Z

    # Inicializar tabla con ceros
    tabla = np.zeros((filas + 1, columnas))

    # Llenar restricciones
    for i in range(filas):
        tabla[i, :len(A[0])] = A[i]
        tabla[i, len(A[0]) + i] = 1  # variable de holgura
        tabla[i, -1] = b[i]

    # Llenar función objetivo
    tabla[-1, :len(c)] = -np.array(c)

    return tabla

def construir_tabla_big_m(c, A, b, ops, M=1e6):
    """Construye la tabla inicial para problemas con restricciones mixtas usando Big M.
    - c: lista coeficientes de FO (maximización)
    - A: matriz coeficientes restricciones
    - b: RHS de restricciones
    - ops: lista de operadores por restricción: '<=', '>=', '='
    - M: penalización grande positiva
    Devuelve: (tabla numpy, nombres_columnas)
    """
    A = [list(row) for row in A]
    b = list(b)
    m = len(A)
    n = len(A[0]) if m>0 else 0

    # Normalizar filas con b<0 invirtiendo y volteando operador
    ops_norm = []
    for i in range(m):
        if b[i] < 0:
            A[i] = [-val for val in A[i]]
            b[i] = -b[i]
            if ops[i] == '<=':
                ops_norm.append('>=')
            elif ops[i] == '>=':
                ops_norm.append('<=')
            else:
                ops_norm.append('=')
        else:
            ops_norm.append(ops[i])

    # Contar variables adicionales
    slack_idx = []  # posiciones por restricción
    surplus_idx = []
    artificial_idx = []
    slack_count = sum(1 for op in ops_norm if op == '<=')
    surplus_count = sum(1 for op in ops_norm if op == '>=')
    artificial_count = sum(1 for op in ops_norm if op in ('>=', '='))

    total_cols = n + slack_count + surplus_count + artificial_count + 1
    tabla = np.zeros((m+1, total_cols), dtype=float)

    # Construir nombres de columnas
    col_names = [f"x{i+1}" for i in range(n)]
    slack_names = []
    surplus_names = []
    artificial_names = []

    s_ptr = 0
    e_ptr = 0
    a_ptr = 0
    # Mapas a índice absoluto dentro de la tabla
    def idx_slack(k):
        return n + k
    def idx_surplus(k):
        return n + slack_count + k
    def idx_artificial(k):
        return n + slack_count + surplus_count + k

    # Llenar restricciones
    for i in range(m):
        # coef vars originales
        tabla[i, :n] = A[i]
        if ops_norm[i] == '<=':
            # + slack
            tabla[i, idx_slack(s_ptr)] = 1.0
            slack_names.append(f"h{s_ptr+1}")
            slack_idx.append(idx_slack(s_ptr))
            s_ptr += 1
        elif ops_norm[i] == '>=':
            # - surplus + artificial
            tabla[i, idx_surplus(e_ptr)] = -1.0
            surplus_names.append(f"e{e_ptr+1}")
            surplus_idx.append(idx_surplus(e_ptr))
            e_ptr += 1
            tabla[i, idx_artificial(a_ptr)] = 1.0
            artificial_names.append(f"a{a_ptr+1}")
            artificial_idx.append(idx_artificial(a_ptr))
            a_ptr += 1
        else:  # '='
            # + artificial
            tabla[i, idx_artificial(a_ptr)] = 1.0
            artificial_names.append(f"a{a_ptr+1}")
            artificial_idx.append(idx_artificial(a_ptr))
            a_ptr += 1
        tabla[i, -1] = b[i]

    # Función objetivo (Z row)
    # Z row almacena -c en columnas de x. Para Big M (max), artificiales deben tener +M.
    tabla[-1, :n] = -np.array(c, dtype=float)
    # Artificial penalizadas con +M
    for a_i in range(artificial_count):
        tabla[-1, idx_artificial(a_i)] = M

    # Ajuste canónico: si artificial está en la base inicialmente (lo está),
    # restamos M * fila_restricción correspondiente para anular el coef en Z
    # Identificamos por columna identidad en fila i
    a_track = 0
    for i in range(m):
        # ¿esta restricción tiene una artificial marcada con 1?
        has_artificial = False
        a_col = -1
        for a_i in range(artificial_count):
            col = idx_artificial(a_i)
            if abs(tabla[i, col] - 1.0) < 1e-9:
                has_artificial = True
                a_col = col
                break
        if has_artificial:
            tabla[-1, :] -= M * tabla[i, :]

    col_names = col_names + slack_names + surplus_names + artificial_names + ["LD"]
    return tabla, col_names

def encontrar_columna_pivote(tabla):
    """
    Encuentra la columna pivote (columna con valor más negativo en la última fila).
    """
    ultima_fila = tabla[-1, :-1]
    # Candidatas: índices con coeficiente negativo
    candidatas = [i for i, v in enumerate(ultima_fila) if v < 0]
    if not candidatas:
        return None
    # Ordenar por valor más negativo primero
    candidatas.sort(key=lambda i: ultima_fila[i])
    return candidatas

def encontrar_fila_pivote(tabla, col_pivote):
    """
    Encuentra la fila pivote usando la razón mínima.
    """
    rhs = tabla[:-1, -1]
    columna = tabla[:-1, col_pivote]
    razones = []

    for i in range(len(rhs)):
        if columna[i] > 0:
            razones.append(rhs[i] / columna[i])
        else:
            razones.append(np.inf)

    fila = np.argmin(razones)
    if razones[fila] == np.inf:
        return None  # Solución no acotada
    return fila

def pivotear(tabla, fila_pivote, col_pivote):
    """
    Realiza la operación de pivoteo.
    """
    # Normalizar fila pivote
    tabla[fila_pivote] = tabla[fila_pivote] / tabla[fila_pivote, col_pivote]

    # Hacer ceros en la columna pivote
    for i in range(len(tabla)):
        if i != fila_pivote:
            factor = tabla[i, col_pivote]
            tabla[i] -= factor * tabla[fila_pivote]

def resolver_simplex(c, A, b):
    """
    Implementación del método simplex que retorna todas las iteraciones.
    """
    tabla = crear_tabla(c, A, b)
    iteraciones = [tabla.copy()]
    
    while True:
        candidatas = encontrar_columna_pivote(tabla)
        if candidatas is None:
            break  # Solución óptima encontrada
        pivoteado = False
        for col_pivote in candidatas:
            fila_pivote = encontrar_fila_pivote(tabla, col_pivote)
            if fila_pivote is not None:
                pivotear(tabla, fila_pivote, col_pivote)
                iteraciones.append(tabla.copy())
                pivoteado = True
                break
        if not pivoteado:
            raise Exception("La solución es no acotada.")

    # Extraer solución
    solucion = np.zeros(len(c))
    filas, columnas = tabla.shape
    for i in range(len(c)):
        columna = tabla[:, i]
        if list(columna[:-1]).count(1) == 1 and list(columna[:-1]).count(0) == len(columna[:-1]) - 1:
            fila = np.where(columna == 1)[0][0]
            solucion[i] = tabla[fila, -1]

    valor_optimo = tabla[-1, -1]
    return iteraciones, solucion, valor_optimo

def resolver_simplex_desde_tabla(tabla_inicial, num_vars_originales):
    """Itera el simplex partiendo de una tabla inicial (por ejemplo, de Big M).
    Devuelve (iteraciones, solucion_x, valor_optimo)."""
    tabla = np.array(tabla_inicial, dtype=float)
    iteraciones = [tabla.copy()]

    while True:
        candidatas = encontrar_columna_pivote(tabla)
        if candidatas is None:
            break
        pivoteado = False
        for col_pivote in candidatas:
            fila_pivote = encontrar_fila_pivote(tabla, col_pivote)
            if fila_pivote is not None:
                pivotear(tabla, fila_pivote, col_pivote)
                iteraciones.append(tabla.copy())
                pivoteado = True
                break
        if not pivoteado:
            raise Exception("La solución es no acotada.")

    # Extraer solución solo para variables originales x1..xn (primeras columnas)
    solucion = np.zeros(num_vars_originales)
    for i in range(num_vars_originales):
        columna = tabla[:, i]
        if list(columna[:-1]).count(1) == 1 and list(columna[:-1]).count(0) == len(columna[:-1]) - 1:
            fila = np.where(columna == 1)[0][0]
            solucion[i] = tabla[fila, -1]
    valor_optimo = tabla[-1, -1]
    return iteraciones, solucion, valor_optimo

def simplex():
    console.clear()
    f = Figlet(font='big')
    console.print(f.renderText('Metodo Simplex'), style="bold blue")
    console.print("Resuelve problemas de programación lineal con cualquier número de variables.", style="italic")

    try:
        # 1. Solicitar tipo de optimización
        console.print("\n[bold cyan]📋 CONFIGURACIÓN DEL PROBLEMA[/bold cyan]")
        tipo_optimizacion = questionary.select(
            "¿Qué tipo de optimización deseas realizar?",
            choices=["Maximizar", "Minimizar"]
        ).ask()

        # 2. Solicitar número de variables
        num_variables = questionary.text(
            "¿Cuántas variables tiene tu función objetivo? (ej: 2)",
            validate=lambda x: x.isdigit() and int(x) > 0
        ).ask()
        num_variables = int(num_variables)

        # 3. Solicitar coeficientes de la función objetivo
        console.print(f"\n[bold yellow]🎯 FUNCIÓN OBJETIVO ({tipo_optimizacion.upper()})[/bold yellow]")
        c = []
        for i in range(num_variables):
            coef = questionary.text(
                f"Coeficiente de x{i+1} (puede ser negativo, ej -2.5):",
                validate=validar_numero
            ).ask()
            c.append(float(coef))

        # Mostrar función objetivo
        objetivo_str = formatear_expresion(c)
        console.print(f"Función objetivo: {tipo_optimizacion} Z = {objetivo_str}")

        # 4. Solicitar número de restricciones
        num_restricciones = questionary.text(
            "\n¿Cuántas restricciones tiene el problema? (ej: 3)",
            validate=lambda x: x.isdigit() and int(x) > 0
        ).ask()
        num_restricciones = int(num_restricciones)

        # 5. Solicitar restricciones
        console.print(f"\n[bold yellow]📏 RESTRICCIONES[/bold yellow]")
        A = []
        b = []
        ops = []
        
        for i in range(num_restricciones):
            console.print(f"\n[bold]Restricción {i+1}:[/bold]")
            fila = []
            for j in range(num_variables):
                coef = questionary.text(
                    f"Coeficiente de x{j+1} (puede ser negativo, ej -1):",
                    validate=validar_numero
                ).ask()
                fila.append(float(coef))
            # Tipo de restricción
            op = questionary.select(
                "Tipo de restricción:",
                choices=["<=", ">=", "="]
            ).ask()
            lado_derecho = questionary.text(
                "Lado derecho de la restricción (RHS):",
                validate=validar_numero
            ).ask()
            
            A.append(fila)
            b.append(float(lado_derecho))
            ops.append(op)
            
            # Mostrar restricción
            restriccion_str = formatear_expresion(fila)
            console.print(f"Restricción {i+1}: {restriccion_str} {op} {lado_derecho}")

        # 6. Convertir a minimización si es necesario
        if tipo_optimizacion == "Minimizar":
            c = [-coef for coef in c]

        # 7. Resolver el problema
        console.print(f"\n[bold green]🚀 RESOLVIENDO PROBLEMA...[/bold green]")
        console.input("Presiona Enter para comenzar...")

        # ¿Se requiere Big M?
        requiere_big_m = any(op in (">=", "=") for op in ops)
        if requiere_big_m:
            tabla0, col_names = construir_tabla_big_m(c, A, b, ops)
            iteraciones, solucion, valor_optimo = resolver_simplex_desde_tabla(tabla0, num_variables)
            variables_basicas = ["VB"] + col_names
        else:
            iteraciones, solucion, valor_optimo = resolver_simplex(c, A, b)
            # Encabezados estándar: x + holguras h + LD
            variables_basicas = ["VB"] + [f"x{i+1}" for i in range(num_variables)] + [f"h{i+1}" for i in range(num_restricciones)] + ["LD"]

        # 8. Mostrar todas las iteraciones
        for i, tabla in enumerate(iteraciones):
            tabla_mostrar = preparar_tabla_para_mostrar(tabla)
            tabla_mostrar = ajustar_visual_minimizacion(tabla_mostrar, es_minimizacion=(tipo_optimizacion == "Minimizar"))
            show_simplex_table(tabla_mostrar, iteracion=i+1 if i < len(iteraciones)-1 else "FINAL",
                               variables_basicas=variables_basicas)
            if i < len(iteraciones) - 1:
                console.input(f"\n[bold cyan]➡️  Presiona Enter para ver la iteración {i+2}...[/bold cyan]")

        # 8.1 Verificación de factibilidad cuando se usa Big M
        if requiere_big_m:
            final_tabla = iteraciones[-1]
            # columnas artificiales empiezan con 'a'
            artificial_cols = []
            for idx, name in enumerate(variables_basicas[1:-1], start=0):
                # variables_basicas = ["VB"] + col_names
                # col_names incluye LD al final, ya ajustado en variables_basicas
                if isinstance(name, str) and name.startswith('a'):
                    artificial_cols.append(idx)
            # Revisar si alguna artificial es básica con RHS > 0
            infeasible = False
            for a_idx in artificial_cols:
                col_vec = final_tabla[:, a_idx]
                if list(col_vec[:-1]).count(1) == 1 and list(col_vec[:-1]).count(0) == len(col_vec[:-1]) - 1:
                    row = np.where(col_vec == 1)[0][0]
                    rhs_val = final_tabla[row, -1]
                    if rhs_val > 1e-8:
                        infeasible = True
                        break
            if infeasible:
                console.print("\n[bold red]❌ El problema es INFACTIBLE (variables artificiales permanecen básicas con RHS > 0).[/bold red]\nPor favor verifica que el conjunto de restricciones sea consistente.")
                console.input("\n[bold cyan]Presiona Enter para volver al menú...[/bold cyan]")
                return

        # 9. Mostrar solución final
        console.print("\n[bold green]✅ SOLUCIÓN ÓPTIMA ENCONTRADA[/bold green]")
        
        # Ajustar valor óptimo si era minimización
        if tipo_optimizacion == "Minimizar":
            valor_optimo = -valor_optimo

        solucion_str = ", ".join([f"x{i+1} = {fmt_num(solucion[i])}" for i in range(num_variables)])
        console.print(f"[bold yellow]{solucion_str}[/bold yellow]")
        console.print(f"[bold yellow]Valor óptimo Z* = {fmt_num(valor_optimo)}[/bold yellow]")

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]")
        console.print("Verifica que todos los datos ingresados sean correctos.")

    console.input("\n[bold cyan]Presiona Enter para volver al menú...[/bold cyan]")