EPS0 = 1e-14        
MAX_ITER = 10000    


def read_matrix(filename):
    """Зчитування матриці A з текстового файлу."""
    with open(filename) as f:
        return [[float(v) for v in line.split()] for line in f if line.strip()]


def read_vector(filename):
    """Зчитування вектора B з текстового файлу."""
    with open(filename) as f:
        return [float(line) for line in f if line.strip()]


def mat_vec(A, x):
    """Добуток матриці на вектор."""
    return [sum(a * b for a, b in zip(row, x)) for row in A]


def vector_norm(v):
    """Норма вектора: максимум модулів елементів."""
    return max(abs(t) for t in v)


def matrix_norm(A):
    """Норма матриці: максимальна сума модулів елементів рядка."""
    return max(sum(abs(a) for a in row) for row in A)


def is_done(A, B, x_new, x_old):
    """Умови закінчення: ||X(k+1) - X(k)|| < eps та ||AX(k+1) - B|| <= eps."""
    diff = vector_norm([a - b for a, b in zip(x_new, x_old)])
    residual = vector_norm([ax - b for ax, b in zip(mat_vec(A, x_new), B)])
    return diff < EPS0 and residual <= EPS0


def simple_iteration(A, B, x0):
    """Метод простої ітерації: x_i(k+1) = x_i(k) - tau * (sum(a_ij * x_j(k)) - b_i)."""
    n = len(B)
    tau = 1 / matrix_norm(A)          # 0 < tau < 2 / ||A||
    x = x0[:]
    for k in range(1, MAX_ITER + 1):
        Ax = mat_vec(A, x)
        x_new = [x[i] - tau * (Ax[i] - B[i]) for i in range(n)]
        if is_done(A, B, x_new, x):
            return x_new, k
        x = x_new
    return x, MAX_ITER


def jacobi(A, B, x0):
    """Метод Якобі: x_i(k+1) = (b_i - sum_{j!=i} a_ij * x_j(k)) / a_ii."""
    n = len(B)
    x = x0[:]
    for k in range(1, MAX_ITER + 1):
        x_new = [0.0] * n
        for i in range(n):
            s = sum(A[i][j] * x[j] for j in range(n) if j != i)
            x_new[i] = (B[i] - s) / A[i][i]
        if is_done(A, B, x_new, x):
            return x_new, k
        x = x_new
    return x, MAX_ITER


def seidel(A, B, x0):
    """Метод Зейделя: для j < i беруться вже нові значення x_j(k+1)."""
    n = len(B)
    x = x0[:]
    for k in range(1, MAX_ITER + 1):
        x_new = x[:]
        for i in range(n):
            s1 = sum(A[i][j] * x_new[j] for j in range(i))         # нові значення
            s2 = sum(A[i][j] * x[j] for j in range(i + 1, n))      # старі значення
            x_new[i] = (B[i] - s1 - s2) / A[i][i]
        if is_done(A, B, x_new, x):
            return x_new, k
        x = x_new
    return x, MAX_ITER


if __name__ == "__main__":
    A = read_matrix("matrix_A.txt")
    B = read_vector("vector_B.txt")
    n = len(B)

    x0 = [1.0] * n     # початкове наближення x_i(0) = 1.0

    print(f"Норма матриці ||A|| = {matrix_norm(A):.6f}")
    print(f"Параметр tau = 1/||A|| = {1 / matrix_norm(A):.6f}")

    methods = [("Метод простої ітерації", simple_iteration),
               ("Метод Якобі", jacobi),
               ("Метод Зейделя", seidel)]

    for name, method in methods:
        x, iterations = method(A, B, x0)
        eps = vector_norm([ax - b for ax, b in zip(mat_vec(A, x), B)])
        print(f"\n{name}")
        print(f"  Розв'язок (перші 5 елементів): {x[:5]}")
        print(f"  Кількість ітерацій: {iterations}")
        print(f"  Точність eps = ||AX - B|| = {eps:.3e}")