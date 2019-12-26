from database import database
from database.sql import SQL
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
                values ($1, $2) returning points, user_id, guild_id, pg_xact_commit_timestamp(xmin) as last_time_updated;;''', user_id, guild_id)

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
    async def last_updated(cls, user_id, guild_id):
        fetched = await database.connection.fetchrow('''
            select pg_xact_commit_timestamp(xmin) as last_time_updated, * from activity where user_id = $1 and guild_id = $2;
        ''', user_id, guild_id)
        last_updated = fetched['last_time_updated']
        return last_updated
