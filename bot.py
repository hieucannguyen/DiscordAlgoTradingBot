import trade
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

prefix = "$$"
client = commands.Bot(command_prefix=prefix, intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

# create chart command
@client.command(name="chart")
async def create_chart(ctx):
    # asks user for a stock and returns a 1 day chart for specified stock ticker
    await ctx.send('Enter a stock: ')

    # checks same user and channel
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
    # ensure correct stock ticker
    try:
        msg = await client.wait_for("message", check=check, timeout=30)
        stock = trade.trade()
        stock.create_charts(f'{msg.content}')  # 30 seconds to reply
        await ctx.channel.send(file=discord.File('chart.png')) # send chart image
    except:
        await ctx.send("Not a real stock.")

# End of day stock information
@client.command(name="EOD")
async def create_chart(ctx):
    await ctx.send('Enter a stock: ')

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
    try:
        msg = await client.wait_for("message", check=check, timeout=30)
        stock = trade.trade()
        stockEOD = stock.EOD(f'{msg.content}')
        await ctx.channel.send(stockEOD)
    except:
        await ctx.send("Not a real stock.")

# compare 2 different stocks
# displays 2 charts side by side
@client.command(name="compare")
async def create_chart(ctx):
    await ctx.send('Enter a stock: ')

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
    try:
        msg1 = await client.wait_for("message", check=check, timeout=30)
        await ctx.send('Enter another stock: ')
        msg2 = await client.wait_for("message", check=check, timeout=30)
        stock = trade.trade()
        stock.compare_stocks(f'{msg1.content}', f'{msg2.content}')
        await ctx.channel.send(file=discord.File('chart.png'))
    except:
        await ctx.send("At least one of the stocks is not real")

# ultilize bollinger strategy on a stock
@client.command(name="bollinger")
async def bollinger_strategy(ctx):
    stock = trade.trade()

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
    await ctx.send('Enter a stock: ')
    msg = await client.wait_for("message", check=check, timeout=30)
    await ctx.send('Available intervals [1d, 1mo, 1y, 2y, max]\nEnter an interval: ') # specify interval
    interval = await client.wait_for("message", check=check, timeout=30)
    bollinger = stock.bollinger(f'{msg.content}', f'{interval.content}')
    try:
        if (bollinger == 'Not a real stock' or bollinger == 'Interval unavailable'):
            raise Exception
        await ctx.channel.send(file=discord.File('chart.png'))
        await ctx.channel.send(bollinger)
    except:
        await ctx.channel.send(bollinger)

# run the bot
client.run(TOKEN)
