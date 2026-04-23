from typing import Callable
from dataclasses import dataclass

import numpy as np
from jaxtyping import Float
from utils.numpy import Array

@dataclass
class PSOGenData:
    gen: int
    best_x: Float[Array, "D"]

type PSOGenCallback = Callable[[PSOGenData], None]

SEARCHABLE_PARAMS = ["v_max", "omega", "omega_min", "phi1", "phi2"]

@dataclass
class PSO:
    N: int
    D: int
    gen_max: int

    xl: Float[Array, "D"]
    xu: Float[Array, "D"]
    v_max: float

    omega: float
    omega_min: float
    phi1: float
    phi2: float

    fitness: Callable[[Float[Array, "N D"]], Float[Array, "N"]]

    def start(
        self,
        *,
        on_gen: PSOGenCallback | None = None
    ) -> Float[Array, "D"]:
        N, D = self.N, self.D
        ND = (N, D)

        v: Float[Array, "N D"] = np.random.uniform(-self.v_max, self.v_max, size=ND)
        x: Float[Array, "N D"] = np.random.uniform(self.xl, self.xu, size=ND)
        best_x: Float[Array, "N D"] = np.zeros(ND)
        best_f: Float[Array, "N"] = np.full(N, -np.inf)
        best_x_g: Float[Array, "D"] = np.zeros(D)

        for gen in range(self.gen_max):
            f = self.fitness(x)

            is_better = f > best_f
            best_x[is_better] = x[is_better]
            best_f[is_better] = f[is_better]
            best_x_g = best_x[np.argmax(best_f)]

            alpha = gen / self.gen_max
            omega = self.omega + (self.omega_min - self.omega) * alpha

            v = (
                omega * v
                + self.phi1 * np.random.uniform(size=ND) * (best_x - x)
                + self.phi2 * np.random.uniform(size=ND) * (best_x_g - x)
            )

            v = np.clip(v, -self.v_max, self.v_max)

            x += v
            x = np.clip(x, self.xl, self.xu)

            if on_gen:
                on_gen(PSOGenData(gen=gen, best_x=best_x_g))

        return best_x_g
