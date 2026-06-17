FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git && rm -rf /var/lib/apt/lists/*

# Rust for entropy module
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
ENV PATH="/root/.cargo/bin:${PATH}"

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt maturin

# Build Rust entropy module
COPY entropy/ entropy/
RUN cd entropy && maturin build --release && pip install target/wheels/*.whl

# Copy source
COPY . .

# Create data directory
RUN mkdir -p data

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
