import asyncpg

connection = None


async def connect():
    global connection
    connection = await asyncpg.connect(user="postgres", password="", host="172.18.0.2", port=5432, database='bitch_bot')


async def createTables():
    await connection.execute('''
    CREATE TABLE IF NOT EXISTS Emojis (
        id bigint NOT NULL PRIMARY KEY,
        name text NOT NULL,
        command text NOT NULL,
        is_epic bool NOT NULL,
        is_animated bool NOT NULL
    );''')


async def init():
    await connect()
    await createTables()


async def close():
    await connection.close()
