"""What-if analysis: how does the best plan change when assumptions change?"""
import pandas as pd
from .cost_model import Params, DEFAULTS
from .search import best_plan

INPUTS = ("escape_cost", "detection_rate", "inspection_cost", "delay_cost", "defect_rate")


def tornado(p: Params = DEFAULTS, swing: float = 0.5, **kw) -> pd.DataFrame:
    """Change one input at a time by +/- `swing` (0.5 = 50%) and record the result."""
    base_plan, base_cost = best_plan(p, **kw)
    rows = []
    for name in INPUTS:
        for label, factor in (("low", 1 - swing), ("high", 1 + swing)):
            q = p.scaled(**{name: factor})
            if name == "detection_rate":
                q = Params(**{**q.__dict__, "detection_rate": min(1.0, q.detection_rate)})
            plan, cost = best_plan(q, **kw)
            rows.append({"input": name, "case": label, "best_plan": plan,
                         "best_cost": cost, "change_vs_base": cost - base_cost,
                         "plan_changed": plan != base_plan})
    return pd.DataFrame(rows)


def breakeven_scan(p: Params = DEFAULTS, multipliers=(0.1, 0.25, 0.5, 1, 2, 4, 8), **kw) -> pd.DataFrame:
    """How the best plan shifts as the cost of a missed defect changes."""
    rows = []
    for m in multipliers:
        plan, cost = best_plan(p.scaled(escape_cost=m), **kw)
        rows.append({"escape_cost_multiplier": m, "escape_cost": p.escape_cost * m,
                     "best_plan": plan, "best_cost": cost})
    return pd.DataFrame(rows)
