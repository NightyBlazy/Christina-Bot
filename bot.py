import os
import asyncio
import datetime
import sys
import time as ti

import discord
from discord.ext import commands
from discord.errors import HTTPException
import wavelink

from typing import Union
from data import *
import random
import traceback
import re
import itertools
from dotenv import load_dotenv

RURL = re.compile('https?:\/\/(?:www\.)?.+')



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


class Bot(commands.Bot):
    def __init__(self):
        super(Bot,self).__init__(command_prefix='<',help_command=None)

        self.add_cog(Music(self))
        self.add_cog(Komutlar(self))

    async def on_ready(self):
        print("{0.user} is activated!".format(self))
        print(f"Bot's Latency:{round (self.latency * 1000)}ms")
        print("-------------------------------")

    async def on_message(self,message):
        if message.author == self.user:
            return

        msg = message.content
        snd = message.channel

        if msg == 'kendini tanıt aptal bot':
            response = "Ben ben aptal bir bot olan Christina- Sen bana aptal mı dedin seni lanet olası pislik?"
            await snd.send(response)
        if msg == 'ismin niye christina':
            response = "Ne bileyim ben! Benim ismim Christina değil, Makise Kurisu!"
            await snd.send(response)
        if 'sex' in msg:
            if message.author.id == 399210730777346048:
                await message.add_reaction(flamed)
                await snd.send('Haha! Çok komiksin Tuna...')
            else:
                return
        for t in tsun_word:
            if t in msg:
                for a in anti_tsun:
                    if a in msg:
                        await message.add_reaction(thumbsdown)
                        await message.add_reaction(anger)
                        return
                for s in tsun_baka:
                    if s in msg:
                        await snd.send(f"Sen nasıl '{msg}' dersin!? BAKA!")
                        return
                else:
                    await message.add_reaction(thumbsup)
        if msg == 'christina konuş':
            await snd.send("Niye konuşayim ki? Sırf senin keyfin istedi diye konuşmak mı zorundayım?")
        if 'roblox nasıl oyun' in msg:
            await snd.send("Çöp.(nokta)")
        if 'tsundere marşını yolla christina' in msg:
            await snd.send("https://www.youtube.com/watch?v=tOzOD-82mW0")
        if msg == 'bruh':
            await snd.send("Moment...")

        if msg == f"@!{self.user.id}>":
            await snd.send("M-Merhaba, ben Christina bot! Komutlarımı kullanmak için '**<**' prefixini kullan.")
            await snd.send("Diğer komutlarımı öğrenmek için '**<help**' veya '**<yardım**' komutlarını kullan!")
        if 'napim' in msg:
            await snd.send("Asıl ben napim...")


        await self.process_commands(message)

class Controller:
    def __init__(self,bot,guild_id):
        self.bot = bot
        self.guild_id = guild_id
        self.channel = None

        self.next = asyncio.Event()
        self.queue = asyncio.Queue()

        self.now_playing = None

        self.bot.loop.create_task(self.controller_loop())
    async def controller_loop(self):
        await self.bot.wait_until_ready()

        player = self.bot.wavelink.get_player(self.guild_id)

        while True:
            if self.now_playing:
                await self.now_playing.delete()

            self.next.clear()

            song = await self.queue.get()
            await player.play(song)

            self.now_playing = await self.channel.send(f'**Şuanda Oynatılıyor:** `{song}`')

            await self.next.wait()


class Music(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.controllers = {}

        if not hasattr(bot, 'wavelink'):
            self.bot.wavelink = wavelink.Client(bot=self.bot)

        self.bot.loop.create_task(self.start_nodes())
    async def start_nodes(self):
        await self.bot.wait_until_ready()

        node = await self.bot.wavelink.initiate_node(host='127.0.0.1',
                                              port=2333,
                                              rest_uri='http://127.0.0.1:2333',
                                              password='youshallnotpass',
                                              identifier='TEST',
                                              region='us_central')
        node.set_hook(self.on_event_hook)

    async def on_event_hook(self,event):
        if isinstance(event,(wavelink.TrackEnd,wavelink.TrackException)):
            controller = self.get_controller(event.player)
            controller.next.set()

    def get_controller(self, value:Union[commands.Context,wavelink.Player]):
        if isinstance(value,commands.Context):
            gid = value.guild.id
        else:
            gid = value.guild_id
        try:
            controller = self.controllers[gid]
        except KeyError:
            controller = Controller(self.bot,gid)
            self.controllers[gid] = controller

        return controller

    async def cog_check(self, ctx):
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True
    async def cog_command_error(self, ctx, error):
        if isinstance(error,commands.NoPrivateMessage):
            try:
                return await ctx.send("Bu komut DM olarak kullanılamaz.")
            except HTTPException:
                pass
        print("Ignoring exception in command{}".format(ctx.command),file= sys.stderr)
        traceback.print_exception(type(error),error,error.__traceback__,file=sys.stderr)

    @commands.command(aliases=['gel','bağlan'])
    async def connect(self,ctx,*,channel:discord.VoiceChannel=None):
        if not channel:
            try:
                channel= ctx.author.voice.channel
            except AttributeError:
                await ctx.send('Bir sesliye bağlı değilsin... Sesli chate bağlansan da beni uğraştırmasan?!')
                raise discord.DiscordException("User is not connected any voice channel")

        player = self.bot.wavelink.get_player(ctx.guild.id)

        if channel.id == player.channel_id:
            return await ctx.send("Körmüsün?! Zaten seninle aynı odadayım!")

        await ctx.send(f"Şu chate bağlanıyorum: **`{channel.name}`**")
        await player.connect(channel.id)

        controller = self.get_controller(ctx)
        controller.channel = ctx.channel

    @commands.command(aliases=['çal','ç','oynat'])
    async def play(self,ctx,*, query: str):
        if not RURL.match(query):
            query = f'ytsearch:{query}'

        tracks = await self.bot.wavelink.get_tracks(f'ytsearch:{query}')

        if not tracks:
            return await ctx.send("Bana verdiğin linkten oynatacak müzik bulamadım. Daha düzgün bir **link** versen mesela?")

        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.is_connected:
            await ctx.invoke(self.connect)

        track = tracks[0]

        controller = self.get_controller(ctx)
        await controller.queue.put(track)
        await ctx.send(f'{str(track)} **oynatma listesine eklendi**')


    @commands.command(aliases=['ayrıl','leave','terket'])
    async def disconnect(self,ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)

        try:
            del self.controllers[ctx.guild.id]
        except KeyError:
            await player.disconnect()
            return await ctx.send("Sen gerizekalı mısın?! Bir odaya katılmadım ki ayrılayim!")
        if player.is_playing:
            await player.stop()

        await player.disconnect()
        await ctx.send("Peki, o zaman sesliden ayrılıyorum. Z-Zaten seni sevdiğim için filan gelmemiştim tamam mı?!")


    @commands.command(aliases=['s','geç','g'])
    async def skip(self,ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Şuan bir şey çalıyora mı benziyorum?!')

        await ctx.send("Tamam be tamam, geçtik müziği!")
        await player.stop()

    @commands.command(aliases=['dur','durdur','du'])
    async def pause(self,ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send("Müzik zaten durmuş durumda gerizekalı!")

        await ctx.send("Tamamdır müziği durdurdum.")
        await player.set_pause(True)

    @commands.command(aliases=['devam','de'])
    async def resume(self,ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.is_paused:
            return await ctx.send("Müzik zaten çalıyor gerizekalı!")

        await ctx.send("Oh be, hiç devam ettirmiyeceksin sanmıştım... D-Devam ettirmek istediğimden filan değil tabi...")
        await player.set_pause(False)

    @commands.command(aliases=['np','şuan','current'])
    async def now_playing(self,ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.current:
            return await ctx.send("Şuan bir şey çalıyora mı benziyorum?!")

        controller = self.get_controller(ctx)

        await controller.now_playing.delete()
        controller.now_playing = await ctx.send(f"**Şuanda çalınan şarkı:**{player.current}")

    @commands.command(aliases=['sıra','sı','q'])
    async def queue(self,ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)
        controller = self.get_controller(ctx)

        if not player.current or not controller.queue._queue:
            return await ctx.send("Oynatma listemde hiçbir şarkı yok ki!")

        upcoming = list(itertools.islice(controller.queue._queue, 0, 5))

        fmt = '\n'.join(f'**`{str(song)}`**' for song in upcoming)
        embed = discord.Embed(title = f"Sıradaki - Next {len(upcoming)}", description = fmt)

        await ctx.send(embed=embed)


class Komutlar(commands.Cog):
    def __init__(self,bot,mention=discord.mentions):
        self.bot = bot
        self.mention= mention

    @commands.command(aliases=['hamilton','h'])
    async def hami(self,ctx):
        await ctx.send(random.choice(hamilton_jokes))

    @commands.command(aliases = ['yardım'])
    async def help(self,ctx):
        help_embed = discord.Embed(title="**Tüm Komutlar**")
        help_text = ""

        for commands in self.bot.commands:
            help_text += f"{commands}\n"

        help_embed.add_field(
            name="Komutlarım:",
            value= help_text ,
            inline= False
        )

        await ctx.send(embed = help_embed)

bot = Bot()
print("Welcome to the Christina Bot starting interface")
print("Are You Gonna Start Her Now?")
start = input("y/n\n")
if start == "y":
    print("Activating the Christina...")
    print("Please wait while her systems are starting...")
    bot.run(TOKEN)
elif start == "n":
    print("Okay... Why are you started this app then?")
    ti.sleep(3)
    exit()
else:
    print("Wrong command... I'm gonna pretend you sayed 'Yes!'...")
    print("Activating the Christina...")
    print("Please wait while her systems are starting...")
    bot.run(TOKEN)
