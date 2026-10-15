import csv
from math import factorial

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


# факторіальні многочлени працюють на рівновіддалених вузлах,
# тому будуємо рівномірну сітку на [x0, xn] за допомогою многочлена Ньютона
n_uzl = len(x) - 1
h = (x[-1] - x[0]) / n_uzl
x_equal = [x[0] + i * h for i in range(n_uzl + 1)]
y_equal = [newton_poly(x, table, xv) for xv in x_equal]

fd_table = finite_diff_table(y_equal)
pred_factorial = factorial_poly(x_equal[0], h, fd_table, 6000)
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
plt.title('Похибка інтерполяції залежно від кількості вузлів')
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
x_dense = np.linspace(a, b, 400)
f_reference = np.array([runge_test_func(xv, a, b) for xv in x_dense])

print()
plt.figure(figsize=(8, 5))
results_step = []
for n_nodes in node_counts:
    x_sub = list(np.linspace(a, b, n_nodes))
    y_sub = [runge_test_func(xv, a, b) for xv in x_sub]
    table_sub = divided_diff_table(x_sub, y_sub)

    y_interp = np.array([newton_poly(x_sub, table_sub, xv) for xv in x_dense])
    err = np.abs(y_interp - f_reference)
    max_err = err.max()
    results_step.append((n_nodes, max_err))
    print(f"n_nodes={n_nodes}: крок h={(b - a) / (n_nodes - 1):.2f}, макс. похибка={max_err:.6e}")

    plt.plot(x_dense, err, label=f'{n_nodes} вузлів')

plt.xlabel('x')
plt.ylabel('|похибка|')
plt.yscale('log')
plt.title('Вплив кроку h на точність (фіксований інтервал)')
plt.legend()
plt.grid(True)
plt.savefig('error_step_influence.png')
plt.show()

# ---- 2. Вплив кількості вузлів: фіксований крок, змінний інтервал ----
h_fixed = (b - a) / 20.0   # фіксований крок
print(f"\nФіксований крок h = {h_fixed:.3f}")

plt.figure(figsize=(8, 5))
results_interval = []
for n_nodes in node_counts:
    b_var = a + h_fixed * (n_nodes - 1)                  # останній вузол при кроці h
    x_sub = [a + i * h_fixed for i in range(n_nodes)]    # вузли з точно фіксованим кроком
    y_sub = [runge_test_func(xv, a, b_var) for xv in x_sub]
    table_sub = divided_diff_table(x_sub, y_sub)

    x_dense_var = np.linspace(a, b_var, 300)
    f_ref_var = np.array([runge_test_func(xv, a, b_var) for xv in x_dense_var])
    y_interp_var = np.array([newton_poly(x_sub, table_sub, xv) for xv in x_dense_var])
    err_var = np.abs(y_interp_var - f_ref_var)
    max_err = err_var.max()
    results_interval.append((n_nodes, b_var, max_err))
    print(f"n_nodes={n_nodes}: інтервал=[{a:.0f}, {b_var:.0f}], макс. похибка={max_err:.6e}")

    plt.plot(x_dense_var, err_var, label=f'{n_nodes} вузлів, b={b_var:.0f}')

plt.xlabel('x')
plt.ylabel('|похибка|')
plt.yscale('log')
plt.title('Вплив розширення інтервалу на точність (фіксований крок)')
plt.legend()
plt.grid(True)
plt.savefig('error_interval_influence.png')
plt.show()

# ---- 3. Аналіз ефекту Рунге ----
print("\nАналіз ефекту Рунге:")
for n_nodes, max_err in results_step:
    print(f"  n={n_nodes:3d}  максимальна похибка = {max_err:.6e}")