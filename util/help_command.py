import discord
from discord.ext import commands
import itertools
from util import funs, BloodyMenuPages, EmbedPagesData

NEW_LINE = '\n'  # working around python's limitation of not allowing `\n` in f-strings
SUPPORT_SERVER = 'https://discord.gg/ga9fNZq'


# noinspection PyMethodMayBeStatic,PyShadowingNames
class BloodyHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    def generate_base_help_embed(self):
        embed = discord.Embed(title='**You wanted help? Help is provided**', color=funs.random_discord_color())
        embed.add_field(name="Need more help? Have any ideas for the bot? Want to report a bug?",
                        value=f"[Join our support server]({SUPPORT_SERVER})")
        embed.set_footer(text=f'Do "{self.context.invoked_with}help command/group name" for information about it')
        return embed

    def format_command_embed(self, embed, command):
        embed.add_field(name=f'**{command.qualified_name}**', value=command.help, inline=False)
        embed.add_field(name='Format', value=self.get_command_signature(command), inline=False)

        return embed

    def short_help_string(self, command):
        if command.help is None:
            help_str = f"Help not available. [Join the support server]({SUPPORT_SERVER})"
        else:
            help_str = str(command.help).strip().split('\n')[0]

        return help_str

    async def send_bot_help(self, mapping):
        def key(c):
            return c.cog_name or '\u200bNo Category'

        bot = self.context.bot
        entries = await self.filter_commands(bot.commands, sort=True, key=key)

        data = []

        for cog, cmds in itertools.groupby(entries, key=key):
            cmds = sorted(cmds, key=lambda c: c.name)
            if len(cmds) == 0:
                continue

            actual_cog = bot.get_cog(cog)

            if actual_cog is None:
                continue

            embed = self.generate_base_help_embed()
            embed.title += f'\n{actual_cog.qualified_name} Commands'
            embed.description = actual_cog.description
            for cmd in set(actual_cog.walk_commands()):
                try:
                    if isinstance(cmd, commands.Group) and not cmd.invoke_without_command:
                        continue
                except AttributeError:
                    pass

                embed.add_field(name=f'**{cmd.qualified_name}**', value=self.short_help_string(cmd), inline=False)

            data.append(embed)

        pages = BloodyMenuPages(EmbedPagesData(data))
        await pages.start(self.context)

    async def send_cog_help(self, cog):
        embed = self.generate_base_help_embed()
        embed.title += f'\n{cog.qualified_name} Commands'
        cog_commands = await self.filter_commands(set(cog.walk_commands()), sort=True)
        for command in cog_commands:
            embed.add_field(name=command.qualified_name, value=self.short_help_string(command), inline=False)

        await self.context.send(embed=embed)

    async def send_command_help(self, command):
        embed = self.format_command_embed(self.generate_base_help_embed(), command)
        await self.context.send(embed=embed)

    async def send_group_help(self, group):
        subcommands = set(group.walk_commands())

        if len(subcommands) == 0:
            return await self.send_command_help(group)

        subcommands = await self.filter_commands(subcommands, sort=True)

        if group.invoke_without_command:
            embed = self.format_command_embed(self.generate_base_help_embed(), group)
        else:
            embed = self.generate_base_help_embed()
            embed.title += f'\n{group.qualified_name}'
            embed.description = group.help

        out = []
        for cmd in subcommands:
            out.append(f"**{cmd.qualified_name}**:\t{self.short_help_string(cmd)}")

        if out:
            embed.add_field(name='Sub Commands', value='\n'.join(out), inline=False)

        await self.context.send(embed=embed)
