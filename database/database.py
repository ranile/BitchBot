import asyncpg
import services
from keys import db


async def connect(loop):
    pool = await asyncpg.create_pool(user=db['user'], password=db['password'], host=db['host'], port=db['port'],
                                     database='bitch_bot', loop=loop)
    return pool


async def createTables(connection):
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
    pool = await connect(loop)
    async with pool.acquire() as conn:
        await createTables(conn)

    return pool
