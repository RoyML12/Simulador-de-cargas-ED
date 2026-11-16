import unittest
from campo import ColeccionCargas, CampoElectrico, K, MICRO


class PruebasCampo(unittest.TestCase):
    def test_carga_positiva(self):
        lista = ColeccionCargas()
        lista.agregar(0, 0, 1)
        ex, ey = CampoElectrico(lista.cargas).evaluar(1, 0)
        self.assertAlmostEqual(ex, K * MICRO)
        self.assertAlmostEqual(ey, 0)

    def test_carga_negativa(self):
        lista = ColeccionCargas()
        lista.agregar(0, 0, -1)
        ex, ey = CampoElectrico(lista.cargas).evaluar(1, 0)
        self.assertLess(ex, 0)
        self.assertAlmostEqual(ey, 0)

    def test_dipolo(self):
        lista = ColeccionCargas()
        lista.agregar(-1, 0, 1)
        lista.agregar(1, 0, -1)
        ex, ey = CampoElectrico(lista.cargas).evaluar(0, 0)
        self.assertAlmostEqual(ex, 2 * K * MICRO)
        self.assertAlmostEqual(ey, 0)

    def test_dos_positivas(self):
        lista = ColeccionCargas()
        lista.agregar(-1, 0, 1)
        lista.agregar(1, 0, 1)
        campo = CampoElectrico(lista.cargas)
        self.assertAlmostEqual(campo.evaluar(0, 0)[0], 0)
        self.assertIsNone(campo.norma_y_direccion(0, 0))

    def test_singularidad(self):
        lista = ColeccionCargas()
        lista.agregar(0, 0, 1)
        with self.assertRaises(ValueError):
            CampoElectrico(lista.cargas).evaluar(0, 0)

    def test_sin_cargas(self):
        self.assertEqual(CampoElectrico([]).evaluar(1, 2), (0, 0))

    def test_modificar(self):
        lista = ColeccionCargas()
        carga = lista.agregar(0, 0, 2)
        lista.modificar(carga.id, 1, 2, -3)
        self.assertEqual((carga.x, carga.y, carga.q_uc), (1, 2, -3))

    def test_limite_cinco(self):
        lista = ColeccionCargas()
        for i in range(5):
            lista.agregar(i, 0, 1)
        with self.assertRaises(ValueError):
            lista.agregar(0, 0, 1)

    def test_valores_invalidos(self):
        lista = ColeccionCargas()
        for valor in (0, 21, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                lista.agregar(0, 0, valor)
        with self.assertRaises(ValueError):
            lista.agregar(6, 0, 1)

    def test_eliminar_y_limpiar(self):
        lista = ColeccionCargas()
        carga = lista.agregar(0, 0, 2)
        lista.eliminar(carga.id)
        self.assertEqual(len(lista.cargas), 0)
        lista.agregar(0, 0, -1)
        lista.limpiar()
        self.assertEqual(len(lista.cargas), 0)
