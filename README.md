# Simulador de campo eléctrico en Python

**Proyecto integrador:** Ecuaciones Diferenciales y Arquitectura de Computadoras  
**Lenguaje utilizado:** Python 3.9  
**Repositorio:** https://github.com/RoyML12/Simulador-de-cargas-ED.git

## 1. Descripción

Aplicación de escritorio que permite agregar, modificar y mover cargas eléctricas positivas y negativas sobre un plano bidimensional. Las líneas del campo eléctrico se calculan con la **ley de Coulomb**, el **principio de superposición** y el **método de Euler** para aproximar las trayectorias.

El simulador permite trabajar con hasta **cinco cargas** y muestra indicadores de tiempo de cálculo y memoria.

## 2. Requisitos

- Windows con **Python 3.9** instalado.
- Acceso a una terminal (PowerShell o terminal de Visual Studio Code).
- Bibliotecas indicadas en `requirements.txt`: **NumPy**, **Matplotlib** y **psutil**.
- **Tkinter**, incluido normalmente en la instalación oficial de Python para Windows.

Para comprobar la versión de Python:

```powershell
py -3.9 --version
```

Si el comando anterior no funciona, prueba `python --version` y comprueba que tengas instalada la versión apropiada.

## 3. Instalación y ejecución

1. Descarga o descomprime el proyecto.
2. Abre en VS Code la carpeta que contiene `main.py` y `requirements.txt`.
3. Abre una terminal en esa misma carpeta.
4. Instala las dependencias:

   ```powershell
   py -3.9 -m pip install -r requirements.txt
   ```

5. Inicia el simulador:

   ```powershell
   py -3.9 main.py
   ```

**Alternativa:** si tu equipo utiliza `python` en lugar de `py -3.9`, ejecuta:

```powershell
python -m pip install -r requirements.txt
python main.py
```

No se necesita configurar una base de datos ni un servidor web.

## 4. Uso del simulador

| Control | Función |
|---|---|
| **+ Positiva** | Agrega una carga positiva. |
| **− Negativa** | Agrega una carga negativa. |
| **Arrastrar una carga** | Cambia su posición con el mouse; las líneas se recalculan al soltarla. |
| **Valor (µC) / Aplicar** | Modifica la magnitud y el signo de la carga seleccionada. |
| **Eliminar** | Quita la carga seleccionada. |
| **Limpiar** | Elimina todas las cargas. |
| **Reiniciar** | Restaura la configuración inicial. |
| **Modelo matemático** | Muestra las ecuaciones utilizadas. |
| **Rendimiento** | Compara el cálculo con 1, 2 y 5 cargas y guarda resultados. |

En la parte inferior de la ventana se muestran el **tiempo de cálculo (ms)**, el **pico de memoria rastreada por Python (MiB)** y la **RAM total del proceso (MiB)**. Los primeros dos valores se actualizan al recalcular las trayectorias; la RAM del proceso se consulta periódicamente.

## 5. Realizar mediciones de rendimiento

Las mediciones pueden realizarse desde el botón **Rendimiento** de la interfaz, seleccionando **Medir y guardar resultados**.

También puedes ejecutarlas directamente desde la terminal:

```powershell
py -3.9 mediciones.py --salida resultados --repeticiones 3
```

Se comparan escenarios de **1, 2 y 5 cargas**, con tres ejecuciones por escenario. Los archivos se guardan en `resultados/`:

- `rendimiento.csv`: tabla de tiempos, memoria, líneas y puntos calculados.
- `rendimiento.png`: gráfica de tiempo según la cantidad de cargas.
- `memoria.png`: gráfica del pico de memoria rastreada por Python.

**Interpretación:** la memoria de `tracemalloc` no equivale a toda la memoria RAM utilizada por la aplicación. La medición de tiempos del experimento se realiza sin contar el redibujado de la gráfica.

## 6. Ejecutar pruebas

Para las pruebas automáticas del modelo y el cálculo numérico:

```powershell
py -3.9 -m unittest discover -s tests -v
```

Para probar la interacción gráfica (requiere escritorio con ventana disponible):

```powershell
py -3.9 tests/gui_smoke.py
```

**Nota:** la prueba de interfaz puede regenerar archivos dentro de `resultados/`.

## 7. Generar evidencias del funcionamiento

```powershell
py -3.9 generar_evidencias.py
```

Este comando crea imágenes de configuraciones eléctricas y archivos que permiten estudiar la estabilidad del método de Euler en la carpeta `evidencias/`.

## 8. Archivos principales

```text
main.py                Interfaz y ejecución de la aplicación
campo.py               Cargas eléctricas y ley de Coulomb
trayectorias.py        Integración de trayectorias con Euler
mediciones.py          Medición de tiempo y memoria
generar_evidencias.py   Generación de figuras de prueba
requirements.txt       Dependencias del proyecto
tests/                 Pruebas automatizadas
evidencias/            Capturas y validaciones
resultados/            CSV y gráficas de rendimiento
```

## 9. Problemas comunes

- **`py` no se reconoce:** usa `python` en los comandos o instala Python agregándolo al `PATH`.
- **`No module named numpy`, `matplotlib` o `psutil`:** vuelve a instalar las dependencias desde la carpeta del proyecto.
- **No abre la ventana:** asegúrate de ejecutar el programa en un equipo con entorno gráfico y con Tkinter disponible.
- **No se encuentran los archivos:** abre la terminal en la carpeta donde se encuentra `main.py`.

---

**Ejecución rápida, después de instalar las dependencias:**

```powershell
py -3.9 main.py
```
