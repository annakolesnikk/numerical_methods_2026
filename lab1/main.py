import requests
import numpy as np
import matplotlib.pyplot as plt

# 1. Запит до Open-Elevation API
url = ("https://api.open-elevation.com/api/v1/lookup?locations="
       "48.164214,24.536044|48.164983,24.534836|48.165605,24.534068|"
       "48.166228,24.532915|48.166777,24.531927|48.167326,24.530884|"
       "48.167011,24.530061|48.166053,24.528039|48.166655,24.526064|"
       "48.166497,24.523574|48.166128,24.520214|48.165416,24.517170|"
       "48.164546,24.514640|48.163412,24.512980|48.162331,24.511715|"
       "48.162015,24.509462|48.162147,24.506932|48.161751,24.504244|"
       "48.161197,24.501793|48.160580,24.500537|48.160250,24.500106")

response = requests.get(url, timeout=10)
data = response.json()
results = data["results"]
n = len(results)
print("Кількість вузлів:", n)

# 2. Табуляція вузлів
print("\nТабуляція вузлів:")
print("№ | Latitude | Longitude | Elevation (m)")
for i, point in enumerate(results):
    print(f"{i:2d} | {point['latitude']:.6f} | "
          f"{point['longitude']:.6f} | "
          f"{point['elevation']:.2f}")

# Збереження результатів у текстовий файл
with open("nodes.txt", "w", encoding="utf-8") as f:
    f.write("№ | Latitude | Longitude | Elevation (m)\n")
    for i, point in enumerate(results):
        f.write(f"{i:2d} | {point['latitude']:.6f} | "
                f"{point['longitude']:.6f} | "
                f"{point['elevation']:.2f}\n")

print("\nРезультати збережено у файл nodes.txt")

# 3. Кумулятивна відстань (формула гаверсинуса)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # радіус Землі в метрах
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2) ** 2
    return 2 * R * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

coords = [(p["latitude"], p["longitude"]) for p in results]
elevations = [p["elevation"] for p in results]

distances = [0]
for i in range(1, n):
    d = haversine(*coords[i - 1], *coords[i])
    distances.append(distances[-1] + d)

print("\nТабуляція (відстань, висота):")
print("№ | Distance (m) | Elevation (m)")
for i in range(n):
    print(f"{i:2d} | {distances[i]:10.2f} | {elevations[i]:8.2f}")

# 4. Графік вихідних точок
plt.figure(figsize=(10, 5))
plt.plot(distances, elevations, 'o-', color='tab:blue')
plt.xlabel("Відстань, м")
plt.ylabel("Висота, м")
plt.title("Профіль маршруту Заросляк — Говерла (вихідні дані)")
plt.grid(True)
plt.savefig("raw_profile.png", dpi=150)
plt.show()

# 5. Побудова кубічного сплайна (власна реалізація)

def build_spline_system(x, y):
    """
    Формує коефіцієнти трьохдіагональної системи для знаходження c_i.
    x, y — списки вузлів (відстань, висота)
    Повертає alpha, beta, gamma, delta для системи відносно c
    """
    m = len(x)  # кількість вузлів
    h = [x[i+1] - x[i] for i in range(m - 1)]  # кроки між вузлами

    alpha = [0.0] * m
    beta = [0.0] * m
    gamma = [0.0] * m
    delta = [0.0] * m

    # Крайові умови вільного сплайна: c[0] = 0, c[m-1] = 0
    beta[0] = 1.0
    delta[0] = 0.0

    for i in range(1, m - 1):
        alpha[i] = h[i - 1]
        beta[i] = 2 * (h[i - 1] + h[i])
        gamma[i] = h[i]
        delta[i] = 3 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1])

    beta[m - 1] = 1.0
    delta[m - 1] = 0.0

    return alpha, beta, gamma, delta, h

def thomas_algorithm(alpha, beta, gamma, delta):
    """
    Розв'язує трьохдіагональну систему методом прогонки.
    """
    m = len(beta)
    A = [0.0] * m
    B = [0.0] * m
    c = [0.0] * m

    # Пряма прогонка
    A[0] = -gamma[0] / beta[0]
    B[0] = delta[0] / beta[0]

    for i in range(1, m):
        denom = beta[i] + alpha[i] * A[i - 1]
        if i < m - 1:
            A[i] = -gamma[i] / denom
        B[i] = (delta[i] - alpha[i] * B[i - 1]) / denom

    # Зворотна прогонка
    c[m - 1] = B[m - 1]
    for i in range(m - 2, -1, -1):
        c[i] = A[i] * c[i + 1] + B[i]

    return c
def compute_spline_coeffs(x, y):
    m = len(x)
    alpha, beta, gamma, delta, h = build_spline_system(x, y)
    c = thomas_algorithm(alpha, beta, gamma, delta)

    a = [0.0] * (m - 1)
    b = [0.0] * (m - 1)
    d = [0.0] * (m - 1)

    for i in range(m - 1):
        a[i] = y[i]
        b[i] = (y[i + 1] - y[i]) / h[i] - h[i] * (2 * c[i] + c[i + 1]) / 3
        d[i] = (c[i + 1] - c[i]) / (3 * h[i])

    return a, b, c, d, h


def spline_value(x_nodes, a, b, c, d, x_val):
    """Обчислює значення сплайна в точці x_val"""
    m = len(x_nodes) - 1
    # знаходимо відповідний інтервал
    if x_val <= x_nodes[0]:
        i = 0
    elif x_val >= x_nodes[-1]:
        i = m - 1
    else:
        i = np.searchsorted(x_nodes, x_val) - 1
        i = max(0, min(i, m - 1))

    dx = x_val - x_nodes[i]
    return a[i] + b[i] * dx + c[i] * dx ** 2 + d[i] * dx ** 3
# Обчислюємо коефіцієнти сплайна для повного набору вузлів
a_coef, b_coef, c_coef, d_coef, h_steps = compute_spline_coeffs(distances, elevations)

print("\nКоефіцієнти сплайна (i, a, b, c, d):")
for i in range(len(a_coef)):
    print(f"{i:2d} | a={a_coef[i]:10.3f} | b={b_coef[i]:10.5f} | "
          f"c={c_coef[i]:10.7f} | d={d_coef[i]:12.9f}")

# 6. Дрібна табуляція та графік гладкого сплайна
N_fine = 20 * (len(distances) - 1)
xx_full = np.linspace(distances[0], distances[-1], N_fine)
yy_full = [spline_value(distances, a_coef, b_coef, c_coef, d_coef, xv) for xv in xx_full]

plt.figure(figsize=(10, 5))
plt.plot(distances, elevations, 'o', color='red', label='Вузли (вихідні дані)')
plt.plot(xx_full, yy_full, '-', color='tab:blue', label='Кубічний сплайн')
plt.xlabel("Відстань, м")
plt.ylabel("Висота, м")
plt.title("Гладкий профіль маршруту (кубічний сплайн, 21 вузол)")
plt.legend()
plt.grid(True)
plt.savefig("spline_21_nodes.png", dpi=150)
plt.show()

# 7. Порівняння з різною кількістю вузлів
def subsample(x_full, y_full, k):
    """Вибирає k вузлів рівномірно з повного набору"""
    idx = np.round(np.linspace(0, len(x_full) - 1, k)).astype(int)
    x_sub = [x_full[i] for i in idx]
    y_sub = [y_full[i] for i in idx]
    return x_sub, y_sub

node_counts = [10, 15, 20]
colors = ['tab:green', 'tab:orange', 'tab:purple']

plt.figure(figsize=(10, 6))
plt.plot(distances, elevations, 'o', color='red', markersize=4, label='Повний набір вузлів (21)')

for k, col in zip(node_counts, colors):
    xs, ys = subsample(distances, elevations, k)
    a_k, b_k, c_k, d_k, h_k = compute_spline_coeffs(xs, ys)
    xx_k = np.linspace(xs[0], xs[-1], 400)
    yy_k = [spline_value(xs, a_k, b_k, c_k, d_k, xv) for xv in xx_k]
    plt.plot(xx_k, yy_k, '-', color=col, label=f'Сплайн, {k} вузлів')

plt.xlabel("Відстань, м")
plt.ylabel("Висота, м")
plt.title("Порівняння сплайнів з різною кількістю вузлів")
plt.legend()
plt.grid(True)
plt.savefig("comparison_nodes.png", dpi=150)
plt.show()

# 8. Графік похибки (на прикладі 10 вузлів)
xs10, ys10 = subsample(distances, elevations, 10)
a10, b10, c10, d10, h10 = compute_spline_coeffs(xs10, ys10)

y_approx = [spline_value(xs10, a10, b10, c10, d10, xv) for xv in xx_full]
y_exact = yy_full  # сплайн на повному наборі вважаємо "точним" еталоном

error = [abs(e - a) for e, a in zip(y_exact, y_approx)]

fig, axs = plt.subplots(2, 1, figsize=(10, 8))

axs[0].plot(xx_full, y_exact, label="Еталон (21 вузол)", color='tab:blue')
axs[0].plot(xx_full, y_approx, label="Наближення (10 вузлів)", color='tab:orange', linestyle='--')
axs[0].set_ylabel("Висота, м")
axs[0].set_title("Порівняння еталонної та наближеної функції")
axs[0].legend()
axs[0].grid(True)

axs[1].plot(xx_full, error, color='tab:red')
axs[1].set_xlabel("Відстань, м")
axs[1].set_ylabel("Похибка, м")
axs[1].set_title("Похибка наближення")
axs[1].grid(True)

plt.tight_layout()
plt.savefig("error_plot.png", dpi=150)
plt.show()

print("\nМаксимальна похибка (10 вузлів):", max(error))
print("Середня похибка (10 вузлів):", np.mean(error))

# ДОДАТКОВО: характеристики маршруту
print("\n--- Характеристики маршруту ---")
print("Загальна довжина маршруту (м):", round(distances[-1], 2))

total_ascent = sum(max(elevations[i] - elevations[i-1], 0) for i in range(1, n))
total_descent = sum(max(elevations[i-1] - elevations[i], 0) for i in range(1, n))
print("Сумарний набір висоти (м):", round(total_ascent, 2))
print("Сумарний спуск (м):", round(total_descent, 2))

# Аналіз градієнта
grad_full = np.gradient(yy_full, xx_full) * 100
print("Максимальний підйом (%):", round(np.max(grad_full), 2))
print("Максимальний спуск (%):", round(np.min(grad_full), 2))
print("Середній градієнт (%):", round(np.mean(np.abs(grad_full)), 2))

# Механічна енергія підйому
mass = 80
g = 9.81
energy = mass * g * total_ascent
print("Механічна робота (Дж):", round(energy, 2))
print("Механічна робота (кДж):", round(energy / 1000, 2))
print("Енергія (ккал):", round(energy / 4184, 2))