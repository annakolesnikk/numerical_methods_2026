import matplotlib.pyplot as plt
from equation import A, B, Y0, exact, rk4_step

H = 1e-2            # заданий крок
EPS = 1e-8          # задана точність
K = 2 ** 5          # k = 2^(s+1), s = 4 - порядок методу


def runge_kutta(a, b, y0, h):
    """Розв'язок задачі Коші методом Рунге-Кутта 4-го порядку зі сталим кроком h."""
    n = round((b - a) / h)
    xs = [a + i * h for i in range(n + 1)]
    ys = [y0]
    for i in range(n):
        ys.append(rk4_step(xs[i], ys[i], h))
    return xs, ys


def error_exact(xs, ys):
    """Похибка phi_n = y_n - y(x_n) за точним розв'язком."""
    return [y - exact(x) for x, y in zip(xs, ys)]


def error_runge(a, b, y0, h):
    """Похибка за методом Рунге: phi_n = 16/15 * (y_n(h/2) - y_n(h))."""
    xs, ys_h = runge_kutta(a, b, y0, h)
    _, ys_h2 = runge_kutta(a, b, y0, h / 2)
    return xs, [16 / 15 * (ys_h2[2 * i] - ys_h[i]) for i in range(len(xs))]


def runge_kutta_auto(a, b, y0, h, eps):
    """Метод Рунге-Кутта 4-го порядку з автоматичним вибором кроку."""
    x, y = a, y0
    xs, ys, hs = [x], [y], []
    while x < b - 1e-12:
        h = min(h, b - x)                           # останній крок точно до b
        y_h = rk4_step(x, y, h)                     # один крок h
        y_half = rk4_step(x + h / 2, rk4_step(x, y, h / 2), h / 2)   # два кроки h/2
        err = 16 / 15 * abs(y_h - y_half)
        if err > eps:                               # похибка завелика: зменшує крок
            h /= 2
            continue
        x, y = x + h, y_half                        # крок прийнято
        xs.append(x)
        ys.append(y)
        hs.append(h)
        if err < eps / K:                           # похибка дуже мала: збільшує крок
            h *= 2
    return xs, ys, hs


def plot(xs, ys, title, ylabel, filename):
    plt.figure()
    plt.plot(xs, ys)
    plt.grid(True)
    plt.xlabel("x")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.savefig(filename)


if __name__ == "__main__":
    # Розв'язок зі сталим кроком h = 0.01
    xs, ys = runge_kutta(A, B, Y0, H)
    errors = error_exact(xs, ys)
    print(f"Метод Рунге-Кутта 4-го порядку, h = {H}")
    print(f"  y({B}) = {ys[-1]:.12f}, точне y({B}) = {exact(B):.12f}")
    print(f"  max|y_n - y(x_n)| = {max(abs(e) for e in errors):.3e}")
    plot(xs, errors, "Похибка y_n - y(x_n), метод Рунге-Кутта", "похибка", "rk4_error_exact.png")

    # Залежність похибки від кроку
    print("\nЗалежність похибки від кроку:")
    print(f"  {'h':>8} {'max|похибки|':>14}")
    for h in [0.2, 0.1, 0.05, 0.02, 0.01]:
        xs_h, ys_h = runge_kutta(A, B, Y0, h)
        print(f"  {h:>8} {max(abs(e) for e in error_exact(xs_h, ys_h)):>14.3e}")

    # Похибка за методом Рунге
    xs, errors_runge = error_runge(A, B, Y0, H)
    max_runge = max(abs(e) for e in errors_runge)
    print(f"\nПохибка за методом Рунге, h = {H}")
    print(f"  max|phi_n| = {max_runge:.3e}, eps = {EPS}, eps/k = {EPS / K:.3e}")
    if max_runge > EPS:
        print("  Крок завеликий: його треба зменшити")
    elif max_runge < EPS / K:
        print("  Крок можна збільшити")
    else:
        print("  Крок оптимальний")
    h_need = H * (EPS / max_runge) ** (1 / 4)
    print(f"  Необхідна величина кроку для точності eps: h ≈ {h_need:.4f}")
    plot(xs, errors_runge, "Похибка за методом Рунге, метод Рунге-Кутта", "похибка",
         "rk4_error_runge.png")

    # Автоматичний вибір кроку
    xs, ys, hs = runge_kutta_auto(A, B, Y0, H, EPS)
    print(f"\nАвтоматичний вибір кроку, eps = {EPS}")
    print(f"  Кількість кроків: {len(hs)}")
    print(f"  Крок від {min(hs):.5f} до {max(hs):.5f}")
    print(f"  max|y_n - y(x_n)| = {max(abs(y - exact(x)) for x, y in zip(xs, ys)):.3e}")
    plot(xs[1:], hs, "Залежність кроку h(x), метод Рунге-Кутта", "h", "rk4_step.png")
    print("\nГрафіки збережено: rk4_error_exact.png, rk4_error_runge.png, rk4_step.png")