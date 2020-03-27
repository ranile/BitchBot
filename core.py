import keys
from BitchBot import BitchBot

cogs = ["admin", "cause", "emojis", "internet", "starboard", 'stats', 'jsk', 'logs', 'mod', 'misc', 'reminders',
        'covid19']

bot = BitchBot(cogs=cogs)

bot.run(keys.bot)
