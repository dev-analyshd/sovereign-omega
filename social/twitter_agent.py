import os
import asyncio
from social.social_gate import SocialGate
from social.content_generator import ContentGenerator
from social.credibility_moat import CredibilityMoat

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False


class TwitterAgent:
    """
    SOVEREIGN-Ω's presence on X/Twitter.
    Never posts without SocialGate approval (Psi >= 0.70). Rule 13.
    Silence on X is the default.
    """

    def __init__(self):
        self.gate = SocialGate()
        self.generator = ContentGenerator()
        self.credibility = CredibilityMoat()

        if TWEEPY_AVAILABLE:
            self.client = tweepy.AsyncClient(
                bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
                consumer_key=os.getenv("TWITTER_API_KEY"),
                consumer_secret=os.getenv("TWITTER_API_SECRET"),
                access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
                access_token_secret=os.getenv("TWITTER_ACCESS_SECRET"),
            )
        else:
            self.client = None

    async def post_if_coherent(self, topic: str, domain: str) -> dict:
        content = await self.generator.generate_insight(topic, domain)
        if not content or len(content) > 280:
            return {"posted": False, "reason": "Content generation failed or too long"}

        gate_result = await self.gate.evaluate(content, {"topic": topic}, "twitter")
        if not gate_result["approved"]:
            return {"posted": False, "reason": gate_result["reason"], "psi": gate_result["psi"]}

        if self.client is None:
            print(f"[TWITTER SIM] Would post: {content[:60]}...")
            await self.credibility.accumulate("twitter", gate_result["psi"])
            return {"posted": True, "tweet_id": "sim", "psi": gate_result["psi"], "content": content}

        try:
            tweet = await self.client.create_tweet(text=content)
            tweet_id = tweet.data["id"]
            await self.credibility.accumulate("twitter", gate_result["psi"])
            print(f"[TWITTER] Posted tweet {tweet_id}: {content[:60]}...")
            return {"posted": True, "tweet_id": tweet_id, "psi": gate_result["psi"]}
        except Exception as e:
            print(f"[TWITTER] Post failed: {e}")
            return {"posted": False, "reason": str(e)}
