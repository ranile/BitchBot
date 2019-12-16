import asyncio
import discord

class EmbedField:
    def __init__(self, name, value, inline = True):
        self.name = name
        self.value = value
        self.inline = inline

    @classmethod
    def build(cls, data):
        if isinstance(data, EmbedField):
            return data
        elif isinstance(data, dict):
            return EmbedField.from_dict(data)
        else:
            raise Exception('bruh moment happened')

    @classmethod
    def from_dict(cls, dict):
        try:
            return cls(name = dict['name'], value = dict['value'], inline = dict['inline'])
        except KeyError:
            return cls(name = dict['name'], value = dict['value'], inline = True)
        

    def add_to_embed(self, embed: discord.Embed, pages):
        new_embed = embed.copy()
        for i in range(len(new_embed.fields)):
            new_embed.remove_field(i)
        
        new_embed.add_field(name = self.name, value = self.value, inline=self.inline)
        embed.set_footer(text = 'bruh')
        footer = f'{embed.footer.text}\nPage {pages[0]} of {pages[1]}'
        new_embed.set_footer(text=footer)
        return new_embed
        

class PaginatorData:
    def __init__(self, data, is_embed):
        if is_embed:
            self.data = [EmbedField.build(d) for d in data]
        else:
            self.data = data
        
        self.max_pages = len(self.data) - 1

    def first(self):
        return self.data[0]


class Paginator:
    def __init__(self, ctx, data: PaginatorData, is_embed = True, base_embed = discord.Embed()):
        self.ctx = ctx
        self.is_embed = is_embed
        self.data = data
        self.base_embed = base_embed
        self.current = 0
        self.paginating = True
        self.reactions = [('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', self.first_page),
                          ('\N{BLACK LEFT-POINTING TRIANGLE}', self.backward),
                          ('\N{BLACK RIGHT-POINTING TRIANGLE}', self.forward),
                          ('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', self.last_page),]

    def _check(self, reaction, user):
        if user.id != self.ctx.author.id:
            return False

        if reaction.message.id != self.msg.id:
            return False

        for (emoji, func) in self.reactions:
            if reaction.emoji == emoji:
                self.execute = func
                return True
        return False

    async def alter(self, page: int):
        if self.is_embed:
            await self.msg.edit(embed=self.data.data[page].add_to_embed(self.base_embed, (self.current, self.data.max_pages)))
        else:
            await self.msg.edit(content=self.data.data[page])

    async def first_page(self):
        self.current = 0
        await self.alter(self.current)

    async def backward(self):
        if self.current == 0:
            self.current = self.data.max_pages
            await self.alter(self.current)
        else:
            self.current -= 1
            await self.alter(self.current)

    async def forward(self):
        if self.current == self.data.max_pages:
            self.current = 0
            await self.alter(self.current)
        else:
            self.current += 1
            await self.alter(self.current)

    async def last_page(self):
        self.current = self.data.max_pages
        await self.alter(self.current)

    async def start(self):
        if self.is_embed:
            embed = self.data.first().add_to_embed(self.base_embed, (self.current, self.data.max_pages))
            self.msg = await self.ctx.send(embed=embed)
        
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
                    return self.stop()

                for future in pending:
                    future.cancel()
                await self.execute()
