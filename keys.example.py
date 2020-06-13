bot = 'Bot token'

logWebhook = 'Webhook to send logs to'
rabbitWebhook = "Placeholder so I don't risk AttributeErrors. You'll never need this"

db = {  # postgres config
    'host': 'localhost',  # hostname where postgres is running
    'port': 5432,  # port on which postgres is running
    'user': 'postgres',  # username of postgres user
    'password': ''  # password of postgres user
}

can_use_private_commands = []  # list of people who can use private commands

trusted_guilds = []  # guilds where anyone can say anything through the bot

debug = True  # if this is running in a debug env

client_id = 0  # bot's client id

lavalink_pass = 'youshallnotpass'  # lavalink server's password

# bot list tokens for posting stats

dbl_token = ''
dbl_webhook_auth = ''
list_my_bots_token = ''
dbots_token = ''
discordapps_token = ''
