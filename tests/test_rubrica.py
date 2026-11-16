import math
import unittest

from campo import ColeccionCargas, CampoElectrico, K, MICRO
from trayectorias import Parametros, integrar_euler, generar_lineas


class PruebasRubrica(unittest.TestCase):
    def test_campo_manual_carga_aislada(self):
        coleccion = ColeccionCargas()
        coleccion.agregar(0, 0, 1)
        ex, ey = CampoElectrico(coleccion.cargas).evaluar(1, 0)
        self.assertAlmostEqual(ex, K * MICRO, places=6)
        self.assertAlmostEqual(ey, 0)

    def test_campo_manual_dipolo(self):
        coleccion = ColeccionCargas()
        coleccion.agregar(-1, 0, 1)
        coleccion.agregar(1, 0, -1)
        ex, ey = CampoElectrico(coleccion.cargas).evaluar(0, 0)
        self.assertAlmostEqual(ex, 2 * K * MICRO, places=6)
        self.assertAlmostEqual(ey, 0)

    def test_positivas_simetria(self):
        coleccion = ColeccionCargas()
        coleccion.agregar(-1, 0, 2)
        coleccion.agregar(1, 0, 2)
        self.assertEqual(CampoElectrico(coleccion.cargas).evaluar(0, 0), (0, 0))

    def test_paso_menor_se_aproxima_referencia(self):
        coleccion = ColeccionCargas()
        coleccion.agregar(-1.5, 0, 2)
        coleccion.agregar(1.5, 0, -2)
        campo = CampoElectrico(coleccion.cargas)
        inicio = (-1.5 + 0.23 * math.cos(math.pi / 3),
                  0.23 * math.sin(math.pi / 3))
        extremos = []
        for h in (0.015, 0.03, 0.06, 0.12):
            linea = integrar_euler(campo, inicio, Parametros(paso=h))
            extremos.append(linea.puntos[int(round(1.2/h))])
        def distancia(a, b):
            return math.hypot(a[0]-b[0], a[1]-b[1])
        self.assertLess(distancia(extremos[1], extremos[0]),
                        distancia(extremos[2], extremos[0]))
        self.assertLess(distancia(extremos[2], extremos[0]),
                        distancia(extremos[3], extremos[0]))


if __name__ == '__main__':
    unittest.main()
