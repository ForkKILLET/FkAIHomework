import argparse

from tqdm import tqdm

from rasga import RasGA, ChromoWithFitness
from utils import unzip2, partition, float_range

type Point = tuple[float, float]

def get_is_passed(eps: float):
    def is_passed(x: Point) -> bool:
        x1, x2 = x
        return abs(x1) < eps and abs(x2) < eps
    return is_passed

def extract_point(chromo_with_fitness: ChromoWithFitness) -> Point:
    x, _ = chromo_with_fitness
    return tuple(x)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rastrigin GA experiment")
    subparsers = parser.add_subparsers(dest="command", help="Sub commands")

    parser_run = subparsers.add_parser("run", help="Run the GA and print the best solution")
    parser_run.add_argument("--debug", action="store_true", help="Print debug information for each generation")
    parser_run.add_argument("--plot", action="store_true", help="Plot the generation progress")

    parser_pass = subparsers.add_parser("pass", help="Run multiple times and report pass rate")
    parser_pass.add_argument("--runs", type=int, default=100, help="Number of runs to perform")
    parser_pass.add_argument("--plot", action="store_true", help="Plot the distribution of best solutions")
    parser_pass.add_argument("--eps", type=float, default=1e-3, help="Epsilon threshold for passing" )

    parser_search = subparsers.add_parser("search", help="Search for good parameters")
    searchable_params = ["mutation_rate", "crossover_rate", "sbx_eta", "mutate_noise_std"]
    parser_search.add_argument("--param", choices=searchable_params, required=True, help="Parameter to search")
    parser_search.add_argument("--min", type=float, required=True, help="Minimum value of the parameter")
    parser_search.add_argument("--max", type=float, required=True, help="Maximum value of the parameter")
    parser_search.add_argument("--step", type=float, required=True, help="Step size for the parameter")
    parser_search.add_argument("--runs", type=int, default=100, help="Number of runs to perform for each search")
    parser_search.add_argument("--eps", type=float, default=1e-3, help="Epsilon threshold for passing" )
    parser_search.add_argument("--plot", action="store_true", help="Plot the search results")

    args = parser.parse_args()

    try:
        match args.command:
            case "run":
                ga = RasGA.default()

                progress = []
                def on_generation(gen, best):
                    _, fitness = best
                    progress.append((gen, fitness))

                best = ga.start(debug=args.debug, on_generation=on_generation)
                ga.print_chromo_with_fitness("Best", *best)

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
                ga = RasGA.default()

                runs: int = args.runs
                eps: float = args.eps
                is_passed = get_is_passed(eps)

                xs = (extract_point(ga.start()) for _ in tqdm(range(runs), desc="  Runs", leave=False, unit="run"))
                not_passed_xs, passed_xs = (list(xs) for xs in partition(is_passed, xs))
                passed_runs = len(passed_xs)
                print(f"Pass: {passed_runs}/{runs} = {passed_runs / runs:.2%}")

                if args.plot:
                    from plt import plt

                    plt.scatter(*unzip2(passed_xs), alpha=0.5, color="blue")
                    plt.scatter(*unzip2(not_passed_xs), alpha=0.5, color="red")

                    plt.xlabel("x1")
                    plt.ylabel("x2")
                    plt.title("Distribution of Best Solutions")
                    plt.grid()
                    plt.show()

            case "search":
                runs: int = args.runs
                eps: float = args.eps
                is_passed = get_is_passed(eps)

                values: list[float] = []
                accs: list[float] = []

                best_value: float = 0.0
                best_acc: float = 0.0

                ga = RasGA.default()

                if args.plot:
                    from plt import plt

                    plt.ion()
                    fig, ax = plt.subplots()
                    line, = ax.plot([], [], marker="o")
                    plt.xlabel(args.param)
                    plt.ylabel("Pass Rate")
                    plt.title(f"Search for {args.param}")

                for value in tqdm(float_range(args.min, args.max, args.step), desc=f"Searching {args.param}", unit="value"):
                    setattr(ga, args.param, value)
                    
                    xs = (extract_point(ga.start()) for _ in tqdm(range(runs), desc=f"\\ Runs at {value:.4f}", leave=False, unit="run"))
                    passed_runs = sum(is_passed(x) for x in xs)
                    acc = passed_runs / runs

                    values.append(value)
                    accs.append(acc)

                    if acc > best_acc:
                        best_value = value
                        best_acc = acc

                    if args.plot:
                        line.set_data(values, accs)
                        ax.relim()
                        ax.autoscale_view()
                        fig.canvas.draw_idle()
                        fig.canvas.flush_events()

                print(f"Best {args.param}: {best_value} with pass rate {best_acc:.2%}")
                if args.plot:
                    plt.ioff()
                    plt.show()

    except KeyboardInterrupt:
        print("Interrupted by user, exiting...")