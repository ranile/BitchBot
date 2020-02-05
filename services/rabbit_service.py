from resources import Counter


class CounterService:
    def __init__(self, pool):
        self.pool = pool

    async def get(self, name, value):
        async with self.pool.acquire() as connection:
            rabbit = await connection.fetchrow(
                f"""select count, summoned_at, summoned_by from Counters 
                where name = 'rabbit' and {name} = $1;""", value)
        return Counter.convert(rabbit)

    async def insert(self, res):
        async with self.pool.acquire() as connection:
            inserted = await connection.fetchrow(
                """insert into Counters (name, summoned_at, summoned_by)
                values ($1, $2, $3)
                returning name, count, summoned_at, summoned_by;""",
                res.name, res.summonedAt, res.summonedBy)
        return Counter.convert(inserted)
