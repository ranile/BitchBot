from discord import Color
from random import randint

def random_discord_color():
    return Color(value=randint(0, 16777215))