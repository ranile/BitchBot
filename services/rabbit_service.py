from resources import RabbitCounter


class RabbitService:
    def __init__(self, pool):
        self.pool = pool

    async def get(self, name, value):
        async with self.pool.acquire() as connection:
            rabbit = await connection.fetchrow(
                f"""select count, summoned_at, summoned_by from Counters 
                where name = 'rabbit' and {name} = $1;""", value)
        return RabbitCounter.convert(rabbit)

    async def insert(self, res):
        async with self.pool.acquire() as connection:
            inserted = await connection.fetchrow(
                """insert into Counters (name, summoned_at, summoned_by)
                values ('rabbit', $1, $2)
                returning count, summoned_at, summoned_by;""",
                res.summonedAt, res.summonedBy)
        return RabbitCounter.convert(inserted)
