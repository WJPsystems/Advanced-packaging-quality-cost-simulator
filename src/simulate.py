"""Monte Carlo simulation of production lots under an inspection plan.

We make random units, let defects appear at random, let inspections catch or
miss them at random, and average the cost. "Common random numbers" means every
plan is tested on the SAME random units, so differences between plans come from
the plans, not from luck.
"""
import numpy as np
from .cost_model import Params, DEFAULTS


class Draws:
    """A fixed batch of random numbers, reusable across plans."""

    def __init__(self, n_units: int, n_steps: int, seed: int = 0):
        rng = np.random.default_rng(seed)
        self.n_units, self.n_steps = n_units, n_steps
        self.u_defect = rng.random((n_units, n_steps))
        self.u_sample = rng.random((n_units, n_steps))
        self.u_detect = rng.random((n_units, n_steps))


def simulate_plan(plan, draws: Draws, p: Params = DEFAULTS) -> dict:
    """Average cost per unit produced, split by component, plus a standard error."""
    f = np.asarray(plan, dtype=float)
    n, S = draws.n_units, p.n_steps
    alive = np.ones(n, dtype=bool)
    defective = np.zeros(n, dtype=bool)
    unit_cost = np.zeros(n)
    parts = {k: np.zeros(n) for k in ("inspection", "slowdown", "scrap", "escaped")}
    for s in range(S):
        defective |= alive & (draws.u_defect[:, s] < p.defect_rate[s])
        sampled = alive & (draws.u_sample[:, s] < f[s])
        parts["inspection"] += sampled * p.inspection_cost
        parts["slowdown"] += sampled * p.delay_cost
        caught = sampled & defective & (draws.u_detect[:, s] < p.detection_rate)
        parts["scrap"] += caught * p.scrap_cost[s]
        alive &= ~caught
    parts["escaped"] += (alive & defective) * p.escape_cost
    total = sum(parts.values())
    out = {k: float(v.mean()) for k, v in parts.items()}
    out["total"] = float(total.mean())
    out["std_error"] = float(total.std(ddof=1) / np.sqrt(n))
    return out
