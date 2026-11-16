import math
import numpy as np
from campo import CampoElectrico


class Parametros:
    def __init__(self, paso=0.06, lineas=24, pasos_max=700,
                 radio_semilla=0.23, radio_parada=0.15):
        self.xmin = -5
        self.xmax = 5
        self.ymin = -5
        self.ymax = 5
        self.paso = paso
        self.lineas = lineas
        self.pasos_max = pasos_max
        self.radio_semilla = radio_semilla
        self.radio_parada = radio_parada
        self.campo_minimo = 1e-9

    def validar(self):
        if not 0.015 <= self.paso <= 0.30:
            raise ValueError("El paso de Euler debe estar entre 0.015 y 0.30.")
        if not isinstance(self.lineas, int) or not 8 <= self.lineas <= 80:
            raise ValueError("La cantidad de líneas debe estar entre 8 y 80.")
        if not isinstance(self.pasos_max, int) or not 100 <= self.pasos_max <= 1500:
            raise ValueError("La cantidad de pasos debe estar entre 100 y 1500.")
        if not 0 < self.radio_parada < self.radio_semilla:
            raise ValueError("Los radios de inicio y parada no son correctos.")


class LineaCampo:
    def __init__(self, puntos, sentido, id_origen, termino):
        self.puntos = np.array(puntos)
        self.sentido = sentido
        self.id_origen = id_origen
        self.termino = termino


def integrar_euler(campo, inicio, parametros, sentido=1, id_origen=-1):
    x, y = inicio
    puntos = [(x, y)]
    motivo = "máximo de pasos"

    for paso in range(parametros.pasos_max):
        # Detener al salir de la gráfica.
        if abs(x) > 5 or abs(y) > 5:
            motivo = "fuera del área"
            break

        # Detener al acercarse a una carga para evitar singularidades.
        cerca = False
        for carga in campo.cargas:
            distancia = math.hypot(x - carga.x, y - carga.y)
            if distancia <= parametros.radio_parada:
                cerca = True
                break
        if cerca:
            motivo = "cercanía a una carga"
            break

        try:
            direccion = campo.norma_y_direccion(x, y)
        except ValueError:
            motivo = "singularidad"
            break

        if direccion is None:
            motivo = "campo casi nulo"
            break

        # Ecuaciones diferenciales: dx/ds = Ex/|E| y dy/ds = Ey/|E|
        # Método de Euler: nuevo = anterior + paso * dirección.
        x = x + sentido * parametros.paso * direccion[0]
        y = y + sentido * parametros.paso * direccion[1]
        puntos.append((x, y))

    return LineaCampo(puntos, sentido, id_origen, motivo)


def generar_lineas(cargas, parametros=None):
    if parametros is None:
        parametros = Parametros()
    parametros.validar()

    if not cargas:
        return []

    # Normalmente se comienza desde las cargas positivas.
    origenes = [c for c in cargas if c.q > 0]
    sentido = 1
    if not origenes:
        # Si solo hay negativas, trazamos al revés.
        origenes = [c for c in cargas if c.q < 0]
        sentido = -1

    campo = CampoElectrico(cargas)
    resultado = []

    # Repartimos siempre el mismo total de líneas entre los orígenes.
    cantidad_base = parametros.lineas // len(origenes)
    sobrantes = parametros.lineas % len(origenes)

    for indice, carga in enumerate(origenes):
        cantidad = cantidad_base
        if indice < sobrantes:
            cantidad += 1

        for i in range(cantidad):
            angulo = 2 * math.pi * i / cantidad
            x = carga.x + parametros.radio_semilla * math.cos(angulo)
            y = carga.y + parametros.radio_semilla * math.sin(angulo)
            if abs(x) > 5 or abs(y) > 5:
                continue
            linea = integrar_euler(campo, (x, y), parametros, sentido, carga.id)
            if len(linea.puntos) > 1:
                resultado.append(linea)

    return resultado
