from datetime import datetime, timezone


class SilenceProtocol:
    """
    SILENCE is not failure. SILENCE is information.
    Logged before any other action in that cycle. Rule 4.
    """

    def log_silence(
        self, cycle_id: str, psi: float, delta: float, plane_scores: dict
    ) -> str:
        gap = delta - psi
        failing = [
            k
            for k, v in {
                "P": plane_scores.get("p", 0),
                "I": plane_scores.get("i", 0),
                "C": plane_scores.get("c", 0),
                "S": plane_scores.get("s", 0),
                "W": plane_scores.get("w", 0),
            }.items()
            if v < 0.5
        ]

        reason = (
            f"SILENCE: Ψ={psi:.4f} < Δ={delta:.4f} (gap={gap:.4f}). "
            f"Failing planes: {failing or ['none below 0.5']}"
        )
        ts = datetime.now(timezone.utc).isoformat()
        print(f"[SILENCE {ts}] cycle={cycle_id} | {reason}")
        return reason

    def get_failing_planes(self, plane_scores: dict) -> list:
        return [
            k
            for k, v in {
                "P": plane_scores.get("p", 0),
                "I": plane_scores.get("i", 0),
                "C": plane_scores.get("c", 0),
                "S": plane_scores.get("s", 0),
                "W": plane_scores.get("w", 0),
            }.items()
            if v < 0.5
        ]
