import os
import asyncio
from social.social_gate import SocialGate
from social.content_generator import ContentGenerator
from social.credibility_moat import CredibilityMoat

try:
    import discord
    from discord.ext import commands, tasks
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False


class DiscordAgent:
    """
    SOVEREIGN-Ω's Discord presence. Responds only when Psi >= 0.70. Rule 13.
    """

    def __init__(self):
        self.gate = SocialGate()
        self.generator = ContentGenerator()
        self.credibility = CredibilityMoat()
        self.token = os.getenv("DISCORD_BOT_TOKEN")
        self.channel_id = int(os.getenv("DISCORD_CHANNEL_ID", "0"))
        self.bot = None

        if DISCORD_AVAILABLE and self.token:
            intents = discord.Intents.default()
            intents.message_content = True
            self.bot = commands.Bot(command_prefix="!", intents=intents)
            self._register_events()

    def _register_events(self):
        bot = self.bot

        @bot.event
        async def on_ready():
            print(f"[DISCORD] SOVEREIGN-Ω connected as {bot.user}")

        @bot.event
        async def on_message(message):
            if message.author == bot.user:
                return
            if bot.user.mentioned_in(message) or message.content.startswith("!ask"):
                query = message.content.replace(f"<@{bot.user.id}>", "").replace("!ask", "").strip()
                if not query:
                    await message.reply("Ask me something specific.")
                    return

                content = await self.generator.generate_insight(query, "discord")
                if not content:
                    await message.reply("**[SILENCE]** Cognitive planes insufficient. Ask again with more context.")
                    return

                gate_result = await self.gate.evaluate(content, {"query": query}, "discord")
                if not gate_result["approved"]:
                    await message.reply(f"**[SILENCE]** Ψ={gate_result['psi']:.4f} < Δ=0.70. {gate_result['reason']}")
                    return

                if discord:
                    embed = discord.Embed(description=content, color=0x00FF88)
                    embed.set_footer(text=f"SOVEREIGN-Ω | Ψ={gate_result['psi']:.4f} | Gate: OPEN")
                    await message.reply(embed=embed)
                else:
                    await message.reply(f"{content}\n— Ψ={gate_result['psi']:.4f}")

                await self.credibility.accumulate("discord", gate_result["psi"])

            await bot.process_commands(message)

    def run_agent(self):
        if self.bot and self.token:
            self.bot.run(self.token)
        else:
            print("[DISCORD] No token or discord.py unavailable. Agent not started.")
