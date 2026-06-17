import math
import uuid
from fastapi import APIRouter
from api.schemas import ActionRequest, ActionResponse

router = APIRouter()

_coherence_engine = None
_action_gate = None
_moat_acc = None
_silence_protocol = None
_chain_manager = None
_learner = None


def _get_components():
    global _coherence_engine, _action_gate, _moat_acc, _silence_protocol, _chain_manager, _learner
    if _coherence_engine is None:
        from core.coherence_engine import CoherenceEngine
        from core.action_gate import ActionGate
        from core.moat_accumulator import MoatAccumulator
        from core.silence_protocol import SilenceProtocol
        from reasoning.chain_manager import ChainManager
        from learning.continuous_learner import ContinuousLearner
        _coherence_engine = CoherenceEngine()
        _action_gate = ActionGate()
        _moat_acc = MoatAccumulator()
        _silence_protocol = SilenceProtocol()
        _chain_manager = ChainManager()
        _learner = ContinuousLearner()
    return _coherence_engine, _action_gate, _moat_acc, _silence_protocol, _chain_manager, _learner


@router.post("/action", response_model=ActionResponse)
async def evaluate_action(req: ActionRequest):
    coherence_engine, action_gate, moat_acc, silence_protocol, chain_manager, learner = _get_components()
    cycle_id = str(uuid.uuid4())

    reasoning_chains = await chain_manager.run_chains(req.query, req.context)
    context = {
        **req.context,
        "reasoning_chains": reasoning_chains,
        "input_channels": req.context.get("input_channels", {"query": [len(req.query) / 500.0]}),
        "environmental_signals": req.context.get("environmental_signals", {}),
        "volatility": req.context.get("volatility", 0.2),
        "novelty": req.context.get("novelty", 0.5),
    }

    plane_scores = await coherence_engine.compute_all_planes(req.query, context, cycle_id)
    psi = plane_scores["psi_total"]
    delta = action_gate.compute_threshold(plane_scores["volatility"], plane_scores["novelty"])
    gate_open = action_gate.is_open(psi, delta)

    lambda_val = moat_acc.get_current_lambda()
    t_norm = moat_acc.get_t_normalized()

    if not gate_open:
        reason = silence_protocol.log_silence(cycle_id, psi, delta, plane_scores)
        omega = 0.0
        action_output = None
    else:
        best_chain = max(reasoning_chains, key=lambda c: c.get("confidence", 0), default={"response": "No output"})
        action_output = best_chain.get("response", "")
        moat_acc.accumulate(eta_i=0.85, rho_i=psi, cycle_id=cycle_id)
        omega = psi * math.exp(lambda_val * t_norm)
        reason = None

    await learner.learn_from_cycle(
        cycle_id=cycle_id,
        query=req.query,
        action_output=action_output or "",
        gate_open=gate_open,
        domain=req.domain,
        plane_scores=plane_scores,
    )

    return ActionResponse(
        cycle_id=cycle_id,
        gate_open=gate_open,
        action_output=action_output,
        silence_reason=reason,
        psi_score=psi,
        delta_threshold=delta,
        lambda_value=lambda_val,
        omega_value=omega,
        plane_breakdown={"p": plane_scores["p"], "i": plane_scores["i"], "c": plane_scores["c"], "s": plane_scores["s"], "w": plane_scores["w"]},
        message="ACTION" if gate_open else "SILENCE",
    )
