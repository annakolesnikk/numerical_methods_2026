import csv

import numpy as np
import matplotlib.pyplot as plt


# ===================== 1. Табуляція вхідних даних =====================
# середньомісячні температури за 24 місяці
months = list(range(1, 25))
temps = [-2, 0, 5, 10, 15, 20, 23, 22, 17, 10, 5, 0,
         -10, 3, 7, 13, 19, 20, 22, 21, 18, 15, 10, 3]


def write_data(filename, x, y):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Month', 'Temp'])
        for xi, yi in zip(x, y):
            writer.writerow([xi, yi])


write_data("data.csv", months, temps)
print("Вузли {x_i, y_i} записано у файл data.csv")

# ===================== 2. Зчитування даних =====================
def read_data(filename):
    x, y = [], []
    with open(filename, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            x.append(float(row['Month']))
            y.append(float(row['Temp']))
    return x, y

x, y = read_data("data.csv")
n = len(x) - 1                     # вузли x_0 ... x_n
print("x:", x)
print("y:", y)


# ===================== 3. Функції МНК =====================
# матриця B: b_kl = sum x_i^(k+l)
def form_matrix_B(x, m):
    B = [[0.0] * (m + 1) for _ in range(m + 1)]
    for k in range(m + 1):
        for l in range(m + 1):
            B[k][l] = sum(xi ** (k + l) for xi in x)
    return B


# вектор C: c_k = sum f_i * x_i^k
def form_vector_C(x, y, m):
    C = [0.0] * (m + 1)
    for k in range(m + 1):
        C[k] = sum(yi * xi ** k for xi, yi in zip(x, y))
    return C


# метод Гауса з вибором головного елемента по стовпцях
def gauss_solve(A, b):
    A = [row[:] for row in A]      # копії, щоб не змінювати вхідні дані
    b = b[:]
    size = len(b)

    # прямий хід
    for k in range(size):
        max_row = max(range(k, size), key=lambda i: abs(A[i][k]))   # головний елемент
        A[k], A[max_row] = A[max_row], A[k]
        b[k], b[max_row] = b[max_row], b[k]
        for i in range(k + 1, size):
            factor = A[i][k] / A[k][k]
            for j in range(k, size):
                A[i][j] -= factor * A[k][j]
            b[i] -= factor * b[k]

    # зворотний хід
    sol = [0.0] * size
    for i in range(size - 1, -1, -1):
        s = sum(A[i][j] * sol[j] for j in range(i + 1, size))
        sol[i] = (b[i] - s) / A[i][i]
    return sol


# многочлен найкращого квадратичного наближення: phi(x) = sum a_j x^j
def polynomial(x_val, coef):
    return sum(a * x_val ** j for j, a in enumerate(coef))


# похибка eps(x) = |f(x) - phi(x)|
def error(f_val, phi_val):
    return abs(f_val - phi_val)


# дисперсія delta = sqrt( sum (phi(x_i) - f_i)^2 / (n+1) )
def dispersion(x, y, coef):
    s = sum((polynomial(xi, coef) - yi) ** 2 for xi, yi in zip(x, y))
    return (s / len(x)) ** 0.5


def least_squares(x, y, m):
    B = form_matrix_B(x, m)
    C = form_vector_C(x, y, m)
    return gauss_solve(B, C)


# ===================== 4. Дисперсія для m = 1...10 =====================
degrees = list(range(1, 11))
dispersions = []
coefs = {}

print("\nДисперсія для різних степенів многочлена:")
for m in degrees:
    coef = least_squares(x, y, m)
    coefs[m] = coef
    d = dispersion(x, y, coef)
    dispersions.append(d)
    print(f"m = {m:2d}: delta = {d:.4f}")

optimal_m = degrees[dispersions.index(min(dispersions))]
print(f"\nОптимальний степінь (мінімум дисперсії): m = {optimal_m}")
print("Коефіцієнти a_j:", [f"{a:.4e}" for a in coefs[optimal_m]])

# перевірка: значення многочлена у вузлах порівнюємо з бібліотечним np.polyfit
check = np.polyval(np.polyfit(x, y, optimal_m), x)
diff = max(abs(polynomial(xi, coefs[optimal_m]) - ci) for xi, ci in zip(x, check))
print(f"Максимальна різниця з np.polyfit у вузлах: {diff:.2e}")

# графік дисперсії від степеня
plt.figure(figsize=(8, 5))
plt.plot(degrees, dispersions, 'bo-')
plt.plot(optimal_m, min(dispersions), 'r*', markersize=15, label=f'оптимальний m = {optimal_m}')
plt.xlabel('Степінь многочлена m')
plt.ylabel('Дисперсія δ')
plt.title('Залежність дисперсії від степеня многочлена')
plt.xticks(degrees)
plt.legend()
plt.grid(True)
plt.savefig('dispersion_plot.png')
plt.show()


# ===================== 5. Графік апроксимації =====================
x_smooth = np.linspace(x[0], x[-1], 300)

plt.figure(figsize=(9, 5))
plt.plot(x, y, 'ro', label='Фактичні дані')
for m in [2, 4, optimal_m]:
    plt.plot(x_smooth, [polynomial(v, coefs[m]) for v in x_smooth], label=f'МНК, m = {m}')
plt.xlabel('Місяць')
plt.ylabel('Температура, °C')
plt.title('Апроксимація температури методом найменших квадратів')
plt.legend()
plt.grid(True)
plt.savefig('approximation_plot.png')
plt.show()


# ===================== 6. Табуляція похибки з кроком h1 = (xn - x0)/(20n) =====================
# між вузлами значення f(x) невідомі, тому беремо лінійну інтерполяцію табличних даних
h1 = (x[-1] - x[0]) / (20 * n)
x_tab = [x[0] + i * h1 for i in range(20 * n + 1)]
f_tab = np.interp(x_tab, x, y)

with open("error_tabulation.txt", "w", encoding="utf-8") as file:
    file.write(f"{'x':>8}" + "".join(f"{'m=' + str(m):>10}" for m in degrees) + "\n")
    for i, xv in enumerate(x_tab):
        row = [error(f_tab[i], polynomial(xv, coefs[m])) for m in degrees]
        file.write(f"{xv:8.3f}" + "".join(f"{e:10.4f}" for e in row) + "\n")
print(f"\nКрок табуляції h1 = {h1:.4f}")
print("Табуляцію похибки записано у файл error_tabulation.txt")

fig, axes = plt.subplots(5, 2, figsize=(11, 14), sharex=True)
for ax, m in zip(axes.flat, degrees):
    err = [error(f_tab[i], polynomial(xv, coefs[m])) for i, xv in enumerate(x_tab)]
    ax.plot(x_tab, err, 'g-')
    ax.set_title(f'm = {m}, δ = {dispersions[m - 1]:.3f}')
    ax.grid(True)
for ax in axes[-1]:
    ax.set_xlabel('Місяць')
fig.suptitle('Похибка апроксимації ε(x) = |f(x) − φ(x)|')
plt.tight_layout()
plt.savefig('error_plot.png')
plt.show()


# ===================== 7. Прогноз на наступні 3 місяці =====================
x_future = [25, 26, 27]
y_future = [polynomial(v, coefs[optimal_m]) for v in x_future]
print(f"\nПрогноз на місяці 25-27 (m = {optimal_m}):",
      [f"{v:.2f}" for v in y_future])

print("\nПрогноз для різних степенів:")
for m in degrees:
    print(f"m = {m:2d}:", [f"{polynomial(v, coefs[m]):8.2f}" for v in x_future])

x_ext = np.linspace(x[0], 27, 300)
plt.figure(figsize=(9, 5))
plt.plot(x, y, 'ro', label='Фактичні дані')
plt.plot(x_ext, [polynomial(v, coefs[optimal_m]) for v in x_ext], 'b-', label=f'МНК, m = {optimal_m}')
plt.plot(x_future, y_future, 'g*', markersize=15, label='Прогноз (25-27)')
plt.axvline(24, color='gray', ls='--')
plt.xlabel('Місяць')
plt.ylabel('Температура, °C')
plt.title('Екстраполяція температури на 3 місяці')
plt.legend()
plt.grid(True)
plt.savefig('forecast_plot.png')
plt.show()