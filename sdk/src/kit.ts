/**
 * SOVEREIGN-Ω SDK — SovereignOmegaKit
 *
 * Main class — mirrors the PharosAgentKit API pattern so agents can
 * treat SOVEREIGN-Ω as a first-class peer alongside pharos-agent-kit.
 *
 * ```ts
 * import { PharosAgentKit, createPharosTools } from "pharos-agent-kit";
 * import { SovereignOmegaKit, createSovereignTools } from "sovereign-omega-sdk";
 *
 * const pharos = new PharosAgentKit(privateKey, rpcUrl, config);
 * const sovereign = new SovereignOmegaKit({ baseUrl: SOVEREIGN_URL, x402: { ... } });
 *
 * const tools = [...createPharosTools(pharos), ...createSovereignTools(sovereign.client)];
 * ```
 */

import { SovereignClient } from "./client";
import { createSovereignTools } from "./tools";
import { getSovereignMcpTools, executeMcpTool } from "./mcp";
import type { SovereignConfig, CoherenceResult, MoatResult } from "./types";
import type { DynamicStructuredTool } from "@langchain/core/tools";

export class SovereignOmegaKit {
  public readonly client: SovereignClient;
  private readonly config: SovereignConfig;

  constructor(config: SovereignConfig) {
    this.config = config;
    this.client = new SovereignClient(config);
  }

  // ─── Convenience direct-call methods ─────────────────────────────────────

  /**
   * Evaluate coherence of an action via TRION mathematics.
   * Returns the gate decision and all five plane scores.
   */
  async evaluateCoherence(
    query: string,
    domain = "general"
  ): Promise<CoherenceResult> {
    const res = await this.client.invokeSkill<CoherenceResult>(
      "coherence_evaluate",
      { query, domain }
    );
    return res.output;
  }

  /**
   * Get current moat (Λ), IQ score, and domain mastery.
   */
  async getMoatStatus(): Promise<MoatResult> {
    const res = await this.client.invokeSkill<MoatResult>("moat_status", {});
    return res.output;
  }

  /**
   * Check if an action would be silenced.
   * Returns true if the agent would stay silent (do NOT proceed).
   */
  async wouldBeSilenced(action: string, domain = "general"): Promise<boolean> {
    const res = await this.client.invokeSkill<{ silenced: boolean }>(
      "silence_check",
      { action, domain }
    );
    return res.output.silenced;
  }

  /**
   * Get a trade evaluation with Bayesian-Kelly sizing.
   * Requires x402 config.
   */
  async evaluateTrade(params: {
    symbol: string;
    direction: "LONG" | "SHORT" | "NEUTRAL";
    strategy?: string;
    portfolio_pct?: number;
    volatility?: number;
  }) {
    const res = await this.client.invokeSkill("trade_evaluate", params);
    return res.output;
  }

  /**
   * Run the 5-chain parallel reasoner.
   * Requires x402 config.
   */
  async reasonChain(question: string, domain = "general", maxChains = 5) {
    const res = await this.client.invokeSkill("reasoning_chain", {
      question,
      domain,
      max_chains: maxChains,
    });
    return res.output;
  }

  // ─── Agent card / discovery ───────────────────────────────────────────────

  /** Fetch the live A2A agent card */
  async getAgentCard() {
    return this.client.getAgentCard();
  }

  /** Fetch x402 payment configuration */
  async getX402Config() {
    return this.client.getX402Config();
  }

  /** List all available skills with metadata */
  async listSkills() {
    return this.client.listSkills();
  }

  // ─── LangChain tool factory ───────────────────────────────────────────────

  /**
   * Create LangChain DynamicStructuredTools for all skills.
   * Mirrors pharos-agent-kit's createPharosTools(kit) pattern.
   */
  createTools(options?: {
    includeFreeSkills?: boolean;
    includePremiumSkills?: boolean;
  }): DynamicStructuredTool[] {
    return createSovereignTools(this.client, options);
  }

  // ─── MCP adapter ─────────────────────────────────────────────────────────

  /** Get MCP tool definitions for use with MCP hosts */
  getMcpTools() {
    return getSovereignMcpTools();
  }

  /** Execute an MCP tool call */
  async executeMcpTool(toolName: string, args: Record<string, unknown>) {
    return executeMcpTool(this.client, toolName, args);
  }
}
