EPS0 = 1e-14       # задана точність
MAX_ITER = 100     # захист від нескінченного циклу


def read_matrix(filename):
    """Зчитування матриці A з текстового файлу."""
    with open(filename) as f:
        return [[float(v) for v in line.split()] for line in f if line.strip()]


def read_vector(filename):
    """Зчитування вектора B з текстового файлу."""
    with open(filename) as f:
        return [float(line) for line in f if line.strip()]


def lu_decomposition(A):
    """Знаходження LU-розкладу: L - нижня трикутна, U - верхня з одиницями на діагоналі."""
    n = len(A)
    L = [[0.0] * n for _ in range(n)]
    U = [[0.0] * n for _ in range(n)]
    for i in range(n):
        U[i][i] = 1.0

    for k in range(n):
        # k-й стовпець матриці L
        for i in range(k, n):
            L[i][k] = A[i][k] - sum(L[i][j] * U[j][k] for j in range(k))
        # k-й рядок матриці U
        for j in range(k + 1, n):
            U[k][j] = (A[k][j] - sum(L[k][p] * U[p][j] for p in range(k))) / L[k][k]
    return L, U


def write_lu(filename, L, U):
    """Запис LU-розкладу матриці A у текстовий файл."""
    with open(filename, "w") as f:
        f.write("Matrix L:\n")
        for row in L:
            f.write(" ".join(f"{v:12.6f}" for v in row) + "\n")
        f.write("\nMatrix U:\n")
        for row in U:
            f.write(" ".join(f"{v:12.6f}" for v in row) + "\n")


def lu_solve(L, U, B):
    """Розв'язок AX = B за допомогою LU-розкладу: спочатку LZ = B, потім UX = Z."""
    n = len(B)
    Z = [0.0] * n
    for k in range(n):
        Z[k] = (B[k] - sum(L[k][j] * Z[j] for j in range(k))) / L[k][k]

    X = [0.0] * n
    for k in range(n - 1, -1, -1):
        X[k] = Z[k] - sum(U[k][j] * X[j] for j in range(k + 1, n))
    return X


def mat_vec(A, x):
    """Добуток матриці на вектор."""
    return [sum(a * b for a, b in zip(row, x)) for row in A]


def vector_norm(v):
    """Норма вектора (максимум модуля елементів)."""
    return max(abs(t) for t in v)


if __name__ == "__main__":
    A = read_matrix("matrix_A.txt")
    B = read_vector("vector_B.txt")

    # LU-розклад
    L, U = lu_decomposition(A)
    write_lu("lu_result.txt", L, U)
    print("LU-розклад записано у lu_result.txt")

    # Розв'язок системи
    X = lu_solve(L, U, B)
    print("\nРозв'язок (перші 5 елементів):", X[:5])

    # Оцінка точності eps = max|sum(a_ij*x_j) - b_i|
    eps = vector_norm([ax - b for ax, b in zip(mat_vec(A, X), B)])
    print(f"Точність знайденого розв'язку eps = {eps:.3e}")

    # Ітераційне уточнення
    iterations = 0
    while iterations < MAX_ITER:
        R = [b - ax for b, ax in zip(B, mat_vec(A, X))]   # R = B - AX(0)
        dX = lu_solve(L, U, R)                             # A*dX = R
        X = [x + d for x, d in zip(X, dX)]                 # X = X(0) + dX
        iterations += 1

        eps = vector_norm([ax - b for ax, b in zip(mat_vec(A, X), B)])
        if vector_norm(dX) <= EPS0 and eps <= EPS0:
            break

    print(f"\nУточнений розв'язок (перші 5 елементів): {X[:5]}")
    print(f"Кількість ітерацій: {iterations}")
    print(f"Точність уточненого розв'язку eps = {eps:.3e}")