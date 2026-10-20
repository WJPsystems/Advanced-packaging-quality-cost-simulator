"""Cost-of-quality model: what a given inspection plan costs per unit produced.

All numbers in DEFAULTS are ILLUSTRATIVE. They are not from any real factory.

Plain-language idea
-------------------
An advanced-packaging product (for example a stacked memory module or a chiplet
package) passes through several assembly steps. At each step a defect can creep
in. After each step we may inspect a share of the units. Inspecting costs money
and slows production; a defective unit that reaches a customer costs far more.
The "cost of quality" adds up all of it. Costs are in generic "cost units".
"""
from dataclasses import dataclass, field, replace
from typing import Tuple
import numpy as np


@dataclass(frozen=True)
class Params:
    """Inputs of the model. Change them to describe your own process."""
    step_names: Tuple[str, ...] = ("Surface prep", "Stack assembly", "Final integration")
    defect_rate: Tuple[float, ...] = (0.02, 0.03, 0.015)   # chance a defect is introduced at each step
    value_added: Tuple[float, ...] = (10.0, 25.0, 40.0)    # cost units invested in a unit at each step
    detection_rate: float = 0.90        # chance an inspection spots an existing defect
    inspection_cost: float = 2.0        # direct cost of inspecting one unit
    delay_cost: float = 1.0             # slowdown cost per inspected unit (lost throughput)
    escape_cost: float = 500.0          # cost when a defective unit reaches the customer

    @property
    def n_steps(self) -> int:
        return len(self.defect_rate)

    @property
    def scrap_cost(self) -> np.ndarray:
        """Cost of throwing away a unit caught after each step (value invested so far)."""
        return np.cumsum(np.asarray(self.value_added, dtype=float))

    def scaled(self, **factors) -> "Params":
        """Return a copy with named inputs multiplied, e.g. scaled(escape_cost=2.0)."""
        changes = {}
        for k, f in factors.items():
            v = getattr(self, k)
            changes[k] = tuple(x * f for x in v) if isinstance(v, tuple) else v * f
        return replace(self, **changes)


DEFAULTS = Params()
COMPONENTS = ("inspection", "slowdown", "scrap", "escaped")


def expected_cost_analytic(plan, p: Params = DEFAULTS) -> dict:
    """Exact expected cost per unit (no randomness) for a plan.

    `plan` gives, for each step, the share of units inspected (0 to 1).
    Used to double-check the simulation: the two should agree.
    """
    f = np.asarray(plan, dtype=float)
    d, S = p.detection_rate, p.n_steps
    q = np.asarray(p.defect_rate, dtype=float)
    g = f * d                                   # chance a defective unit is caught at a step
    insp = slow = scrap = esc = 0.0
    clean_prefix = 1.0                          # chance no defect introduced before this step
    for k in range(S):
        p_first = clean_prefix * q[k]           # defect first appears at step k
        # inspections of a unit before its defect appears (it looks clean)
        before = f[:k].sum()
        alive, n_insp = 1.0, 0.0
        for s in range(k, S):
            n_insp += alive * f[s]
            scrap += p_first * alive * g[s] * p.scrap_cost[s]
            alive *= (1.0 - g[s])
        esc += p_first * alive * p.escape_cost
        insp += p_first * (before + n_insp)
        clean_prefix *= (1.0 - q[k])
    insp += clean_prefix * f.sum()              # units that never get a defect
    n_inspections = insp
    return {
        "inspection": n_inspections * p.inspection_cost,
        "slowdown": n_inspections * p.delay_cost,
        "scrap": scrap,
        "escaped": esc,
        "total": n_inspections * (p.inspection_cost + p.delay_cost) + scrap + esc,
    }
