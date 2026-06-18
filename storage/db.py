import os
import ssl
import asyncpg

_pool = None


async def get_pool():
    global _pool
    if _pool is None:
        url = os.getenv("TIMESCALE_URL")
        if not url:
            return None
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        _pool = await asyncpg.create_pool(url, ssl=ctx, min_size=1, max_size=5)
        await _init_schema(_pool)
        print("[DB] TimescaleDB pool ready")
    return _pool


async def _init_schema(pool):
    async with pool.acquire() as conn:
        await conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")

        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path) as f:
            schema = f.read()
        for stmt in schema.split(";"):
            stmt = stmt.strip()
            if stmt and not stmt.startswith("--"):
                try:
                    await conn.execute(stmt)
                except Exception:
                    pass

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_strands (
                id          BIGSERIAL PRIMARY KEY,
                timestamp   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                cycle_id    TEXT,
                domain      TEXT,
                gate_open   BOOLEAN,
                psi         DOUBLE PRECISION,
                embedding   vector(384),
                meta_json   JSONB
            )
        """)
        try:
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS memory_strands_vec_idx "
                "ON memory_strands USING hnsw (embedding vector_cosine_ops)"
            )
        except Exception:
            pass
        print("[DB] Schema applied")
