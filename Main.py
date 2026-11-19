import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread
import os
from supabase import create_client

# UTAN NI LLAMA - Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_memory(user_id, username, message, llama_reply):
    supabase.table("llama_memories").insert({
        "user_id": str(user_id),
        "username": username,
        "message": message,
        "llama_reply": llama_reply
    }).execute()

def get_memories(user_id):
    data = supabase.table("llama_memories").select("*").eq("user_id", str(user_id)).order("created_at", desc=True).limit(5).execute()
    return data.data
Compose

app = Flask('')
@app.route('/')
def home():
    return "Llama Bot is Online! 💖"
def run():
    app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Online na si {bot.user}!")

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="📩-new-folks")
    if channel:
        await channel.send(f"Hi {member.mention}! Welcome sa E2 - generous Discord! 💖🐾 Welcome sa Llama Storytelling Gallery! Anong hanap mo beh? Paano kita matutulungan? Type **!shop** para makita yung shop!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    msg = message.content.lower()

    english_words = ["hello", "hi", "hey", "how much", "price", "how to", "order", "shop", "what", "how are you", "help"]
    tagalog_words = ["kamusta", "magkano", "paano", "bili", "presyo"]
    is_english = any(w in msg for w in english_words) and not any(w in msg for w in tagalog_words)
                if "llama" in msg:
                if is_english:
                      await message.channel.send(f"Yes beh? I'm here! ❤️ How can I help you? What story do you want?")
            return
        else:
                      await message.channel.send(f"Yes beh? Andito ako! ❤️ Paano kita matutulungan? Anong story gusto mo?")
            return
                if "hi" in msg or "hello" in msg or "hey" in msg or "kamusta" in msg:
                if is_english:
                      await message.channel.send(f"Hi {message.author.mention}! Welcome beh! ❤️ What are you looking for? How can I help you?"
        else:
                      await message.channel.send(f"Hi {message.author.mention}! Welcome beh! ❤️ Anong hanap mo? Paano kita matutulungan?")
           elif "magkano" in msg or "price" in msg or "how much" in msg or "presyo" in msg:
                if is_english:
                      await message.channel.send(f"Only 15 PHP beh! 3 Pages + Cover already! ❤️ What story do you want?")
         else:
                      await message.channel.send(f"15 PHP lang beh! 3 Pages + Cover na! ❤️ Anong story gusto mo? Paano pa kita matutulungan?")
           elif "order" in msg or "paano" in msg or "bili" in msg or "how to" in msg:
                if is_english:
                      await message.channel.send(f"It's easy to order beh! 1. Pick here: https://kawaii-shop-update.netlify.app 2. Tell me your story!")
         else:
                      await message.channel.send(f"Madali lang mag-order beh! 1. Pili ka dito: https://kawaii-shop-update.netlify.app 2. Sabihin mo sakin story mo!")
           elif "shop" in msg or "story" in msg:
               if is_english:
                      await message.channel.send(f"Here is my shop beh! ❤️ https://kawaii-shop-update.netlify.app What are you looking for?")
         else:
                      await message.channel.send(f"Eto yung shop ko beh! ❤️ https://kawaii-shop-update.netlify.app Anong hanap mo? Pang-cute ba?")
           elif "?" in msg:
             if is_english:
                     await message.channel.send(f"Ay beh, I want to help you! ❤️ What are you looking for? How can I help you? Just type it!")
         else:
                     await message.channel.send(f"Ay beh, gusto ko tulungan ka! ❤️ Anong hanap mo? Paano kita matutulungan? Type mo lang!")
        await bot.process_commands(message)
@bot.command()
async def shop(ctx):
    await ctx.send("Eto yung shop ko beh! 👇 https://kawaii-shop-update.netlify.app")
@bot.command()
async def price(ctx):
    await ctx.send("15 PHP lang beh! 3 Pages + Cover na! 💖")
@bot.command()
async def order(ctx):
    await ctx.send("Pili ka sa shop tapos DM mo si Ermalieh beh!")

keep_alive()
bot.run(os.environ.get("TOKEN"))
