# BitchBot

**No Bitches. This project has been abandoned**

 Fun Discord bot with moderation and utility tools like reminders, starboard, activity tracking and more  
 [Invite her to your server](https://discordapp.com/oauth2/authorize?client_id=595363392886145046&scope=bot&permissions=388160)
 
# Features

Fun bot that provides a lot of commands like:

* Send animated emojis or any emoji that the bot can see
* Activity tracking
* Starboard
* Moderation
* And more...

# Getting started

## Running my instance

All you need to do is [invite](https://discordapp.com/oauth2/authorize?client_id=595363392886145046&scope=bot&permissions=388160) the bot to your server. Once the bot is in your server, you can setup the features using the following commands:

* `starboard setup` (for setting up starboard)
* `mod roles` (comamnd groups for setting up mod roles. `mod roles add` for adding mod roles; `mod roles add` for removing them)
* `mute config` (for setting up the mute role)

Detailed information can be obtained using the help command

## Running own instance

* Create a `keys.py` file in the root of the directory. An example keys file is provided
* Install the dependencies from `requirements.txt`
* Place your DialogFlow `service-account.json` file in the root of the directory.
* Run `core.py`

# Getting Help

## Help Command

All the commands can be viewed via `>help`. Detailed information can be accessed by provided the command/commands group to help as `>help command_name/group_name`.

## Need more help? Have any ideas for the bot? Want to report a bug?


[![](https://discordapp.com/api/v7/guilds/693765408787922994/widget.png?style=banner4)](https://discord.gg/k2ysVzd)

### Permissions:

If you do not want the bot to delete the messages for things like emoji commands, simply deny `Manage Messages` permission for the bot. You need to provide the required permissions for each moderation command you want to use. For example `Ban Members` to ban members, `Kick Members` to kick members, etc.

# Contributions

Your pull requests are welcome
