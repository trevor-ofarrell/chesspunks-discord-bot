import discord
import json
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio

class Admin(commands.Cog):

    def __init__(self, bot, owner_id):
        self.bot = bot
        self._last_member = None
        self.owner_id = owner_id

    async def cog_check(self, ctx):
        if ctx.message.author.guild_permissions.administrator or ctx.message.author.id == int(self.owner_id):
            return True
        await ctx.send("You dont have permission to use this command.")
        return False
    
    @commands.command()
    async def ban(self, ctx, member : discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(member.name + " has been banned")

    @commands.command()
    async def unban(self, ctx, id: int, reason=None):
        if not id:
            await ctx.send("you failed to specify the user's id.")
            return False
        user = await self.bot.fetch_user(id)
        print(type(user), flush=True)
        await ctx.guild.unban(user, reason=reason)
        await ctx.send(user.name + " has been unbanned")
        return True

    @commands.command()
    async def addRole(self, ctx, member: discord.Member, role: discord.Role):
        await member.add_roles(role)
        return True

    @commands.command()
    async def removeRole(self, ctx, member: discord.Member, role: discord.Role):
        await member.remove_roles(role)
        return True

    @commands.command(pass_context=True)
    async def broadcast(self, ctx, *, message : str = None):
        """Broadcasts a message to all connected servers.  Can only be done by the owner."""

        channel = ctx.message.channel
        author  = ctx.message.author

        if message == None:
            await channel.send(usage)
            return

        for server in self.bot.guilds:
            # Get the default channel
            targetChan = discord.utils.get(server.channels, name="general")
            
            try:
                await targetChan.send(message)
            except Exception:
                pass

