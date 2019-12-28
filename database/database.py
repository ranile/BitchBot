import asyncio
import time
import asyncpg
import services
from keys import db
import datetime

connection = None


async def connect():
    global connection
    connection = await asyncpg.connect(
        user=db['user'], password=db['password'], host=db['host'], port=db['port'], database='bitch_bot'
    )


async def createTables():
    # await connection.execute('''
    # CREATE TABLE IF NOT EXISTS Emojis (
    #     id bigint NOT NULL PRIMARY KEY,
    #     name text NOT NULL,
    #     command text NOT NULL,
    #     is_epic bool NOT NULL,
    #     is_animated bool NOT NULL
    # );''')

    await connection.execute('''
    create table if not exists Counters
    (
        count serial not null primary key,
        name text not null,
        summoned_by bigint not null,
        summoned_at int not null
    );
    ''')

    await connection.execute(services.ActivityService.sql().createTable)
    await connection.execute(services.StarboardService.sql().createTable)
    await connection.execute(services.ConfigService.sql().createTable)


async def init():
    await connect()
    await createTables()


async def close():
    await connection.close()
