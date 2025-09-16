# metodo_grafico.py
from rich.console import Console
from pyfiglet import Figlet
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np

console = Console()

def graphic():
    console.clear()
    f = Figlet(font='big')
    console.print(f.renderText('Metodo Grafico'), style="bold green")
    console.print("Este método resuelve problemas de PL con 2 variables visualmente.", style="italic")


    ## LOGICA DEL METODO ##

    # Pedir datos del problema (funcion objetivo y restricciones)
    # Pedir restricciones (limites de cada variable)
    # Graficar plano cartesiano (ventana gráfica emergente)
    # Mostrar restricciones en el plano cartesiano
    # Mostrar Polígono factible (Área factible)
    # Mostrar solución óptima
    # etc...

    # =============================================
    # 📝 Problema de ejemplo
    # =============================================
    console.print("\n[bold blue]📌 Problema de ejemplo:[/bold blue]")
    console.print("Max Z = 3x₁ + 5x₂")
    console.print("Sujeto a:")
    console.print("  x₁ ≤ 4")
    console.print("  2x₂ ≤ 12 → x₂ ≤ 6")
    console.print("  3x₁ + 2x₂ ≤ 18")
    console.print("  x₁, x₂ ≥ 0")

    # =============================================
    # 🧮 Definir rango de valores para x1 y x2
    # =============================================
    x1 = np.linspace(0, 6, 400)
    x2 = np.linspace(0, 7, 400)
    X1, X2 = np.meshgrid(x1, x2)

    factible = (
        (X1 <= 4) &
        (X2 <= 6) &
        (3*X1 + 2*X2 <= 18) &
        (X1 >= 0) &
        (X2 >= 0)
    )

    # =============================================
    # 🎨 Graficar
    # =============================================
    plt.figure(figsize=(10, 8))

    # Sombrear región factible
    plt.imshow(factible.astype(int),
               extent=(x1.min(), x1.max(), x2.min(), x2.max()),
               origin="lower",
               cmap="Greens",
               alpha=0.3,
               aspect='auto')

    # Restricciones
    plt.axvline(x=4, color='blue', label='x₁ ≤ 4')
    plt.axhline(y=6, color='red', label='x₂ ≤ 6')
    x2_line = (18 - 3*x1) / 2
    plt.plot(x1, x2_line, color='purple', label='3x₁ + 2x₂ ≤ 18')

    # Puntos de esquina
    puntos = np.array([[0, 0], [0, 6], [2, 6], [4, 3], [4, 0]])
    plt.plot(puntos[:,0], puntos[:,1], 'ko--', markersize=6, label='Puntos factibles')

    # Solución óptima
    Z = 3*puntos[:,0] + 5*puntos[:,1]
    idx_optimo = np.argmax(Z)
    optimo = puntos[idx_optimo]
    plt.plot(optimo[0], optimo[1], 'r*', markersize=15, label=f'Óptimo: Z={Z[idx_optimo]:.0f} en ({optimo[0]:.0f}, {optimo[1]:.0f})')

    plt.xlim(0, 6)
    plt.ylim(0, 7)
    plt.xlabel('x₁')
    plt.ylabel('x₂')
    plt.title('Método Gráfico - Región Factible y Solución Óptima')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.gca().set_aspect('equal', adjustable='box')

    # 👇 Esto ahora SÍ abrirá una ventana
    console.print("\n[bold cyan]📈 Mostrando gráfica en ventana emergente...[/bold cyan]")
    plt.show()  # ← Ahora debería funcionar

    console.print(f"\n[bold green]✅ Solución óptima encontrada: Z = {Z[idx_optimo]:.0f} en (x₁={optimo[0]:.0f}, x₂={optimo[1]:.0f})[/bold green]")
    console.input("\n[bold cyan]Presiona Enter para volver al menú...[/bold cyan]")