from fastapi import APIRouter
from core.moat_accumulator import MoatAccumulator
from learning.intelligence_score import IntelligenceScorer
import math

router = APIRouter()


@router.get("/moat")
async def get_moat():
    moat = MoatAccumulator()
    scorer = IntelligenceScorer()
    iq_data = await scorer.get_breakdown()
    lambda_val = moat.get_current_lambda()
    t_norm = moat.get_t_normalized()

    projections = {}
    for days in [1, 7, 30, 90, 365]:
        t_future = t_norm + days / 30.0
        projections[f"{days}d"] = lambda_val * math.exp(lambda_val * t_future)

    return {
        "lambda": lambda_val,
        "log_lambda": moat.log_lambda,
        "n_cycles": moat.n_cycles,
        "t_normalized": t_norm,
        "iq_score": iq_data["iq_score"],
        "iq_interpretation": iq_data["interpretation"],
        "projections": projections,
        "lambda_0": MoatAccumulator.LAMBDA_0,
        "growth_since_start": lambda_val / MoatAccumulator.LAMBDA_0,
    }
