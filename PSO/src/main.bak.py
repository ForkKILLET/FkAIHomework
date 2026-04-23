
import argparse
import time

from tqdm import tqdm
import numpy as np

from pso import PSO, Array
from cases import CASES
from utils.plt import plt
from utils.numpy import FmtArray

try:
    parser = argparse.ArgumentParser(description="PSO experiment")
    parser.add_argument(
        "case", choices=["test", "ackley", "griewank"], help="Test case to run"
    )
    parser.add_argument("--dim", type=int, help="Dimension of the test function")
    parser.add_argument(
        "--runs", type=int, default=1, help="Number of runs to perform (default: 1)"
    )
    parser.add_argument(
        "--tol", type=float, default=1e-3, help="Accuracy tolerance (default: 1e-3)"
    )
    args = parser.parse_args()

    case_id = args.case
    case = CASES[case_id]

    D: int = args.dim
    if D is None:
        D = case.default_dim
    elif not case.validate_dim(D):
        raise ValueError(f"Invalid dimension {D} for case {case_id}")

    runs: int = args.runs
    if runs < 1:
        raise ValueError(f"Invalid runs={runs}; runs must be >= 1")

    xb: float = case.bound
    xl = np.full(D, -xb)
    xu = np.full(D, xb)

    pso = PSO(
        N=30,
        D=D,
        gen_max=max(1000, 100 * D),

        xl=xl,
        xu=xu,

        v_max=xb * 0.3,
        omega=0.95,
        omega_min=0.35,
        phi1=1.6,
        phi2=1.1,

        fitness=case.calc_fitness,
    )

    actual_best_x = case.calc_optimal(D)
    actual_best_y, = case.fn(actual_best_x[None, :])

    run_best_x = np.empty((runs, D))
    run_best_y = np.empty(runs)
    run_elapsed = np.empty(runs)

    for run_idx in tqdm(range(runs), desc="Running", unit="run"):
        t_start = time.perf_counter()
        best_x = pso.start()
        t_end = time.perf_counter()

        best_y, = case.fn(best_x[None, :])
        run_best_x[run_idx] = best_x
        run_best_y[run_idx] = best_y
        run_elapsed[run_idx] = t_end - t_start

    global_best_idx = np.argmin(run_best_y)
    global_best_x = run_best_x[global_best_idx]
    global_best_y = run_best_y[global_best_idx]

    accuracy_tol = args.tol
    success = np.abs(run_best_y - actual_best_y) <= accuracy_tol
    success_count = int(np.sum(success))
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
        alpha=0.8
    )

    print(f"Case: {case.name} (D={D})")
    print(f"Global best x: {FmtArray(global_best_x):.3f}")
    print(f"Global best f(x): {global_best_y:.6f}")
    print(f"Accuracy: {success_count}/{runs} = {accuracy:.2%}")
    print(f"Mean best f(x): {np.mean(run_best_y):.6f} ± {np.std(run_best_y):.6f}")
    print(f"Mean elapsed: {np.mean(run_elapsed):.3f}s")

    if D == 1:
        dom = np.linspace(-xb, xb, 200)
        x = dom[:, None]
        y = case.fn(x)

        plt.plot(dom, y, zorder=1)
        plt.scatter(
            run_best_x[:, 0],
            run_best_y,
            color="red",
            s=20,
            alpha=0.5,
            zorder=2,
            label=f"PSO best ({runs} runs)",
        )
        plt.scatter(
            actual_best_x,
            actual_best_y,
            color="black",
            s=70,
            marker="+",
            zorder=3,
            label="Actual best",
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
        dom = np.linspace(-xb, xb, 200)
        x1, x2 = np.meshgrid(dom, dom)
        grid = np.stack((x1.ravel(), x2.ravel()), axis=1)
        y = case.fn(grid).reshape(x1.shape)

        fig = plt.figure(figsize=(12, 5))

        ax1 = fig.add_subplot(1, 2, 1, projection="3d", computed_zorder=False)
        ax1.plot_surface(x1, x2, y, cmap="viridis", linewidth=0, alpha=0.2, zorder=1)
        ax1.scatter(
            run_best_x[:, 0],
            run_best_x[:, 1],
            run_best_y,
            color="red",
            s=20,
            alpha=0.5,
            zorder=2,
            label=f"PSO best ({runs} runs)",
        )
        ax1.scatter(
            *global_best_x,
            global_best_y,
            color="red",
            s=40,
            marker="x",
            alpha=1.0,
            zorder=3,
            label="Global best",
        )
        ax1.scatter(
            *actual_best_x,
            actual_best_y,
            color="black",
            s=80,
            marker="+",
            alpha=1.0,
            zorder=4,
            label="Actual best",
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
            run_best_x[:, 0],
            run_best_x[:, 1],
            color="red",
            s=20,
            alpha=0.5,
            label=f"PSO best ({runs} runs)",
        )
        ax2.scatter(*global_best_x, color="red", s=50, marker="x", label="Global best")
        ax2.scatter(*actual_best_x, color="white", linewidth=2, s=85, marker="+")
        ax2.scatter(
            *actual_best_x, color="black", s=80, marker="+", label="Actual best"
        )
        ax2.set_title(f"{case.name} Contour ($D = 2$)")
        ax2.set_xlabel("$x_1$")
        ax2.set_ylabel("$x_2$")
        ax2.legend()
        fig.colorbar(contour, ax=ax2, shrink=0.9)

        fig.tight_layout()

        plt.show()

except KeyboardInterrupt:
    print("Experiment interrupted by user.")
