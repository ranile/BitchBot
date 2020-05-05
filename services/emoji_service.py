from database.sql import SQL


class EmojiService:
    def __init__(self, pool):
        self.pool = pool

    async def mark_safe(self, emoji_id, marked_by):
        async with self.pool.acquire() as connection:
            fetched = await connection.fetchrow('''
            insert into emojis (emoji_id, marked_by)
            values ($1, $2)
            returning *;
            ''', emoji_id, marked_by)
            return fetched

    async def fetch_all_safe_emojis(self):
        async with self.pool.acquire() as connection:
            fetched = await connection.fetch('''
            select emoji_id from emojis
            ''')
            return [x['emoji_id'] for x in fetched] if fetched is not None else []

    @classmethod
    def sql(cls):
        return SQL(
            createTable='''
                create table if not exists emojis
                (
                    emoji_id        bigint,
                    marked_by bigint
                );
                create unique index if not exists unique_emoji_index on emojis (emoji_id, marked_by);
            '''
        )
