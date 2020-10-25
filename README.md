# MindfulnessBot
A discord bot fostering a mindful lifestyle

# Dev Setup
Currently Reading off of [this](https://realpython.com/how-to-make-a-discord-bot-python/) tutorial.

You will need to install
`pip install -U discord.py`
`pip install -U dotenv`
`pip install -U pymongo`

You will also need to install and set up mongo db.  [OSX install instructions](https://github.com/mongodb/homebrew-brew)

# Environment Variables
You'll need the discord token in a `.env` file

The bot will connect to discord by running `python mindful_bot.py`

# Docker notes

Install Docker via brew or something

To start the dockerized mongo instance:
`docker-compose up`

To rebuild python:
`docker-compose up -d --no-deps --build discord_bot`

To Access Mongo:

`docker ps`
`docker exec -it <mongo container name> mongo`

You will need a hostname in your .env file to connect to mongo.
This will be
```
MONGO_HOSTNAME="mongodb_container"
```
if using docker, otherwise if running mongo yourself,

```
MONGO_HOSTNAME="localhost"
```
