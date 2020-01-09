from database.sql import SQL
from resources.activity import Activity
import discord
from database import errors


class ActivityService:
    def __init__(self, pool):
        self.pool = pool

    async def increment(self, user_id, guild_id, by):
        async with self.pool.acquire() as connection:
            # Attempt at incrementing the activity
            increment = await connection.fetchrow(''' 
            update activity
            set points = activity.points + $1
            where user_id = $2 and guild_id = $3
            returning points, user_id, guild_id, pg_xact_commit_timestamp(xmin) as last_time_updated;
            ''', by, user_id, guild_id)

            if increment is None:  # If no row is returned, it means that user was not in the table
                # Insert the default amount of activity points for that user

                increment = await connection.fetchrow('''insert into Activity (user_id, guild_id)
                    values ($1, $2) returning points, user_id, guild_id, pg_xact_commit_timestamp(xmin) as last_time_updated;;''',
                                                      user_id, guild_id)

            return increment

    async def get(self, user_id, guild_id):
        async with self.pool.acquire() as conn:
            fetched = await conn.fetch('''
                select *, row_number() over ( order by points desc ) as position
                from ActivityView
                where guild_id = $1
                order by points desc;
            ''', guild_id)

            for_user = discord.utils.find(lambda x: x['user_id'] == user_id, fetched)
            if fetched is None or for_user is None:
                raise errors.NotFound(f'Activity for user with user id: {user_id} in guild {guild_id} not found')

            return Activity.convert(for_user)

    async def get_top(self, guild, limit=10):
        query = '''
        select *, row_number() over ( order by points desc ) as position
        from ActivityView
        where guild_id = $1
        order by points desc
        limit $2;
        '''
        async with self.pool.acquire() as connection:
            fetched = await connection.fetch(query, guild.id, limit)
        converted = []
        for fetch in fetched:
            user_activity = Activity.convert(fetch)
            user_activity.guild = guild
            user_activity.user = guild.get_member(user_activity.user)
            converted.append(user_activity)

        return converted

    async def update_material_view(self):
        async with self.pool.acquire() as connection:
            return await connection.execute('''
                REFRESH MATERIALIZED VIEW ActivityView;
            ''')

    @classmethod
    def sql(cls):
        return SQL(createTable='''
        create table if not exists Activity
        (
            user_id  bigint,
            guild_id bigint,
            points   int not null default 0,
            primary key (user_id, guild_id)
        );
        ''')
