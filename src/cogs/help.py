"""Help command cog for the Zion Discord Bot."""

import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="Help",
            description="List of available commands:",
            color=discord.Color.blue(),
        )
        embed.add_field(
            name=".play <url>", value="Play a song from a URL.", inline=False
        )
        embed.add_field(name=".pause", value="Pause the current song.", inline=False)
        embed.add_field(name=".resume", value="Resume the paused song.", inline=False)
        embed.add_field(name=".stop", value="Stop the current song.", inline=False)
        embed.add_field(
            name=".skip", value="Skip to the next song in the queue.", inline=False
        )
        embed.add_field(name=".queue", value="Show the current queue.", inline=False)
        await ctx.send(embed=embed)
