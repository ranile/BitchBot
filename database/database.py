import asyncpg

connection = None


async def connect():
    global connection
    connection = await asyncpg.connect(user="postgres", password="", host="172.18.0.2", port=5432)


async def createTables():
    pass


async def init():
    await connect()
    await createTables()


async def close():
    await connection.close()
