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


async def yeet():
    pass
    # rabbit = RabbitCounter(
    #     summonedAt=int(time.time()),
    #     summonedBy=453068315858960395
    # )
    # res = await RabbitService.insert(rabbit)
    # print(res)
    # print(type(res))
    # print('---------------------------------------')
    # [print(x) for x in await RabbitService.getAll()]
    # res = await RabbitService.get('count', 2)
    # print(res)
    # print(type(res))

    # f = await connection.fetchrow('''
    # update activity
    # set points = activity.points + 2
    # where user_id = 644563454648254475
    # returning points;
    # ''')
    #
    # print(f)
    # print(type(f))
    #
    # if f is None:
    #     f = await connection.fetchrow('''insert into Activity (user_id, guild_id)
    #         values (644563454648254475, 453068315858960395) returning points;''')
    #     print(f)
    #     print(type(f))

    start = datetime.datetime.now()
    fetched = await connection.fetchrow(
        '''select pg_xact_commit_timestamp(xmin) as last_time_updated, * from activity where user_id = 453068315858960395;''')
    last_updated = fetched['last_time_updated']
    # print(fetched['last_time_updated'])
    # print(type(fetched['last_time_updated']))
    # print(last_updated.tzinfo)
    delta = (datetime.datetime.now(tz=last_updated.tzinfo) - last_updated)  # > datetime.timedelta(seconds=5)
    end = datetime.datetime.now()
    cache = {}
    print(delta)
    for i in range(5):
        try:
            fetched_c = cache['453068315858960395-644563454648254475']
        except KeyError:
            fetched_c = None

        print(fetched_c is None)
        if fetched_c is None or fetched_c > datetime.timedelta(seconds=5):
            await services.ActivityService.increment(453068315858960395, 644563454648254475, 2)
            fetched = await connection.fetchrow(
                '''select pg_xact_commit_timestamp(xmin) as last_time_updated, * from activity where user_id = 453068315858960395;''')
            last_updated = fetched['last_time_updated']
            delta = (datetime.datetime.now(tz=last_updated.tzinfo) - last_updated)  # > datetime.timedelta(seconds=5)
            cache['453068315858960395-644563454648254475'] = delta
            print(cache)
            await asyncio.sleep(2)
        else:
            print('no')
    print((end - start).microseconds)


async def init():
    await connect()
    await createTables()
    # await yeet()


async def close():
    await connection.close()
