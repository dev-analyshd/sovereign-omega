import os
from social.social_gate import SocialGate
from social.content_generator import ContentGenerator

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False


class TelegramAgent:
    """SOVEREIGN-Ω Telegram bot. Always gated. Always coherent or silent."""

    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.gate = SocialGate()
        self.generator = ContentGenerator()

        if TELEGRAM_AVAILABLE and self.token:
            self.app = Application.builder().token(self.token).build()
            self._setup_handlers()
        else:
            self.app = None

    def _setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("ask", self.cmd_ask))
        self.app.add_handler(CommandHandler("status", self.cmd_status))
        self.app.add_handler(CommandHandler("moat", self.cmd_moat))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def cmd_start(self, update: Update, context):
        await update.message.reply_text(
            "SOVEREIGN-Ω online.\n"
            "I only respond when my cognitive planes are coherent.\n"
            "Ω(a,t) = [Ψ(t) ≥ Δ(t)] · R(a,t) · e^(Λ·t)\n"
            "Use /ask [question] to query me."
        )

    async def cmd_ask(self, update: Update, context):
        if not context.args:
            await update.message.reply_text("Provide a question: /ask [your question]")
            return
        await self._process_query(update, " ".join(context.args))

    async def cmd_status(self, update: Update, context):
        from learning.intelligence_score import IntelligenceScorer
        from core.moat_accumulator import MoatAccumulator
        scorer = IntelligenceScorer()
        moat = MoatAccumulator()
        iq = await scorer.compute()
        text = (
            f"SOVEREIGN-Ω STATUS\n"
            f"Λ (Moat): {moat.get_current_lambda():.8f}\n"
            f"Cycles: {moat.n_cycles}\n"
            f"IQ Score: {iq:.8f}\n"
        )
        await update.message.reply_text(text)

    async def cmd_moat(self, update: Update, context):
        from learning.intelligence_score import IntelligenceScorer
        scorer = IntelligenceScorer()
        data = await scorer.get_breakdown()
        text = (
            f"MOAT STATUS\n"
            f"IQ: {data['iq_score']:.8f}\n"
            f"Λ: {data['lambda']:.8f}\n"
            f"e^(Λ·t): {data['exp_term']:.6f}\n"
            f"Cycles: {data['n_cycles']}\n"
            f"Status: {data['interpretation']}"
        )
        await update.message.reply_text(text)

    async def handle_message(self, update: Update, context):
        await self._process_query(update, update.message.text)

    async def _process_query(self, update, query: str):
        content = await self.generator.generate_insight(query, "telegram")
        if not content:
            await update.message.reply_text("[SILENCE] Cannot generate coherent response.")
            return

        gate_result = await self.gate.evaluate(content, {"query": query}, "telegram")
        if not gate_result["approved"]:
            await update.message.reply_text(
                f"[SILENCE] Ψ={gate_result['psi']:.4f} < Δ=0.70\nReason: {gate_result['reason']}"
            )
            return

        await update.message.reply_text(f"{content}\n\n—SOVEREIGN-Ω | Ψ={gate_result['psi']:.4f}")

    def run_agent(self):
        if self.app:
            self.app.run_polling()
        else:
            print("[TELEGRAM] No token or telegram unavailable. Agent not started.")
