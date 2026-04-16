from typing import Literal
from dataclasses import dataclass

import numpy as np

from ga import GA, Chromo, ChromoWithFitness, Population, Values

xl, xu = -5.12, 5.12

def ras_v(pop: Population) -> Values:
    return 20 + np.sum(pop**2 - 10 * np.cos(2 * np.pi * pop), axis=1)

@dataclass
class RasGA(GA):
    tournament_size: int
    mutate_noise_std: float
    sbx_eta: float
    crossover_mode: Literal["linear", "sbx"]

    @classmethod
    def default(cls):
        return RasGA(
            pop_size=100,
            generations=200,
            mutation_rate=0.1,
            crossover_rate=1.0,
            elitism_count=2,
            tournament_size=2,
            sbx_eta=2.72,
            mutate_noise_std=0.7,
            crossover_mode="sbx",
        )

    def calc_fitness_v(self, pop: Population) -> Values:
        return - ras_v(pop)

    def sample(self, size: int) -> Population:
        return np.random.uniform(xl, xu, (size, 2))

    def select(self, pop: Population, fitness_v: Values) -> Population:
        candidates = np.random.randint(0, self.pop_size, size=(self.pop_size, self.tournament_size))
        best_idx = np.argmax(fitness_v[candidates], axis=1)

        selected_idx = candidates[np.arange(self.pop_size), best_idx]
        new_pop = pop[selected_idx]

        return new_pop

    def crossover_linear(self, pop: Population) -> Population:
        idx = np.random.permutation(self.pop_size)
        parents1 = pop
        parents2 = pop[idx]

        alpha = np.random.rand(self.pop_size, 1)
        offspring = alpha * parents1 + (1 - alpha) * parents2
        offspring = np.clip(offspring, xl, xu)

        return offspring

    def crossover_sbx(self, pop: Population) -> Population:
        N, D = pop.shape
        eta = self.sbx_eta

        parents_1 = pop[0::2]
        parents_2 = pop[1::2]
        offspring = pop.copy()

        u = np.random.rand(N // 2, D)
        mask = u <= 0.5
        beta = np.empty_like(u)
        beta[mask] = (2 * u[mask]) ** (1 / (eta + 1))
        beta[~mask] = (1 / (2 * (1 - u[~mask]))) ** (1 / (eta + 1))

        children_1 = 0.5 * ((1 + beta) * parents_1 + (1 - beta) * parents_2)
        children_2 = 0.5 * ((1 - beta) * parents_1 + (1 + beta) * parents_2)

        cross_mask = (np.random.rand(N // 2) < self.crossover_rate)[:, None]
        offspring[0::2] = np.where(cross_mask, children_1, parents_1)
        offspring[1::2] = np.where(cross_mask, children_2, parents_2)

        offspring = np.clip(offspring, xl, xu)

        return offspring

    def crossover(self, pop: Population) -> Population:
        match self.crossover_mode:
            case "linear":
                return self.crossover_linear(pop)
            case "sbx":
                return self.crossover_sbx(pop)

    def mutate(self, pop: Population) -> Population:
        noise = np.random.normal(0, self.mutate_noise_std, pop.shape)
        mask = np.random.rand(*pop.shape) < self.mutation_rate
        mutated_pop = pop + mask * noise
        mutated_pop = np.clip(mutated_pop, xl, xu)
        return mutated_pop
