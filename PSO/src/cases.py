from __future__ import annotations
from typing import Literal, NamedTuple
from matplotlib.pylab import axis
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from jaxtyping import Float

from pso import Float, Array

def test(x: Float[Array, "N 1"]) -> Float[Array, "N"]:
    return np.sum(2.1 * (1 - x + 2 * x**2) * np.exp(-x**2 / 2), axis=1)

def test_fitness(x: Float[Array, "N 1"]) -> Float[Array, "N"]:
    return test(x)

def ackley(x: Float[Array, "N D"]) -> Float[Array, "N"]:
    return (
        - 20 * np.exp(-0.2 * np.sqrt(np.mean(x**2, axis=1)))
        - np.exp(np.mean(np.cos(2 * np.pi * x), axis=1))
        + 20 + np.e
    )

def ackley_fitness(x: Float[Array, "N D"]) -> Float[Array, "N"]:
    return -ackley(x)

def griewank(x: Float[Array, "N D"]) -> Float[Array, "N"]:
    _, D = x.shape
    i = np.arange(1, D + 1)
    return np.sum(x**2, axis=1) / 4000 - np.prod(np.cos(x / np.sqrt(i)), axis=1) + 1

def griewank_fitness(x: Float[Array, "N D"]) -> Float[Array, "N"]:
    return -griewank(x)


@dataclass
class PSOOptimal:
    x: Float[Array, "D"]
    y: float
    fitness: float

@dataclass
class PSOCase:
    id: str
    name: str
    fn: Callable[[Float[Array, "N D"]], Float[Array, "N"]]
    calc_fitness: Callable[[Float[Array, "N D"]], Float[Array, "N"]]
    default_dim: int
    validate_dim: Callable[[int], bool]
    bound: float
    calc_optimal: Callable[[int], Float[Array, "D"]]


class PSOCaseDim(NamedTuple):
    case: PSOCase
    D: int

    def get_optimal(self) -> PSOOptimal:
        x = self.case.calc_optimal(self.D)
        y = self.case.fn(x[None, :])[0]
        fitness = self.case.calc_fitness(x[None, :])[0]
        return PSOOptimal(x=x, y=y, fitness=fitness)

CASES = dict[str, PSOCase](
    test=PSOCase(
        id="test",
        name="Test Function",
        fn=test,
        calc_fitness=test_fitness,
        default_dim=1,
        validate_dim=lambda D: D == 1,
        bound=5.0,
        calc_optimal=lambda _D: np.array([-1.162]),
    ),
    ackley=PSOCase(
        id="ackley",
        name="Ackley",
        fn=ackley,
        calc_fitness=ackley_fitness,
        default_dim=2,
        validate_dim=lambda D: D >= 2,
        bound=50.0,
        calc_optimal=lambda D: np.full(D, 0.0),
    ),
    griewank=PSOCase(
        id="griewank",
        name="Griewank",
        fn=griewank,
        calc_fitness=griewank_fitness,
        default_dim=2,
        validate_dim=lambda D: D >= 2,
        bound=50.0,
        calc_optimal=lambda D: np.full(D, 0.0),
    ),
)