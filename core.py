import keys
from BitchBot import BitchBot

cogs = ["admin", "cause", "emojis", "internet", "starboard", 'stats', 'jsk', 'logs', 'mod', 'misc']

bot = BitchBot(cogs=cogs)

bot.run(keys.bot)
