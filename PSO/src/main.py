from typing import TypedDict, cast
from jaxtyping import Float
from dataclasses import dataclass
import argparse
import time

import numpy as np
from tqdm import tqdm

from pso import PSO, SEARCHABLE_PARAMS
from cases import PSOCase, PSOCaseDim, CASES
from utils.numpy import FmtArray, Array
from utils.basic import float_range


@dataclass
class PSORunResult:
    best_x: Float[Array, "D"]
    elapsed: float

@dataclass
class PSORunMultiResult:
    best_x: Float[Array, "R D"]
    best_y: Float[Array, "R"]
    best_fitness: Float[Array, "R"]
    elapsed: Float[Array, "R"]

    global_best_x: Float[Array, "D"]
    global_best_y: Float[Array, "D"]
    global_best_fitness: Float[Array, "D"]

@dataclass
class PSORunArgs:
    tol: float
    runs: int
    plot: bool

@dataclass
class PSOSearchArgs:
    tol: float
    runs: int
    plot: bool
    min: float
    max: float
    step: float
    param: str


def build_pso(cased: PSOCaseDim, *, override: dict[str, float] | None = None) -> PSO:
    case, D = cased

    xb = case.bound
    params = dict(
        v_max=xb * 0.233,
        omega=0.920,
        omega_min=0.164,
        phi1=2.307,
        phi2=0.771,
    )

    if override:
        params.update(override)

    if params["omega_min"] > params["omega"]:
        raise ValueError(f"Invalid inertia range: omega_min={params['omega_min']} > omega={params['omega']}")

    return PSO(
        N=20 + 5 * D,
        D=D,
        gen_max=max(1000, 100 * D),
        xl=np.full(D, -xb),
        xu=np.full(D, xb),
        fitness=case.calc_fitness,
        **params,
    )


def run(pso: PSO) -> PSORunResult:
    t_start = time.perf_counter()
    best_x = pso.start()
    elapsed = time.perf_counter() - t_start
    return PSORunResult(best_x=best_x, elapsed=elapsed)


def run_multi(cased: PSOCaseDim, runs: int, pso: PSO, *, desc: str = "Running", is_sub: bool = False) -> PSORunMultiResult:
    case, D = cased

    best_x = np.empty((runs, D))
    elapsed = np.empty(runs)

    for idx in tqdm(range(runs), desc=desc, unit="run", leave=not is_sub):
        res = run(pso)
        best_x[idx] = res.best_x
        elapsed[idx] = res.elapsed

    best_y = case.fn(best_x)
    best_fitness = case.calc_fitness(best_x)
    global_best_idx = np.argmax(best_fitness)

    return PSORunMultiResult(
        best_x=best_x,
        best_y=best_y,
        best_fitness=best_fitness,
        elapsed=elapsed,
        global_best_x=best_x[global_best_idx],
        global_best_y=best_y[global_best_idx],
        global_best_fitness=best_fitness[global_best_idx],
    )


def report(cased: PSOCaseDim, args: PSORunArgs, res: PSORunMultiResult):
    case, D = cased

    tol = args.tol
    runs = args.runs

    global_best_x = res.global_best_x
    global_best_y = res.global_best_y
    global_best_fitness = res.global_best_fitness

    optimal = cased.get_optimal()
    success = case.calc_fitness(res.best_x) + tol >= optimal.fitness
    success_count = np.sum(success)
    accuracy = success_count / runs

    best_info = (
        f"Best $x$: {FmtArray(global_best_x):.3f}\n"
        f"Best $f(x)$: {global_best_y:.3f}\n"
        f"Accuracy: {success_count}/{runs} = {accuracy:.2%}"
    )
    bbox = dict(
        boxstyle="round",
        pad=0.3,
        facecolor="white",
        edgecolor="lightgrey",
        alpha=0.8,
    )

    print(f"Case: {case.name} (D={D})")
    print(f"Global best x: {FmtArray(global_best_x):.3f}")
    print(f"Global best fitness: {global_best_fitness:.6f}")
    print(f"Accuracy: {success_count}/{runs} = {accuracy:.2%}")
    print(f"Mean best fitness: {np.mean(res.best_fitness):.6f} ± {np.std(res.best_fitness):.6f}")
    print(f"Mean elapsed: {np.mean(res.elapsed):.3f}s")

    if not args.plot:
        return

    from utils.plt import plt

    if D == 1:
        xb = case.bound
        dom = np.linspace(-xb, xb, 200)
        x = dom[:, None]
        y = case.fn(x)

        plt.plot(dom, y, zorder=1)
        plt.scatter(
            res.best_x[:, 0],
            res.best_y,
            color="red",
            s=20,
            alpha=0.5,
            zorder=2,
            label=f"PSO best ({runs} runs)",
        )
        plt.scatter(
            optimal.x,
            optimal.y,
            color="black",
            s=70,
            marker="+",
            zorder=3,
            label="Optimal",
        )
        plt.scatter(
            global_best_x,
            global_best_y,
            color="red",
            s=50,
            marker="x",
            zorder=4,
            label="Global best",
        )
        plt.title(f"{case.name} Curve ($D = 1$)")
        plt.xlabel("$x$")
        plt.ylabel("$f(x)$")
        plt.text(
            0.02,
            0.98,
            best_info,
            transform=plt.gca().transAxes,
            ha="left",
            va="top",
            bbox=bbox,
        )
        plt.legend()
        plt.show()

    elif D == 2:
        xb = case.bound
        dom = np.linspace(-xb, xb, 200)
        x1, x2 = np.meshgrid(dom, dom)
        grid = np.stack((x1.ravel(), x2.ravel()), axis=1)
        y = case.fn(grid).reshape(x1.shape)

        fig = plt.figure(figsize=(12, 5))

        ax1 = fig.add_subplot(1, 2, 1, projection="3d", computed_zorder=False)
        ax1.plot_surface(x1, x2, y, cmap="viridis", linewidth=0, alpha=0.2, zorder=1)
        ax1.scatter(
            res.best_x[:, 0],
            res.best_x[:, 1],
            res.best_y,
            color="red",
            s=20,
            alpha=0.5,
            zorder=2,
            label=f"PSO best ({runs} runs)",
        )
        ax1.scatter(
            global_best_x[0],
            global_best_x[1],
            global_best_y,
            color="red",
            s=40,
            marker="x",
            alpha=1.0,
            zorder=3,
            label="Global best",
        )
        ax1.scatter(
            optimal.x[0],
            optimal.x[1],
            optimal.y,
            color="black",
            s=80,
            marker="+",
            alpha=1.0,
            zorder=4,
            label="Optimal",
        )
        ax1.set_title(f"{case.name} Surface ($D = 2$)")
        ax1.set_xlabel("$x_1$")
        ax1.set_ylabel("$x_2$")
        ax1.set_zlabel("$f(x)$")
        ax1.text2D(
            0.02,
            0.98,
            best_info,
            transform=ax1.transAxes,
            ha="left",
            va="top",
            bbox=bbox,
        )
        ax1.legend()

        ax2 = fig.add_subplot(1, 2, 2)
        contour = ax2.contourf(x1, x2, y, levels=40, cmap="viridis")
        ax2.scatter(
            res.best_x[:, 0],
            res.best_x[:, 1],
            color="red",
            s=20,
            alpha=0.5,
            label=f"PSO best ({runs} runs)",
        )
        ax2.scatter(*global_best_x, color="red", s=50, marker="x", label="Global best")
        ax2.scatter(*optimal.x, color="white", linewidth=2, s=85, marker="+")
        ax2.scatter(
            optimal.x[0],
            optimal.x[1],
            color="black",
            s=80,
            marker="+",
            label="Optimal",
        )
        ax2.set_title(f"{case.name} Contour ($D = 2$)")
        ax2.set_xlabel("$x_1$")
        ax2.set_ylabel("$x_2$")
        ax2.legend()
        fig.colorbar(contour, ax=ax2, shrink=0.9)

        fig.tight_layout()
        plt.show()

    else:
        print(f"D={D} is too big to plot")

def search(cased: PSOCaseDim, args: PSOSearchArgs):
    case, D = cased

    runs: int = args.runs
    if runs < 1:
        raise ValueError(f"Invalid runs={runs}; runs must be >= 1")

    tol: float = args.tol
    if tol <= 0:
        raise ValueError(f"Invalid tol={tol}; tol must be > 0")

    values: list[float] = []
    accs: list[float] = []

    best_value: float = 0.0
    best_acc: float = -1.0

    optimal = cased.get_optimal()

    if args.plot:
        from utils.plt import plt

        plt.ion()
        fig, ax = plt.subplots()
        line, = ax.plot([], [], marker="o")
        ax.set_xlabel(args.param)
        ax.set_ylabel("Accuracy")
        ax.set_title(f"Search for {args.param} ({case.name}, $D={D}$)")

    search_desc = f"Searching {args.param}"
    run_desc = "\\ Running".rjust(len(search_desc))

    for value in tqdm(float_range(args.min, args.max, args.step), desc=search_desc, unit="iter"):
        pso = build_pso(cased, override={args.param: value})

        res = run_multi(cased, runs, pso, desc=run_desc, is_sub=True)

        success = np.abs(res.best_fitness - optimal.fitness) <= tol
        acc = float(np.mean(success))

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

    print(f"Best {args.param}: {best_value:.6f} with accuracy {best_acc:.2%}")

    if args.plot:
        plt.ioff()
        plt.show()


def main():
    parser = argparse.ArgumentParser(description="PSO experiment")
    parser.add_argument("case", choices=CASES.keys(), help="Test case to run")
    parser.add_argument("--dim", type=int, help="Dimension of the test function")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Sub commands")

    parser_run = subparsers.add_parser("run", help="Run PSO for one or multiple runs")
    parser_run.add_argument("--runs", type=int, default=1, help="Number of runs to perform")
    parser_run.add_argument("--tol", type=float, default=1e-2, help="Accuracy tolerance")
    parser_run.add_argument("--plot", action="store_true", help="Plot run result")

    parser_search = subparsers.add_parser("search", help="Search for PSO hyper-parameters")
    parser_search.add_argument("--runs", type=int, default=50, help="Runs for each value")
    parser_search.add_argument("--tol", type=float, default=1e-2, help="Accuracy tolerance")
    parser_search.add_argument("--param", choices=SEARCHABLE_PARAMS, required=True)
    parser_search.add_argument("--min", type=float, required=True)
    parser_search.add_argument("--max", type=float, required=True)
    parser_search.add_argument("--step", type=float, required=True)
    parser_search.add_argument("--plot", action="store_true", help="Plot search accuracy")

    args = parser.parse_args()

    case = CASES[args.case]

    if args.dim is None:
        D = case.default_dim
    else:
        D = args.dim
        if not case.validate_dim(D):
            raise ValueError(f"Invalid dimension {D} for case {case.id}")

    cased = PSOCaseDim(case, D)

    match args.command:
        case "run":
            runs: int = args.runs
            if runs < 1:
                raise ValueError(f"Invalid runs={runs}; runs must be >= 1")

            res = run_multi(cased, runs, build_pso(cased))
            report(cased, cast(PSORunArgs, args), res)

        case "search":
            search(cased, cast(PSOSearchArgs, args))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted by user.")
