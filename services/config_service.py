from resources import Prefix, GuildConfig, Blacklist
import asyncpg


class ConfigService:

    @staticmethod
    async def get(db: asyncpg.Connection, guild_id: int):
        fetched = await db.fetchrow('''
        select * from config_view
        where guild_id = $1
        ''', guild_id)
        if fetched is None:
            return None
        return GuildConfig.convert(fetched)

    @staticmethod
    async def setup_starboard(db: asyncpg.Connection, guild_id, starboard_channel_id, star_limit):
        query = '''
        insert into guildconfig (guild_id, starboard_channel, star_limit)
        values ($1, $2, $3)
        on conflict(guild_id) do update set starboard_channel = $2, star_limit = $3 
        returning *;
        '''

        inserted = await db.fetchrow(query, guild_id, starboard_channel_id, star_limit)
        return GuildConfig.convert(inserted)

    @staticmethod
    async def add_mod_role(db: asyncpg.Connection, role_id, guild_id):
        query = '''
        update guildconfig
        set mod_roles = guildconfig.mod_roles || $2
        where guild_id = $1
        returning *;
        '''

        return GuildConfig.convert(await db.fetchrow(query, guild_id, [role_id]))

    @staticmethod
    async def set_mute_role(db: asyncpg.Connection, guild_id, mute_role_id):
        fetched = await db.fetchrow(f'''
        insert into guildconfig (guild_id, mute_role_id)
        values ($1, $2)
        on conflict(guild_id) do update set mute_role_id = $2
        returning *;
        ''', guild_id, mute_role_id)

        return GuildConfig.convert(fetched)

    @staticmethod
    async def remove_mute_role(db: asyncpg.Connection, guild_id, role_id):
        fetched = await db.fetchrow(f'''
        update guildconfig
        set mod_roles = array_remove(mod_roles, $2)
        where guild_id = $1
        returning *;
        ''', guild_id, role_id)

        return GuildConfig.convert(fetched) if fetched is not None else None

    @staticmethod
    async def delete_starboard(db: asyncpg.Connection, guild_id):
        fetched = await db.fetchrow(f'''
        update GuildConfig
        set starboard_channel = null, star_limit = null
        where guild_id = $1
        returning *;
        ''', guild_id)

        return GuildConfig.convert(fetched) if fetched is not None else None

    @staticmethod
    async def insert_prefix(db: asyncpg.Connection, prefix):
        fetched = await db.fetchrow('''
        insert into GuildConfig (guild_id, prefix)
        values ($1, $2)
        on conflict(guild_id) do update set prefix = $2
        returning *;
        ''', prefix.guild_id, prefix.prefix)

        return Prefix.convert(fetched)

    @staticmethod
    async def delete_prefix(db: asyncpg.Connection, guild_id):
        await db.execute('''
        update GuildConfig
        set prefix = null
        where guild_id = $1;
        ''', guild_id)

    @staticmethod
    async def get_all_prefixes(db: asyncpg.Connection):
        fetched = await db.fetch('''
        select guild_id, prefix from GuildConfig
        where prefix is not null;
        ''')

        return Prefix.convertMany(fetched) if fetched is not None else []

    @staticmethod
    async def get_blacklisted_users(db: asyncpg.Connection):
        fetched = await db.fetch('''
        select *
        from blacklist;
        ''')

        return Blacklist.convertMany(fetched) if fetched is not None else []

    @staticmethod
    async def blacklist_user(db: asyncpg.Connection, user_id, *, reason=None, until=None):
        inserted = await db.fetchrow('''
        insert into blacklist (user_id, reason, blacklisted_until)
        values ($1, $2, $3)
        returning *;
        ''', user_id, reason, until)

        return Blacklist.convert(inserted)

    @staticmethod
    async def remove_user_from_blacklist(db: asyncpg.Connection, user_id):
        return await db.execute('''
        delete from blacklist
        where user_id = $1;
        ''', user_id)

    initial_sql = '''
        create table if not exists GuildConfig
        (
            guild_id          bigint primary key,
            starboard_channel bigint,
            event_log_webhook text,
            mute_role_id bigint,
            mod_roles bigint[] not null default '{}',
            prefix text,
            wants_activity_tracking bool not null default false 
        );
        
        create materialized view if not exists config_view as
        select *
        from guildconfig;
        
        create or replace function refresh_config_view()
            returns trigger
            language plpgsql
        as
        $$
        begin
            refresh materialized view config_view;
            return null;
        end
        $$;
        
        drop trigger if exists refresh_config_view_on_update
            on GuildConfig;
        
        create trigger refresh_config_view_on_update
            after update or insert
            on GuildConfig
        execute function refresh_config_view();
        
        create table if not exists blacklist
        (
            user_id           bigint primary key,
            blacklisted_at    timestamptz not null default now(),
            blacklisted_until timestamptz,
            reason text
        );
        '''
