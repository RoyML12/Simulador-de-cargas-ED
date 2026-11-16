import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import Simulador


def evento(app, x, y):
    px, py = app.ejes.transData.transform((x, y))
    return SimpleNamespace(button=1, inaxes=app.ejes, xdata=x, ydata=y,
                           x=px, y=py)


def guardar_captura(app, nombre):
    try:
        from PIL import ImageGrab
        app.update()
        app.canvas.draw()
        x, y = app.winfo_rootx(), app.winfo_rooty()
        ruta = Path(__file__).resolve().parents[1] / "evidencias" / nombre
        ImageGrab.grab(bbox=(x, y, x + app.winfo_width(),
                             y + app.winfo_height())).save(ruta)
        print("Captura:", ruta)
    except (ImportError, OSError):
        print("No se pudo tomar la captura")


def main():
    app = Simulador()
    try:
        app.update()
        app.canvas.draw()
        assert len(app.cargas.cargas) == 2
        assert hasattr(app, "entrada")
        assert hasattr(app, "datos_tiempo")
        assert app.tiempo_ms >= 0
        assert app.pico_mib >= 0
        assert not hasattr(app, "lista")  # Ya no hay lista lateral.

        carga = app.cargas.cargas[0]
        app.presionar_mouse(evento(app, carga.x, carga.y))
        assert app.seleccionada == carga.id
        app.mover_mouse(evento(app, carga.x + 0.7, carga.y + 0.4))
        app.soltar_mouse(evento(app, carga.x + 0.7, carga.y + 0.4))
        assert abs(carga.x - (-0.8)) < 0.0001
        assert abs(carga.y - 0.4) < 0.0001

        app.valor.set("-3,5")
        app.cambiar_valor()
        assert abs(carga.q_uc + 3.5) < 0.0001
        guardar_captura(app, "edicion_y_arrastre.png")

        app.agregar_positiva()
        assert len(app.cargas.cargas) == 3
        app.eliminar()
        assert len(app.cargas.cargas) == 2
        app.limpiar()
        assert len(app.cargas.cargas) == 0
        guardar_captura(app, "limpiar.png")
        app.reiniciar()
        assert len(app.cargas.cargas) == 2
        guardar_captura(app, "reiniciar.png")

        app.mostrar_modelo()
        ventanas = [h for h in app.winfo_children() if h.winfo_class() == "Toplevel"]
        assert len(ventanas) == 1
        ventanas[0].destroy()

        # Abrir y ejecutar la comparación desde la interfaz.
        app.mostrar_rendimiento()
        ventanas = [h for h in app.winfo_children() if h.winfo_class() == "Toplevel"]
        assert len(ventanas) == 1
        ventana = ventanas[0]
        botones = [h for h in ventana.winfo_children() if h.winfo_class() == "Button"]
        assert len(botones) == 1
        botones[0].invoke()
        textos = [h for h in ventana.winfo_children() if h.winfo_class() == "Text"]
        assert "Pico Python" in textos[0].get("1.0", "end")
        ventana.destroy()

        # Captura real de la ventana en el entorno de prueba.
        app.geometry("1050x720+20+20")
        app.update()
        app.canvas.draw()
        import time
        time.sleep(0.25)
        app.update()
        assert "RAM del proceso:" in app.datos_tiempo.get()
        guardar_captura(app, "captura_entrega_final.png")

        print("OK: arrastre, edición, controles, modelo, rendimiento y memoria en vivo.")
    finally:
        app.destroy()


if __name__ == "__main__":
    main()
