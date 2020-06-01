import util
from cogs import jsk, cause
from quart import jsonify
from discord.ext import commands

blueprint = util.BlueprintWithBot('command_rouetes', __name__, url_prefix='/api/commands')


def filter_commands(commands_):
    print('whaaat')
    for command in commands_:
        if isinstance(command.cog, (jsk.MyJishaku, cause.Cause)):
            continue
        elif command.hidden:
            print('hidden', command.name)
            continue
        else:
            yield command


def get_command_signature(command):
    parent = command.full_parent_name
    if len(command.aliases) > 0:
        aliases = '|'.join(command.aliases)
        fmt = f'[{command.name}|{aliases}]'
        if parent:
            fmt = parent + ' ' + fmt
        alias = fmt
    else:
        alias = command.name if not parent else f'{parent} {command.name}'

    return f'{alias} {command.signature}'


@blueprint.route('/')
async def commands_route():
    bot = blueprint.bot

    json = []

    for actual_cog in bot.cogs.values():
        filtered_commands = sorted(filter_commands(actual_cog.walk_commands()), key=lambda c: c.name)
        if len(filtered_commands) == 0:
            continue

        data = {
            'name': actual_cog.qualified_name,
            'description': actual_cog.description,
            'commands': []
        }

        for command in filtered_commands:
            if isinstance(command, commands.Group) and not command.invoke_without_command:
                continue

            data['commands'].append({
                'name': command.qualified_name,
                'help': command.help,
                'signature': get_command_signature(command)
            })

        json.append(data)

    return jsonify(json)


def setup(bot):
    bot.quart_app.register_blueprint_with_bot(blueprint, bot)
