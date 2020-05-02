from database.sql import SQL
from resources.activity import Activity
from database import errors


class ActivityService:
    def __init__(self, pool):
        self.pool = pool

    async def increment(self, user_id, guild_id, by):
        async with self.pool.acquire() as connection:
            increment = await connection.fetchrow('''
            insert into Activity as a (user_id, guild_id)
            values ($1, $2)
            on conflict (user_id, guild_id) do update set points = a.points + $3
            returning points, user_id, guild_id, pg_xact_commit_timestamp(xmin) as last_time_updated;
            ''', user_id, guild_id, by)
            return increment

    async def get(self, member):
        async with self.pool.acquire() as conn:
            fetched = await conn.fetchrow('''
            select *
            from (
                     select *, dense_rank() over (order by points desc) as position, 
                       pg_xact_commit_timestamp(xmin) as last_time_updated
                     from activity
                     where guild_id = $1
                       and user_id = any ($2::bigint[])
                 ) as x
            where x.user_id = $3;
            ''', member.guild.id, [x.id for x in member.guild.members], member.id)

            if fetched is None:
                raise errors.NotFound(
                    f'Activity for user with user id: {member.id} in guild {member.guild.id} not found')

            return Activity.convert(fetched)

    async def get_top(self, guild, limit=20):
        async with self.pool.acquire() as connection:
            fetched = await connection.fetch('''
            select *
            from (
                 select *, dense_rank() over (order by points desc) as position,
                   pg_xact_commit_timestamp(xmin) as last_time_updated
                 from activity
                 where guild_id = $1
                   and user_id = any ($2::bigint[])
            ) as x
            limit $3;
            ''', guild.id, [x.id for x in guild.members], limit)

        return Activity.convertMany(fetched)

    async def set_tracking_state(self, guild_id, state):
        async with self.pool.acquire() as connection:
            return await connection.fetchrow('''
            update guildconfig
            set wants_activity_tracking = $1
            where guild_id = $2
            returning wants_activity_tracking;
            ''', state, guild_id)

    async def get_guilds_with_tracking_enabled(self):
        async with self.pool.acquire() as connection:
            fetched = await connection.fetch('''
            select guild_id from config_view
            where wants_activity_tracking = true;
            ''')

            return [row['guild_id'] for row in fetched] if fetched is not None else []

    sql = SQL(createTable='''
        create table if not exists Activity
        (
            user_id  bigint,
            guild_id bigint,
            points   int not null default 0,
            primary key (user_id, guild_id)
        );
        ''')
