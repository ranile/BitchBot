import discord
from discord.ext import commands
import itertools
from util import funs

class PaginatedHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()
        
    async def on_help_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(str(error.original))
        else:
            raise error.original

    def get_command_signature(self, command):
        parent = command.full_parent_name
        out = command.name
        
        aliases = ''
        if len(command.aliases) > 0:
            aliases = ', '.join(command.aliases)
            out = f'[{command.name}, {aliases}]'
        
        if parent:
            aliases = f" , {aliases}" if (aliases != '') else ""
            out = f'[{parent} {command.name}{aliases}]'

        return f'{out} {command.signature}'

    def addCommandsToEmbed(self, bot, commands, cogName, embed, description = None):
        
        out = ''
        embed.description = description
        for cmd in commands:
            
            try:
                helpStr = str(cmd.help).split('\n')[0]
                out += f"**{cmd.name}**:\t{helpStr}\n"
            except:
                continue
            
        if out:
            embed.add_field(name=f'**{cogName}**', value=out, inline=False)

        return embed

    def generateBaseHelpEmbed(self):
        embed = discord.Embed(title='**You wanted help? Help is provided**', color = funs.random_discord_color())
        embed.set_footer(text = 'Do >help command/group name for information about it')
        return embed

    async def send_bot_help(self, mapping):
        def key(c):
            return c.cog_name or '\u200bNo Category'

        bot = self.context.bot
        entries = await self.filter_commands(bot.commands, sort=True, key=key)

        embed = self.generateBaseHelpEmbed()

        for cog, cmds in itertools.groupby(entries, key=key):
            cmds = sorted(cmds, key=lambda c: c.name)
            if len(cmds) == 0:
                continue
            
            actualCog = bot.get_cog(cog)
        
            if actualCog is None:
                continue

            embed = self.addCommandsToEmbed(bot, actualCog.get_commands(), actualCog.qualified_name, embed)
                    
        await self.context.send(embed=embed)
                
    async def send_cog_help(self, cog):
        commands = await self.filter_commands(cog.get_commands(), sort=True)
        embed = self.generateBaseHelpEmbed()
        embed = self.addCommandsToEmbed(self.context.bot, commands, f'{cog.qualified_name} Commands', embed, cog.description)
        await self.context.send(embed=embed)

    def formatCommandEmbed(self, embed, command):
        embed.add_field(name = 'Format', value = self.get_command_signature(command), inline=False)

        try:
            commandHelp = funs.getInfoFromDocstring(command.help)
        except:
            commandHelp = ("", command.help)

        embed.description = commandHelp[1]
        try:
            argsString = funs.generateArgStringForEmbed(commandHelp[0])
        except:
            argsString = ''

        if argsString != "":
            embed.add_field(name = f'Parameters', value = argsString, inline=False)
        elif argsString == "" and list(command.clean_params):
            embed.add_field(name = f'Parameters', value = 'The docs are incomplete', inline=False)
        
        return embed

    async def send_command_help(self, command):
        embed = self.formatCommandEmbed(self.generateBaseHelpEmbed(), command)
        await self.context.send(embed=embed)

    async def send_group_help(self, group):
        subcommands = group.commands

        if len(subcommands) == 0:
            return await self.send_command_help(group)

        subcommands = await self.filter_commands(subcommands, sort=True)
        
        embed = self.addCommandsToEmbed(
            self.context.bot,
            subcommands,
            group.qualified_name,
            self.generateBaseHelpEmbed(),
            group.help
        )

        for subcommand in subcommands:
            if subcommand.invoke_without_command:
                pass

        await self.context.send(embed = embed)

