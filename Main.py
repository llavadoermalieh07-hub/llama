import os
import re
from threading import Thread

import discord
from discord.ext import commands
from flask import Flask

# Small health-check web server for hosting platforms.
app = Flask(__name__)


@app.route("/")
def home():
    return "Llama is alive! 💖"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


Thread(target=run_web, daemon=True).start()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

SHOP_URL = "https://kawaii-shop-update.netlify.app/"

ENGLISH_WORDS = {
    "a", "about", "are", "can", "create", "do", " hello", "help", "how",
    "i", "make", "me", "please", "price", "sure", "tell", "the", "there",
    "want", "what", "write", "you", "your", "alive", "story", "order", "shop",
}
TAGALOG_WORDS = {
    "ako", "ano", "at", "ba", "bakit", "buhay", "gawa", "gawan", "gumawa",
    "ka", "kamusta", "kumusta", "lang", "magkano", "musta", " paano", "paano",
    "presyo", "saan", "sa", "si", "sige", "tulong", "tungkol", "ikaw", "ko",
    "mo", "naman", "oo", "hindi", "beh", "kuwento", "kwento", "bili",
}


def detect_language(text):
    """Choose English when English keywords outnumber Tagalog keywords; otherwise use Taglish."""
    words = set(re.findall(r"[a-zA-Z]+", text.lower()))
    english_count = len(words & ENGLISH_WORDS)
    tagalog_count = len(words & TAGALOG_WORDS)
    return "en" if english_count > tagalog_count else "tl"


def make_story(topic, language="tl"):
    """Make a short, cute story that includes the user's chosen topic."""
    topic = topic.strip(" .,!?:;\"'") or ("a little adventure" if language == "en" else "munting adventure")
    if language == "en":
        return (
            f"Once upon a time, beh, there was a little friend named {topic}. "
            "One morning, they found a tiny, sparkling star who had lost its way. "
            "They helped the star find its way home, and it granted them one wish: "
            "to fill the world with kindness and smiles. From then on, they shared "
            "happiness wherever they went. The end! ❤️✨"
        )
    return (
        f"Noong unang panahon, beh, may isang munting kaibigan na nagngangalang {topic}. "
        "Isang umaga, nakakita siya ng kumikislap na bituin na naligaw. "
        "Tinulungan niya itong makauwi sa langit, at bilang pasasalamat, "
        "binigyan siya nito ng wish na punuin ng kabaitan at smiles ang mundo. "
        "Mula noon, nagbahagi sila ng saya sa lahat. The end! ❤️✨"
    )


@bot.event
async def on_ready():
    print(f"Online na si {bot.user}!")


@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="📩-new-folks")
    if channel:
        await channel.send(
            f"Hi {member.mention}! Welcome sa E2 - generous Discord! 💖🐾 "
            "Welcome sa Llama Storytelling Gallery! Type **!shop** para makita ang shop namin!"
        )


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    text = message.content.strip()
    msg = text.lower()
    language = detect_language(text)
    english = language == "en"

    # Keep the existing shop commands working, matching the user's language.
    if msg.startswith(("!shop", "!store")):
        if english:
            reply = f"Here's our shop, beh! 👇\n{SHOP_URL}\nWhat are you looking for? ❤️"
        else:
            reply = f"Eto yung shop namin beh! 👇\n{SHOP_URL}\nAnong hanap mo? ❤️"
        await message.channel.send(reply)
        return
    if msg.startswith("!price") or "price" in msg or "how much" in msg or "magkano" in msg or "presyo" in msg:
        if english:
            reply = "It's only 15 PHP per set, beh! ❤️ Each set has a cover + 3 inside pages. Choose from Desert, Strawberries, Starry Hill, and E2 Garden!"
        else:
            reply = "Beh! 15 PHP lang per set! ❤️ May cover + 3 inside pages na! Pili ka: Desert, Strawberries, Starry Hill, at E2 Garden!"
        await message.channel.send(reply)
        return
    if msg.startswith("!order") or "order" in msg or "bili" in msg:
        if english:
            reply = f"Choose something from the shop, then DM Ermalieh, beh! ❤️\n{SHOP_URL}"
        else:
            reply = f"Pili ka sa shop tapos DM mo si Ermalieh beh! ❤️\n{SHOP_URL}"
        await message.channel.send(reply)
        return

    # Stories are handled before general questions, so a story request gets a story.
    story_match = re.search(
        r"(?:make|write|tell me|create)\s+(?:me\s+)?(?:a\s+)?story\s+about\s+(.+)",
        text,
        flags=re.IGNORECASE,
    )
    if not story_match:
        story_match = re.search(
            r"(?:gumawa|gawan|gawa)\s+(?:ka\s+)?(?:ng\s+)?story\s+(?:tungkol\s+sa|about)?\s*(.*)",
            text,
            flags=re.IGNORECASE,
        )
    if story_match:
        topic = story_match.group(1).strip()
        if not topic:
            prompt = "What topic should the story be about, beh? ❤️" if english else "Anong topic ng story, beh? ❤️"
            await message.channel.send(prompt)
        else:
            await message.channel.send(make_story(topic, language))
        return

    # Respond to the actual question in the language the user used.
    if "sure" in msg:
        reply = "Yes beh, I'm sure! ❤️" if english else "Oo naman beh, sure ako! ❤️"
        await message.channel.send(reply)
        return
    if "how are you" in msg or "kamusta ka" in msg or "kumusta ka" in msg:
        if english:
            reply = "I'm doing great, beh—ready to chat and make cute stories! How are you? ❤️"
        else:
            reply = "Okay naman ako, beh—ready makipagkuwentuhan at gumawa ng cute stories! Ikaw, kamusta? ❤️"
        await message.channel.send(reply)
        return
    if "buhay ka pala" in msg or "are you alive" in msg or "you alive" in msg:
        if english:
            reply = "Yep, I'm alive and ready to chat, beh! What can I help you with? ❤️🐾"
        else:
            reply = "Oo naman, buhay na buhay sa chat, beh! Naka-ready akong tumulong at magkuwento. ❤️🐾"
        await message.channel.send(reply)
        return
    if "llama" in msg and any(word in msg for word in ("hello", "hi", "hey", "hoy")):
        if english:
            reply = f"Hi {message.author.mention}, Llama's here, beh! What story or question do you have? ❤️"
        else:
            reply = f"Hi {message.author.mention}, andito si Llama, beh! Anong kuwento o tanong mo? ❤️"
        await message.channel.send(reply)
        return
    if any(word in msg for word in ("hello", "hi", "hey", "kamusta", "kumusta")):
        if english:
            reply = f"Hi {message.author.mention}, beh! Welcome! How can I help you? ❤️"
        else:
            reply = f"Hi {message.author.mention}, beh! Welcome! Anong maitutulong ko sa'yo? ❤️"
        await message.channel.send(reply)
        return
    if "help" in msg or "tulong" in msg:
        if english:
            reply = "Of course, beh! Tell me what you need—I can also make a cute story. ❤️"
        else:
            reply = "Sure, beh! Sabihin mo lang kung anong kailangan mo—puwede rin akong gumawa ng cute story. ❤️"
        await message.channel.send(reply)
        return
    if "llama" in msg:
        if english:
            reply = "Yes beh, I'm here! Ask me anything or tell me a story topic. ❤️"
        else:
            reply = "Yes beh, andito ako! Tanong ka lang o sabihin ang topic ng story na gusto mo. ❤️"
        await message.channel.send(reply)
        return

    # on_message overrides the default command handler, so pass commands through.
    await bot.process_commands(message)


bot.run(os.getenv("TOKEN"))
