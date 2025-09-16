# 📊 LinOpt — Optimización Lineal en Terminal 🧮

Resuelve problemas de **Programación Lineal** con métodos **Simplex**, **Gran M** y **Dos Fases** — todo desde tu terminal.  

Una aplicación de consola interactiva, modular y visualmente atractiva, construida en **Python**, ideal para estudiantes, profesores o profesionales que necesitan resolver problemas de PL paso a paso con tablas y explicaciones claras.

---

## 🚀 Características
- ✅ Menú interactivo con navegación por flechas (**questionary**).
- ✅ Logo ASCII impactante al inicio (**pyfiglet**).
- ✅ Tablas profesionales y coloreadas en terminal (**rich**).
- ✅ Tres métodos implementados:
  - **Simplex Estándar** (para problemas con solo ≤).
  - **Método de la Gran M** (para problemas con ≥ o =).
  - **Método de las Dos Fases** (alternativa profesional a la Gran M).
- ✅ Código modular y comentado — ideal para trabajo en equipo.
- ✅ Compatible con **Linux**, **macOS** y **Windows**.

---

## 📦 Instalación

### Requisitos
- Python 3.8 o superior  
- pip  

### Pasos
1. Clona el repositorio o descarga los archivos:

```bash
git clone https://github.com/tu-usuario/LinOpt.git
cd LinOpt
```

2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

💡 Si no tienes el archivo `requirements.txt`, crea uno con el contenido de tu lista de paquetes (abajo) o instala manualmente:

```bash
pip install pyfiglet rich questionary numpy matplotlib
```

3. ¡Ejecuta la aplicación!

```bash
python main.py
```

---

## 🖥️ Uso

Al ejecutar `python main.py`, verás:

```
 _      _        ____        _  
| |    (_)      / __ \      | | 
| |     _ _ __ | |  | |_ __ | | 
| |    | | '_ \| |  | | '_ \| __| 
| |____| | | | | |__| | |_) | |_
|______|_|_| |_|\____/| .__/ \__|
                      | |
                      |_|
```

Luego, un menú interactivo:

```
👉 Elige un método para resolver tu problema:
➡️   Método Simplex
     Método Gran M
     Método Dos Fases
     Salir
```

Selecciona un método con las flechas ↑↓ y presiona **Enter**.

Cada método te guiará paso a paso con:
- Explicación del problema de ejemplo.
- Tablas del Simplex coloreadas.
- Instrucciones claras en cada iteración.
- Solución final con interpretación.

---

## 📁 Estructura del Proyecto

```
LinOpt/
│
├── main.py                  # Menú principal e inicialización
├── requirements.txt         # Dependencias
│
└── Methods/
    ├── Simplex.py           # Método Simplex estándar
    ├── BigM.py              # Método de la Gran M
    └── DoublePhase.py       # Método de las Dos Fases
```

---

## 🖼️ Capturas de Pantalla (Texto)

### Menú Principal
```
 _      _        ____        _  
| |    (_)      / __ \      | | 
| |     _ _ __ | |  | |_ __ | | 
| |    | | '_ \| |  | | '_ \| __| 
| |____| | | | | |__| | |_) | |_
|______|_|_| |_|\____/| .__/ \__|
                      | |
                      |_|

📊 Optimización Lineal en Terminal 🧮

👉 Elige un método para resolver tu problema:
➡️   Método Simplex
     Método Gran M
     Método Dos Fases
     Salir
```

### Tabla Simplex (ejemplo)
```
                  Tabla Simplex                  
┏━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━┓
┃ VB ┃ x1  ┃ x2  ┃ h1  ┃ h2  ┃ h3  ┃ LD ┃
┡━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━┩
│ Z  │ -3  │ -5  │ 0   │ 0   │ 0   │ 0  │
│ x3 │ 1   │ 0   │ 1   │ 0   │ 0   │ 4  │
│ x4 │ 0   │ 2   │ 0   │ 1   │ 0   │ 12 │
│ x5 │ 3   │ 2   │ 0   │ 0   │ 1   │ 18 │
└────┴─────┴─────┴─────┴─────┴─────┴────┘
```

---

## 📜 Licencia
MIT — Libre para usar, modificar y distribuir. Ideal para proyectos académicos y personales.

---

💡 **Hecho con ❤️ por RENOVA**  
> “La optimización no es un lujo, es una necesidad. Y ahora, también es accesible desde la terminal.”
