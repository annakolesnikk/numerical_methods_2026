import matplotlib.pyplot as plt
import methods as m

# ---------- Вхідні параметри ----------
FUNC = "50*exp(-0.1*t) + 5*sin(t)"   # модель вологості ґрунту M(t)
X0 = 1.0                              # точка диференціювання
K_MIN, K_MAX = -20, 3                 # діапазон кроків 10^-20 ... 10^3
H = 1e-3                              # базовий крок (п.3)
Q = 2                                 # коефіцієнт зміни кроку (h, 2h, 4h)
P = 2                                 # теоретичний порядок центральної різниці

# ---------- 1. Аналітична похідна ----------
f, df, expr, d_expr = m.make_functions(FUNC)
exact = df(X0)
print("=== 1. Аналітичний розв'язок ===")
print(f"M(t)  = {expr}")
print(f"M'(t) = {d_expr}")
print(f"y'(x0) = M'({X0}) = {exact:.15f}\n")

# ---------- 2. Залежність похибки від кроку ----------
hs = m.step_grid(K_MIN, K_MAX)
errors, h0, R0 = m.error_study(f, X0, exact, hs)
print("=== 2. Залежність похибки від кроку h ===")
print(f"{'h':>10} | {'R(h)':>12}")
for h, r in zip(hs[::9], errors[::9]):          # друк по одному кроку на декаду
    print(f"{h:>10.0e} | {r:>12.4e}")
print(f"Оптимальний крок h0 = {h0:.0e}")
print(f"Досягнута точність R0 = {R0:.6e}\n")

plt.loglog(hs, errors, label="R(h)")
plt.scatter([h0], [R0], color="red", zorder=5, label=f"h0 = {h0:.0e}")
plt.xlabel("h")
plt.ylabel("R(h)")
plt.title("Залежність похибки від кроку h")
plt.grid(True, which="both", alpha=0.4)
plt.legend()
plt.show()

# ---------- 3–4. Похідна на сітках h та 2h ----------
y_h = m.central_diff(f, X0, H)
y_2h = m.central_diff(f, X0, Q * H)
print(f"=== 4. Обчислення на сітках h = {H} та {Q}h ===")
print(f"y'(h)  = {y_h:.15f}")
print(f"y'(2h) = {y_2h:.15f}\n")

# ---------- 5. Похибка при кроці h ----------
R1 = m.abs_error(y_h, exact)
print("=== 5. Похибка при кроці h ===")
print(f"R1 = {R1:.6e}\n")

# ---------- 6. Метод Рунге-Ромберга ----------
y_R = m.runge_romberg(y_h, y_2h, Q, P)
R2 = m.abs_error(y_R, exact)
print("=== 6. Метод Рунге-Ромберга ===")
print(f"y'R = {y_R:.15f}")
print(f"R2 = {R2:.6e}")
print(f"Похибка зменшилась у {R1 / R2:.2e} разів\n")

# ---------- 7. Метод Ейткена ----------
y_4h = m.central_diff(f, X0, Q**2 * H)
y_E = m.aitken(y_h, y_2h, y_4h)
p_est = m.aitken_order(y_h, y_2h, y_4h, Q)
R3 = m.abs_error(y_E, exact)
print("=== 7. Метод Ейткена ===")
print(f"y'(h)  = {y_h:.15f}")
print(f"y'(2h) = {y_2h:.15f}")
print(f"y'(4h) = {y_4h:.15f}")
print(f"y'E = {y_E:.15f}")
print(f"Порядок точності p = {p_est:.6f}")
print(f"R3 = {R3:.6e}")
print(f"Похибка зменшилась у {R1 / R3:.2e} разів")