/**
 * SOVEREIGN-Ω SDK — LangChain DynamicStructuredTool Wrappers
 *
 * Drop-in tools compatible with pharos-agent-kit's createPharosTools pattern.
 * Each tool is a DynamicStructuredTool with full Zod validation, error handling,
 * and automatic x402 payment retry for premium skills.
 *
 * Usage:
 *   import { createSovereignTools } from "sovereign-omega-sdk";
 *   const tools = createSovereignTools(client);
 *   const allTools = [...createPharosTools(pharosKit), ...tools];
 */

import { DynamicStructuredTool } from "@langchain/core/tools";
import { z } from "zod";
import type { SovereignClient } from "./client";
import type {
  CoherenceResult,
  MoatResult,
  TradeResult,
  SilenceResult,
  IntelligenceResult,
  ReasoningResult,
  SkillResponse,
} from "./types";

// ─── Helpers ─────────────────────────────────────────────────────────────────

function formatResponse<T>(res: SkillResponse<T>): string {
  if (!res.success) {
    return `SOVEREIGN-Ω Error: ${res.error ?? "Unknown error"} (invocation_id=${res.invocation_id})`;
  }
  return JSON.stringify(
    { ...res.output, _meta: { invocation_id: res.invocation_id, psi: res.psi_at_invoke, lambda: res.lambda_at_invoke } },
    null,
    2
  );
}

// ─── Tool 1: coherence_evaluate (FREE) ───────────────────────────────────────

function makeCoherenceEvaluateTool(client: SovereignClient): DynamicStructuredTool {
  return new DynamicStructuredTool({
    name: "sovereign_coherence_evaluate",
    description:
      "Run SOVEREIGN-Ω TRION mathematics on a query. Returns a Ψ (psi) coherence score, " +
      "a dynamic threshold Δ, and a binary gate decision (ACT or SILENCE) across five " +
      "cognitive planes: Perceptual, Inferential, Consensus, Self-Reflection, World Model. " +
      "Use this before any high-stakes action to check if conditions support acting. " +
      "Free skill — no payment required.",
    schema: z.object({
      query: z
        .string()
        .describe("The action, trade, or question to evaluate for cognitive coherence"),
      domain: z
        .enum(["trading", "social", "research", "reasoning", "general"])
        .optional()
        .default("general")
        .describe("Domain context for the evaluation"),
    }),
    func: async ({ query, domain }) => {
      const res = await client.invokeSkill<CoherenceResult>("coherence_evaluate", {
        query,
        domain: domain ?? "general",
      });
      return formatResponse(res);
    },
  });
}

// ─── Tool 2: moat_status (FREE) ──────────────────────────────────────────────

function makeMoatStatusTool(client: SovereignClient): DynamicStructuredTool {
  return new DynamicStructuredTool({
    name: "sovereign_moat_status",
    description:
      "Get SOVEREIGN-Ω's current intelligence moat coefficient (Λ), IQ score, total cycles, " +
      "silence rate, domain mastery breakdown, and 30-day projections. " +
      "Higher Λ means the agent has compounded more experience — exponential growth via e^(Λ·t). " +
      "Free skill — no payment required.",
    schema: z.object({
      _dummy: z
        .string()
        .optional()
        .describe("No input required — pass an empty string or omit"),
    }),
    func: async (_) => {
      const res = await client.invokeSkill<MoatResult>("moat_status", {});
      return formatResponse(res);
    },
  });
}

// ─── Tool 3: silence_check (FREE) ────────────────────────────────────────────

function makeSilenceCheckTool(client: SovereignClient): DynamicStructuredTool {
  return new DynamicStructuredTool({
    name: "sovereign_silence_check",
    description:
      "Check whether SOVEREIGN-Ω's Silence Protocol would suppress a given action. " +
      "Returns whether the action would be silenced, which cognitive planes are failing, " +
      "and a human-readable silence reason. " +
      "Use to pre-screen risky actions: if silenced=true, do NOT proceed. " +
      "Free skill — no payment required.",
    schema: z.object({
      action: z
        .string()
        .describe("The action to check — describe it in plain language"),
      domain: z
        .enum(["trading", "social", "research", "reasoning", "general"])
        .optional()
        .default("general")
        .describe("Domain context"),
    }),
    func: async ({ action, domain }) => {
      const res = await client.invokeSkill<SilenceResult>("silence_check", {
        action,
        domain: domain ?? "general",
      });
      return formatResponse(res);
    },
  });
}

// ─── Tool 4: intelligence_score (FREE) ───────────────────────────────────────

function makeIntelligenceScoreTool(client: SovereignClient): DynamicStructuredTool {
  return new DynamicStructuredTool({
    name: "sovereign_intelligence_score",
    description:
      "Get SOVEREIGN-Ω's full intelligence report: Λ (moat), IQ score with human-readable " +
      "interpretation (Initializing / Growing / Advanced / Expert / Elite), total cycle count, " +
      "and domain mastery percentages. Useful for understanding the agent's current capability level. " +
      "Free skill — no payment required.",
    schema: z.object({
      include_projection: z
        .boolean()
        .optional()
        .default(false)
        .describe("Whether to include 30-day growth projection"),
    }),
    func: async ({ include_projection }) => {
      const res = await client.invokeSkill<IntelligenceResult>("intelligence_score", {
        include_projection: include_projection ?? false,
      });
      return formatResponse(res);
    },
  });
}

// ─── Tool 5: trade_evaluate (PREMIUM — x402 required) ────────────────────────

function makeTradeEvaluateTool(client: SovereignClient): DynamicStructuredTool {
  return new DynamicStructuredTool({
    name: "sovereign_trade_evaluate",
    description:
      "Get a Bayesian-Kelly trade evaluation from SOVEREIGN-Ω. Returns: EXECUTE / WAIT / SILENCE " +
      "decision, Kelly fraction (optimal position size), Bayesian win probability, expected value, " +
      "risk level, and TRION coherence score at evaluation time. " +
      "PREMIUM skill — requires x402 payment in $PROS (1.0 PROS, 20% discount) or USDC (0.10). " +
      "Configure x402 in SovereignConfig to enable automatic payment.",
    schema: z.object({
      symbol: z
        .string()
        .describe("Trading pair symbol, e.g. 'BTC/USDT', 'ETH/USDC', 'PROS/USDT'"),
      direction: z
        .enum(["LONG", "SHORT", "NEUTRAL"])
        .describe("Intended trade direction"),
      strategy: z
        .enum(["momentum", "mean_reversion", "breakout", "range", "arbitrage"])
        .optional()
        .default("momentum")
        .describe("Trading strategy being applied"),
      portfolio_pct: z
        .number()
        .min(0)
        .max(100)
        .optional()
        .describe("Current portfolio allocation percentage to this asset (for Kelly capping)"),
      volatility: z
        .number()
        .min(0)
        .optional()
        .describe("Current 24h volatility as a decimal (e.g. 0.04 for 4%)"),
    }),
    func: async ({ symbol, direction, strategy, portfolio_pct, volatility }) => {
      const res = await client.invokeSkill<TradeResult>("trade_evaluate", {
        symbol,
        direction,
        strategy: strategy ?? "momentum",
        ...(portfolio_pct !== undefined && { portfolio_pct }),
        ...(volatility !== undefined && { volatility }),
      });
      return formatResponse(res);
    },
  });
}

// ─── Tool 6: reasoning_chain (PREMIUM — x402 required) ───────────────────────

function makeReasoningChainTool(client: SovereignClient): DynamicStructuredTool {
  return new DynamicStructuredTool({
    name: "sovereign_reasoning_chain",
    description:
      "Run SOVEREIGN-Ω's multi-chain parallel reasoner on a question. Spawns 5 independent " +
      "reasoning chains using different methods (deductive, inductive, abductive, analogical, " +
      "counterfactual), checks for contradictions via Inferential plane, then returns the best " +
      "answer with consensus level (STRONG / MODERATE / WEAK / CONTRADICTION). " +
      "PREMIUM skill — requires x402 payment in $PROS (2.0 PROS, 20% discount) or USDC (0.20). " +
      "Configure x402 in SovereignConfig to enable automatic payment.",
    schema: z.object({
      question: z
        .string()
        .describe("The question or problem to reason about"),
      domain: z
        .enum(["trading", "research", "general", "defi", "security", "strategy"])
        .optional()
        .default("general")
        .describe("Domain context for the reasoning"),
      max_chains: z
        .number()
        .int()
        .min(2)
        .max(5)
        .optional()
        .default(5)
        .describe("Number of independent reasoning chains to run (2–5)"),
    }),
    func: async ({ question, domain, max_chains }) => {
      const res = await client.invokeSkill<ReasoningResult>("reasoning_chain", {
        question,
        domain: domain ?? "general",
        max_chains: max_chains ?? 5,
      });
      return formatResponse(res);
    },
  });
}

// ─── Main Export ──────────────────────────────────────────────────────────────

/**
 * Create all SOVEREIGN-Ω LangChain tools from a configured client.
 *
 * Compatible with pharos-agent-kit's tool array pattern:
 *
 * ```ts
 * const pharosTools = createPharosTools(pharosKit);
 * const sovereignTools = createSovereignTools(sovereignClient);
 * const allTools = [...pharosTools, ...sovereignTools];
 * ```
 *
 * @param client - A configured SovereignClient instance
 * @param options - Optional: select which tools to include
 */
export function createSovereignTools(
  client: SovereignClient,
  options: {
    includeFreeSkills?: boolean;
    includePremiumSkills?: boolean;
  } = {}
): DynamicStructuredTool[] {
  const { includeFreeSkills = true, includePremiumSkills = true } = options;

  const tools: DynamicStructuredTool[] = [];

  if (includeFreeSkills) {
    tools.push(
      makeCoherenceEvaluateTool(client),
      makeMoatStatusTool(client),
      makeSilenceCheckTool(client),
      makeIntelligenceScoreTool(client)
    );
  }

  if (includePremiumSkills) {
    tools.push(
      makeTradeEvaluateTool(client),
      makeReasoningChainTool(client)
    );
  }

  return tools;
}

/** Export individual tool factories for selective use */
export {
  makeCoherenceEvaluateTool,
  makeMoatStatusTool,
  makeSilenceCheckTool,
  makeIntelligenceScoreTool,
  makeTradeEvaluateTool,
  makeReasoningChainTool,
};
