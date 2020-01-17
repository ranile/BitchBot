import asyncio
import discord


class Paginator:
    def __init__(self, ctx, data, is_embed=True):
        self.ctx = ctx
        self.is_embed = is_embed
        self.data = data
        self.current = 0
        self.paginating = True
        self.max_pages = len(data) - 1
        self.reactions = [('<:backward:656488824129454080>', self.first_page),
                          ('<:previous:656488303243034654>', self.previous_page),
                          ('<:next:656487474297569318>', self.next_page),
                          ('<:forward:656487435957698560>', self.last_page), ]

    def _check(self, reaction, user):
        if user.id != self.ctx.author.id or reaction.message.id != self.msg.id:
            return False

        for (emoji, func) in self.reactions:
            if str(reaction.emoji) == emoji:
                self.execute = func
                return True
        return False

    def set_page_number_footer(self, embed):
        footer = f'{self.original_footer}\nPage {self.current} of {self.max_pages}'
        embed.set_footer(text=footer)
        return embed

    async def update(self, page: int):
        if self.is_embed:
            embed = self.set_page_number_footer(self.data[page])
            await self.msg.edit(embed=embed)
        else:
            await self.msg.edit(content=self.data.data[page])

    async def first_page(self):
        self.current = 0
        await self.update(self.current)

    async def previous_page(self):
        if self.current == 0:
            self.current = self.max_pages
            await self.update(self.current)
        else:
            self.current -= 1
            await self.update(self.current)

    async def next_page(self):
        if self.current == self.max_pages:
            self.current = 0
            await self.update(self.current)
        else:
            self.current += 1
            await self.update(self.current)

    async def last_page(self):
        self.current = self.max_pages
        await self.update(self.current)

    # noinspection PyAttributeOutsideInit
    async def start(self):
        if self.is_embed:
            self.original_footer = self.data[0].footer.text
            embed = self.set_page_number_footer(self.data[0])
            self.msg = await self.ctx.send(embed=embed)
        else:
            data = self.data[0]
            data += f'\n*Page {self.current} of {self.max_pages}*'
            self.msg = await self.ctx.send(data)

        if self.max_pages == 0:
            self.paginating = False
            return

        for (r, _) in self.reactions:
            await self.msg.add_reaction(r)

    async def stop(self):
        try:
            await self.msg.clear_reactions()
        except discord.Forbidden:
            await self.msg.delete()

        self.paginating = False

    async def paginate(self):
        perms = self.ctx.me.guild_permissions.manage_messages
        await self.start()
        while self.paginating:
            if perms:
                try:
                    reaction, user = await self.ctx.bot.wait_for('reaction_add', check=self._check, timeout=120)
                except asyncio.TimeoutError:
                    return await self.stop()

                try:
                    await self.execute()
                    await self.msg.remove_reaction(reaction, user)
                except discord.HTTPException:
                    pass

            else:
                done, pending = await asyncio.wait(
                    [self.ctx.bot.wait_for('reaction_add', check=self._check, timeout=120),
                     self.ctx.bot.wait_for('reaction_remove', check=self._check, timeout=120)],
                    return_when=asyncio.FIRST_COMPLETED)
                try:
                    done.pop().result()
                except asyncio.TimeoutError:
                    return await self.stop()

                for future in pending:
                    future.cancel()
                await self.execute()
