import matplotlib.pyplot as plt
import numpy as np
import methods as m

# ---------- Вхідні параметри ----------
FUNC = "50 + 20*sin(pi*x/12) + 5*exp(-0.2*(x-12)**2)"  # навантаження на сервер
A, B = 0, 24                 # інтервал часу
N_MIN, N_MAX = 10, 1000      # діапазон числа розбиттів
EPS = 1e-12                  # задана точність
P = 4                        # порядок складової формули Сімпсона
Q = 2                        # коефіцієнт зміни кроку
DELTAS = [10.0**k for k in range(-1, -13, -1)]  # параметри δ для адаптивного алгоритму

# ---------- 2. Точне значення ----------
f, expr, x = m.make_function(FUNC)
I0 = m.exact_integral(expr, x, A, B)
print("=== 2. Точне значення ===")
print(f"f(x) = {expr}")
print(f"I0 = {I0:.15f}\n")

# ---------- 3. Метод Сімпсона ----------
print("=== 3. Метод Сімпсона ===")
print(f"I({N_MIN}) = {m.simpson(f, A, B, N_MIN):.15f}\n")

# ---------- 4. Залежність похибки від N ----------
ns = np.arange(N_MIN, N_MAX + 1, 2)          # тільки парні N
errors = [m.abs_error(m.simpson(f, A, B, n), I0) for n in ns]
n_opt = m.find_n_opt(errors, ns, EPS)
if n_opt is None:
    raise SystemExit(f"Точність {EPS} не досягнута при N <= {N_MAX}")
print("=== 4. Залежність похибки від N ===")
for n, e in zip(ns, errors):
    if n > n_opt:                            # друк до N_opt включно
        break
    print(f"N = {n:4d} | eps = {e:.4e}")
eps_opt = m.abs_error(m.simpson(f, A, B, n_opt), I0)
print(f"N_opt = {n_opt}")
print(f"epsopt = {eps_opt:.4e}\n")

plt.semilogy(ns, errors)
plt.axhline(EPS, color="gray", ls="--", label=f"ε = {EPS:.0e}")
plt.scatter([n_opt], [eps_opt], color="red", zorder=5, label=f"N_opt = {n_opt}")
plt.xlabel("N")
plt.ylabel("ε(N)")
plt.title("Залежність похибки методу Сімпсона від N")
plt.grid(True, which="both", alpha=0.4)
plt.legend()
plt.show()

# ---------- 5. Похибка при N0 ----------
N0 = m.choose_n0(n_opt)
I_N0 = m.simpson(f, A, B, N0)
eps0 = m.abs_error(I_N0, I0)
print("=== 5. Похибка при N0 ===")
print(f"N0 = {N0}")
print(f"I(N0) = {I_N0:.15f}")
print(f"eps0 = {eps0:.4e}\n")

# ---------- 6. Метод Рунге-Ромберга ----------
I_N0_2 = m.simpson(f, A, B, N0 // Q)
I_R = m.runge_romberg(I_N0, I_N0_2, Q, P)
epsR = m.abs_error(I_R, I0)
print("=== 6. Метод Рунге-Ромберга ===")
print(f"I(N0/2) = {I_N0_2:.15f}")
print(f"I_R = {I_R:.15f}")
print(f"epsR = {epsR:.4e}\n")

# ---------- 7. Метод Ейткена ----------
I_N0_4 = m.simpson(f, A, B, N0 // Q**2)
I_E = m.aitken(I_N0, I_N0_2, I_N0_4)
p_est = m.aitken_order(I_N0, I_N0_2, I_N0_4, Q)
epsE = m.abs_error(I_E, I0)
print("=== 7. Метод Ейткена ===")
print(f"I(N0)   = {I_N0:.15f}")
print(f"I(N0/2) = {I_N0_2:.15f}")
print(f"I(N0/4) = {I_N0_4:.15f}")
print(f"I_E = {I_E:.15f}")
print(f"p = {p_est:.6f}")
print(f"epsE = {epsE:.4e}\n")

# ---------- 8. Порівняння похибок ----------
print("=== 8. Порівняння похибок ===")
print(f"Сімпсон (N0)   : {eps0:.4e}")
print(f"Рунге-Ромберг  : {epsR:.4e}")
print(f"Ейткен         : {epsE:.4e}\n")

# ---------- 9. Адаптивний алгоритм ----------
print("=== 9. Адаптивний алгоритм ===")
print(f"{'δ':>8} | {'I':>20} | {'ε':>10} | {'к-сть f':>7}")
res = [m.adaptive_simpson(f, A, B, d) for d in DELTAS]
eps_ad = [m.abs_error(i, I0) for i, _ in res]
calls = [c for _, c in res]
for d, (i, c), e in zip(DELTAS, res, eps_ad):
    print(f"{d:>8.0e} | {i:>20.15f} | {e:>10.4e} | {c:>7d}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
ax1.loglog(DELTAS, eps_ad, "o-")
ax1.set_xlabel("δ")
ax1.set_ylabel("ε")
ax1.set_title("Похибка від δ")
ax1.invert_xaxis()
ax1.grid(True, which="both", alpha=0.4)
ax2.semilogx(DELTAS, calls, "o-")
ax2.set_xlabel("δ")
ax2.set_ylabel("Кількість обчислень f")
ax2.set_title("Кількість обчислень f від δ")
ax2.invert_xaxis()
ax2.grid(True, which="both", alpha=0.4)
plt.tight_layout()
plt.show()