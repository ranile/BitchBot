import asyncpg
import json
import services
from keys import db


async def connect(loop):
    def _encode_jsonb(value):
        return json.dumps(value)

    def _decode_jsonb(value):
        return json.loads(value)

    async def pool_init(con):
        await con.set_type_codec('jsonb', schema='pg_catalog', encoder=_encode_jsonb, decoder=_decode_jsonb,
                                 format='text')

    pool = await asyncpg.create_pool(user=db['user'], password=db['password'], host=db['host'], port=db['port'],
                                     database='bitch_bot', loop=loop, init=pool_init)
    return pool


async def create_tables(connection):
    await connection.execute(services.ActivityService.initial_sql)
    await connection.execute(services.StarboardService.initial_sql)
    await connection.execute(services.ConfigService.initial_sql)
    await connection.execute(services.WarningsService.initial_sql)
    await connection.execute(services.TimersService.sql().createTable)
    await connection.execute(services.EmojiService.initial_sql)


async def init(loop):
    pool = await connect(loop)
    async with pool.acquire() as conn:
        await create_tables(conn)

    return pool
