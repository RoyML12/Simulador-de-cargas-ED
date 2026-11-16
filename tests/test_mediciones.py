import tempfile
from pathlib import Path
import unittest
from mediciones import ejecutar_mediciones
from trayectorias import Parametros


class PruebaRendimiento(unittest.TestCase):
    def test_exportar(self):
        with tempfile.TemporaryDirectory() as carpeta:
            datos = ejecutar_mediciones(carpeta, 1, Parametros(lineas=8, pasos_max=100))
            self.assertEqual([d["cargas"] for d in datos], [1, 2, 5])
            self.assertTrue((Path(carpeta) / "rendimiento.csv").exists())
            self.assertTrue((Path(carpeta) / "rendimiento.png").exists())
