import csv
from math import factorial, log2

import numpy as np
import matplotlib.pyplot as plt


# ===================== Зчитування даних =====================
def read_data(filename):
    x, y = [], []
    with open(filename, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            keys = list(row.keys())
            x.append(float(row[keys[0]]))
            y.append(float(row[keys[1]]))
    return x, y


x, y = read_data("data.csv")
print("x:", x)
print("y:", y)


# ===================== Таблиця розділених різниць =====================
def divided_diff_table(x, y):
    n = len(x)
    table = [[0.0] * n for _ in range(n)]
    for i in range(n):
        table[i][0] = y[i]
    for j in range(1, n):
        for i in range(n - j):
            table[i][j] = (table[i + 1][j - 1] - table[i][j - 1]) / (x[i + j] - x[i])
    return table


table = divided_diff_table(x, y)
print("\nТаблиця розділених різниць:")
for row in table:
    print(["%.6e" % v for v in row])


# ===================== Многочлен Ньютона =====================
def newton_poly(x_data, table, x_val):
    n = len(x_data)
    result = table[0][0]
    product_term = 1.0
    for k in range(1, n):
        product_term *= (x_val - x_data[k - 1])
        result += table[0][k] * product_term
    return result


pred_newton = newton_poly(x, table, 6000)
print(f"\nПрогноз методом Ньютона при n=6000: {pred_newton:.4f} мс")


# omega_k(x) = (x - x0)(x - x1)...(x - xk)
def omega(x_val, x_data, k):
    result = 1.0
    for i in range(k + 1):
        result *= (x_val - x_data[i])
    return result

# розділена різниця k-го порядку за явною формулою:
# f(x0,...,xk) = sum f(xi) / prod(xi - xj), j != i
def divided_diff_explicit(x_data, y_data, k):
    total = 0.0
    for i in range(k + 1):
        denom = 1.0
        for j in range(k + 1):
            if j != i:
                denom *= (x_data[i] - x_data[j])
        total += y_data[i] / denom
    return total

# многочлен Ньютона за формулою: N(x) = f0 + sum omega_{k-1}(x) * f(x0,...,xk)
def newton_poly_explicit(x_data, y_data, x_val):
    result = y_data[0]
    for k in range(1, len(x_data)):
        result += omega(x_val, x_data, k - 1) * divided_diff_explicit(x_data, y_data, k)
    return result


# перевірка: явна формула дає ті самі різниці, що й рекурентна таблиця
print("\nПорівняння розділених різниць (таблиця / явна формула):")
for k in range(len(x)):
    print(f"k={k}: {table[0][k]:.6e}  /  {divided_diff_explicit(x, y, k):.6e}")

pred_explicit = newton_poly_explicit(x, y, 6000)
print(f"Прогноз за явною формулою при n=6000: {pred_explicit:.4f} мс")


# ===================== Факторіальні многочлени =====================
def finite_diff_table(y):
    n = len(y)
    table = [[0.0] * n for _ in range(n)]
    for i in range(n):
        table[i][0] = y[i]
    for j in range(1, n):
        for i in range(n - j):
            table[i][j] = table[i + 1][j - 1] - table[i][j - 1]
    return table


def factorial_poly(x0, h, fd_table, x_val):
    n = len(fd_table)
    t = (x_val - x0) / h
    result = fd_table[0][0]
    t_fact = 1.0
    for k in range(1, n):
        t_fact *= (t - (k - 1))
        result += fd_table[0][k] * t_fact / factorial(k)
    return result


# факторіальні многочлени працюють на рівновіддалених вузлах.
# Вузли 1000, 2000, 4000, 8000, 16000 кожен раз подвоюються, тому в змінній
# t = log2(n / x0) вони рівновіддалені: t = 0, 1, 2, 3, 4 з кроком h = 1
t_nodes = [log2(xv / x[0]) for xv in x]
print("\nВузли у змінній t = log2(n/1000):", t_nodes)

fd_table = finite_diff_table(y)
print("Скінченні різниці:", [fd_table[0][k] for k in range(len(y))])

t_val = log2(6000 / x[0])
pred_factorial = factorial_poly(0.0, 1.0, fd_table, t_val)
print(f"t(6000) = log2(6) = {t_val:.4f}")
print(f"Прогноз факторіальним многочленом при n=6000: {pred_factorial:.4f} мс")


# ===================== Графік інтерполяції =====================
x_plot = np.linspace(min(x), max(x), 300)
y_plot = [newton_poly(x, table, xv) for xv in x_plot]

plt.figure(figsize=(8, 5))
plt.plot(x, y, 'ro', markersize=8, label='Експериментальні точки')
plt.plot(x_plot, y_plot, 'b-', label='Многочлен Ньютона N(x)')
plt.plot(6000, pred_newton, 'g*', markersize=15, label='Прогноз x=6000')
plt.xlabel('n (розмір вхідних даних)')
plt.ylabel('t (час виконання, мс)')
plt.title('Інтерполяція методом Ньютона')
plt.legend()
plt.grid(True)
plt.savefig('newton_plot.png')
plt.show()


# ===================== 5, 10, 20 вузлів =====================
print()
for n_nodes in [5, 10, 20]:
    x_sub = list(np.linspace(min(x), max(x), n_nodes))
    y_sub = [newton_poly(x, table, xv) for xv in x_sub]
    table_sub = divided_diff_table(x_sub, y_sub)
    pred = newton_poly(x_sub, table_sub, 6000)
    print(f"n_nodes={n_nodes}: прогноз при x=6000 = {pred:.4f}")

# точність прогнозу на реальних даних: додаємо вузли, найближчі до 6000
order = sorted(range(len(x)), key=lambda i: abs(x[i] - 6000))
print("\nПрогноз при додаванні реальних вузлів (найближчих до 6000):")
prev = None
for k in range(2, len(x) + 1):
    idx = sorted(order[:k])
    xs = [x[i] for i in idx]
    ys = [y[i] for i in idx]
    p = newton_poly(xs, divided_diff_table(xs, ys), 6000)
    diff = "" if prev is None else f", зміна = {abs(p - prev):.4f}"
    print(f"{k} вузли {[int(v) for v in xs]}: N(6000) = {p:.4f}{diff}")
    prev = p

x_dense = np.linspace(min(x), max(x), 400)
f_reference = np.array([newton_poly(x, table, xv) for xv in x_dense])

plt.figure(figsize=(8, 5))
for n_nodes in [5, 10, 20]:
    x_sub = list(np.linspace(min(x), max(x), n_nodes))
    y_sub = [newton_poly(x, table, xv) for xv in x_sub]
    table_sub = divided_diff_table(x_sub, y_sub)
    y_interp = np.array([newton_poly(x_sub, table_sub, xv) for xv in x_dense])
    err = np.abs(y_interp - f_reference)
    print(f"n_nodes={n_nodes}: максимальна похибка = {err.max():.6e}")
    plt.plot(x_dense, err, label=f'{n_nodes} вузлів')

plt.xlabel('x')
plt.ylabel('|похибка|')
plt.title('Відхилення від еталонного многочлена (похибки округлення)')
plt.legend()
plt.grid(True)
plt.yscale('log')
plt.savefig('error_plot.png')
plt.show()


# ===================== Тестова функція Рунге =====================
def runge_test_func(x_val, a, b):
    t = -1.0 + 2.0 * (x_val - a) / (b - a)
    return 1.0 / (1.0 + 25.0 * t ** 2)


# ===== Табуляція f(x), N_n(x), eps(x), w_n(x) на [a,b] з кроком h = (b-a)/(20n) =====
a, b = x[0], x[-1]
n = 5                                            # кількість інтервалів (n+1 вузол)
x_nodes = [a + i * (b - a) / n for i in range(n + 1)]
y_nodes = [runge_test_func(xv, a, b) for xv in x_nodes]
table_n = divided_diff_table(x_nodes, y_nodes)

h_tab = (b - a) / (20 * n)
x_tab = [a + i * h_tab for i in range(20 * n + 1)]
f_tab = [runge_test_func(xv, a, b) for xv in x_tab]
N_tab = [newton_poly(x_nodes, table_n, xv) for xv in x_tab]
eps_tab = [abs(f - N) for f, N in zip(f_tab, N_tab)]
w_tab = [omega(xv, x_nodes, n) for xv in x_tab]

# запис результатів табуляції в текстовий файл
with open("tabulation.txt", "w", encoding="utf-8") as file:
    file.write(f"{'x':>10} {'f(x)':>14} {'N_n(x)':>14} {'eps(x)':>14} {'w_n(x)':>14}\n")
    for row in zip(x_tab, f_tab, N_tab, eps_tab, w_tab):
        file.write(f"{row[0]:10.2f} {row[1]:14.6e} {row[2]:14.6e} {row[3]:14.6e} {row[4]:14.6e}\n")
print("\nТабуляцію записано у файл tabulation.txt")
print(f"Максимальна похибка eps(x) при n={n}: {max(eps_tab):.6e}")

fig, axes = plt.subplots(3, 1, figsize=(8, 10))

axes[0].plot(x_tab, f_tab, 'b-', label='f(x)')
axes[0].plot(x_tab, N_tab, 'r--', label='N_n(x)')
axes[0].plot(x_nodes, y_nodes, 'ko', label='вузли')
axes[0].set_title('Функція f(x) та многочлен Ньютона N_n(x)')
axes[0].legend()
axes[0].grid(True)

axes[1].plot(x_tab, eps_tab, 'g-')
axes[1].set_title('Похибка інтерполяції ε(x) = |f(x) − N_n(x)|')
axes[1].grid(True)

axes[2].plot(x_tab, w_tab, 'm-')
axes[2].axhline(0, color='k', lw=0.8)
axes[2].set_title('Функція w_n(x) = ∏(x − xᵢ)')
axes[2].set_xlabel('x')
axes[2].grid(True)

plt.tight_layout()
plt.savefig('tabulation_plot.png')
plt.show()


# ===================== ДОСЛІДНИЦЬКА ЧАСТИНА =====================
node_counts = [5, 10, 20]

# ---- 1. Вплив кроку: фіксований інтервал, різна кількість вузлів ----
print()
plt.figure(figsize=(8, 5))
results_step = []
for n_nodes in node_counts:
    h = (b - a) / (n_nodes - 1)                          # крок між вузлами
    x_sub = [a + k * h for k in range(n_nodes)]          # вузли: x_k = a + k*h
    y_sub = [runge_test_func(xv, a, b) for xv in x_sub]
    table_sub = divided_diff_table(x_sub, y_sub)

    h_tab = h / 20                                       # крок табуляції
    x_tab_r = [a + i * h_tab for i in range(20 * (n_nodes - 1) + 1)]   # x_i = a + i*h_tab
    err = np.array([abs(newton_poly(x_sub, table_sub, xv) - runge_test_func(xv, a, b))
                    for xv in x_tab_r])
    max_err = err.max()
    results_step.append((n_nodes, h, max_err))
    print(f"n_nodes={n_nodes}: крок h={h:.2f}, макс. похибка={max_err:.6e}")

    plt.plot(x_tab_r, err, label=f'{n_nodes} вузлів, h={h:.0f}')

plt.xlabel('x')
plt.ylabel('|f(x) − N(x)|')
plt.title('Похибка інтерполяції при різному кроці h (фіксований інтервал)')
plt.legend(loc='upper center')
plt.grid(True)
plt.savefig('error_step_influence.png')
plt.show()

# залежність максимальної похибки від кроку h
plt.figure(figsize=(8, 5))
plt.plot([r[1] for r in results_step], [r[2] for r in results_step], 'bo-')
for n_nodes, h, max_err in results_step:
    plt.annotate(f'{n_nodes} вузлів', (h, max_err), textcoords='offset points', xytext=(5, 5))
plt.xlabel('крок h')
plt.ylabel('максимальна похибка')
plt.yscale('log')
plt.title('Залежність максимальної похибки від кроку h')
plt.grid(True)
plt.savefig('max_error_vs_step.png')
plt.show()

# ---- 2. Вплив кількості вузлів: фіксований крок, змінний інтервал ----
# функція Рунге залишається заданою на [a, b] = [1000, 16000],
# змінюється лише ділянка [a, b_var], яку покривають вузли
h_fixed = (b - a) / 20.0   # фіксований крок
print(f"\nФіксований крок h = {h_fixed:.3f}")

plt.figure(figsize=(8, 5))
results_interval = []
for n_nodes in node_counts:
    b_var = a + h_fixed * (n_nodes - 1)                  # b = a + h*(n-1)
    x_sub = [a + k * h_fixed for k in range(n_nodes)]    # вузли: x_k = a + k*h
    y_sub = [runge_test_func(xv, a, b) for xv in x_sub]  # функція та сама, на [a, b]
    table_sub = divided_diff_table(x_sub, y_sub)

    h_tab = h_fixed / 20
    x_tab_r = [a + i * h_tab for i in range(20 * (n_nodes - 1) + 1)]
    err_var = np.array([abs(newton_poly(x_sub, table_sub, xv) - runge_test_func(xv, a, b))
                        for xv in x_tab_r])
    max_err = err_var.max()
    results_interval.append((n_nodes, b_var, max_err))
    print(f"n_nodes={n_nodes}: інтервал=[{a:.0f}, {b_var:.0f}], макс. похибка={max_err:.6e}")

    plt.plot(x_tab_r, err_var, label=f'{n_nodes} вузлів, b={b_var:.0f}')

plt.xlabel('x')
plt.ylabel('|f(x) − N(x)|')
plt.yscale('log')
plt.title('Похибка інтерполяції при фіксованому кроці h = 750')
plt.legend(loc='upper left')
plt.grid(True)
plt.savefig('error_interval_influence.png')
plt.show()

# ---- 3. Аналіз ефекту Рунге ----
print("\nАналіз ефекту Рунге:")
print("  фіксований інтервал:")
for n_nodes, h, max_err in results_step:
    print(f"    n={n_nodes:3d}  h={h:.2f}  максимальна похибка = {max_err:.6e}")
print("  фіксований крок:")
for n_nodes, b_var, max_err in results_interval:
    print(f"    n={n_nodes:3d}  b={b_var:.0f}  максимальна похибка = {max_err:.6e}")