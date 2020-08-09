import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix= '!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='hello', help = "I'm saying hello!")
async def say_hello(context):
    response = "Hello, World!"
    await context.send(response)


@bot.command(name='questions', help = "Asks mindfulness questions")
async def say_hello(context):
    questions = [
        "What are the three most important tasks for the day?",
        "Are those tasks specific, measurable, achievable, relevant, and time-bound?"
    ]

    for question in questions:
        await context.send(question)

bot.run(DISCORD_TOKEN)
