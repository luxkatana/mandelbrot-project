import numpy as np
import matplotlib.pyplot as plt

MAX_ITERATION: int = 20


def complex_matrix(xmin, xmax, ymin, ymax, pixel_density):
    re = np.linspace(xmin, xmax, int((xmax - xmin) * pixel_density))
    im = np.linspace(ymin, ymax, int((ymax - ymin) * pixel_density))
    return re[np.newaxis, :] + im[:, np.newaxis] * 1j


def is_stable_candidate(c: int):
    # Stable betekent convergeren naar een bepaalde getal
    # Dus lim x->inf zorgt ervoor dat je naar een bepaalde getal gaat
    z = 0
    for _ in range(0, MAX_ITERATION):
        z = z**2 + c
    return abs(z) <= 2


def get_members(complex_matrix):
    mask = is_stable_candidate(complex_matrix)
    return c[mask]


c = complex_matrix(-2, 0.5, -1.5, 1.5, pixel_density=100)
members = get_members(c)

plt.scatter(members.real, members.imag, color="black", marker=",", s=1)
plt.gca().set_aspect("equal")
plt.axis("off")
plt.tight_layout()
plt.show()
