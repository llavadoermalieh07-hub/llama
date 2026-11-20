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


def make_story(topic):
    """Make a short, cute story that includes the user's chosen topic."""
    topic = topic.strip(" .,!?:;\"'") or "a little adventure"
    return (
        f"Once upon a time, beh, may isang munting kaibigan na nagngangalang {topic}. "
        f"Isang umaga, nakakita siya ng kumikinang na bituin sa daan. "
        f"Tinulungan niya itong makauwi sa langit, at bilang pasasalamat, "
        f"binigyan siya nito ng isang wish: punuin ng saya at kabaitan ang buong mundo. "
        f"Mula noon, araw-araw silang nagbahagi ng smiles sa lahat. The end! ❤️✨"
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

    # Keep the existing shop commands working.
    if msg.startswith(("!shop", "!store")):
        await message.channel.send(
            f"Eto yung shop namin beh! 👇\n{SHOP_URL}\nAnong hanap mo? ❤️"
        )
        return
    if msg.startswith("!price") or "price" in msg or "how much" in msg or "magkano" in msg or "presyo" in msg:
        await message.channel.send(
            "Beh! 15 PHP lang per set! ❤️ May cover + 3 inside pages na! "
            "Pili ka: Desert, Strawberries, Starry Hill, at E2 Garden!"
        )
        return
    if msg.startswith("!order") or "order" in msg or "bili" in msg:
        await message.channel.send(
            f"Pili ka sa shop tapos DM mo si Ermalieh beh! ❤️\n{SHOP_URL}"
        )
        return

    # Stories are handled before general questions, so a story request gets a story.
    story_match = re.search(
        r"(?:make|write|tell me|create)\s+(?:me\s+)?(?:a\s+)?story\s+about\s+(.+)",
        text,
        flags=re.IGNORECASE,
    )
    if not story_match:
        story_match = re.search(
            r"(?:gumawa|gawan)\s+(?:ka\s+)?(?:ng\s+)?story\s+(?:tungkol\s+sa|about)\s+(.+)",
            text,
            flags=re.IGNORECASE,
        )
    if story_match:
        await message.channel.send(make_story(story_match.group(1)))
        return

    # Respond to the actual question instead of replying with the same generic line.
    if "how are you" in msg or "kamusta ka" in msg or "kumusta ka" in msg:
        await message.channel.send("Okay naman ako, beh—ready makipagkuwentuhan at gumawa ng cute stories! Ikaw, kamusta? ❤️")
        return
    if "buhay ka pala" in msg or "are you alive" in msg or "you alive" in msg:
        await message.channel.send("Oo naman, buhay na buhay sa chat, beh! Naka-ready akong tumulong at magkuwento. ❤️🐾")
        return
    if "llama" in msg and any(word in msg for word in ("hello", "hi", "hey", "hoy")):
        await message.channel.send(f"Hi {message.author.mention}, andito si Llama, beh! Anong kuwento o tanong mo? ❤️")
        return
    if any(word in msg for word in ("hello", "hi", "hey", "kamusta", "kumusta")):
        await message.channel.send(f"Hi {message.author.mention}, beh! Welcome! Anong maitutulong ko sa'yo? ❤️")
        return
    if "help" in msg or "tulong" in msg:
        await message.channel.send("Sure, beh! Sabihin mo lang kung anong kailangan mo—puwede rin akong gumawa ng cute story. ❤️")
        return
    if "llama" in msg:
        await message.channel.send("Yes beh, andito ako! Tanong ka lang o sabihin ang topic ng story na gusto mo. ❤️")
        return

    # on_message overrides the default command handler, so pass commands through.
    await bot.process_commands(message)


bot.run(os.getenv("TOKEN"))
