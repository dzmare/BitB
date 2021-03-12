import datetime as dt
import random
import asyncio
import requests
import avwx
import os

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
auth = os.getenv('AUTH')
bot_token = os.getenv('BOT_TOKEN')
nasa_api = os.getenv('NASA_API')
windy_api = os.getenv('WINDY_API')

windy_url = 'https://api.windy.com/api/webcams/v2/'
taf_url = f'https://avwx.rest/api/taf/'
metar_url = f'https://avwx.rest/api/metar/'

bot = commands.Bot(command_prefix='!')

def to_upper(argument):
    return argument.upper()

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command()
async def apod(ctx, flags=None):
    apod = requests.get(f'https://api.nasa.gov/planetary/apod?api_key={nasa_api}')
    title = apod.json()['title']
    narration = apod.json()['explanation']

    async with ctx.typing():
        try:
            img_link = apod.json()['hdurl']
        except KeyError:
            img_link = apod.json()['url']


        if flags in ['explanation', '-e']:
            await ctx.send(f'''*Astronomy Photo of the Day:* \n\n**Title:** *{title}*\n\n**Explanation:** {narration}\n
                        {img_link}''')
        else:
            await ctx.send(f'''*Astronomy Photo of the Day:* \n\n**Title:** *{title}*\n {img_link}''')

@bot.command('halp')
async def explain(ctx):
    await ctx.send(f'''
    Welcome to the helpful help page. Here are some flags you can pass to any `!wx <airport>` command:
    ```
        -m ---> returns the METAR
        -t ---> returns the TAF
        -mh --> returns a translated METAR
        -th --> returns a translated TAF
        -h ---> returns a translated METAR and TAF
        -hc --> returns a translated METAR and TAF, with webcam images
        -c ---> returns the METAR and TAF, with webcam images
    ```
    For example, `!wx cyvr -hc` will give you a translated METAR and TAF, as well as webcams within a 2 mile radius of CYVR.

    You can also change the webcam search radius by passing a nummber *after* the flags, like so:
    `!wx cyvr -c 5`.

    The webcams are found using the lat/long from an AWOS; this means that if the airport you're looking for doesn't have one, you don't be able
    to get the webcams either (this is a WIP).
    ''')


@bot.command(name='wx')
async def get_wx(ctx, airport: to_upper, flags=None, radius=2):

    def get_metar(airport):
        raw_metar = requests.get(f'{metar_url}{airport}?token={auth}').json()['raw']
        metar = avwx.Metar(airport)
        metar._update(raw_metar, dt.datetime.now(), False)

        return metar

    def get_taf(airport):
        raw_taf = requests.get(f'{taf_url}{airport}?token={auth}').json()['raw']
        taf = avwx.Taf(airport)
        taf._update(raw_taf, dt.datetime.now(), False)

        return taf

    def get_webcams(lat,long, radius):
        header = {'x-windy-key': f'{windy_api}'}
        webcams = requests.get(f'{windy_url}list/nearby={lat},{long},{radius}?show=webcams:image,url',  headers=header)

        return webcams.json()['result']['webcams']

    try:

        if flags in ['metar', '-m']:
            metar = get_metar(airport)
            await ctx.send(f"METAR for {airport}: ```{metar.raw}```")

        elif flags in ['taf', '-t']:
            taf = get_taf(airport)
            await ctx.send(f'TAF for {airport}: ```{taf.raw}```')

        elif flags in ['-mh']:
            metar = get_metar(airport)
            await ctx.send(f'METAR for {airport}: ```{metar.summary}```')

        elif flags in ['-th']:
            taf = get_taf(airport)
            await ctx.send(f'TAF for {airport}: ```{taf.summary}```')

        elif flags in ['human', '-h']:
            metar = get_metar(airport)
            taf = get_taf(airport)
            await ctx.send(f'METAR for {airport}: ```{metar.summary}```\n TAF for {airport}: ```{taf.summary}```')

        elif flags in ['-hc']:
            metar = get_metar(airport)
            taf = get_taf(airport)

            await ctx.send(f'METAR for {airport}: ```{metar.summary}```\n TAF for {airport}: ```{taf.summary}```')

            for cam in get_webcams(metar.station.latitude, metar.station.longitude):
                await ctx.send(f"{cam['title']}: {cam['image']['current']['preview']}")

        elif flags in ['cam', 'camera', '-c']:
            metar = get_metar(airport)
            taf = get_taf(airport)

            await ctx.send(f'METAR for {airport}: ```{metar.raw}```\n TAF for {airport}: ```{taf.raw}```')

            for cam in get_webcams(metar.station.latitude, metar.station.longitude, radius):
                await ctx.send(f"{cam['title']}: {cam['image']['current']['preview']}")

        else:
            metar = get_metar(airport)
            taf = get_taf(airport)

            await ctx.send(f'METAR for {airport}: ```{metar.raw}```\n TAF for {airport}: ```{taf.raw}```')
    except KeyError:
        await ctx.send('That was an invalid selection.')

bot.run(bot_token)








#METAR.raw   -m
#
#TAF.raw     -t
#
#METAR human -mh
#
#TAF human   -th
#
#METAR + TAF human -h
#
#METAR + TAF + WEBCAM human -hc
#
#METAR + TAF + WEBCAM -c
#
#METAR + TAF
