import asyncpg
import typing


class EmojiService:

    @staticmethod
    async def mark_safe(db: asyncpg.Connection, emoji_id: int, marked_by: int) -> typing.Dict[str, str]:
        fetched = await db.fetchrow('''
            insert into emojis (emoji_id, marked_by)
            values ($1, $2)
            returning *;
        ''', emoji_id, marked_by)

        return {  # doing this only so i can return `dict` and have it be accurate
            'emoji_id': fetched['emoji_id'],
            'marked_by': fetched['marked_by'],
        }

    @staticmethod
    async def fetch_all_safe_emojis(db: asyncpg.Connection) -> typing.List[int]:
        fetched = await db.fetch('''
            select emoji_id from emojis
        ''')
        return [x['emoji_id'] for x in fetched] if fetched is not None else []

    initial_sql = '''
        create table if not exists emojis
        (
            emoji_id        bigint,
            marked_by bigint
        );
        create unique index if not exists unique_emoji_index on emojis (emoji_id, marked_by);
    '''
