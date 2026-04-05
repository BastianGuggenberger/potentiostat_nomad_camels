import numpy as np
import random


def cvmeasurement_stat(U):
    """
    - starker Anstieg links
    - flacher Mittelteil
    - starker Anstieg rechts
    - feste Erhebung in der Mitte (1/6 vom Maximum)
    - optionaler kleiner zufälliger Hügel (40%)
    - großes gaußsches Rauschen
    """

    # Basisform
    I_base = (
        0.9 / (1 + np.exp(-(U + 0.15) / 0.03)) +
        1.8 / (1 + np.exp(-(U - 0.52) / 0.05)) +
        0.05 * U
    )

    # Approx. Maximum bei U ≈ 0.6
    I_max = (
        0.9 / (1 + np.exp(-(0.6 + 0.15) / 0.03)) +
        1.8 / (1 + np.exp(-(0.6 - 0.52) / 0.05)) +
        0.05 * 0.6
    )

    # Mittlere feste Erhebung
    middle_center = 0.2
    middle_width = 0.06
    middle_height = I_max / 10.5

    I = I_base + middle_height * np.exp(-(U - middle_center)**2 / (2 * middle_width**2))



    # Großes gaußsches Rauschen
    noise_sigma = 0.035 * I_max   # 15% vom Maximalwert → deutlich sichtbar
    I += np.random.normal(0, noise_sigma)

    return I

import matplotlib.pyplot as plt
U_vec = [-0.2 + 0.001 *i for i in range(800)]
I_vec = [cvmeasurement_stat(U) for U in U_vec]

plt.plot(U_vec,I_vec)
plt.savefig("u_i.png")