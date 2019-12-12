from database import database
from resources import RabbitCounter
from services import Service


class RabbitService(Service):
    @classmethod
    async def get(cls, name, value):
        rabbit = await database.connection.fetchrow(f"""select * from RabbitCounter where {name} = $1;""", value)
        return RabbitCounter.convert(rabbit)

    @classmethod
    async def getAll(cls):
        rabbits = await database.connection.fetch(f"""select * from RabbitCounter""")
        return RabbitCounter.convertMany(rabbits)

    @classmethod
    async def insert(cls, res):
        inserted =  await database.connection.fetchrow(
            """insert into RabbitCounter (summoned_at, summoned_by) values ($1, $2) returning *;""",
            res.summonedAt,
            res.summonedBy,
        )
        return RabbitCounter.convert(inserted)

    @classmethod
    async def update(cls, replacement):
        return await super().update(replacement)

    @classmethod
    async def delete(cls, id):
        return await super().delete(id)

    @classmethod
    async def rawSelectQuery(cls, query, args):
        fetched = await database.connection.fetch(f'''select * from RabbitCounter where {query}''', *args)
        return RabbitCounter.convertMany(fetched)

    @classmethod
    async def rawQuery(cls, query, args):
        return await database.connection.fetch(query, *args)
