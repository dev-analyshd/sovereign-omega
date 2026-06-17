/**
 * sovereign-omega-sdk
 *
 * Pharos-native SOVEREIGN-Ω skills as LangChain tools.
 * Plug TRION coherence scoring, Bayesian-Kelly trading, and x402-gated
 * premium reasoning into any pharos-agent-kit agent in two lines.
 *
 * ─── Quick Start ───────────────────────────────────────────────────────────
 *
 *   import { SovereignOmegaKit, createSovereignTools } from "sovereign-omega-sdk";
 *   import { PharosAgentKit, createPharosTools }       from "pharos-agent-kit";
 *
 *   const sovereign = new SovereignOmegaKit({ baseUrl: "https://your-agent.replit.dev" });
 *   const pharos    = new PharosAgentKit(privateKey, rpcUrl, { OPENAI_API_KEY: key });
 *
 *   const tools = [
 *     ...createPharosTools(pharos),
 *     ...createSovereignTools(sovereign.client),
 *   ];
 *
 * ───────────────────────────────────────────────────────────────────────────
 */

// Main kit class
export { SovereignOmegaKit } from "./kit";

// HTTP client
export { SovereignClient, X402Error } from "./client";

// LangChain tool factory + individual factories
export {
  createSovereignTools,
  makeCoherenceEvaluateTool,
  makeMoatStatusTool,
  makeSilenceCheckTool,
  makeIntelligenceScoreTool,
  makeTradeEvaluateTool,
  makeReasoningChainTool,
} from "./tools";

// MCP adapter
export {
  getSovereignMcpTools,
  executeMcpTool,
} from "./mcp";

// All types
export type {
  SovereignConfig,
  X402Config,
  X402PaymentRequest,
  X402Required,
  PlaneBreakdown,
  CoherenceResult,
  MoatResult,
  TradeResult,
  SilenceResult,
  IntelligenceResult,
  ReasoningResult,
  SkillResponse,
  McpToolDefinition,
  McpToolResult,
} from "./types";
export type { McpToolDefinition as MCP_ToolDefinition } from "./mcp";
