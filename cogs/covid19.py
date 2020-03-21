import aiohttp
import discord
from discord.ext import commands, tasks


class CoronaChanWrapper:
    url = 'https://coronavirus-tracker-api.herokuapp.com/v2'

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self._cache = {}

    async def _request(self, endpoint, params=None):
        if endpoint not in self._cache.keys():
            response = await self.session.get(self.url + endpoint, params=params)
            json = await response.json()
            self._cache[endpoint] = json
        return self._cache[endpoint]

    async def get_latest(self):
        data = await self._request("/latest")
        return data["latest"]

    async def get_locations(self, rank_by=None):
        data = await self._request("/locations")
        data = data["locations"]

        ranking_criteria = ['confirmed', 'deaths', 'recovered']
        if rank_by is not None and rank_by not in ranking_criteria:
            raise ValueError(f"Invalid ranking criteria. Expected one of: {ranking_criteria}")

        return sorted(data, key=lambda i: i['latest'][rank_by], reverse=True)

    async def get_location_by_country_code(self, country_code):
        data = await self._request("/locations", {"country_code": country_code})
        return data["locations"]

    async def get_for_country(self, country_code):
        locations = await self.get_location_by_country_code(country_code)
        data = {
            'confirmed': 0,
            'recovered': 0,
            'deaths': 0
        }
        for location in locations:
            data['country'] = location['country']
            latest = location['latest']
            data['confirmed'] += latest['confirmed']
            data['recovered'] += latest['recovered']
            data['deaths'] += latest['deaths']

        return data

    @tasks.loop(hours=1)
    async def _invalidate_cache(self):
        self._cache = {}


class CoronaChan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.corona_chan = CoronaChanWrapper(bot.clientSession)

    @commands.group(aliases=['coronachan', 'covid'])
    async def corona(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx)

    def _build_basic_embed(self, data):
        embed = discord.Embed(title="Corona Chan's stats")
        for i in ('confirmed', 'recovered', 'deaths'):
            embed.add_field(name=i.title(), value=data[i], inline=True)
        embed.add_field(
            name='Source',
            value='[coronavirus-tracker-api](https://github.com/ExpDev07/coronavirus-tracker-api)',
            inline=False
        )
        return embed

    @corona.command(name='stats')
    async def corona_stats(self, ctx, country_code=None):
        if country_code is None:
            data = await self.corona_chan.get_latest()
        else:
            data = await self.corona_chan.get_for_country(country_code)
        embed = self._build_basic_embed(data)
        if 'country' in data:
            embed.insert_field_at(0, name='Country', value=data['country'])
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(CoronaChan(bot))
