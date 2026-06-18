FROM python:3.11-slim

WORKDIR /app

# System deps (build tools for faiss-cpu, web3, numpy)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Rust toolchain (for sovereign_entropy Rust extension)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | \
    sh -s -- -y --default-toolchain stable --profile minimal
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir maturin && \
    pip install --no-cache-dir -r requirements.txt

# Build Rust entropy module (falls back gracefully if build fails)
COPY entropy/ entropy/
RUN cd entropy && \
    maturin build --release 2>/dev/null && \
    pip install --no-cache-dir target/wheels/*.whl 2>/dev/null || \
    echo "Rust entropy module not built — using Python fallback"

# Copy application source
COPY . .

# Create persistent data directories
RUN mkdir -p data memory/faiss_index

# Render injects PORT; default to 8000 for local Docker
ENV PORT=8000

EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/v1/health || exit 1

CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT}
