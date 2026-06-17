from fastapi import APIRouter, HTTPException
from api.schemas import TradeRequest, TradeResponse
from trading.decision_engine import TradingDecisionEngine

router = APIRouter()
decision_engine = TradingDecisionEngine()


@router.post("/trade/evaluate", response_model=TradeResponse)
async def evaluate_trade(req: TradeRequest):
    result = await decision_engine.evaluate_trade(
        symbol=req.symbol,
        direction=req.direction,
        strategy=req.strategy,
    )
    return TradeResponse(**{k: v for k, v in result.items() if k in TradeResponse.model_fields})


@router.post("/trade/close/{trade_id}")
async def close_trade(trade_id: str, exit_price: float, pnl: float, won: bool):
    await decision_engine.close_trade_on_outcome(trade_id, exit_price, pnl, won)
    return {"status": "closed", "trade_id": trade_id, "won": won, "pnl": pnl}
