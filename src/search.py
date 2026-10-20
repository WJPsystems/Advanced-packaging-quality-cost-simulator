"""Try every inspection plan on a grid and rank them by cost."""
import itertools
import pandas as pd
from .cost_model import Params, DEFAULTS
from .simulate import Draws, simulate_plan

LEVELS = (0.0, 0.1, 0.25, 0.5, 1.0)   # share of units inspected at a step


def all_plans(n_steps: int, levels=LEVELS):
    return list(itertools.product(levels, repeat=n_steps))


def rank_plans(p: Params = DEFAULTS, levels=LEVELS, n_units: int = 100_000, seed: int = 0) -> pd.DataFrame:
    draws = Draws(n_units, p.n_steps, seed)
    rows = []
    for plan in all_plans(p.n_steps, levels):
        r = simulate_plan(plan, draws, p)
        rows.append({"plan": plan, "units_inspected_per_100": 100 * sum(plan), **r})
    df = pd.DataFrame(rows).sort_values("total").reset_index(drop=True)
    df.index = df.index + 1
    df.index.name = "rank"
    return df


def best_plan(p: Params = DEFAULTS, **kw):
    df = rank_plans(p, **kw)
    top = df.iloc[0]
    return top["plan"], float(top["total"])


def describe_plan(plan, names=DEFAULTS.step_names) -> str:
    """Plain-English label for a plan, e.g. 'Step 1: none | Step 2: all | Step 3: 25%'."""
    def share(x):
        return "none" if x == 0 else "all" if x == 1 else f"{int(round(x * 100))}%"
    return " | ".join(f"{n}: {share(x)}" for n, x in zip(names, plan))
