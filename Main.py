import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

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
    if "hi" in msg or "hello" in msg or "hey" in msg:
        await message.channel.send(f"Hi {message.author.mention}! Welcome beh! 💖 Anong hanap mo? Paano kita matutulungan? Gusto mo ba makita yung shop? Type **!shop**!")
    elif "magkano" in msg or "price" in msg or "how much" in msg or "presyo" in msg:
        await message.channel.send(f"15 PHP lang beh! 3 Pages + Cover na! 💖 Anong story gusto mo? Paano pa kita matutulungan?")
    elif "order" in msg or "paano" in msg or "bili" in msg:
        await message.channel.send(f"Madali lang mag-order beh! 1. Pili ka dito: https://kawaii-shop-update.netlify.app 2. DM mo si Ermalieh! Anong story ba hanap mo beh?")
    elif "shop" in msg or "story" in msg:
        await message.channel.send(f"Eto yung shop ko beh! 👇 https://kawaii-shop-update.netlify.app Anong hanap mo? Pang-cute ba? Pang-adventure? Sabihin mo lang!")
    elif "?" in msg:
        await message.channel.send(f"Ay beh, gusto ko tulungan ka! 💖 Anong hanap mo? Paano kita matutulungan? Type mo lang **!shop**, **!price**, o **!order**!")
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
