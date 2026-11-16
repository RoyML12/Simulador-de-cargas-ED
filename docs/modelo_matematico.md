# Modelo matemático y validación numérica

## Variables y unidades

| Variable | Definición | Unidad |
|---|---|---|
| `q_i` | Carga puntual con signo | coulomb (C) |
| `x_i, y_i` | Posición de carga `i` | metro (m) |
| `x, y` | Punto de evaluación | metro (m) |
| `Ex, Ey` | Componentes del campo eléctrico | newton por coulomb (N/C) |
| `k` | Constante de Coulomb | N·m²/C² |
| `s` | Parámetro de longitud de trayectoria | metro (m) |
| `h` | Paso de Euler para `s` | metro (m) |

## Ley de Coulomb y superposición

En un punto `(x,y)` que no coincida con una carga puntual:

```text
r_i²   = (x − x_i)² + (y − y_i)²
Ex(x,y)= k * Σ_i [ q_i (x − x_i) / (r_i²)^(3/2) ]
Ey(x,y)= k * Σ_i [ q_i (y − y_i) / (r_i²)^(3/2) ]
```

La ley vectorial equivale a `E(r) = Σ k q_i (r-r_i)/|r-r_i|³`. El signo de `q_i` da la dirección correspondiente. Se trabaja con la representación en el plano `z=0` de cargas puntuales; no se afirma representar el campo tridimensional completo.

## Sistema de EDO para líneas de campo

La tangente de una línea de campo debe coincidir con la dirección de `E`. Cuando `||E|| ≠ 0`:

```text
dx/ds = Ex(x,y) / sqrt(Ex(x,y)² + Ey(x,y)²)
dy/ds = Ey(x,y) / sqrt(Ex(x,y)² + Ey(x,y)²)
```

Estas son EDO acopladas de primer orden. La normalización evita que los pasos se hagan arbitrariamente largos en zonas de campo fuerte. No se usa `dy/dx=Ey/Ex`, que fallaría para `Ex=0` en tangentes verticales.

## Método de Euler explícito

Con `u=(x,y)`, `F=E/||E||` y paso fijo `h`:

```text
u_(n+1) = u_n + h F(u_n)
```

Para un conjunto sin cargas positivas, se integra en el sentido opuesto (`u_(n+1)=u_n−hF(u_n)`) para obtener curvas que emerjan del entorno de una negativa en el orden de los datos. Las flechas se invierten al dibujar, representando que el sentido físico es hacia la carga negativa.

## Dos comprobaciones manuales de campo

**Caso 1: una carga positiva en el origen.** `q=+1 µC`, punto de evaluación `(1,0)` m. Distancia `1 m`, `k=8.9875517923e9 N·m²/C²`:

- `Ex = 8.9875517923e9 · 1e−6 = +8987.5517923 N/C`.
- `Ey = 0 N/C`.
- Con `h=0.06 m`, `u1=(1.06,0)` m.

**Caso 2: dipolo simétrico.** `q1=+1 µC` en `(−1,0)` m, `q2=−1 µC` en `(+1,0)` m; evaluación en `(0,0)`:

- `Ex1 = +8987.5517923 N/C`, `Ey1=0`.
- `Ex2 = +8987.5517923 N/C`, `Ey2=0`.
- `Ex_total = +17975.1035846 N/C`, `Ey_total=0`.

**Caso complementario:** `+1 µC` en `(−1,0)` y `+1 µC` en `(+1,0)` producen `E=(0,0)` en el origen.

## Criterios de parada y estabilidad

Se detiene una línea si sale del cuadrado `[−5,+5]²`, si alcanza `radio_parada=0.15 m` alrededor de una carga, si `||E|| < 1e−9 N/C`, si aparece una singularidad o si se alcanzan 700 pasos. Se empieza en un radio de `0.23 m`, mayor que el radio de parada. Se valida que las entradas numéricas sean finitas.

**Experimento de estabilidad recomendado:** escoger el dipolo, mantener número de líneas y máximo de pasos, y comparar `h=0.12`, `0.06` y `0.03 m`. Capturar las trayectorias y comentar cómo cambia su suavidad, sobre todo cerca de cargas. Euler tiene error global de orden `O(h)` en condiciones regulares.

## Interpretación computacional

Evaluar `E` en un punto requiere sumar `N` contribuciones: `O(N)`. Para `L` semillas y un máximo de `S` pasos, el trabajo límite es `O(NLS)` y los puntos almacenados como arreglos de coordenadas son `O(LS)`. La memoria de `tracemalloc` cubre asignaciones trazadas de Python, no todo el proceso. Al comparar tiempos reales, registrar puntos efectivamente generados porque las condiciones de terminación pueden reducir iteraciones.
