import math
import matplotlib.pyplot as plt

# Перше рівняння x1^2 + x2^2 - 4 = 0: коло радіуса 2
t = [2 * math.pi * i / 400 for i in range(401)]
circle_x = [2 * math.cos(a) for a in t]
circle_y = [2 * math.sin(a) for a in t]

# Друге рівняння e^x1 + x2 - 1 = 0, тобто x2 = 1 - e^x1
xs = [-3 + 5 * i / 400 for i in range(401)]
ys = [1 - math.exp(x) for x in xs]

plt.plot(circle_x, circle_y, label="x1² + x2² - 4 = 0")
plt.plot(xs, ys, label="e^x1 + x2 - 1 = 0")
plt.plot(1.0, -1.5, "ro", label="початкове наближення (1; -1.5)")
plt.axhline(0, color="black", linewidth=0.8)
plt.axvline(0, color="black", linewidth=0.8)
plt.xlim(-3, 2)
plt.ylim(-3, 3)
plt.gca().set_aspect("equal")
plt.grid(True)
plt.xlabel("x1")
plt.ylabel("x2")
plt.title("Графіки рівнянь системи")
plt.legend(loc="lower left", fontsize=8)
plt.savefig("system_plot.png")
print("Графік збережено у system_plot.png")