import json
import os
import numpy as np

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

INDEX_FILE = "data/faiss_index.bin"
META_FILE = "data/faiss_meta.json"
DIM = 384


class FAISSStore:
    """
    FAISS persistent vector store.
    Rule 1: Persists to disk on every write. No exceptions.
    """

    def __init__(self, dim: int = DIM):
        self.dim = dim
        self.metadata = []
        os.makedirs("data", exist_ok=True)

        if FAISS_AVAILABLE:
            self._load_or_init_faiss()
        else:
            self.index = None
            self._vectors = []
            self._load_meta()

    def _load_or_init_faiss(self):
        if os.path.exists(INDEX_FILE) and os.path.exists(META_FILE):
            self.index = faiss.read_index(INDEX_FILE)
            with open(META_FILE) as f:
                self.metadata = json.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dim)
            self.metadata = []

    def _load_meta(self):
        if os.path.exists(META_FILE):
            with open(META_FILE) as f:
                self.metadata = json.load(f)

    def add(self, vector: np.ndarray, meta: dict):
        vec = np.array(vector, dtype=np.float32).flatten()
        if len(vec) > self.dim:
            vec = vec[: self.dim]
        elif len(vec) < self.dim:
            vec = np.pad(vec, (0, self.dim - len(vec)))

        if FAISS_AVAILABLE and self.index is not None:
            self.index.add(vec.reshape(1, -1))
            faiss.write_index(self.index, INDEX_FILE)
        else:
            self._vectors.append(vec.tolist())

        self.metadata.append(meta)
        with open(META_FILE, "w") as f:
            json.dump(self.metadata[-10000:], f)

    def search(self, vector: np.ndarray, k: int = 5):
        vec = np.array(vector, dtype=np.float32).flatten()
        if len(vec) > self.dim:
            vec = vec[: self.dim]
        elif len(vec) < self.dim:
            vec = np.pad(vec, (0, self.dim - len(vec)))

        if FAISS_AVAILABLE and self.index is not None and self.index.ntotal > 0:
            k = min(k, self.index.ntotal)
            distances, indices = self.index.search(vec.reshape(1, -1), k)
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx < len(self.metadata):
                    results.append({"distance": float(dist), "meta": self.metadata[idx]})
            return results
        return []

    def total(self) -> int:
        if FAISS_AVAILABLE and self.index is not None:
            return self.index.ntotal
        return len(self.metadata)
