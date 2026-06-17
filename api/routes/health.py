from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()


@router.get("/health")
async def health():
    from core.moat_accumulator import MoatAccumulator
    from learning.intelligence_score import IntelligenceScorer
    moat = MoatAccumulator()
    scorer = IntelligenceScorer()
    iq = await scorer.compute()
    return {
        "status": "SOVEREIGN-Ω ONLINE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "lambda": moat.get_current_lambda(),
        "cycles": moat.n_cycles,
        "iq": iq,
        "version": "2.0.0",
        "chain": "Pharos",
    }
