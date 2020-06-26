import asyncpg
import discord

from resources.activity import Activity


class ActivityService:

    @staticmethod
    async def increment(db: asyncpg.Connection, user_id: int, guild_id: int, by: int):
        increment = await db.fetchrow('''
            insert into Activity as a (user_id, guild_id)
            values ($1, $2)
            on conflict (user_id, guild_id) do update set points = a.points + $3
            returning points, user_id, guild_id, pg_xact_commit_timestamp(xmin) as last_time_updated;
        ''', user_id, guild_id, by)
        return increment

    @staticmethod
    async def get(db: asyncpg.Connection, member: discord.Member):
        fetched = await db.fetchrow('''
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
        # f'Activity for user with user id: {member.id} in guild {member.guild.id} not found'
        return Activity.convert(fetched) if fetched is not None else None

    @staticmethod
    async def get_top(db: asyncpg.Connection, guild: discord.Guild, limit: int = 20):
        fetched = await db.fetch('''
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

    @staticmethod
    async def set_tracking_state(db: asyncpg.Connection, guild_id: int, state: bool):
        return await db.fetchrow('''
            update guildconfig
            set wants_activity_tracking = $1
            where guild_id = $2
            returning wants_activity_tracking;
        ''', state, guild_id)

    @staticmethod
    async def get_guilds_with_tracking_enabled(db: asyncpg.Connection):
        fetched = await db.fetch('''
            select guild_id from config_view
            where wants_activity_tracking = true;
        ''')

        return [row['guild_id'] for row in fetched] if fetched is not None else []

    @staticmethod
    async def delete_for_guild(db: asyncpg.Connection, guild_id: int):
        return await db.execute('''
            delete from activity
            where guild_id = $1;
        ''', guild_id)

    @staticmethod
    async def delete_for_member(db: asyncpg.Connection, guild_id: int, member_id: int):
        return await db.execute('''
            delete from activity
            where guild_id = $1 and user_id=$2;
        ''', guild_id, member_id)

    initial_sql = '''
        create table if not exists Activity
        (
            user_id  bigint,
            guild_id bigint,
            points   int not null default 0,
            primary key (user_id, guild_id)
        );
    '''
