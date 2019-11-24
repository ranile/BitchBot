from discord.ext import commands
import discord
import inspect
from util import funs # pylint: disable=no-name-in-module


class BotStuff(commands.Cog, name='My Stuff'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, module: str):
        """
        Reloads a cog

        Args:
            module: The cog to reload
        """

        self.bot.reload_extension(f'cogs.{module}')
        await ctx.send("🔄")

    @commands.command()
    async def help(self, ctx: commands.Context, command: str = None):
        """
        Displays help message

        Args:
            command: The command to get help for. Optional
        """

        embed = discord.Embed(title='**You wanted help? Help is provided**', color = funs.random_discord_color())
        
        embed.set_footer(text=f'Do {self.bot.command_prefix}help commndName to get help for a specific command')

        if command is None:

            for name, cog in self.bot.cogs.items():
                out = ''
                for cmd in cog.get_commands():
                    if not (await funs.canRunCommand(ctx, cmd)):
                        continue

                    try:
                        helpStr = str(cmd.help).split('\n')[0]
                        out += f"**{cmd.name}**:\t{helpStr}\n"
                    except:
                        continue
                    
                if out:
                    embed.add_field(name=f'**{name}**', value=out, inline=False)

        else:
            
            cmd = self.bot.get_command(command)

            if cmd is None:
                await ctx.send(f"Command {command} doesn't exist")
                return

            elif not (await funs.canRunCommand(ctx, cmd)):
                await ctx.send(f"You don't have permission to run {command} command")
                return

            try:
                commandHelp = funs.getInfoFromDocstring(cmd.help)
            except:
                commandHelp = ("", cmd.help)

            embed.add_field(name = f'{cmd.name}', value = commandHelp[1], inline=False)

            argsString = funs.generateArgStringForEmbed(commandHelp[0])
            if argsString is not None and argsString != "":
                embed.add_field(name = f'Parameters', value = argsString, inline=False)
            

            cmdAliases = cmd.aliases
            if (cmdAliases):
                aliases = ', '.join(cmdAliases)
                embed.add_field(name='Aliases:', value=aliases, inline=False)
            
        await ctx.send(embed=embed)


def setup(bot):
    bot.remove_command('help')
    bot.add_cog(BotStuff(bot))
