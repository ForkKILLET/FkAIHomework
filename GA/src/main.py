from dataclasses import dataclass
import argparse
import numpy as np
from utils import unzip2, partition

from ga import GA, Chromosome, ChromosomeWithFitness, Population, Values

eps = 1e-2
x_min, x_max = -5.12, 5.12

def ras_v(pop: Population) -> Values:
    return 20 + np.sum(pop**2 - 10 * np.cos(2 * np.pi * pop), axis=1)

@dataclass
class RasGA(GA):
    tournament_size: int
    mutate_noise_std: float

    def calc_fitness_v(self, pop: Population) -> Values:
        return - ras_v(pop)

    def sample(self, size: int) -> Population:
        return np.random.uniform(x_min, x_max, (size, 2))

    def select(self, pop: Population, fitness_v: Values) -> Population:
        candidates = np.random.randint(0, self.pop_size, size=(self.pop_size, self.tournament_size))
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
        noise = np.random.normal(0, self.mutate_noise_std, pop.shape)
        mask = np.random.rand(*pop.shape) < self.mutation_rate
        mutated_pop = pop + mask * noise
        mutated_pop = np.clip(mutated_pop, x_min, x_max)
        return mutated_pop

if __name__ == "__main__":
    ga = RasGA(
        pop_size=500,
        generations=50,
        mutation_rate=0.1,
        crossover_rate=0.9,
        elitism_count=3,
        tournament_size=3,
        mutate_noise_std=0.1,
    )

    parser = argparse.ArgumentParser(description="Rastrigin GA experiment")
    subparsers = parser.add_subparsers(dest="command")

    parser_run = subparsers.add_parser("run", help="Run the GA and print the best solution")
    parser_run.add_argument("--debug", action="store_true", help="Print debug information for each generation")
    parser_run.add_argument("--plot", action="store_true", help="Plot the generation progress")

    parser_pass = subparsers.add_parser("pass", help="Run multiple times and report pass rate")
    parser_pass.add_argument("--runs", type=int, default=100, help="Number of runs to perform")
    parser_pass.add_argument("--plot", action="store_true", help="Plot the distribution of best solutions")

    args = parser.parse_args()

    match args.command:
        case "run":
            progress = []
            def on_generation(gen, best):
                _, fitness = best
                progress.append((gen, fitness))

            best = ga.start(debug=args.debug, on_generation=on_generation)
            ga.print_chromosome_with_fitness("Best", *best)

            if args.plot:
                from plt import plt

                gens, fitnesses = zip(*progress)

                plt.plot(gens, fitnesses, label="Fitness")
                plt.xlabel("Generation")
                plt.ylabel("Fitness")
                plt.title("Fitness Progress")
                plt.legend()
                plt.grid()
                plt.show()

        case "pass":
            type Point = tuple[float, float]

            def is_passed(x: Point) -> bool:
                x1, x2 = x
                return abs(x1) < eps and abs(x2) < eps

            def extract_point(chromo_with_fitness: ChromosomeWithFitness) -> Point:
                x, _ = chromo_with_fitness
                return tuple(x)

            total_count: int = args.runs
            xs = (extract_point(ga.start()) for _ in range(total_count))
            not_passed_xs, passed_xs = (list(xs) for xs in partition(is_passed, xs))
            passed_count = len(passed_xs)
            print(f"Pass: {passed_count}/{total_count} = {passed_count/total_count:.2%}")

            if args.plot:
                from plt import plt

                plt.scatter(*unzip2(passed_xs), alpha=0.5, color="blue")
                plt.scatter(*unzip2(not_passed_xs), alpha=0.5, color="red")

                plt.xlabel("x1")
                plt.ylabel("x2")
                plt.title("Distribution of Best Solutions")
                plt.grid()
                plt.show()
