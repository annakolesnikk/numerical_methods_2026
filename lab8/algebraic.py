import math
import matplotlib.pyplot as plt

EPS = 1e-10         
MAX_ITER = 1000     


def read_coefficients(filename):
    """Зчитує коефіцієнти a0, a1, ..., am многочлена з текстового файлу."""
    with open(filename) as f:
        return [float(v) for v in f.read().split()]


def poly_value(a, x):
    """Значення многочлена F(x) = a0 + a1*x + ... + am*x^m (схема Горнера)."""
    result = 0.0
    for coef in reversed(a):
        result = result * x + coef
    return result


def plot_polynomial(a, x_min, x_max, filename):
    """Будує графік многочлена та зберігає його у файл."""
    n = 400
    xs = [x_min + i * (x_max - x_min) / n for i in range(n + 1)]
    ys = [poly_value(a, x) for x in xs]
    plt.plot(xs, ys, label="F(x)")
    plt.axhline(0, color="black", linewidth=0.8)
    plt.grid(True)
    plt.xlabel("x")
    plt.ylabel("F(x)")
    plt.title("Графік многочлена F(x) = x³ - 2x² - 2x - 3")
    plt.legend()
    plt.savefig(filename)


def newton_horner(a, x0):
    """Метод Ньютона з використанням схеми Горнера: x_n+1 = x_n - b0 / c1."""
    m = len(a) - 1
    x = x0
    for k in range(1, MAX_ITER + 1):
        b = [0.0] * (m + 1)
        b[m] = a[m]
        for i in range(m - 1, -1, -1):          # b_i = a_i + x_n * b_i+1
            b[i] = a[i] + x * b[i + 1]
        c = [0.0] * (m + 1)
        c[m] = b[m]
        for i in range(m - 1, 0, -1):           # c_i = b_i + x_n * c_i+1
            c[i] = b[i] + x * c[i + 1]
        x_new = x - b[0] / c[1]                 # b0 = F(x_n), c1 = F'(x_n)
        if abs(poly_value(a, x_new)) < EPS and abs(x_new - x) < EPS:
            return x_new, k
        x = x_new
    return x, MAX_ITER


def lin(a, alpha0, beta0):
    """Метод Ліна: знаходження комплексно-спряжених коренів alpha ± i*beta."""
    m = len(a) - 1
    for k in range(1, MAX_ITER + 1):
        p = -2 * alpha0
        q = alpha0 ** 2 + beta0 ** 2
        b = [0.0] * (m + 3)
        for i in range(m, 1, -1):               # b_i = a_i - p*b_i+1 - q*b_i+2
            b[i] = a[i] - p * b[i + 1] - q * b[i + 2]
        q1 = a[0] / b[2]
        p1 = (a[1] * b[2] - a[0] * b[3]) / b[2] ** 2
        alpha1 = -p1 / 2
        beta1 = math.sqrt(q1 - alpha1 ** 2)
        if abs(alpha1 - alpha0) <= EPS and abs(beta1 - beta0) <= EPS:
            return alpha1, beta1, k
        alpha0, beta0 = alpha1, beta1
    return alpha0, beta0, MAX_ITER


if __name__ == "__main__":
    a = read_coefficients("coefficients.txt")
    print("Коефіцієнти a0, a1, ..., am:", a)

    plot_polynomial(a, -2, 4, "polynomial.png")
    print("Графік збережено у polynomial.png")

    x0 = 3.5
    root, iterations = newton_horner(a, x0)
    print(f"\nМетод Ньютона (схема Горнера), x0 = {x0}")
    print(f"  Дійсний корінь x = {root:.15f}")
    print(f"  F(x) = {poly_value(a, root):.1e}")
    print(f"  Кількість ітерацій: {iterations}")

    alpha0, beta0 = 0.0, 1.0
    alpha, beta, iterations = lin(a, alpha0, beta0)
    print(f"\nМетод Ліна, початкове наближення {alpha0} ± {beta0}i")
    print(f"  Комплексні корені: {alpha:.15f} ± {beta:.15f}i")
    print(f"  Кількість ітерацій: {iterations}")