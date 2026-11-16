import argparse
import csv
import statistics
import time
import tracemalloc
from pathlib import Path

from campo import ColeccionCargas
from trayectorias import Parametros, generar_lineas


# Estas configuraciones solo se usan para las pruebas de rendimiento.
CONFIGURACIONES = {
    1: [(0, 0, 2)],
    2: [(-1.5, 0, 2), (1.5, 0, -2)],
    5: [(-2.5, 1.5, 2), (2.5, 1.5, -2), (0, -1.5, 3),
        (-2.5, -2.4, -1), (2.5, -2.4, 1)],
}


def medir(numero, repeticiones, parametros):
    almacen = ColeccionCargas()
    for x, y, valor in CONFIGURACIONES[numero]:
        almacen.agregar(x, y, valor)

    cargas = almacen.cargas
    generar_lineas(cargas, parametros)  # Una ejecución previa para calentar.
    tiempos = []
    lineas = []

    for i in range(repeticiones):
        inicio = time.perf_counter()
        lineas = generar_lineas(cargas, parametros)
        tiempo_ms = (time.perf_counter() - inicio) * 1000
        tiempos.append(tiempo_ms)

    # La memoria se mide por separado para no afectar los tiempos.
    tracemalloc.start()
    tracemalloc.reset_peak()
    generar_lineas(cargas, parametros)
    memoria_actual, memoria_pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "cargas": numero,
        "repeticiones": repeticiones,
        "tiempo_ms": statistics.mean(tiempos),
        "memoria_mib": memoria_pico / (1024 * 1024),
        "lineas": len(lineas),
        "puntos": sum(len(linea.puntos) for linea in lineas),
    }


def ejecutar_mediciones(salida="resultados", repeticiones=3, parametros=None):
    if repeticiones < 1:
        raise ValueError("Debe realizarse al menos una repetición.")
    if parametros is None:
        parametros = Parametros()
    parametros.validar()

    carpeta = Path(salida)
    carpeta.mkdir(parents=True, exist_ok=True)
    resultados = []
    for numero in (1, 2, 5):
        resultados.append(medir(numero, repeticiones, parametros))

    archivo = carpeta / "rendimiento.csv"
    with open(archivo, "w", newline="", encoding="utf-8-sig") as f:
        columnas = ["cargas", "repeticiones", "tiempo_ms", "memoria_mib", "lineas", "puntos"]
        escritor = csv.DictWriter(f, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(resultados)

    # Se crean las gráficas sin cambiar el backend de Tkinter.
    from matplotlib.figure import Figure

    fig = Figure(figsize=(7, 4), dpi=130)
    ax = fig.add_subplot(111)
    ax.plot([r["cargas"] for r in resultados],
            [r["tiempo_ms"] for r in resultados], marker="o", color="#176A8A")
    ax.set_title("Tiempo de cálculo según la cantidad de cargas")
    ax.set_xlabel("Número de cargas")
    ax.set_ylabel("Tiempo promedio (ms)")
    ax.set_xticks([1, 2, 5])
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(carpeta / "rendimiento.png")

    fig2 = Figure(figsize=(7, 4), dpi=130)
    ax2 = fig2.add_subplot(111)
    ax2.plot([r["cargas"] for r in resultados],
             [r["memoria_mib"] for r in resultados], marker="o", color="#178D72")
    ax2.set_title("Pico de memoria Python por configuración")
    ax2.set_xlabel("Número de cargas")
    ax2.set_ylabel("Memoria rastreada (MiB)")
    ax2.set_xticks([1, 2, 5])
    ax2.grid(True, alpha=0.25)
    fig2.tight_layout()
    fig2.savefig(carpeta / "memoria.png")
    return resultados


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="resultados")
    parser.add_argument("--repeticiones", type=int, default=3)
    argumentos = parser.parse_args()

    datos = ejecutar_mediciones(argumentos.salida, argumentos.repeticiones)
    for dato in datos:
        print("{cargas} cargas: {tiempo_ms:.2f} ms; {memoria_mib:.3f} MiB".format(**dato))
    print("Archivos guardados en:", Path(argumentos.salida).resolve())
    print("Memoria: pico rastreado por tracemalloc (no RAM total del proceso).")
