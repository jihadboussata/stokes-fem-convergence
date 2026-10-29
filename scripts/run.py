"""Run the manufactured-solution mesh study without a graphical session."""
import argparse
import csv
import json
import math
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ERRORS = ("l2_velocity", "h1_velocity", "l2_pressure", "l2_divergence")


def solve(n, element, output, executable="FreeFem++", fields=False, nu=1., penalty=1e-10):
    if n < 2 or element not in ("P1", "P2") or nu <= 0 or penalty <= 0:
        raise ValueError("Invalid solver parameters.")
    executable = shutil.which(executable)
    if executable is None: raise RuntimeError("Install FreeFEM as described in README.")
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    boundary = (8 if element == "P2" else 4) * n
    config = f"int n={n}, boundaryDofs={boundary}; real nu={nu:.17g}, pressurePenalty={penalty:.17g};\n"
    config += f"bool exportFields={str(fields).lower()};\nmacro VelElement {element} // EOM\n"
    (output / "run.edp").write_text(config + (ROOT / "solver/stokes.edp").read_text())
    result = subprocess.run([executable, "-nw", "-v", "0", "run.edp"], cwd=output,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    (output / "solver.log").write_text(result.stdout)
    if result.returncode: raise RuntimeError(f"FreeFEM failed; inspect {output / 'solver.log'}")
    with open(output / "errors.csv") as stream:
        row = {key: float(value) for key, value in next(csv.DictReader(stream)).items()}
    return row


def study(output, meshes=(10,20,40,80), executable="FreeFem++"):
    output = Path(output).resolve()
    if len(meshes) < 2 or any(b <= a for a, b in zip(meshes, meshes[1:])):
        raise ValueError("Supply at least two strictly increasing mesh sizes.")
    rows = []
    for name, element in [("Taylor-Hood P2/P1", "P2"), ("Equal-order P1/P1", "P1")]:
        previous = None
        for n in meshes:
            directory = output / "runs" / f"{element}_n{n}"
            row = solve(n, element, directory, executable, fields=n == meshes[-1])
            row["method"] = name
            for error in ERRORS:
                row[f"rate_{error}"] = (math.log(previous[error] / row[error]) / math.log(previous["h"] / row["h"])) if previous else None
            if n == meshes[-1]: shutil.copy2(directory / "fields.csv", output / f"fields_{element}.csv")
            rows.append(row)
            previous = row
    with open(output / "convergence.csv", "w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    (output / "parameters.json").write_text(json.dumps({"meshes": list(meshes), "viscosity": 1.,
        "pressure_penalty": 1e-10, "quadrature_order": 8,
        "ndof_total_definition": "2 * scalar velocity space dimension + pressure space dimension, including boundary values"}, indent=2) + "\n")
    return rows


def figures(output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import NullFormatter
    import numpy as np
    import pandas as pd
    output = Path(output)
    frame = pd.read_csv(output / "convergence.csv")
    fig, axes = plt.subplots(2, 2, figsize=(9, 7))
    for ax, error, title in zip(axes.flat, ERRORS, ["Velocity L² error", "Velocity H¹ seminorm error", "Pressure L² error", "Divergence L² norm"]):
        for method, group in frame.groupby("method", sort=False):
            ax.loglog(group.h, group[error], "o-", label=method)
        ax.set(xlabel="h = 1/N", ylabel="Error", title=title)
        mesh_sizes = sorted(frame.n.unique(), reverse=True)
        ax.set_xticks([1/n for n in mesh_sizes], [f"1/{int(n)}" for n in mesh_sizes])
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.grid(alpha=.25, which="both"); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(output / "convergence.png", dpi=160); plt.close(fig)
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.7))
    th = pd.read_csv(output / "fields_P2.csv")
    p1 = pd.read_csv(output / "fields_P1.csv")
    speed = np.hypot(th.u1, th.u2)
    for ax, field, z, title in [(axes[0], th, speed, "Taylor–Hood velocity magnitude"),
        (axes[1], th, th.pressure, "Taylor–Hood pressure (mean zero)"),
        (axes[2], p1, p1.pressure, "Equal-order pressure (mean zero)")]:
        plot = ax.tricontourf(field.x, field.y, z, levels=24, cmap="viridis")
        fig.colorbar(plot, ax=ax, fraction=.046)
        ax.set(xlabel="x", ylabel="y", title=title, aspect="equal")
    fig.tight_layout(); fig.savefig(output / "fields.png", dpi=160); plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    parser.add_argument("--meshes", nargs="+", type=int, default=[10,20,40,80])
    parser.add_argument("--freefem", default="FreeFem++")
    args = parser.parse_args()
    rows = study(args.output, args.meshes, args.freefem)
    figures(args.output)
    for row in rows:
        print(row["method"], int(row["n"]), {key: row[key] for key in ERRORS})
