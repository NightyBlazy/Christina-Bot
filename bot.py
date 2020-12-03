import os
import discord
from discord import guild
from dotenv import load_dotenv
from words import *
import random
import asyncio

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_TOKEN')

client = discord.Client()


@client.event
async def on_ready():
    print("{0.user} is activated!".format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == 'kendini tanıt aptal bot':
        response = "Ben ben aptal bir bot olan Christina- Sen bana aptal mı dedin seni lanet olası pislik?"
        await message.channel.send(response)
    if message.content == 'ismin niye christina':
        response = "Ne bileyim ben! Benim ismim Christina değil, Makise Kurisu!"
        await message.channel.send(response)
    if 'sex' in message.content:
        if message.author.id == 399210730777346048:
            await message.add_reaction(flamed)
            await message.channel.send('Haha! Çok komiksin Tuna...')
        else:
            return
    for h in hamilton:
        if h in message.content:
            await message.channel.send(random.choice(hamilton_jokes))
    for t in tsun_word:
        if t in message.content:
            for a in anti_tsun:
                if a in message.content:
                    await message.add_reaction(thumbsdown)
                    await message.add_reaction(anger)
                    return
            if 'salak' in message.content:
                await message.channel.send("Sen kime salak diyon lan tek hücreli şerefsiz?!")
                return
            else:
                await message.add_reaction(thumbsup)
    if message.content == 'christina konuş':
        await message.channel.send("Niye konuşayim ki? Sırf senin keyfin istedi diye konuşmak mı zorundayım?")
    if 'roblox nasıl oyun' in message.content:
        await message.channel.send("Çöp.(nokta)")
    if 'tsundere marşını yolla christina' in message.content:
        await message.channel.send("https://www.youtube.com/watch?v=tOzOD-82mW0")
    if message.content == 'bruh':
        await message.channel.send("Moment...")
    if message.content == 'emmin arkanda':
        await message.channel.send("Maddi Manevi Her Yönden")
        await asyncio.sleep(0.5)
        await message.channel.send("Ağzına Sıçar")
        await asyncio.sleep(0.5)
        await message.channel.send("Hadi Öptü- B-Bir dakika! Sen bana ne dedirtiyorsun lan gerizekalı herif?!")

    

client.run(TOKEN)