import math

A, B = 0.0, 5.0     # відрізок [a, b]
Y0 = 1.0            # початкова умова y(a) = y0


def f(x, y):
    """Права частина рівняння dy/dx = f(x, y) = y * cos(x)."""
    return y * math.cos(x)


def exact(x):
    """Аналітичний розв'язок y(x) = e^sin(x)."""
    return math.exp(math.sin(x))


def rk4_step(x, y, h):
    """Один крок методу Рунге-Кутта четвертого порядку."""
    k1 = f(x, y)
    k2 = f(x + h / 2, y + h * k1 / 2)
    k3 = f(x + h / 2, y + h * k2 / 2)
    k4 = f(x + h, y + h * k3)
    return y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)