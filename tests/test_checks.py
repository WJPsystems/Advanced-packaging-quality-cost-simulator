"""Self-checks: the simulation must agree with the exact calculation."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np
from src.cost_model import DEFAULTS, expected_cost_analytic
from src.simulate import Draws, simulate_plan
from src.search import rank_plans


def test_simulation_matches_exact_calculation():
    draws = Draws(400_000, DEFAULTS.n_steps, seed=1)
    for plan in [(0, 0, 0), (1, 1, 1), (0.25, 0.1, 0.5), (0, 0.5, 1)]:
        sim = simulate_plan(plan, draws)
        exact = expected_cost_analytic(plan)
        assert abs(sim["total"] - exact["total"]) < 4 * sim["std_error"] + 1e-9, plan


def test_no_inspection_costs_only_escapes():
    exact = expected_cost_analytic((0, 0, 0))
    assert exact["inspection"] == 0 and exact["scrap"] == 0
    p_any = 1 - np.prod(1 - np.array(DEFAULTS.defect_rate))
    assert abs(exact["escaped"] - p_any * DEFAULTS.escape_cost) < 1e-9


def test_free_perfect_inspection_catches_everything():
    p = DEFAULTS.scaled(inspection_cost=0.0, delay_cost=0.0)
    p = type(p)(**{**p.__dict__, "detection_rate": 1.0})
    assert expected_cost_analytic((1, 1, 1), p)["escaped"] == 0


def test_ranking_is_sorted_and_cheapest_beats_no_inspection():
    df = rank_plans(n_units=20_000)
    assert df["total"].is_monotonic_increasing
    none = df[df["plan"] == (0.0, 0.0, 0.0)]["total"].iloc[0]
    assert df.iloc[0]["total"] < none
