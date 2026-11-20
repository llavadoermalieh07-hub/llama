import asyncio
import os
import re
from random import choice
from threading import Thread

import discord
from discord.ext import commands
from flask import Flask
from supabase import create_client

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

# Configure these as environment variables in your hosting dashboard.
SUPABASE_URL = os.getenv("SUPABASE_URL")
# Prefer a service-role/secret key, since an anon key may be blocked by RLS.
SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("SUPABASE_SECRET_KEY")
    or os.getenv("SUPABASE_KEY")
)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None


async def send_reply(message, reply):
    """Send Llama's reply and store the user/reply pair in Supabase."""
    await message.channel.send(reply)
    if supabase is None:
        print("Supabase memory not saved: set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_KEY).")
        return

    try:
        row = {
            "user_id": str(message.author.id),
            "username": str(message.author),
            "message": message.content,
            "llama_reply": reply,
            "content": message.content,
            "bot_reply": reply,
        }
        result = await asyncio.to_thread(
            lambda: supabase.table("llama_memories").insert(row).execute()
        )
        print(f"Saved conversation to Supabase: {result}")
    except Exception as error:
        # Keep the Discord bot responsive if Supabase is temporarily unavailable.
        print(f"Failed to save conversation to Supabase: {error}")


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
    """Make a short, cute story inspired by the user's chosen topic."""
    topic = topic.strip(" .,!?:;\"'") or ("a little adventure" if language == "en" else "munting adventure")
    if language == "en":
        return choice((
            f"Once upon a time, a tiny bunny found a little bit of magic in {topic}. "
            "With a new friend by their side, they turned it into a garden where everyone felt welcome. "
            "That night, the stars twinkled just for them. The end! ❤️✨",
            f"One sunny day, {topic} led a curious kitten to a shy little cloud. "
            "Together they made the softest rainbows, then shared them with the whole town. "
            "The kitten went home with a new friend and a very happy heart. The end! ❤️✨",
            f"In a cozy little world of {topic}, a small mouse discovered a lost button that belonged to the moon. "
            "A firefly helped carry it home, and the moon shone extra brightly as a thank-you. "
            "They all wished each other sweet dreams. The end! ❤️✨",
        ))
    return choice((
        f"Isang araw, may munting kuneho na nakakita ng kaunting mahika sa {topic}. "
        "Kasama ang bagong kaibigan, ginawa nila itong hardin kung saan masaya at welcome ang lahat. "
        "Kinagabihan, kumindat ang mga bituin para sa kanila. The end! ❤️✨",
        f"Isang maaraw na umaga, dinala ng {topic} ang usisang kuting sa isang mahiyaing ulap. "
        "Sabay silang gumawa ng makukulay na bahaghari at ibinahagi iyon sa buong bayan. "
        "Umuwi ang kuting na may bagong kaibigan at masayang puso. The end! ❤️✨",
        f"Sa isang munting mundong puno ng {topic}, nakakita ang maliit na daga ng butones na nahulog mula sa buwan. "
        "Tinulungan siya ng alitaptap na isauli iyon, kaya lumiwanag ang buwan bilang pasasalamat. "
        "Sabay-sabay silang bumati ng magandang gabi. The end! ❤️✨",
    ))


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
        await send_reply(message, reply)
        return
    if msg.startswith("!price") or "price" in msg or "how much" in msg or "magkano" in msg or "presyo" in msg:
        if english:
            reply = "It's only 15 PHP per set, beh! ❤️ Each set has a cover + 3 inside pages. Choose from Desert, Strawberries, Starry Hill, and E2 Garden!"
        else:
            reply = "Beh! 15 PHP lang per set! ❤️ May cover + 3 inside pages na! Pili ka: Desert, Strawberries, Starry Hill, at E2 Garden!"
        await send_reply(message, reply)
        return
    if msg.startswith("!order") or "order" in msg or "bili" in msg:
        if english:
            reply = f"Choose something from the shop, then DM Ermalieh, beh! ❤️\n{SHOP_URL}"
        else:
            reply = f"Pili ka sa shop tapos DM mo si Ermalieh beh! ❤️\n{SHOP_URL}"
        await send_reply(message, reply)
        return

    # Stories are handled before general questions, so a story request gets a story.
    # Support casual requests like "Llama, kwento about cats" as well.
    story_match = re.search(
        r"\b(?:llama\s*[,!: -]*\s*)?(?:kwento|kuwento)\s+(?:about|tungkol\s+sa)\s+(.+)",
        text,
        flags=re.IGNORECASE,
    )
    if not story_match:
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
            await send_reply(message, prompt)
        else:
            await send_reply(message, make_story(topic, language))
        return

    # Introduce Llama before the general replies and fallback.
    if any(phrase in msg for phrase in ("about yourself", "who are you", "sino ka", "pakilala", "tell me about")):
        if english:
            reply = "Hi beh! I'm Llama! ❤️ I'm your cute little friend here in Discord. I love chatting with you, making cute stories, and helping you with your shop! What do you want to talk about today?"
        else:
            reply = "Hi beh! Ako si Llama! ❤️ Yung cute mong kaibigan dito sa Discord. Mahilig ako makipagkwentuhan, gumawa ng cute stories, at tumulong sa shop mo! Anong kwento natin today?"
        await send_reply(message, reply)
        return

    # Respond to the actual question in the language the user used.
    if "sure" in msg:
        reply = "Yes beh, I'm sure! ❤️" if english else "Oo naman beh, sure ako! ❤️"
        await send_reply(message, reply)
        return
    if "how are you" in msg or "kamusta ka" in msg or "kumusta ka" in msg:
        if english:
            reply = "I'm doing great, beh—ready to chat and make cute stories! How are you? ❤️"
        else:
            reply = "Okay naman ako, beh—ready makipagkuwentuhan at gumawa ng cute stories! Ikaw, kamusta? ❤️"
        await send_reply(message, reply)
        return
    if "buhay ka pala" in msg or "are you alive" in msg or "you alive" in msg:
        if english:
            reply = "Yep, I'm alive and ready to chat, beh! What can I help you with? ❤️🐾"
        else:
            reply = "Oo naman, buhay na buhay sa chat, beh! Naka-ready akong tumulong at magkuwento. ❤️🐾"
        await send_reply(message, reply)
        return
    if "llama" in msg and any(word in msg for word in ("hello", "hi", "hey", "hoy")):
        if english:
            reply = f"Hi {message.author.mention}, Llama's here, beh! What story or question do you have? ❤️"
        else:
            reply = f"Hi {message.author.mention}, andito si Llama, beh! Anong kuwento o tanong mo? ❤️"
        await send_reply(message, reply)
        return
    if any(word in msg for word in ("hello", "hi", "hey", "kamusta", "kumusta")):
        if english:
            reply = f"Hi {message.author.mention}, beh! Welcome! How can I help you? ❤️"
        else:
            reply = f"Hi {message.author.mention}, beh! Welcome! Anong maitutulong ko sa'yo? ❤️"
        await send_reply(message, reply)
        return
    if "help" in msg or "tulong" in msg:
        if english:
            reply = "Of course, beh! Tell me what you need—I can also make a cute story. ❤️"
        else:
            reply = "Sure, beh! Sabihin mo lang kung anong kailangan mo—puwede rin akong gumawa ng cute story. ❤️"
        await send_reply(message, reply)
        return
    if "llama" in msg:
        if english:
            reply = choice((
                "Hmm beh, I didn't quite get that, but I'm here! ❤️ Want me to make you a story or chat about something?",
                "I'm not sure I understood, beh, but I'm listening! ❤️ Want a cute story or just a chat?",
                "Hmm, could you tell me a little more, beh? ❤️ I can make a story or talk with you!",
            ))
        else:
            reply = choice((
                "Hmm beh, hindi ko masyado na-gets, pero andito lang ako! ❤️ Gusto mo gawan kita ng story o kwentuhan tayo?",
                "Medyo nalito ako, beh, pero nakikinig ako! ❤️ Story ba o kwentuhan muna tayo?",
                "Hmm, kwento mo pa sa'kin, beh? ❤️ Puwede kitang gawan ng story o makipagkuwentuhan!",
            ))
        await send_reply(message, reply)
        return

    # Keep command processing, then reply to other messages so each user message
    # receives a reply and is saved as a message/reply pair.
    await bot.process_commands(message)
    if english:
        reply = "I'm here, beh! ❤️ Tell me a little more, or ask me for a cute story."
    else:
        reply = "Andito lang ako, beh! ❤️ Kwento ka pa, o mag-request ka ng cute story."
    await send_reply(message, reply)


bot.run(os.getenv("TOKEN"))
