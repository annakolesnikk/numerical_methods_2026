import numpy as np
import sympy as sp


def make_functions(expr_str, var="t"):
    """Повертає числові f(t), f'(t) та їх символьні вирази."""
    t = sp.Symbol(var)
    expr = sp.sympify(expr_str)
    d_expr = sp.diff(expr, t)                      # аналітична похідна
    f = sp.lambdify(t, expr, "numpy")
    df = sp.lambdify(t, d_expr, "numpy")
    return f, df, expr, d_expr


def central_diff(f, x0, h):
    """y'0(h) = (f(x0+h) - f(x0-h)) / (2h)"""
    return (f(x0 + h) - f(x0 - h)) / (2 * h)


def abs_error(approx, exact):
    """R = |approx - exact|"""
    return abs(approx - exact)


def step_grid(k_min, k_max):
    """Кроки виду m*10^k (m = 1..9), щоб h0 мав формат типу 6e-07."""
    hs = [m * 10.0**k for k in range(k_min, k_max) for m in range(1, 10)]
    hs.append(10.0**k_max)
    return np.array(hs)


def error_study(f, x0, exact, hs):
    """Похибка центральної різниці для кожного h; повертає похибки, h0, R0."""
    errors = np.array([abs_error(central_diff(f, x0, h), exact) for h in hs])
    i = int(np.argmin(errors))
    return errors, hs[i], errors[i]


def runge_romberg(y_h, y_qh, q, p):
    """y'R = y'(h) + (y'(h) - y'(qh)) / (q^p - 1)"""
    return y_h + (y_h - y_qh) / (q**p - 1)


def aitken(y_h, y_qh, y_q2h):
    """y'E = (y'(qh)^2 - y'(q^2 h) y'(h)) / (2y'(qh) - (y'(q^2 h) + y'(h)))"""
    return (y_qh**2 - y_q2h * y_h) / (2 * y_qh - (y_q2h + y_h))


def aitken_order(y_h, y_qh, y_q2h, q):
    """p = ln|(y'(q^2 h) - y'(qh)) / (y'(qh) - y'(h))| / ln(q)"""
    return np.log(abs((y_q2h - y_qh) / (y_qh - y_h))) / np.log(q)