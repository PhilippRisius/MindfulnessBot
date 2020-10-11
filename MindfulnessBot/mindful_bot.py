import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from mongo_client import MindfulMongo

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix= '!')
client = MindfulMongo('localhost', 27017, "MindfulBot")

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name="iam", help = "Tell the bot who you are")
async def tell_user(context, name):
    author = context.author
    author_name = author.name
    discord_id = author.id

    saved_user = client.save_user({
        "discord_id": discord_id,
        "discord_username": author_name,
        "name": name
    })

    response = f'Thanks, I now know who you are!'
    await context.send(response)

@bot.command(name="whoami", help = "Who does the bot think you are?")
async def say_user(context):
    author = context.author
    author_name = author.name
    discord_id = author.id

    user = client.retrieve_user(discord_id)

    if user is None:
        response = f'Hello {author_name}, your discord id is {discord_id}!'
    else:
        response = f"I know you!  Hello {user['name']}, your discord id is {user['discord_id']}, and around here you are known as {user['discord_username']}!"

    await context.send(response)

@bot.command(name='hello', help = "I'm saying hello!")
async def say_hello(context):
    response = "Hello, World!"
    await context.send(response)

@bot.command(name='questions', help = "Asks mindfulness questions")
async def say_questions(context):
    questions = [
        "What are the three most important tasks for the day?",
        "Are those tasks specific, measurable, achievable, relevant, and time-bound?"
    ]

    for question in questions:
        await context.send(question)

bot.run(DISCORD_TOKEN)
