# main.py
import sys
from pyfiglet import Figlet
from rich.console import Console
from rich.align import Align
import questionary

# Metodos
from Methods.Graphic import graphic
from Methods.Simplex import simplex
from Methods.BigM import big_m
from Methods.DoublePhase import double_phase

console = Console()

def show_logo():
    """Muestra un logo ASCII centrado con estilo."""
    f = Figlet(font='big')
    logo = f.renderText('LinOpt')
    console.print(Align.center(logo, vertical="middle"), style="bold cyan")
    console.print(Align.center("📊 Optimización Lineal en Terminal 🧮\n", style="italic green"))

def interactive_menu():
    """Menú principal con questionary que llama a módulos externos."""
    while True:
        console.clear()
        show_logo()

        opciones = [
            "Método Gráfico",
            "Método Simplex",
            "Método Gran M",
            "Método Dos Fases",
            "Salir"
        ]

        seleccion = questionary.select(
            "👉 Elige un método para resolver tu problema:",
            choices=opciones,
            qmark="",
            pointer="➡️  ",
            style=questionary.Style([
                ('pointer', 'fg:#ff9d00 bold'),
                ('highlighted', 'fg:#ff9d00 bold'),
            ])
        ).ask()

        if seleccion == "Salir":
            console.print("\n👋 ¡Gracias por usar LinOpt! Hasta pronto.", style="bold green")
            break
        elif seleccion == "Método Gráfico":
            graphic()
        elif seleccion == "Método Simplex":
            simplex()
        elif seleccion == "Método Gran M":
            big_m()
        elif seleccion == "Método Dos Fases":
            double_phase()

if __name__ == "__main__":
    try:
        interactive_menu()
    except KeyboardInterrupt:
        console.print("\n\n🛑 Interrumpido por el usuario. ¡Adiós!", style="bold red")
        sys.exit(0)