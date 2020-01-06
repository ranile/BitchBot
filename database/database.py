import asyncio
import time
import asyncpg
import services
from keys import db
import datetime

connection = None
pool = None


async def connect(loop):
    global connection
    global pool
    pool = await asyncpg.create_pool(user=db['user'], password=db['password'], host=db['host'], port=db['port'],
                               database='bitch_bot', loop=loop)
    connection = await asyncpg.connect(
        user=db['user'], password=db['password'], host=db['host'], port=db['port'], database='bitch_bot', loop=loop
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
    await connection.execute('''
    create materialized view if not exists ActivityView as
    select *, pg_xact_commit_timestamp(xmin) as last_time_updated
    from Activity;
    ''')
    await connection.execute(services.BanService.sql().createTable)
    await connection.execute(services.MuteService.sql().createTable)
    await connection.execute(services.WarningsService.sql().createTable)


async def init(loop):
    await connect(loop)
    await createTables()


async def close():
    await connection.close()
