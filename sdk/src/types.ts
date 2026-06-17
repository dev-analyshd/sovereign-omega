/**
 * SOVEREIGN-Ω SDK — Type Definitions
 * Ω(a,t) = [Ψ(t) ≥ Δ(t)] · R(a,t) · e^(Λ·t)
 */

export interface SovereignConfig {
  /** Base URL of the SOVEREIGN-Ω API (e.g. https://your-agent.replit.dev) */
  baseUrl: string;
  /** Optional timeout in milliseconds (default: 30000) */
  timeoutMs?: number;
  /** x402 payment config — required for premium (trade_evaluate, reasoning_chain) skills */
  x402?: X402Config;
}

export interface X402Config {
  /** Payer wallet address on Pharos chain */
  walletAddress: string;
  /** Payment token: "PROS" (native, 20% discount) or "USDC" */
  token: "PROS" | "USDC";
  /** Sign an x402 payment header — receives the payment request, returns signed header */
  signPayment: (req: X402PaymentRequest) => Promise<string>;
}

export interface X402PaymentRequest {
  skillId: string;
  amount: string;
  token: string;
  currency: string;
  agentAddress: string;
  nonce: string;
  expiresAt: number;
  chainId: number;
}

/** Five cognitive plane scores from TRION mathematics */
export interface PlaneBreakdown {
  p: number; // Perceptual  — Shannon entropy of input signals
  i: number; // Inferential — internal reasoning consistency
  c: number; // Consensus   — slow independent convergence
  s: number; // Self-Reflection — memory density (familiarity)
  w: number; // World Model — environment normality
}

/** Core coherence evaluation result */
export interface CoherenceResult {
  gate_open: boolean;
  psi_score: number;
  delta_threshold: number;
  plane_breakdown: PlaneBreakdown;
  message: "ACT" | "SILENCE";
  cycle_id: string;
  domain: string;
}

/** Moat (compounding intelligence coefficient) status */
export interface MoatResult {
  lambda: number;
  iq_score: number;
  iq_interpretation: string;
  total_cycles: number;
  successful_actions: number;
  silence_episodes: number;
  silence_rate: number;
  domain_mastery: Record<string, number>;
  projected_lambda_30d: number;
  projected_iq_30d: number;
}

/** Trade evaluation result */
export interface TradeResult {
  decision: "EXECUTE" | "WAIT" | "SILENCE";
  confidence: number;
  kelly_fraction: number;
  suggested_size_pct: number;
  psi_score: number;
  reasons: string[];
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  bayesian_win_prob: number;
  expected_value: number;
}

/** Silence check result */
export interface SilenceResult {
  silenced: boolean;
  psi_score: number;
  delta_threshold: number;
  gate_message: "ACT" | "SILENCE";
  failing_planes: string[];
  silence_reason: string | null;
}

/** Intelligence score result */
export interface IntelligenceResult {
  lambda: number;
  iq_score: number;
  iq_interpretation: string;
  total_cycles: number;
  domain_mastery: Record<string, number>;
}

/** Reasoning chain result */
export interface ReasoningResult {
  question: string;
  best_answer: string;
  best_chain_confidence: number;
  reasoning_method: string;
  chains_run: number;
  psi_score: number;
  gate_decision: "ACT" | "SILENCE";
  consensus_level: "STRONG" | "MODERATE" | "WEAK" | "CONTRADICTION";
  domain: string;
  chain_details: Array<{
    chain_id: number;
    method: string;
    answer: string;
    confidence: number;
    elapsed_ms: number;
  }>;
}

/** Skill invocation response envelope */
export interface SkillResponse<T> {
  skill_id: string;
  invocation_id: string;
  success: boolean;
  output: T;
  on_chain_logged: boolean;
  psi_at_invoke: number;
  lambda_at_invoke: number;
  error?: string;
}

/** x402 payment required response (HTTP 402) */
export interface X402Required {
  error: string;
  x402: {
    scheme: string;
    network: string;
    maxAmountRequired: string;
    resource: string;
    description: string;
    mimeType: string;
    payTo: string;
    maxTimeoutSeconds: number;
    asset: string;
    extra: {
      name: string;
      version: string;
      token: string;
    };
  };
  payment_nonce: string;
  expires_at: number;
  skill_id: string;
  hint: string;
}
