import math

A, B = -5.0, 5.0    # відрізок табуляції
H = 0.1             # крок табуляції


def F(x):
    """Задана трансцендентна функція F(x) = cos(x) - 0.2x."""
    return math.cos(x) - 0.2 * x


def tabulate(a, b, h):
    """Табуляція функції на відрізку [a, b] з кроком h."""
    n = round((b - a) / h)
    xs = [a + i * h for i in range(n + 1)]
    ys = [F(x) for x in xs]
    return xs, ys


def write_table(filename, xs, ys):
    """Запис результатів табуляції у текстовий файл."""
    with open(filename, "w") as f:
        f.write(f"{'x':>8} {'F(x)':>14}\n")
        for x, y in zip(xs, ys):
            f.write(f"{x:8.2f} {y:14.8f}\n")


def find_crossings(xs, ys):
    """Пошук вузлів, між якими функція змінює знак (перетин з віссю x)."""
    crossings = []
    for i in range(len(xs) - 1):
        if ys[i] * ys[i + 1] < 0:
            x_approx = (xs[i] + xs[i + 1]) / 2
            behavior = "зростає" if ys[i] < ys[i + 1] else "спадає"
            crossings.append((xs[i], xs[i + 1], x_approx, behavior))
    return crossings


if __name__ == "__main__":
    xs, ys = tabulate(A, B, H)
    write_table("tabulation.txt", xs, ys)
    print("Результати табуляції записано у tabulation.txt\n")

    print("Точки перетину функції з віссю x:")
    for x1, x2, x_approx, behavior in find_crossings(xs, ys):
        print(f"  [{x1:.1f}; {x2:.1f}]  x ≈ {x_approx:.2f}  функція {behavior}")