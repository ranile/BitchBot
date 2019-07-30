from discord.ext import commands
import discord
import re
import random
import requests
import asyncio
dabs = ["<:thnank:573006494296047625>",
        "<:rabbitman:593375171880943636>",
        "<:hrmmm:553857757510631434>",
        "<:DaveLovesU:550855068929228800>",
        "<:hhngyfdtj:564926491754889218>",
        "<:daway:524473417169109003>",
        "<:fried_wheeze:509526391495065600>",
        "<a:Birb:605416788964147220>"
        ]

emojis_i_can_send = ['<:thonk:524473295345549323>','<:daway:524473417169109003>',
'<:sad_yeehaw:542504166531137556>','<:disappointed_dave:542518626922528769>',
'<:Old_Sport_corrupted:542578324568932382>','<:AHHHH:542578485219295234>',
'<:Jack:542578536007991307>','<:Blackjack:542578578622119977>',
'<:Steven1:542581306937049102>','<:f_:542582487755259915>',
'<:Michael:542582934847094787>','<:PeterPointing:542590076568207403>',
'<:JakesPissed:542599849170829315>','<:HALT:542603773651189760>',
'<:Cumdump:543260690991939584>','<:FredbearPlush:548020515684483072>',
'<:PureEvilJack:548020631191683074>','<:yup:549102182704611328>',
'<:eto:549110549753888779>','<:DaveLovesU:550855068929228800>',
'<:PureFear:550855275830050836>','<:hrmmm:553857757510631434>',
'<:FreddyPlush:553858389403369494>','<:HelpyBoop:553863991982686246>',
'<:Helpy:553864004095836160>','<:loveyizu:564734314567434240>',
'<:thoonk:564737184507101184>','<:Baby:564747238681608192>',
'<:help:564751981726662667>','<:hhngyfdtj:564926491754889218>',
'<:cute:564926571165515797>','<:whatacutie:564927073961902084>',
'<:uwu:565007921641947136>','<:denk:565435459895820288>',
'<:taank:573006288682876929>','<:thnank:573006494296047625>',
'<:thinnnnnnk:573006544246145026>','<:tthhoonnkk:573006630350880778>',
'<:PeterHappy:574807238481281035>','<:inthedark:593334846907088917>',
'<:rabbitman:593375171880943636>','<:iloveyousayitback:605150642230525953>',
'<:takecareofyourselfbitch:605150934640623635>','<:givemeyourteeth:605168016828923924>',
'<:emoji_45:605477313198555347>','<:emoji_46:605477349873549394>','<:angery:605478515776946187>']

rick = "https://tenor.com/view/never-gonna-give-you-up-dont-give-never-give-up-gif-14414705"

haiku_bot = 372175794895585280

seals = """What the fuck did you just fucking say about me, you little bitch? I'll have you know I graduated top of 
my class in the Navy Seals, and I've been involved in numerous secret raids on Al-Quaeda, and I have over 300 
confirmed kills. I am trained in gorilla warfare and I'm the top sniper in the entire US armed forces. You are 
nothing to me but just another target. I will wipe you the fuck out with precision the likes of which has never been 
seen before on this Earth, mark my fucking words. You think you can get away with saying that shit to me over the 
Internet? Think again, fucker. As we speak I am contacting my secret network of spies across the USA and your IP is 
being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic little 
thing you call your life. You're fucking dead, kid. I can be anywhere, anytime, and I can kill you in over seven 
hundred ways, and that's just with my bare hands. Not only am I extensively trained in unarmed combat, but I have 
access to the entire arsenal of the United States Marine Corps and I will use it to its full extent to wipe your 
miserable ass off the face of the continent, you little shit. If only you could have known what unholy retribution 
your little "clever" comment was about to bring down upon you, maybe you would have held your fucking tongue. But you 
couldn't, you didn't, and now you're paying the price, you goddamn idiot. I will shit fury all over you and you will 
drown in it. You're fucking dead, kiddo. """


class Autoresponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """
        Ping Pong
        """
        await ctx.send("Pong")

    @commands.Cog.listener()
    async def on_message(self, ctx):
        msg = ctx.content.lower()
        cnl = ctx.channel

        if ctx.author == self.bot.user:
            return
         
        if (re.search(r"\bepic\b", msg)) and 'not epic' not in msg:
            server_emojis = cnl.guild.emojis
            to_send = random.choice(dabs)
            emojis = []
            for emoji in server_emojis:
                emojis.append(str(emoji))

            if (to_send in emojis_i_can_send) or (to_send in emojis):
                await cnl.send(to_send)
            else:
                splitted = to_send.split(':')
                id = splitted[2].replace('>', '')
                url = f"https://cdn.discordapp.com/emojis/{id}.{'gif' if splitted[0] == '<a' else 'png'}"
                await cnl.send(url)
            

        elif re.fullmatch(r"\bbich\b", msg):
            await cnl.send(random.choice(["Bich", "No u"]))

        elif re.fullmatch(r"\b(bruh|bruh moment)\b", msg):
            await cnl.send("THAT is a bruh moment")

        elif re.search(r"\brip\b", msg):
            await cnl.send("Not epic")

        elif re.search(r"\bnot epic\b", msg):
            await cnl.send(random.choice(["Not epic, indeed", "rip"]))

        elif re.search(r"\buh oh\b", msg):
            await cnl.send("We're in danger")

        # elif ctx.author.id == haiku_bot:
        #     await cnl.send("Shut the fuck up HaikuBot bot shut the fuck up nobody asked you bitch ass i hate you you bad fucking bot st upid ass")

        elif re.match(r"furr(y|ies) on sight!?", msg):
            await cnl.send("TARGET DETECTED,\n\nMISSILES ENROUTE")

        elif re.search(r"\b(o|u)w(o|u)\b", msg, re.IGNORECASE):
            if cnl.id != 561016195780706317: # ID for welcome/leave message channel because well, reasons
                await cnl.send(f"FURRY DETECTED\n\nTARGET DETECTED,\n\nMISSILES ENROUTE")

        elif re.search(r"\b69\b", ctx.clean_content):
            await cnl.send("Ha thats the sex number")
        
        elif re.search(r"\b420\b", ctx.clean_content):
            await cnl.send("Ha thats the weed number")

        elif re.fullmatch(r"\bsmh\b", msg):
            await cnl.send(random.choice(["Shaking my smh", "Smh my head", "Ikr", "Shaking my head"]))
    
        # elif re.fullmatch(r"\b(wtf|what the fuck)\b", msg):
        #     await cnl.send(random.choice(["Smh", "Ikr"]))

        elif re.search(r"good bot", msg):
            await cnl.send(random.choice(["Dank you", "Aww", "Well you're breathtaking"]))
            
        elif re.search(r"(bad bot|stfu bitch bot|stfu bitchbot)", msg):
            await cnl.send(random.choice(["Rip", "Aww", "K", "You sure about that?", seals, "F", "😦"]))
            
        elif re.fullmatch(r'w(ha|u|a)t\?+', msg.lower()) or re.fullmatch(r'w(ha|u|a)t', msg.lower()):
            if str(ctx.content).isupper():
                await cnl.send("YES")
            else:
                await cnl.send("Yes")
        
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if str(reaction) == "📌":
            await reaction.message.pin()
            await reaction.message.remove_reaction(reaction, user)
            await reaction.message.channel.send(f"{user.mention} Pinned a message!")

    @commands.command(aliases=["rick", "rickroll"])
    async def rickroulette(self, ctx):
        """
        Rick Astley = Loose, Doggo = Win
        """
        await ctx.channel.trigger_typing()
        if random.randint(0, 5) == 0:
            await asyncio.sleep(3)
            await ctx.send(f"Get rick rolled\n {rick}")
        else:
            img = requests.get("https://dog.ceo/api/breeds/image/random").json()["message"]
            embed = discord.Embed()
            embed.set_image(url=img)
            await ctx.send(embed=embed)
            

def setup(bot):
    bot.add_cog(Autoresponder(bot))

