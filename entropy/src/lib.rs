use pyo3::prelude::*;
use rand::Rng;
use rand_chacha::ChaCha20Rng;
use rand::SeedableRng;
use sha2::{Sha256, Digest};
use hmac::{Hmac, Mac};

type HmacSha256 = Hmac<Sha256>;

/// Multi-source entropy collector.
/// Combines system noise, crypto random, and deterministic hash-based sampling.
/// Used to seed SOVEREIGN-Ω's stochastic decisions.
#[pyfunction]
fn collect_entropy(seed: Option<u64>) -> PyResult<Vec<f64>> {
    let mut rng = match seed {
        Some(s) => ChaCha20Rng::seed_from_u64(s),
        None => ChaCha20Rng::from_entropy(),
    };

    let entropy: Vec<f64> = (0..256)
        .map(|_| rng.gen::<f64>())
        .collect();

    Ok(entropy)
}

/// Compute normalized Shannon entropy of a sequence.
/// H = -Σ p·log₂(p) / log₂(n)
/// Returns value in [0, 1].
#[pyfunction]
fn shannon_entropy(values: Vec<f64>) -> PyResult<f64> {
    if values.is_empty() {
        return Ok(0.0);
    }
    let total: f64 = values.iter().map(|v| v.abs()).sum();
    if total == 0.0 {
        return Ok(0.0);
    }

    let probs: Vec<f64> = values.iter()
        .filter(|&&v| v > 0.0)
        .map(|&v| v / total)
        .collect();

    let h: f64 = probs.iter()
        .filter(|&&p| p > 0.0)
        .map(|&p| -p * p.log2())
        .sum();

    let n = values.len() as f64;
    let h_max = if n > 1.0 { n.log2() } else { 1.0 };

    Ok((h / h_max).min(1.0))
}

/// Cryptographic entropy fingerprint using HMAC-SHA256.
/// Used to fingerprint knowledge items in dual-strand memory.
#[pyfunction]
fn entropy_fingerprint(data: &str, key: &str) -> PyResult<String> {
    let mut mac = HmacSha256::new_from_slice(key.as_bytes())
        .expect("HMAC can take key of any size");
    mac.update(data.as_bytes());
    let result = mac.finalize();
    Ok(hex::encode(result.into_bytes()))
}

/// Generate a deterministic noise vector from a seed.
/// Used in adversarial robustness testing of coherence scores.
#[pyfunction]
fn generate_noise_vector(seed: u64, dim: usize, scale: f64) -> PyResult<Vec<f64>> {
    let mut rng = ChaCha20Rng::seed_from_u64(seed);
    let noise: Vec<f64> = (0..dim)
        .map(|_| (rng.gen::<f64>() - 0.5) * 2.0 * scale)
        .collect();
    Ok(noise)
}

/// Sample k unique indices without replacement using Fisher-Yates.
/// Used for fair, unbiased random sampling of knowledge items.
#[pyfunction]
fn sample_indices(n: usize, k: usize, seed: u64) -> PyResult<Vec<usize>> {
    if k > n {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("k cannot exceed n"));
    }
    let mut rng = ChaCha20Rng::seed_from_u64(seed);
    let mut indices: Vec<usize> = (0..n).collect();
    for i in 0..k {
        let j = rng.gen_range(i..n);
        indices.swap(i, j);
    }
    Ok(indices[..k].to_vec())
}

/// Hash data with SHA-256 and return as hex string.
#[pyfunction]
fn sha256_hex(data: &str) -> PyResult<String> {
    let mut hasher = Sha256::new();
    hasher.update(data.as_bytes());
    Ok(hex::encode(hasher.finalize()))
}

#[pymodule]
fn sovereign_entropy(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(collect_entropy, m)?)?;
    m.add_function(wrap_pyfunction!(shannon_entropy, m)?)?;
    m.add_function(wrap_pyfunction!(entropy_fingerprint, m)?)?;
    m.add_function(wrap_pyfunction!(generate_noise_vector, m)?)?;
    m.add_function(wrap_pyfunction!(sample_indices, m)?)?;
    m.add_function(wrap_pyfunction!(sha256_hex, m)?)?;
    Ok(())
}
