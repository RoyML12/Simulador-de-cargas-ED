import math

K = 8.9875517923e9       # Constante de Coulomb
MICRO = 0.000001          # Para convertir microculombios a culombios
LIMITE = 4.8             # Límite para mover las cargas


class Carga:
    def __init__(self, numero, x, y, valor):
        self.id = numero
        self.x = x
        self.y = y
        self.q = valor * MICRO

    @property
    def q_uc(self):
        return self.q / MICRO


class ColeccionCargas:
    def __init__(self):
        self.cargas = []
        self.siguiente_id = 1

    def agregar(self, x, y, valor):
        if len(self.cargas) >= 5:
            raise ValueError("Solo se permiten cinco cargas.")
        self.validar(x, y, valor)
        carga = Carga(self.siguiente_id, x, y, valor)
        self.cargas.append(carga)
        self.siguiente_id += 1
        return carga

    def buscar(self, numero):
        for carga in self.cargas:
            if carga.id == numero:
                return carga
        return None

    def modificar(self, numero, x, y, valor):
        self.validar(x, y, valor)
        carga = self.buscar(numero)
        if carga is None:
            raise ValueError("No se encontró la carga.")
        carga.x = x
        carga.y = y
        carga.q = valor * MICRO
        return carga

    def eliminar(self, numero):
        carga = self.buscar(numero)
        if carga is None:
            raise ValueError("Selecciona una carga.")
        self.cargas.remove(carga)

    def limpiar(self):
        self.cargas.clear()

    def validar(self, x, y, valor):
        for dato in (x, y, valor):
            if not isinstance(dato, (int, float)) or not math.isfinite(dato):
                raise ValueError("Los valores deben ser números válidos.")
        if abs(x) > LIMITE or abs(y) > LIMITE:
            raise ValueError("La carga está fuera del área permitida.")
        if valor == 0 or abs(valor) > 20:
            raise ValueError("Usa una carga entre -20 y 20 µC, diferente de cero.")


class CampoElectrico:
    def __init__(self, cargas):
        self.cargas = cargas

    def evaluar(self, x, y):
        # Sumar el campo de todas las cargas (superposición).
        ex = 0.0
        ey = 0.0

        for carga in self.cargas:
            dx = x - carga.x
            dy = y - carga.y
            distancia = math.sqrt(dx * dx + dy * dy)

            if distancia < 0.000000001:
                raise ValueError("No se puede calcular el campo sobre una carga.")

            factor = K * carga.q / (distancia ** 3)
            ex += factor * dx
            ey += factor * dy

        return ex, ey

    def norma_y_direccion(self, x, y, campo_minimo=1e-9):
        ex, ey = self.evaluar(x, y)
        norma = math.sqrt(ex * ex + ey * ey)
        if norma < campo_minimo or not math.isfinite(norma):
            return None
        return ex / norma, ey / norma
