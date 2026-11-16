import math
import unittest
from campo import ColeccionCargas, CampoElectrico
from trayectorias import Parametros, integrar_euler, generar_lineas


class PruebasEuler(unittest.TestCase):
    def test_primera_iteracion(self):
        lista = ColeccionCargas()
        lista.agregar(0, 0, 1)
        p = Parametros(lineas=12, pasos_max=100)
        linea = integrar_euler(CampoElectrico(lista.cargas), (1, 0), p)
        self.assertAlmostEqual(linea.puntos[1, 0], 1.06)
        self.assertAlmostEqual(linea.puntos[1, 1], 0)

    def test_positiva_sale(self):
        lista = ColeccionCargas()
        lista.agregar(0, 0, 1)
        lineas = generar_lineas(lista.cargas, Parametros(lineas=12, pasos_max=100))
        self.assertEqual(len(lineas), 12)
        self.assertGreater(math.hypot(*lineas[0].puntos[1]), math.hypot(*lineas[0].puntos[0]))

    def test_negativa_entro_en_sentido_inverso(self):
        lista = ColeccionCargas()
        lista.agregar(0, 0, -1)
        lineas = generar_lineas(lista.cargas, Parametros(lineas=12, pasos_max=100))
        self.assertEqual(len(lineas), 12)
        self.assertEqual(lineas[0].sentido, -1)

    def test_dipolo(self):
        lista = ColeccionCargas()
        lista.agregar(-1.5, 0, 2)
        lista.agregar(1.5, 0, -2)
        lineas = generar_lineas(lista.cargas, Parametros(lineas=12, pasos_max=100))
        self.assertTrue(len(lineas) > 0)
        self.assertTrue(all(len(linea.puntos) <= 101 for linea in lineas))

    def test_cinco_cargas(self):
        lista = ColeccionCargas()
        for x, y, q in [(-2, 2, 1), (2, 2, -1), (0, 0, 2), (-2, -2, -2), (2, -2, 1)]:
            lista.agregar(x, y, q)
        lineas = generar_lineas(lista.cargas, Parametros(lineas=12, pasos_max=100))
        self.assertEqual(len(lineas), 12)

    def test_parametros_invalidos(self):
        for p in [Parametros(paso=0), Parametros(lineas=3),
                  Parametros(pasos_max=2), Parametros(radio_semilla=0.1, radio_parada=0.2)]:
            with self.assertRaises(ValueError):
                p.validar()

    def test_campo_cero_detiene(self):
        linea = integrar_euler(CampoElectrico([]), (0, 0), Parametros(pasos_max=100))
        self.assertEqual(len(linea.puntos), 1)
