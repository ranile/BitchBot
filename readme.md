# BitchBot

It is a stupid little discord bot written in python3

### Required Libraries:

* discord.py
* wikipedia

You can install these manually or from requirements.txt

### Usage

Get a discord bot token after creating a discord application with a bot from [here](https://discordapp.com/developers/applications/)
Put your token in `keys.py` in `bot` with the `BOT_TOKEN` constant in `core.py` value reading from that file OR
Put your token in `BOT_TOKEN` environment variable

### Currently Availabe Commands
**Syntax: {prefix}command [args]**

Following commands are given in this way: command -> result

* ping -> Ping Pong
* rickroulette -> Rick Astley = Loose, Doggo = Win
* addspaces -> Adds 3 spaces in between every character.

    args: Takes a string as its argument
* totogglecase -> Convert string to toggle case

    args: Takes a string as its argument
* touppercase -> Convert string to toggle case

    args: Takes a string as its argument
* dare -> Gives a dare for you to do
* truth -> Gives a truth for you to tell
* wyr -> Gives a *would you rather* question for you to answer
* bill -> Be like bill

    args: can take a string as its argument to give a *be like bill* for that
* fact -> Gives a fun fact
* joke -> Tells a joke. They are horrible. Seriously
* norris -> Chuck Norris. Need I say more
* reddit -> Get a random reddit post

    args: Takes a subreddit's name as its argument
* urban -> Gets top defination from urban dictionary

    args: Takes a word as its argument to look up on urban dictionary
* wikipedia -> Find a Wikipedia page on a given topic

    args: Takes a word as its argument to look up on Wikipedia
* wikirandom -> Random Wikipedia page
* poll -> Start a poll.

    args: Can take strings as arguments. First argument is the next question. Next argument(s) are answers. If no answers are provided, it will default to yes/no. Upto 10 answers can be provided
* say -> Have the bot say something.

    args: Takes a string as its argument and says it back
* sayembed -> Have the bot say something in embeds.

    args: Takes a string as its argument and says it back in embeds
* rabbitman -> returns a rabbitman picture.
* help -> Shows help message
