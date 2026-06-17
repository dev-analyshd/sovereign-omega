/**
 * SOVEREIGN-Ω SDK — HTTP Client
 * Handles all communication with the SOVEREIGN-Ω FastAPI backend.
 * Transparently manages x402 payment headers for premium skills.
 */

import type {
  SovereignConfig,
  SkillResponse,
  X402Required,
  X402PaymentRequest,
} from "./types";

export class SovereignClient {
  private readonly baseUrl: string;
  private readonly timeoutMs: number;
  private readonly config: SovereignConfig;

  constructor(config: SovereignConfig) {
    this.config = config;
    this.baseUrl = config.baseUrl.replace(/\/$/, "");
    this.timeoutMs = config.timeoutMs ?? 30_000;
  }

  /**
   * Invoke a SOVEREIGN-Ω skill. Handles x402 automatically if config provided.
   */
  async invokeSkill<T>(
    skillId: string,
    input: Record<string, unknown>
  ): Promise<SkillResponse<T>> {
    const url = `${this.baseUrl}/api/v1/skills/invoke/${skillId}`;
    const body = JSON.stringify({ skill_id: skillId, input });

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "User-Agent": "sovereign-omega-sdk/1.0.0",
    };

    // First attempt
    const res = await this._fetch(url, "POST", headers, body);

    // x402 Payment Required — attempt to pay and retry
    if (res.status === 402) {
      const paymentData: { output: X402Required } = await res.json();
      const x402 = paymentData.output ?? (res as unknown as X402Required);

      if (!this.config.x402) {
        throw new X402Error(
          `Skill '${skillId}' requires x402 payment but no x402 config provided. ` +
            `Add x402: { walletAddress, token, signPayment } to SovereignConfig.`,
          x402 as unknown as X402Required
        );
      }

      const paymentHeader = await this._buildPaymentHeader(
        skillId,
        x402 as unknown as X402Required
      );
      headers["X-Payment"] = paymentHeader;

      const retryRes = await this._fetch(url, "POST", headers, body);
      if (!retryRes.ok) {
        const err = await retryRes.json().catch(() => ({}));
        throw new Error(
          `Skill invocation failed after payment: ${retryRes.status} — ${JSON.stringify(err)}`
        );
      }
      return retryRes.json();
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(
        `Skill '${skillId}' failed: ${res.status} — ${JSON.stringify(err)}`
      );
    }

    return res.json();
  }

  /** GET the list of available skills */
  async listSkills(): Promise<unknown> {
    const res = await this._fetch(
      `${this.baseUrl}/api/v1/skills`,
      "GET",
      { "User-Agent": "sovereign-omega-sdk/1.0.0" }
    );
    return res.json();
  }

  /** GET the agent discovery card */
  async getAgentCard(): Promise<unknown> {
    const res = await this._fetch(
      `${this.baseUrl}/.well-known/agent.json`,
      "GET",
      { "User-Agent": "sovereign-omega-sdk/1.0.0" }
    );
    return res.json();
  }

  /** GET x402 config */
  async getX402Config(): Promise<unknown> {
    const res = await this._fetch(
      `${this.baseUrl}/api/v1/x402/config`,
      "GET",
      { "User-Agent": "sovereign-omega-sdk/1.0.0" }
    );
    return res.json();
  }

  private async _buildPaymentHeader(
    skillId: string,
    x402Data: X402Required
  ): Promise<string> {
    if (!this.config.x402) throw new Error("x402 config missing");

    const req: X402PaymentRequest = {
      skillId,
      amount: x402Data.x402?.maxAmountRequired ?? "1.0",
      token: this.config.x402.token,
      currency: this.config.x402.token === "PROS" ? "native" : "erc20",
      agentAddress: x402Data.x402?.payTo ?? "",
      nonce: x402Data.payment_nonce ?? crypto.randomUUID(),
      expiresAt: x402Data.expires_at ?? Date.now() + 300_000,
      chainId: 688688, // Pharos testnet
    };

    const signature = await this.config.x402.signPayment(req);

    const payload = {
      version: "1",
      scheme: "exact",
      network: "pharos-testnet",
      payload: {
        signature,
        authorization: {
          from: this.config.x402.walletAddress,
          to: req.agentAddress,
          value: req.amount,
          validAfter: Math.floor(Date.now() / 1000).toString(),
          validBefore: Math.floor(req.expiresAt / 1000).toString(),
          nonce: req.nonce,
        },
      },
    };

    return Buffer.from(JSON.stringify(payload)).toString("base64");
  }

  private async _fetch(
    url: string,
    method: string,
    headers: Record<string, string>,
    body?: string
  ): Promise<Response> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeoutMs);

    try {
      return await fetch(url, {
        method,
        headers,
        body,
        signal: controller.signal,
      });
    } finally {
      clearTimeout(timer);
    }
  }
}

/** Thrown when x402 payment is required but no payment config was provided */
export class X402Error extends Error {
  public readonly paymentData: X402Required;

  constructor(message: string, paymentData: X402Required) {
    super(message);
    this.name = "X402Error";
    this.paymentData = paymentData;
  }
}
