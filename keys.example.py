bot = 'Bot token'

logWebhook = 'Webhook to send logs to'
rabbitWebhook = "Placeholder so I don't risk Attribute Errors. You'll never need this"

db = {  # postgres config
    'host': 'localhost',  # hostname where postgres is running
    'port': 5432,  # port on which postgres is running
    'user': 'postgres',  # username of postgres user
    'password': ''  # password of postgres user
}

project_id = 'GCP project ID for dialog flow'

can_use_private_commands = []  # list of people who can use private commands

trusted_guilds = []  # guilds where anyone can say anything through the bot

debug = True  # if this is running in a debug env

client_id = 0  # bot's client id
client_secret = ''  # bot's client secert
redirect_uri = 'http://hostname:port/api/auth/callback'  # oauth2 redirect uri
redirect_after_login_url = 'http://hostname:port/home'  # where to redirect after logging the user in
