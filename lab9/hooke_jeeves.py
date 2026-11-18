import math

Q = 2           # коефіцієнт зменшення кроку
P = 2           # коефіцієнт пошуку по зразку
EPS1 = 1e-8     # критерій закінчення за кроком
EPS2 = 1e-12    # критерій закінчення за значенням функції
MAX_ITER = 100000


def f1(x):
    """Перше рівняння системи: x1^2 + x2^2 - 4 = 0."""
    return x[0] ** 2 + x[1] ** 2 - 4


def f2(x):
    """Друге рівняння системи: e^x1 + x2 - 1 = 0."""
    return math.exp(x[0]) + x[1] - 1


def phi(x):
    """Цільова функція Ф(X) = f1^2 + f2^2."""
    return f1(x) ** 2 + f2(x) ** 2


def rosenbrock(x):
    """Функція Розенброка: f(X) = 100(x1^2 - x2)^2 + (x1 - 1)^2."""
    return 100 * (x[0] ** 2 - x[1]) ** 2 + (x[0] - 1) ** 2


def explore(func, base, step, reduce_step):
    """Досліджуючий пошук навколо базисної точки (по кожній координаті)."""
    x = base[:]
    fx = func(x)
    for i in range(len(x)):
        while True:
            x[i] = base[i] + step[i]            # пробує крок вперед
            if func(x) < fx:
                break
            x[i] = base[i] - step[i]            # пробує крок назад
            if func(x) < fx:
                break
            x[i] = base[i]                      # обидва кроки невдалі
            if not reduce_step:
                break
            step[i] /= Q                        # зменшує крок по x_i
            if step[i] < EPS1:
                break
        fx = func(x)
    return x


def hooke_jeeves(func, x0, dx):
    """Метод Хука-Дживса. Повертає точку мінімуму та траєкторію спуску."""
    step = dx[:]
    X0 = x0[:]
    trajectory = [X0[:]]
    for _ in range(MAX_ITER):
        # Досліджуючий пошук 
        X1 = explore(func, X0, step, reduce_step=True)
        if X1 == X0:                                    # п. 5: нова точка не знайдена
            return X0, trajectory
        trajectory.append(X1[:])
        if (math.sqrt(sum(s ** 2 for s in step)) < EPS1
                and abs(func(X1) - func(X0)) < EPS2):   # п. 5: умови закінчення
            return X1, trajectory
        # Пошук по зразку 
        while True:
            Xp = [X1[i] + P * (X1[i] - X0[i]) for i in range(len(X1))]
            X2 = explore(func, Xp, step, reduce_step=False)
            if func(X2) < func(X1):
                X0, X1 = X1, X2
                trajectory.append(X1[:])
            else:
                X0 = X1
                break
    return X0, trajectory


def write_trajectory(filename, func, trajectory):
    """Запис координат точок траєкторії спуску у файл."""
    with open(filename, "w") as f:
        f.write(f"{'k':>5} {'x1':>20} {'x2':>20} {'F(X)':>14}\n")
        for k, x in enumerate(trajectory):
            f.write(f"{k:>5} {x[0]:>20.12f} {x[1]:>20.12f} {func(x):>14.4e}\n")


if __name__ == "__main__":
    # Тестування на функції Розенброка
    x_min, traj = hooke_jeeves(rosenbrock, [-1.2, 0.0], [0.5, 0.5])
    write_trajectory("trajectory_rosenbrock.txt", rosenbrock, traj)
    print("Тест: функція Розенброка, X0 = (-1.2; 0.0)")
    print(f"  Точка мінімуму: x1 = {x_min[0]:.10f}, x2 = {x_min[1]:.10f}")
    print(f"  f(X) = {rosenbrock(x_min):.3e}")
    print(f"  Кількість кроків на траєкторії: {len(traj) - 1}")

    # Розв'язок системи нелінійних рівнянь
    x_sol, traj = hooke_jeeves(phi, [1.0, -1.5], [0.5, 0.5])
    write_trajectory("trajectory_system.txt", phi, traj)
    print("\nСистема рівнянь, X0 = (1.0; -1.5)")
    print(f"  Розв'язок: x1 = {x_sol[0]:.10f}, x2 = {x_sol[1]:.10f}")
    print(f"  f1(X) = {f1(x_sol):.3e}, f2(X) = {f2(x_sol):.3e}")
    print(f"  Ф(X) = {phi(x_sol):.3e}")
    print(f"  Кількість кроків на траєкторії: {len(traj) - 1}")