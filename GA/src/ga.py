from dataclasses import dataclass
from collections.abc import Callable, Iterable
from abc import abstractmethod, ABC
from math import inf

import numpy as np
import numpy.typing as npt

type Chromo = npt.NDArray[np.float64]
type Population = npt.NDArray[np.float64]
type Values = npt.NDArray[np.float64]
type FitnessFnV = Callable[[Population], Values]
type ChromoWithFitness = tuple[Chromo, float]

@dataclass
class GA(ABC):
    pop_size: int
    generations: int
    mutation_rate: float
    crossover_rate: float
    elitism_count: int

    def start(self, *, debug: bool = False, on_generation: Callable[[int, ChromoWithFitness], None] | None = None) -> ChromoWithFitness:
        pop = self.sample(self.pop_size)
        best: ChromoWithFitness = np.zeros(2), -inf

        for gen in range(self.generations):
            fitness_v = self.calc_fitness_v(pop)
            best = self.update_best(best, pop, fitness_v)
            if debug:
                self.print_chromo_with_fitness(str(gen), *best)
            if on_generation:
                on_generation(gen, best)

            elites = self.extract_elites(pop, fitness_v)
            
            pop = self.select(pop, fitness_v)
            pop = self.crossover(pop)
            pop = self.mutate(pop)

            pop = self.inject_elites(pop, elites)

        return best

    def print_chromo_with_fitness(self, prefix: str, chromo: Chromo, fitness: float):
        x1, x2 = chromo
        print(f"{prefix:>6}: fitness = {fitness:<8.4f}, x = ({x1:.4f}, {x2:.4f})")

    @abstractmethod
    def calc_fitness_v(self, pop: Population) -> Values:
        raise NotImplementedError()

    @abstractmethod
    def sample(self, size: int) -> Population:
        raise NotImplementedError()

    @abstractmethod
    def select(self, pop: Population, fitness_v: Values) -> Population:
        raise NotImplementedError()

    @abstractmethod
    def crossover(self, pop: Population) -> Population:
        raise NotImplementedError()

    @abstractmethod
    def mutate(self, pop: Population) -> Population:
        raise NotImplementedError()

    def update_best(self, prev_best: ChromoWithFitness, pop: Population, fitness_v: Values) -> ChromoWithFitness:
        best_idx = np.argmax(fitness_v)
        best_fitness = fitness_v[best_idx]
        best_value = pop[best_idx]

        _, prev_best_fitness = prev_best
        if best_fitness > prev_best_fitness:
            return best_value, best_fitness
        else:
            return prev_best

    def extract_elites(self, pop: Population, fitness_v: Values) -> Population:
        if self.elitism_count <= 0:
            return np.empty((0, pop.shape[1]), dtype=pop.dtype)

        elite_idx = np.argpartition(fitness_v, -self.elitism_count)[-self.elitism_count:]
        return pop[elite_idx].copy()

    def inject_elites(self, pop: Population, elites: Population) -> Population:
        replace_idx = np.random.choice(self.pop_size, size=self.elitism_count, replace=False)
        pop[replace_idx] = elites
        return pop
