import keys
from BitchBot import BitchBot

cogs = ["admin", "cause", "emojis", "internet", "starboard", 'stats', 'jsk', 'logs', 'mod', 'misc', 'reminders']

bot = BitchBot(cogs=cogs)

bot.run(keys.bot)
