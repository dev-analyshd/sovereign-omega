from fastapi import APIRouter

router = APIRouter()

_silence_log = []


@router.get("/silence/log")
async def get_silence_log(limit: int = 50):
    return {"silence_log": _silence_log[-limit:], "total": len(_silence_log)}


@router.get("/silence/stats")
async def get_silence_stats():
    from core.moat_accumulator import MoatAccumulator
    moat = MoatAccumulator()
    total_cycles = moat.n_cycles + len(_silence_log)
    silence_rate = len(_silence_log) / max(total_cycles, 1)
    return {
        "total_silences": len(_silence_log),
        "total_cycles": total_cycles,
        "silence_rate": silence_rate,
        "interpretation": "Silence is information. Higher rate = more discriminating.",
    }
