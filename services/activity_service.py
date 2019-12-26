from database import database
from database.sql import SQL
from resources.activity import Activity
from services import Service


class ActivityService(Service):

    @classmethod
    async def increment(cls, user_id, guild_id, by):
        # Attempt at incrementing the activity
        increment = await database.connection.fetchrow(''' 
        update activity
        set points = activity.points + $1
        where user_id = $2 and guild_id = $3
        returning points, user_id, guild_id, pg_xact_commit_timestamp(xmin) as last_time_updated;
        ''', by, user_id, guild_id)

        if increment is None:  # If no row is returned, it means that user was not in the table
            # Insert the default amount of activity points for that user

            increment = await database.connection.fetchrow('''insert into Activity (user_id, guild_id)
                values ($1, $2) returning points, user_id, guild_id, pg_xact_commit_timestamp(xmin) as last_time_updated;;''',
                                                           user_id, guild_id)

        return increment

    @classmethod
    def sql(cls):
        return SQL(
            createTable='''
        create table if not exists Activity
        (
            user_id  bigint,
            guild_id bigint,
            points   int not null default 0,
            primary key (user_id, guild_id)
        );
        ''')

    @classmethod
    async def get(cls, user_id, guild_id):
        fetched = await database.connection.fetchrow('''
            select pg_xact_commit_timestamp(xmin) as last_time_updated, *, row_number() over ( order by points desc ) as position
            from activity where user_id = $1 and guild_id = $2;
        ''', user_id, guild_id)
        return Activity.convert(fetched)

    @classmethod
    async def get_top(cls, guild, limit=10):
        query = '''
        select *, pg_xact_commit_timestamp(xmin) as last_time_updated, row_number() over ( order by points desc ) as position
        from activity
        where guild_id = $1
        order by points desc
        limit $2;
        '''

        fetched = await database.connection.fetch(query, guild.id, limit)
        converted = []
        for fetch in fetched:
            user_activity = Activity.convert(fetch)
            user_activity.guild = guild
            user_activity.user = guild.get_member(user_activity.user)
            converted.append(user_activity)

        return converted
