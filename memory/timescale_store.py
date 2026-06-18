import json
import numpy as np
from typing import List, Dict

_pool = None


async def _get_pool():
    global _pool
    if _pool is None:
        from storage.db import get_pool
        _pool = await get_pool()
    return _pool


def _vec_str(vector) -> str:
    vec = np.array(vector, dtype=np.float32).flatten()
    if len(vec) > 384:
        vec = vec[:384]
    elif len(vec) < 384:
        vec = np.pad(vec, (0, 384 - len(vec)))
    return "[" + ",".join(f"{x:.6f}" for x in vec) + "]"


class TimescaleStore:
    """
    pgvector-backed memory store for TimescaleDB.
    Drop-in replacement for FAISSStore — same add/search/total interface.
    """

    def add_sync(self, vector, meta: dict):
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(self.add(vector, meta))
            else:
                loop.run_until_complete(self.add(vector, meta))
        except Exception as e:
            print(f"[TimescaleStore] add_sync error: {e}")

    async def add(self, vector, meta: dict):
        pool = await _get_pool()
        if pool is None:
            return
        vs = _vec_str(vector)
        await pool.execute(
            """
            INSERT INTO memory_strands
                (cycle_id, domain, gate_open, psi, embedding, meta_json)
            VALUES ($1, $2, $3, $4, $5::vector, $6::jsonb)
            """,
            meta.get("cycle_id"),
            meta.get("domain"),
            meta.get("gate_open"),
            float(meta.get("psi", 0.0)),
            vs,
            json.dumps(meta),
        )

    async def search(self, vector, k: int = 5) -> List[Dict]:
        pool = await _get_pool()
        if pool is None:
            return []
        vs = _vec_str(vector)
        rows = await pool.fetch(
            """
            SELECT meta_json, (embedding <=> $1::vector) AS distance
            FROM memory_strands
            ORDER BY embedding <=> $1::vector
            LIMIT $2
            """,
            vs,
            k,
        )
        return [
            {"distance": float(r["distance"]), "meta": json.loads(r["meta_json"])}
            for r in rows
        ]

    async def total(self) -> int:
        pool = await _get_pool()
        if pool is None:
            return 0
        row = await pool.fetchrow("SELECT COUNT(*) AS n FROM memory_strands")
        return int(row["n"])
