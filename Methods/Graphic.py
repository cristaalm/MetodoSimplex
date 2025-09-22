# metodo_grafico.py
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Point
import questionary
from rich.console import Console
from rich.table import Table

console = Console()

def validar_numero(x):
    """Valida que el input sea un número válido (entero o decimal, positivo o negativo)"""
    try:
        float(x)
        return True
    except ValueError:
        return False

def validar_entero_positivo(x):
    """Valida que el input sea un entero positivo"""
    return x.isdigit() and int(x) > 0

def metodo_grafico():
    console.clear()
    console.print("\n[bold blue]📊 MÉTODO GRÁFICO PARA PROGRAMACIÓN LINEAL[/bold blue]")
    console.print("Resuelve problemas de PL con 2 variables de decisión.\n")

    try:
        # 1. Solicitar tipo de optimización
        tipo_optimizacion = questionary.select(
            "¿Qué tipo de optimización deseas realizar?",
            choices=["Maximizar", "Minimizar"]
        ).ask()

        # 2. Solicitar coeficientes de la función objetivo Z = c1*x1 + c2*x2
        console.print(f"\n[bold yellow]🎯 FUNCIÓN OBJETIVO ({tipo_optimizacion.upper()})[/bold yellow]")
        c1 = float(questionary.text(
            "Coeficiente de X1 (puede ser negativo, ej: -2.50):",
            validate=validar_numero
        ).ask())
        c2 = float(questionary.text(
            "Coeficiente de X2 (puede ser negativo, ej: -2.50):",
            validate=validar_numero
        ).ask())

        console.print(f"Función objetivo: {tipo_optimizacion} Z = {c1}X1 + {c2}X2")

        # 3. Solicitar número de restricciones
        num_restricciones = int(questionary.text(
            "\n¿Cuántas restricciones tiene el problema? (ej: 3)",
            validate=validar_entero_positivo
        ).ask())

        # 4. Solicitar restricciones: a1*X1 + a2*X2 <= b
        console.print(f"\n[bold yellow]📏 RESTRICCIONES[/bold yellow]")
        restricciones = []  # Lista para almacenar [a1, a2, b, 'operador']

        for i in range(num_restricciones):
            console.print(f"\n[bold]Restricción {i+1}:[/bold]")
            a1 = float(questionary.text(
                f"Coeficiente de X1 (puede ser negativo, ej: -20):",
                validate=validar_numero
            ).ask())
            a2 = float(questionary.text(
                f"Coeficiente de X2 (puede ser negativo, ej: -20):",
                validate=validar_numero
            ).ask())
            op = questionary.select(
                "Tipo de restricción:",
                choices=["<=", ">=", "="]
            ).ask()
            b = float(questionary.text(
                "Lado derecho de la restricción (RHS, ej:500):",
                validate=validar_numero
            ).ask())

            restricciones.append([a1, a2, b, op])
            console.print(f"Restricción {i+1}: {a1}X1 + {a2}X2 {op} {b}")


        # 4.1 Preguntar por restricciones de no negatividad
        console.print(f"\n[bold yellow]📌 RESTRICCIONES DE NO NEGATIVIDAD[/bold yellow]")
        agregar_x1_no_neg = questionary.confirm("¿Deseas agregar la restricción X1 >= 0 (No negatividad)?").ask()
        agregar_x2_no_neg = questionary.confirm("¿Deseas agregar la restricción X2 >= 0 (No negatividad)?").ask()

        if agregar_x1_no_neg:
            restricciones.append([1, 0, 0, '>='])
            console.print("✅ Se agregó: X1 >= 0")

        if agregar_x2_no_neg:
            restricciones.append([0, 1, 0, '>='])
            console.print("✅ Se agregó: X2 >= 0")

        console.print(f"\n[bold green]🚀 RESOLVIENDO PROBLEMA...[/bold green]")
        console.input("Presiona Enter para comenzar...")

        # 5. Encontrar puntos de intersección con los ejes para cada restricción
        console.print(f"\n[bold green]📐 COORDENADAS DE INTERSECCIÓN CON LOS EJES[/bold green]")
        tabla_intersecciones = Table(show_header=True, header_style="bold magenta")
        tabla_intersecciones.add_column("Restricción", style="dim", width=12)
        tabla_intersecciones.add_column("Intersección X1 (X2=0)", justify="right")
        tabla_intersecciones.add_column("Intersección X2 (X1=0)", justify="right")

        for i, (a1, a2, b, op) in enumerate(restricciones):
            # Para X2 = 0
            x1_inter = b / a1 if a1 != 0 else np.inf
            # Para X1 = 0
            x2_inter = b / a2 if a2 != 0 else np.inf

            if op in ['>=', '='] and b < 0:
                x1_inter = np.inf if x1_inter < 0 else x1_inter
                x2_inter = np.inf if x2_inter < 0 else x2_inter

            str_x1 = f"({x1_inter:.2f}, 0)" if np.isfinite(x1_inter) else "No cruza"
            str_x2 = f"(0, {x2_inter:.2f})" if np.isfinite(x2_inter) else "No cruza"

            tabla_intersecciones.add_row(f"R{i+1}", str_x1, str_x2)

        console.print(tabla_intersecciones)
        console.input("Presiona Enter para continuar...")

        # 6. Preparar las líneas para graficar
        rango_temp = 10000
        x_min_temp, x_max_temp = -rango_temp/10, rango_temp  # Permitir un poco de negativo si se permite
        y_min_temp, y_max_temp = -rango_temp/10, rango_temp

        lineas = []
        etiquetas = []

        for i, (a1, a2, b, op) in enumerate(restricciones):
            if a1 == 0 and a2 == 0:
                continue

            if a1 == 0:
                x_vals_line = np.linspace(x_min_temp, x_max_temp, 100)
                y_vals_line = np.full_like(x_vals_line, b / a2)
            elif a2 == 0:
                x_vals_line = np.full(100, b / a1)
                y_vals_line = np.linspace(y_min_temp, y_max_temp, 100)
            else:
                x_vals_line = np.linspace(x_min_temp, x_max_temp, 100)
                y_vals_line = (b - a1 * x_vals_line) / a2

            # Filtrar valores extremadamente fuera de rango (opcional)
            mask = np.isfinite(x_vals_line) & np.isfinite(y_vals_line)
            x_vals_line = x_vals_line[mask]
            y_vals_line = y_vals_line[mask]

            if len(x_vals_line) > 0:
                linea = LineString(np.column_stack((x_vals_line, y_vals_line)))
                lineas.append(linea)
                etiquetas.append(f"R{i+1}")

        # 7. Encontrar todos los vértices (intersecciones entre líneas)
        vertices = []
        for i in range(len(lineas)):
            for j in range(i + 1, len(lineas)):
                interseccion = lineas[i].intersection(lineas[j])
                if isinstance(interseccion, Point):
                    x, y = interseccion.x, interseccion.y
                    # Verificar que el punto cumple todas las restricciones
                    factible = True
                    for a1, a2, b, op in restricciones:
                        valor = a1 * x + a2 * y
                        if op == '<=' and valor > b + 1e-5:
                            factible = False
                            break
                        elif op == '>=' and valor < b - 1e-5:
                            factible = False
                            break
                        elif op == '=' and not abs(valor - b) <= 1e-5:
                            factible = False
                            break
                    if factible:
                        restricciones_activas = 0
                        for a1, a2, b, op in restricciones:
                            valor = a1 * x + a2 * y
                            if op == '<=' and abs(valor - b) < 1e-5:
                                restricciones_activas += 1
                            elif op == '>=' and abs(valor - b) < 1e-5:
                                restricciones_activas += 1
                            elif op == '=':
                                restricciones_activas += 1

                        if restricciones_activas >= 2:
                            punto = (round(x, 6), round(y, 6))
                            if punto not in vertices:  # Evitar duplicados
                                vertices.append(punto)

        # Eliminar duplicados (por si acaso)
        vertices = list(set(vertices))

        if not vertices:
            console.print("\n[bold red]❌ No se encontró una región factible.[/bold red]")
            console.input("\n[bold cyan]Presiona Enter para volver...[/bold cyan]")
            return

        # 8. Calcular límites del gráfico basados en los vértices
        x_coords = [v[0] for v in vertices]
        y_coords = [v[1] for v in vertices]

        margin = 0.1
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)

        x_range = x_max - x_min
        y_range = y_max - y_min

        x_min -= margin * x_range if x_range > 0 else 1
        x_max += margin * x_range if x_range > 0 else 1
        y_min -= margin * y_range if y_range > 0 else 1
        y_max += margin * y_range if y_range > 0 else 1

        # Asegurar que incluya el origen si es factible
        if x_min > 0: x_min = 0
        if y_min > 0: y_min = 0

        # Recrear las líneas usando el rango ajustado
        lineas = []
        etiquetas = []

        for i, (a1, a2, b, op) in enumerate(restricciones):
            if a1 == 0 and a2 == 0:
                continue

            if a1 == 0:
                x_vals_line = np.linspace(x_min, x_max, 100)
                y_vals_line = np.full_like(x_vals_line, b / a2)
            elif a2 == 0:
                x_vals_line = np.full(100, b / a1)
                y_vals_line = np.linspace(y_min, y_max, 100)
            else:
                x_vals_line = np.linspace(x_min, x_max, 100)
                y_vals_line = (b - a1 * x_vals_line) / a2

            # Filtrar puntos fuera de rango
            mask = np.isfinite(x_vals_line) & np.isfinite(y_vals_line)
            x_vals_line = x_vals_line[mask]
            y_vals_line = y_vals_line[mask]

            if len(x_vals_line) > 0:
                linea = LineString(np.column_stack((x_vals_line, y_vals_line)))
                lineas.append(linea)
                etiquetas.append(f"R{i+1}")

        # 9. Evaluar la función objetivo en cada vértice
        console.print(f"\n[bold green]🧮 EVALUACIÓN DE LA FUNCIÓN OBJETIVO EN VÉRTICES[/bold green]")
        tabla_vertices = Table(show_header=True, header_style="bold magenta")
        tabla_vertices.add_column("Vértice", style="dim", width=8)
        tabla_vertices.add_column("X1", justify="right")
        tabla_vertices.add_column("X2", justify="right")
        tabla_vertices.add_column("Z = c1*X1 + c2*X2", justify="right")

        valores_z = []
        for i, (x, y) in enumerate(vertices):
            z = c1 * x + c2 * y
            valores_z.append(z)
            tabla_vertices.add_row(
                f"V{i+1}",
                f"{x:.4f}",
                f"{y:.4f}",
                f"{z:.4f}"
            )

        console.print(tabla_vertices)
        console.input("Presiona Enter para continuar...")

        # 10. Determinar la solución óptima
        if tipo_optimizacion == "Maximizar":
            idx_optimo = np.argmax(valores_z)
            z_optimo = np.max(valores_z)
        else:  # Minimizar
            idx_optimo = np.argmin(valores_z)
            z_optimo = np.min(valores_z)

        x_optimo, y_optimo = vertices[idx_optimo]

        console.print(f"\n[bold green]✅ SOLUCIÓN ÓPTIMA[/bold green]")
        console.print(f"[bold yellow]Tipo: {tipo_optimizacion}[/bold yellow]")
        console.print(f"[bold yellow]X1* = {x_optimo:.4f}[/bold yellow]")
        console.print(f"[bold yellow]X2* = {y_optimo:.4f}[/bold yellow]")
        console.print(f"[bold yellow]Z* = {z_optimo:.4f}[/bold yellow]")

        # 11. Graficar
        fig, ax = plt.subplots(figsize=(12, 9))

        # Establecer límites
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

        # Graficar líneas de restricción
        colores = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        for i, (linea, etiqueta) in enumerate(zip(lineas, etiquetas)):
            x_line, y_line = linea.xy
            x_line = np.array(x_line)
            y_line = np.array(y_line)
            ax.plot(x_line, y_line, '-', linewidth=2, color=colores[i % len(colores)], label=etiqueta)

        # Graficar vértices
        for x, y in vertices:
            ax.plot(x, y, 'o', color='red', markersize=8)

        # Rellenar la región factible
        if len(vertices) >= 3:
            vertices_array = np.array(vertices)
            centro = np.mean(vertices_array, axis=0)

            angles = np.arctan2(vertices_array[:, 1] - centro[1],
                               vertices_array[:, 0] - centro[0])

            sorted_indices = np.argsort(angles)
            vertices_ordenados = vertices_array[sorted_indices]

            poly_x = vertices_ordenados[:, 0]
            poly_y = vertices_ordenados[:, 1]

            ax.fill(poly_x, poly_y, color='lightblue', alpha=0.5, edgecolor='blue', linewidth=2, label='Región Factible')
            ax.plot(np.append(poly_x, poly_x[0]), np.append(poly_y, poly_y[0]),
                   'b-', linewidth=2, alpha=0.8)

        # Anotar la solución óptima
        ax.annotate(f'Óptimo ({x_optimo:.2f}, {y_optimo:.2f})\nZ={z_optimo:.2f}',
                    xy=(x_optimo, y_optimo), xytext=(10, 10),
                    textcoords='offset points', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
                    arrowprops=dict(arrowstyle="->", color='black'))

        ax.set_xlabel('X1')
        ax.set_ylabel('X2')
        ax.set_title('Método Gráfico - Región Factible y Solución Óptima')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]")
        console.print("Verifica que todos los datos ingresados sean correctos.")

    console.input("\n[bold cyan]Presiona Enter para volver...[/bold cyan]")