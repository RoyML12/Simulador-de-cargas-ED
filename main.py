import math
import time
import tracemalloc
import tkinter as tk
from tkinter import messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from campo import ColeccionCargas, LIMITE
from trayectorias import Parametros, generar_lineas
from mediciones import ejecutar_mediciones

try:
    import psutil
except ImportError:
    psutil = None


class Simulador(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de campo eléctrico")
        self.geometry("1050x720")
        self.minsize(930, 550)
        self.configure(bg="white")

        self.cargas = ColeccionCargas()
        self.parametros = Parametros()
        self.seleccionada = None
        self.arrastrando = False
        self.ultima_posicion = None
        self.desplazamiento = (0, 0)
        self.marcadores = {}
        self.ram = "-- MiB"

        # Dos cargas iniciales para que se vea el funcionamiento.
        self.cargas.agregar(-1.5, 0, 2)
        self.cargas.agregar(1.5, 0, -2)

        self.crear_interfaz()
        self.dibujar()
        self.after(500, self.actualizar_ram)

    def crear_interfaz(self):
        titulo = tk.Label(self, text="Campo eléctrico", font=("Arial", 17, "bold"),
                          bg="white", fg="#263238")
        titulo.pack(anchor="w", padx=18, pady=(15, 9))

        # Todos los controles principales están en una sola fila.
        barra = tk.Frame(self, bg="white")
        barra.pack(fill="x", padx=15, pady=(0, 9))

        tk.Button(barra, text="+ Positiva", command=self.agregar_positiva,
                  bg="#DD5555", fg="white", width=10).pack(side="left", padx=3)
        tk.Button(barra, text="− Negativa", command=self.agregar_negativa,
                  bg="#347ABD", fg="white", width=10).pack(side="left", padx=3)

        tk.Label(barra, text="Valor (µC):", bg="white").pack(side="left", padx=(12, 3))
        self.valor = tk.StringVar()
        self.entrada = tk.Entry(barra, textvariable=self.valor, width=8)
        self.entrada.pack(side="left", padx=3)
        self.entrada.bind("<Return>", lambda evento: self.cambiar_valor())

        tk.Button(barra, text="Aplicar", command=self.cambiar_valor).pack(side="left", padx=3)
        tk.Button(barra, text="Eliminar", command=self.eliminar).pack(side="left", padx=3)
        tk.Button(barra, text="Limpiar", command=self.limpiar).pack(side="left", padx=3)
        tk.Button(barra, text="Reiniciar", command=self.reiniciar).pack(side="left", padx=3)
        tk.Button(barra, text="Modelo matemático", command=self.mostrar_modelo).pack(side="left", padx=3)
        tk.Button(barra, text="Rendimiento", command=self.mostrar_rendimiento).pack(side="left", padx=3)

        # Este aviso se coloca abajo antes de la gráfica para reservar su espacio.
        self.mensaje = tk.StringVar(value="Selecciona y arrastra una carga con el mouse.")
        tk.Label(self, textvariable=self.mensaje, bg="white", fg="#5E6872",
                 anchor="w", font=("Arial", 10)).pack(side="bottom", fill="x", padx=17, pady=8)

        # Se actualizan al recalcular las líneas, sin medir cada movimiento del mouse.
        self.datos_tiempo = tk.StringVar(value="Cálculo: -- ms | Pico Python: -- MiB | RAM: -- MiB")
        tk.Label(self, textvariable=self.datos_tiempo, bg="#F2F5F7", fg="#334155",
                 anchor="w", font=("Arial", 10), padx=12, pady=7).pack(
                     side="bottom", fill="x", padx=15)

        self.figura = Figure(figsize=(9, 6), dpi=100)
        self.ejes = self.figura.add_subplot(111)
        self.figura.subplots_adjust(left=0.075, right=0.975, bottom=0.085, top=0.97)

        self.canvas = FigureCanvasTkAgg(self.figura, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=14)

        self.canvas.mpl_connect("button_press_event", self.presionar_mouse)
        self.canvas.mpl_connect("motion_notify_event", self.mover_mouse)
        self.canvas.mpl_connect("button_release_event", self.soltar_mouse)

    def encontrar_espacio(self):
        # Usamos posiciones libres para no crear cargas encima de otras.
        lugares = [(0, 0), (-2, 0), (2, 0), (0, 2), (0, -2),
                   (-2, 2), (2, 2), (-2, -2), (2, -2)]
        for x, y in lugares:
            ocupado = False
            for carga in self.cargas.cargas:
                if math.hypot(x - carga.x, y - carga.y) < 0.7:
                    ocupado = True
            if not ocupado:
                return x, y
        return 0, 0

    def agregar_positiva(self):
        self.agregar(2)

    def agregar_negativa(self):
        self.agregar(-2)

    def agregar(self, valor):
        try:
            x, y = self.encontrar_espacio()
            carga = self.cargas.agregar(x, y, valor)
            self.seleccionada = carga.id
            self.valor.set(str(valor))
            self.dibujar()
        except ValueError as error:
            messagebox.showerror("Error", str(error))

    def cambiar_valor(self):
        carga = self.cargas.buscar(self.seleccionada)
        if carga is None:
            messagebox.showinfo("Información", "Selecciona primero una carga en la gráfica.")
            return
        try:
            numero = float(self.valor.get().strip().replace(",", "."))
            self.cargas.modificar(carga.id, carga.x, carga.y, numero)
            self.dibujar()
        except (ValueError, OverflowError) as error:
            messagebox.showerror("Valor incorrecto", str(error))

    def eliminar(self):
        if self.seleccionada is None:
            messagebox.showinfo("Información", "Selecciona una carga para eliminarla.")
            return
        self.cargas.eliminar(self.seleccionada)
        self.seleccionada = None
        self.valor.set("")
        self.dibujar()

    def limpiar(self):
        self.cargas.limpiar()
        self.seleccionada = None
        self.arrastrando = False
        self.valor.set("")
        self.dibujar()

    def reiniciar(self):
        self.cargas = ColeccionCargas()
        self.cargas.agregar(-1.5, 0, 2)
        self.cargas.agregar(1.5, 0, -2)
        self.parametros = Parametros()
        self.seleccionada = None
        self.arrastrando = False
        self.valor.set("")
        self.dibujar()

    def mostrar_modelo(self):
        # Las fórmulas se consultan aquí, sin ocupar espacio en el simulador.
        ventana = tk.Toplevel(self)
        ventana.title("Modelo matemático")
        ventana.geometry("640x420")
        ventana.configure(bg="white")
        texto = (
            "MODELO MATEMÁTICO\n\n"
            "1. Campo eléctrico (ley de Coulomb):\n"
            "   E = k · q · (r − r₀) / |r − r₀|³\n\n"
            "2. Superposición de varias cargas:\n"
            "   E_total = E₁ + E₂ + ... + Eₙ\n\n"
            "3. Sistema de ecuaciones diferenciales:\n"
            "   dx/ds = Ex / √(Ex² + Ey²)\n"
            "   dy/ds = Ey / √(Ex² + Ey²)\n\n"
            "4. Método de Euler (paso h):\n"
            "   x_nuevo = x + h · Ex / |E|\n"
            "   y_nuevo = y + h · Ey / |E|\n\n"
            "k = 8.99 × 10⁹ N·m²/C². Las posiciones están en metros.\n"
            "La entrada de cargas está en microculombios (µC).\n"
            "Las líneas salen de + y entran a −. Para solo cargas\n"
            "negativas se integra hacia atrás (−h)."
        )
        tk.Label(ventana, text=texto, justify="left", anchor="nw", bg="white",
                 fg="#263238", font=("Consolas", 11), padx=20, pady=18).pack(fill="both")

    def mostrar_rendimiento(self):
        # La comparación usa las mismas 24 semillas y 700 pasos máximos.
        ventana = tk.Toplevel(self)
        ventana.title("Mediciones de rendimiento")
        ventana.geometry("660x370")
        ventana.configure(bg="white")

        tk.Label(ventana, text="Comparación: 1, 2 y 5 cargas", bg="white",
                 font=("Arial", 15, "bold")).pack(pady=(16, 5))
        tk.Label(ventana, text="Tres repeticiones por caso. Tiempo del cálculo, sin dibujar la gráfica.",
                 bg="white").pack(pady=(0, 12))
        resultado = tk.Text(ventana, height=9, width=68, font=("Consolas", 10),
                            bg="#F6F8FA", relief="flat", padx=10, pady=10)
        resultado.pack(fill="both", expand=True, padx=18)
        resultado.insert("end", "Presiona 'Medir' para generar el CSV y las gráficas.\n")
        resultado.config(state="disabled")

        def medir():
            boton.config(state="disabled")
            ventana.update_idletasks()
            try:
                datos = ejecutar_mediciones("resultados", 3, self.parametros)
                filas = ["Cargas    Tiempo (ms)    Pico Python (MiB)    Puntos", "-" * 60]
                for d in datos:
                    filas.append(f"{d['cargas']:>3}       {d['tiempo_ms']:>8.2f}          "
                                 f"{d['memoria_mib']:>7.3f}          {d['puntos']:>5}")
                filas.append("\nArchivos guardados en la carpeta 'resultados'.")
                filas.append("La memoria indicada es el pico rastreado por tracemalloc.")
                resultado.config(state="normal")
                resultado.delete("1.0", "end")
                resultado.insert("end", "\n".join(filas))
                resultado.config(state="disabled")
            except Exception as error:
                messagebox.showerror("Error al medir", str(error), parent=ventana)
            finally:
                boton.config(state="normal")

        boton = tk.Button(ventana, text="Medir y guardar resultados", command=medir)
        boton.pack(pady=12)

    def actualizar_etiqueta(self):
        self.datos_tiempo.set(
            f"Cálculo: {self.tiempo_ms:.2f} ms  |  "
            f"Pico Python: {self.pico_mib:.3f} MiB  |  RAM del proceso: {self.ram}")

    def actualizar_ram(self):
        # RSS: memoria del proceso completo; se revisa cada segundo.
        if psutil is None:
            self.ram = "no disponible"
        else:
            ram_mib = psutil.Process().memory_info().rss / (1024 * 1024)
            self.ram = f"{ram_mib:.1f} MiB"
        self.actualizar_etiqueta()
        self.after(1000, self.actualizar_ram)

    def buscar_carga_mouse(self, evento):
        if evento.inaxes != self.ejes or evento.xdata is None:
            return None
        for carga in self.cargas.cargas:
            # Distancia en píxeles para facilitar hacer clic.
            x_pantalla, y_pantalla = self.ejes.transData.transform((carga.x, carga.y))
            distancia = math.hypot(evento.x - x_pantalla, evento.y - y_pantalla)
            if distancia < 19:
                return carga
        return None

    def presionar_mouse(self, evento):
        if evento.button != 1:
            return
        carga = self.buscar_carga_mouse(evento)
        if carga is None:
            return
        self.seleccionada = carga.id
        self.valor.set("{:g}".format(carga.q_uc))
        self.arrastrando = True
        self.ultima_posicion = (carga.x, carga.y)
        self.desplazamiento = (carga.x - evento.xdata, carga.y - evento.ydata)
        self.dibujar()

    def mover_mouse(self, evento):
        if not self.arrastrando or evento.inaxes != self.ejes:
            return
        if evento.xdata is None or evento.ydata is None:
            return

        x = evento.xdata + self.desplazamiento[0]
        y = evento.ydata + self.desplazamiento[1]
        x = max(-LIMITE, min(LIMITE, x))
        y = max(-LIMITE, min(LIMITE, y))
        self.ultima_posicion = (x, y)

        # Al arrastrar solo movemos el marcador. El campo se calcula al soltar.
        if self.seleccionada in self.marcadores:
            punto, signo, etiqueta = self.marcadores[self.seleccionada]
            punto.set_offsets([[x, y]])
            signo.set_position((x, y))
            etiqueta.set_position((x + 0.2, y + 0.2))
            self.canvas.draw_idle()

    def soltar_mouse(self, evento):
        if not self.arrastrando:
            return
        self.mover_mouse(evento)
        self.arrastrando = False
        carga = self.cargas.buscar(self.seleccionada)
        if carga is not None and self.ultima_posicion is not None:
            x, y = self.ultima_posicion
            self.cargas.modificar(carga.id, x, y, carga.q_uc)
        self.dibujar()

    def dibujar(self):
        self.ejes.clear()
        self.ejes.set_xlim(-5, 5)
        self.ejes.set_ylim(-5, 5)
        self.ejes.set_aspect("equal")
        self.ejes.set_xlabel("x (m)")
        self.ejes.set_ylabel("y (m)")
        self.ejes.grid(True, color="#E0E0E0", linewidth=0.7)
        self.marcadores = {}

        # Medimos el último cálculo real de Euler, no el dibujo de Matplotlib.
        # tracemalloc añade un pequeño costo: el tiempo mostrado incluye ese costo.
        tracemalloc.start()
        inicio = time.perf_counter()
        try:
            lineas = generar_lineas(self.cargas.cargas, self.parametros)
            self.tiempo_ms = (time.perf_counter() - inicio) * 1000
            self.pico_mib = tracemalloc.get_traced_memory()[1] / (1024 * 1024)
        finally:
            tracemalloc.stop()
        for linea in lineas:
            puntos = linea.puntos
            self.ejes.plot(puntos[:, 0], puntos[:, 1], color="#168C8D", linewidth=1.2)

            if len(puntos) > 8:
                medio = len(puntos) // 2
                a = puntos[medio - 4]
                b = puntos[medio + 4]
                if linea.sentido == -1:
                    a, b = b, a
                self.ejes.annotate("", xy=b, xytext=a,
                                   arrowprops={"arrowstyle": "->", "color": "#168C8D", "lw": 1.2})

        for carga in self.cargas.cargas:
            color = "#DD5555" if carga.q > 0 else "#347ABD"
            borde = "#FFB000" if carga.id == self.seleccionada else "white"
            punto = self.ejes.scatter([carga.x], [carga.y], s=370, color=color,
                                      edgecolors=borde, linewidths=3, zorder=5)
            signo = self.ejes.text(carga.x, carga.y, "+" if carga.q > 0 else "−",
                                   color="white", fontsize=16, weight="bold",
                                   ha="center", va="center", zorder=6)
            etiqueta = self.ejes.text(carga.x + 0.2, carga.y + 0.2,
                                      "{:g} µC".format(carga.q_uc), fontsize=9, zorder=6)
            self.marcadores[carga.id] = (punto, signo, etiqueta)

        self.canvas.draw_idle()
        self.actualizar_etiqueta()
        self.mensaje.set("{} / 5 cargas · Selecciona y arrastra con el mouse.".format(len(self.cargas.cargas)))


if __name__ == "__main__":
    aplicacion = Simulador()
    aplicacion.mainloop()
