import keys
from BitchBot import BitchBot

cogs = ["admin", "cause", "emojis", "internet", "starboard", 'stats', 'jsk', 'mod', 'misc', 'reminders',
        'config', 'music']

bot = BitchBot(cogs=cogs)

bot.run(keys.bot)
