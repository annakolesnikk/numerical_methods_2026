import matplotlib.pyplot as plt
from equation import A, B, Y0, f, exact, rk4_step

H = 0.01            # заданий крок
EPS = 1e-6          # задана точність (на один крок)
EPS_ITER = 1e-12    # точність ітерацій на етапі корекції
K = 2 ** 3          # k = 2^(s+1), s = 2 - порядок методу


def adams_step(x_prev, y_prev, x, y, h):
    """Один крок методу прогнозу і корекції Адамса другого порядку."""
    f_prev, f_n = f(x_prev, y_prev), f(x, y)
    y_pr = y + h / 2 * (3 * f_n - f_prev)               # прогноз
    y_kor = y_pr
    for _ in range(20):                                 # корекція (ітерації)
        y_new = y + h / 2 * (f(x + h, y_kor) + f_n)
        if abs(y_new - y_kor) <= EPS_ITER:
            y_kor = y_new
            break
        y_kor = y_new
    return y_pr, y_kor


def adams(a, b, y0, h):
    """Розв'язок задачі Коші методом Адамса 2-го порядку зі сталим кроком h."""
    n = round((b - a) / h)
    xs = [a + i * h for i in range(n + 1)]
    ys = [y0, rk4_step(a, y0, h)]           # y1 знаходимо методом Рунге-Кутта
    estimates = [0.0, 0.0]                  # оцінка похибки -(y_kor - y_pr) / 6
    for i in range(1, n):
        y_pr, y_kor = adams_step(xs[i - 1], ys[i - 1], xs[i], ys[i], h)
        ys.append(y_kor)
        estimates.append(-(y_kor - y_pr) / 6)
    return xs, ys, estimates


def adams_auto(a, b, y0, h, eps):
    """Метод Адамса 2-го порядку з автоматичним вибором кроку."""
    x, y = a, y0
    x_prev, y_prev = x - h, rk4_step(x, y, -h)    # попередній вузол методом Рунге-Кутта
    xs, ys, hs = [x], [y], []
    while x < b - 1e-12:
        if x + h > b:                             # останній крок точно до b
            h = b - x
            x_prev, y_prev = x - h, rk4_step(x, y, -h)
        y_pr, y_kor = adams_step(x_prev, y_prev, x, y, h)
        err = abs(y_kor - y_pr) / 6
        if err > eps:                             # похибка завелика: зменшує крок
            h /= 2
            x_prev, y_prev = x - h, rk4_step(x, y, -h)
            continue
        x_prev, y_prev, x, y = x, y, x + h, y_kor  # крок прийнято
        xs.append(x)
        ys.append(y)
        hs.append(h)
        if err < eps / K:                         # похибка дуже мала: збільшуємо крок
            h *= 2
            x_prev, y_prev = x - h, rk4_step(x, y, -h)
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
    # Розв'язок зі сталим кроком
    xs, ys, estimates = adams(A, B, Y0, H)
    errors = [y - exact(x) for x, y in zip(xs, ys)]
    print(f"Метод Адамса 2-го порядку, h = {H}")
    print(f"  y({B}) = {ys[-1]:.10f}, точне y({B}) = {exact(B):.10f}")
    print(f"  max|y_n - y(x_n)| = {max(abs(e) for e in errors):.3e}")
    plot(xs, errors, "Похибка y_n - y(x_n), метод Адамса", "похибка", "adams_error_exact.png")

    # Оцінка похибки через (y_kor - y_pr)
    max_est = max(abs(e) for e in estimates)
    print(f"  max|оцінки похибки| = {max_est:.3e}, eps = {EPS}, eps/k = {EPS / K:.3e}")
    if max_est > EPS:
        print("  Крок завеликий: його треба зменшити")
    elif max_est < EPS / K:
        print("  Крок можна збільшити")
    else:
        print("  Крок оптимальний")
    plot(xs, estimates, "Оцінка похибки -(y_kor - y_pr)/6, метод Адамса", "похибка",
         "adams_error_estimate.png")

    # Автоматичний вибір кроку
    xs, ys, hs = adams_auto(A, B, Y0, H, EPS)
    print(f"\nАвтоматичний вибір кроку, eps = {EPS}")
    print(f"  Кількість кроків: {len(hs)}")
    print(f"  Крок від {min(hs):.5f} до {max(hs):.5f}")
    print(f"  max|y_n - y(x_n)| = {max(abs(y - exact(x)) for x, y in zip(xs, ys)):.3e}")
    plot(xs[1:], hs, "Залежність кроку h(x), метод Адамса", "h", "adams_step.png")
    print("\nГрафіки збережено: adams_error_exact.png, adams_error_estimate.png, adams_step.png")