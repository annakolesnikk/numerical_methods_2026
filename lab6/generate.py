import random

N = 100          # розмірність матриці
X_VALUE = 2.5    # заданий розв'язок: усі x_i = 2.5


def generate_matrix(n):
    """Генерує випадкову матрицю n x n з елементами в [-1, 1]."""
    return [[random.uniform(-1, 1) for _ in range(n)] for _ in range(n)]


def compute_b(A, x):
    """Обчислює вектор вільних членів b_i = sum(a_ij * x_j)."""
    n = len(A)
    return [sum(A[i][j] * x[j] for j in range(n)) for i in range(n)]


def write_matrix(filename, A):
    with open(filename, "w") as f:
        for row in A:
            f.write(" ".join(repr(v) for v in row) + "\n")


def write_vector(filename, v):
    with open(filename, "w") as f:
        for val in v:
            f.write(repr(val) + "\n")


if __name__ == "__main__":
    A = generate_matrix(N)
    x = [X_VALUE] * N
    B = compute_b(A, x)

    write_matrix("matrix_A.txt", A)
    write_vector("vector_B.txt", B)
    print(f"Матрицю A ({N}x{N}) записано у matrix_A.txt")
    print("Вектор B записано у vector_B.txt")