/**
 * SOVEREIGN-Ω SDK — MCP (Model Context Protocol) Adapter
 *
 * Wraps SOVEREIGN-Ω skills as MCP-compatible tool definitions.
 * Use this when integrating with MCP hosts (Claude Desktop, Continue.dev,
 * any MCP-compatible orchestrator) instead of LangChain.
 *
 * Also includes a lightweight MCP client that speaks the JSON-RPC 2.0
 * protocol against the SOVEREIGN-Ω /api/v1/mcp endpoint.
 */

import type { SovereignClient } from "./client";

export interface McpToolDefinition {
  name: string;
  description: string;
  inputSchema: {
    type: "object";
    properties: Record<string, unknown>;
    required: string[];
  };
}

export interface McpToolResult {
  content: Array<{ type: "text"; text: string }>;
  isError?: boolean;
}

/**
 * Returns the full list of SOVEREIGN-Ω MCP tool definitions.
 * These match the JSON schema format expected by MCP hosts.
 */
export function getSovereignMcpTools(): McpToolDefinition[] {
  return [
    {
      name: "sovereign_coherence_evaluate",
      description:
        "Run TRION mathematics across five cognitive planes (Perceptual · Inferential · " +
        "Consensus · Self-Reflection · World Model). Returns Ψ score, dynamic threshold Δ, " +
        "and gate decision (ACT or SILENCE). Truth or silence — the silence is information.",
      inputSchema: {
        type: "object",
        properties: {
          query: { type: "string", description: "The action or question to evaluate" },
          domain: {
            type: "string",
            enum: ["trading", "social", "research", "reasoning", "general"],
            description: "Domain context",
          },
        },
        required: ["query"],
      },
    },
    {
      name: "sovereign_moat_status",
      description:
        "Get current intelligence moat (Λ), IQ score, cycle count, silence rate, " +
        "domain mastery, and 30-day projections. Free skill.",
      inputSchema: {
        type: "object",
        properties: {},
        required: [],
      },
    },
    {
      name: "sovereign_silence_check",
      description:
        "Check whether SOVEREIGN-Ω's Silence Protocol would suppress an action. " +
        "Returns silenced flag, failing planes, and reason. Free skill.",
      inputSchema: {
        type: "object",
        properties: {
          action: { type: "string", description: "The action to check" },
          domain: {
            type: "string",
            enum: ["trading", "social", "research", "reasoning", "general"],
          },
        },
        required: ["action"],
      },
    },
    {
      name: "sovereign_intelligence_score",
      description:
        "Get full intelligence report: Λ, IQ, interpretation, cycle count, domain mastery. Free skill.",
      inputSchema: {
        type: "object",
        properties: {
          include_projection: {
            type: "boolean",
            description: "Include 30-day projection",
          },
        },
        required: [],
      },
    },
    {
      name: "sovereign_trade_evaluate",
      description:
        "Bayesian-Kelly trade evaluation: EXECUTE / WAIT / SILENCE, Kelly fraction, " +
        "win probability, expected value, risk level. PREMIUM — x402 payment required.",
      inputSchema: {
        type: "object",
        properties: {
          symbol: { type: "string", description: "Trading pair, e.g. BTC/USDT" },
          direction: { type: "string", enum: ["LONG", "SHORT", "NEUTRAL"] },
          strategy: {
            type: "string",
            enum: ["momentum", "mean_reversion", "breakout", "range", "arbitrage"],
          },
          portfolio_pct: { type: "number", description: "Current portfolio allocation %" },
          volatility: { type: "number", description: "24h volatility as decimal" },
        },
        required: ["symbol", "direction"],
      },
    },
    {
      name: "sovereign_reasoning_chain",
      description:
        "Multi-chain parallel reasoner (deductive, inductive, abductive, analogical, " +
        "counterfactual). Returns best answer with consensus level. PREMIUM — x402 required.",
      inputSchema: {
        type: "object",
        properties: {
          question: { type: "string", description: "The question or problem to reason about" },
          domain: {
            type: "string",
            enum: ["trading", "research", "general", "defi", "security", "strategy"],
          },
          max_chains: { type: "number", description: "Number of reasoning chains (2-5)" },
        },
        required: ["question"],
      },
    },
  ];
}

/**
 * Execute a SOVEREIGN-Ω MCP tool call via the SDK client.
 * Maps MCP tool names to skill invocations.
 */
export async function executeMcpTool(
  client: SovereignClient,
  toolName: string,
  args: Record<string, unknown>
): Promise<McpToolResult> {
  const skillMap: Record<string, string> = {
    sovereign_coherence_evaluate: "coherence_evaluate",
    sovereign_moat_status: "moat_status",
    sovereign_silence_check: "silence_check",
    sovereign_intelligence_score: "intelligence_score",
    sovereign_trade_evaluate: "trade_evaluate",
    sovereign_reasoning_chain: "reasoning_chain",
  };

  const skillId = skillMap[toolName];
  if (!skillId) {
    return {
      content: [{ type: "text", text: `Unknown tool: ${toolName}` }],
      isError: true,
    };
  }

  try {
    const res = await client.invokeSkill(skillId, args);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(res.output, null, 2),
        },
      ],
    };
  } catch (err) {
    return {
      content: [
        {
          type: "text",
          text: `Error invoking ${skillId}: ${err instanceof Error ? err.message : String(err)}`,
        },
      ],
      isError: true,
    };
  }
}
