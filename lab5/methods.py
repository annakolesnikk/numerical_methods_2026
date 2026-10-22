import numpy as np
import sympy as sp


def make_function(expr_str, var="x"):
    """Повертає числову f(x) та її символьний вираз."""
    x = sp.Symbol(var)
    expr = sp.sympify(expr_str)
    return sp.lambdify(x, expr, "numpy"), expr, x


def exact_integral(expr, x, a, b):
    """Точне значення інтеграла (символьно)."""
    return float(sp.integrate(expr, (x, a, b)).evalf(20))


def simpson(f, a, b, n):
    """Складова формула Сімпсона, n — парне число розбиттів."""
    h = (b - a) / n
    y = f(a + h * np.arange(n + 1))
    return h / 3 * (y[0] + 4 * y[1:-1:2].sum() + 2 * y[2:-1:2].sum() + y[-1])


def abs_error(approx, exact):
    """eps = |approx - exact|"""
    return abs(approx - exact)


def find_n_opt(errors, ns, eps):
    """Найменше N, при якому похибка <= eps (None, якщо не досягнуто)."""
    for n, e in zip(ns, errors):
        if e <= eps:
            return n
    return None


def choose_n0(n_opt, divisor=10, multiple=8):
    """N0 ≈ N_opt/divisor, кратне multiple (не менше multiple)."""
    return max(multiple, round(n_opt / divisor / multiple) * multiple)


def runge_romberg(i_n, i_n2, q, p):
    """I_R = I(N) + (I(N) - I(N/q)) / (q^p - 1)"""
    return i_n + (i_n - i_n2) / (q**p - 1)


def aitken(i1, i2, i3):
    """I_E = (I2^2 - I1*I3) / (2*I2 - (I1 + I3)); i1 — найдрібніший крок."""
    return (i2**2 - i1 * i3) / (2 * i2 - (i1 + i3))


def aitken_order(i1, i2, i3, q):
    """p = ln|(I3 - I2) / (I2 - I1)| / ln(q)"""
    return np.log(abs((i3 - i2) / (i2 - i1))) / np.log(q)


def adaptive_simpson(f, a, b, delta):
    """Адаптивний алгоритм Сімпсона. Повертає (інтеграл, к-сть обчислень f)."""
    calls = [0]

    def fv(x):
        calls[0] += 1
        return f(x)

    def step(x0, x1, y0, ym, y1):
        h = x1 - x0
        xm = (x0 + x1) / 2
        yq1, yq3 = fv((x0 + xm) / 2), fv((xm + x1) / 2)
        i1 = h / 6 * (y0 + 4 * ym + y1)                              # крок h/2
        i2 = h / 12 * (y0 + 4 * yq1 + ym) + h / 12 * (ym + 4 * yq3 + y1)  # крок h/4
        if abs(i1 - i2) <= delta * h / (b - a):                       # умова (3)
            return i2
        return step(x0, xm, y0, yq1, ym) + step(xm, x1, ym, yq3, y1)

    result = step(a, b, fv(a), fv((a + b) / 2), fv(b))
    return result, calls[0]