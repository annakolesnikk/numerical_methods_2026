import math
from tabulation import F

EPS = 1e-10         
MAX_ITER = 1000     
H = 0.1             # відступ для додаткових початкових точок

# Початкові наближення, отримані з табуляції 
X0_INC = -1.95      # корінь, в околі якого функція зростає
X0_DEC = 1.35       # корінь, в околі якого функція спадає


def dF(x):
    """Перша похідна F'(x) = -sin(x) - 0.2."""
    return -math.sin(x) - 0.2


def d2F(x):
    """Друга похідна F''(x) = -cos(x)."""
    return -math.cos(x)


def is_done(x_new, x_old):
    """Критерій: |F(x_n+1)| < eps та |x_n+1 - x_n| < eps."""
    return abs(F(x_new)) < EPS and abs(x_new - x_old) < EPS


def simple_iteration(x0):
    """Метод простої ітерації (релаксації): x_n+1 = x_n + tau * F(x_n)."""
    tau = -1 / dF(x0)               # забезпечує -2 < tau * F'(x) < 0
    x = x0
    for k in range(1, MAX_ITER + 1):
        x_new = x + tau * F(x)
        if is_done(x_new, x):
            return x_new, k
        x = x_new
    return x, MAX_ITER


def newton(x0):
    """Метод Ньютона: x_n+1 = x_n - F(x_n) / F'(x_n)."""
    x = x0
    for k in range(1, MAX_ITER + 1):
        x_new = x - F(x) / dF(x)
        if is_done(x_new, x):
            return x_new, k
        x = x_new
    return x, MAX_ITER


def chebyshev(x0):
    """Метод Чебишева: x_n+1 = x_n - F/F' - 1/2 * F^2 * F'' / F'^3."""
    x = x0
    for k in range(1, MAX_ITER + 1):
        f, df, d2f = F(x), dF(x), d2F(x)
        x_new = x - f / df - 0.5 * f ** 2 * d2f / df ** 3
        if is_done(x_new, x):
            return x_new, k
        x = x_new
    return x, MAX_ITER


def chords(x0):
    """Метод хорд: x_n+1 = x_n - F(x_n) * (x_n - x_n-1) / (F(x_n) - F(x_n-1))."""
    x_prev, x = x0 - H, x0
    for k in range(1, MAX_ITER + 1):
        x_new = x - F(x) * (x - x_prev) / (F(x) - F(x_prev))
        if is_done(x_new, x):
            return x_new, k
        x_prev, x = x, x_new
    return x, MAX_ITER


def parabolas(x0):
    """Метод парабол: x_n+1 = x_n + delta, delta - менший за модулем корінь квадратного рівняння."""
    x2, x1, x = x0 - H, x0 + H, x0          # x_n-2, x_n-1, x_n
    for k in range(1, MAX_ITER + 1):
        f01 = (F(x) - F(x1)) / (x - x1)                 # F(x_n, x_n-1)
        f12 = (F(x1) - F(x2)) / (x1 - x2)               # F(x_n-1, x_n-2)
        f012 = (f01 - f12) / (x - x2)                   # F(x_n, x_n-1, x_n-2)
        w = (x - x1) * f012 + f01
        d = math.sqrt(max(w ** 2 - 4 * f012 * F(x), 0))
        delta1 = (-w + d) / (2 * f012)
        delta2 = (-w - d) / (2 * f012)
        delta = delta1 if abs(delta1) < abs(delta2) else delta2
        x_new = x + delta
        if is_done(x_new, x):
            return x_new, k
        x2, x1, x = x1, x, x_new
    return x, MAX_ITER


def inverse_interpolation(x0):
    """Метод зворотної інтерполяції (многочлен Лагранжа x = L2(y) за трьома вузлами)."""
    x2, x1, x = x0 - H, x0 + H, x0          # x_n-2, x_n-1, x_n
    for k in range(1, MAX_ITER + 1):
        y2, y1, y = F(x2), F(x1), F(x)
        x_new = (y1 * y / ((y2 - y1) * (y2 - y)) * x2
                 + y2 * y / ((y1 - y2) * (y1 - y)) * x1
                 + y2 * y1 / ((y - y2) * (y - y1)) * x)
        if is_done(x_new, x):
            return x_new, k
        x2, x1, x = x1, x, x_new
    return x, MAX_ITER


if __name__ == "__main__":
    methods = [("Проста ітерація", simple_iteration),
               ("Ньютон", newton),
               ("Чебишев", chebyshev),
               ("Хорди", chords),
               ("Параболи", parabolas),
               ("Зворотна інтерполяція", inverse_interpolation)]

    for x0, title in [(X0_INC, "зростає"), (X0_DEC, "спадає")]:
        print(f"\nКорінь з початковим наближенням x0 = {x0} (функція {title}):")
        print(f"  {'Метод':<24}{'Корінь':>22}{'|F(x)|':>12}{'Ітерацій':>10}")
        for name, method in methods:
            root, iterations = method(x0)
            print(f"  {name:<24}{root:>22.15f}{abs(F(root)):>12.1e}{iterations:>10}")