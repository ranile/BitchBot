import keys
from BitchBot import BitchBot

cogs = [
    'jsk',
    "cause",
    "emojis",
    "fun",
    "starboard",
    'stats',
    'mod',
    'misc',
    'reminders',
    'config',
    'music',
    'test'
]

bot = BitchBot(cogs=cogs)

bot.run(keys.bot)
