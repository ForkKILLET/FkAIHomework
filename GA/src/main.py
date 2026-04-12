from numpy.matlib import ma
import numpy as np

from ga import GA, Population, Values

x_min, x_max = -5.12, 5.12
tournament_size = 5
mutate_noise_std = 0.1

class RasGA(GA):
    def ras_v(self, pop: Population) -> Values:
        return 20 + np.sum(pop**2 - 10 * np.cos(2 * np.pi * pop), axis=1)

    def calc_fitness_v(self, pop: Population) -> Values:
        return 100 - self.ras_v(pop)

    def init_pop(self) -> Population:
        return np.random.uniform(x_min, x_max, (self.pop_size, 2))

    def select(self, pop: Population, fitness_v: Values) -> Population:
        candidates = np.random.randint(0, self.pop_size, size=(self.pop_size, tournament_size))
        best_idx = np.argmax(fitness_v[candidates], axis=1)
        selected_idx = candidates[np.arange(self.pop_size), best_idx]
        new_pop = pop[selected_idx]
        return new_pop

    def crossover(self, pop: Population) -> Population:
        idx = np.random.permutation(self.pop_size)
        parents1 = pop
        parents2 = pop[idx]

        alpha = np.random.rand(self.pop_size, 1)
        offspring = alpha * parents1 + (1 - alpha) * parents2
        offspring = np.clip(offspring, x_min, x_max)

        new_pop = pop.copy()
        mask = np.random.rand(self.pop_size) < self.crossover_rate
        new_pop[mask] = offspring[mask]
        return new_pop

    def mutate(self, pop: Population) -> Population:
        noise = np.random.normal(0, mutate_noise_std, pop.shape)
        mask = np.random.rand(*pop.shape) < self.mutation_rate
        mutated_pop = pop + mask * noise
        mutated_pop = np.clip(mutated_pop, x_min, x_max)
        return mutated_pop

if __name__ == "__main__":
    ga = RasGA(
        pop_size=500,
        generations=200,
        mutation_rate=0.1,
        crossover_rate=0.7,
        elitism_count=5,
        debug=True,
    )
    best = ga.start()
    ga.print_chromosome_with_fitness("Best", *best)