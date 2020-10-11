import asyncio
import datetime
import os
import random

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

DEV_USER = 'Petr#9767'


class Question:
    def __init__(self):
        self.salt = random.randbytes(64)
        self.id = self.__hash__()

    def __hash__(self):
        return self.salt


def store_question_schedule(author, days_time, questions_id):
    """Store the question schedule for author in the database"""
    pass


def store_question_text(questions):
    """Store questions text and reaction scheme in database"""
    pass