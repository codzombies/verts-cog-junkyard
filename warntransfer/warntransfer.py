import datetime

import discord
from redbot.core import commands, modlog

LOADING = "https://i.imgur.com/l3p6EMX.gif"


class WarnTransfer(commands.Cog):
    """Transfer WarnSystem data to core"""

    __author__ = "Vertyco#0117"
    __version__ = "0.0.2"

    def format_help_for_context(self, ctx):
        helpcmd = super().format_help_for_context(ctx)
        info = (
            f"{helpcmd}\n"
            f"Cog Version: {self.__version__}\n"
            f"Author: {self.__author__}"
        )
        return info

    async def red_delete_data_for_user(self, *, requester, user_id: int):
        """No data to delete"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="warntransfer")
    @commands.is_owner()
    async def wtrans(self, ctx):
        """WarnSystem Transfer Options"""
        pass

    async def import_ws(self, ctx, msg: discord.Message, wsmodlogs: dict):
        count = 0
        failed = 0
        update_interval = 100  # Adjust this value based on rate limits and performance

        for guild_id, userdict in wsmodlogs.items():
            if not userdict:
                continue
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                continue

            # ... (same as before)

            for user_id, w in userdict.items():
                warns = w["x"]  # List of warns
                if not warns:
                    continue
                for warning in warns:  # Each warning is a dict
                    # ... (same as before)

                    try:
                        await modlog.create_case(
                            self.bot,
                            guild,
                            time,
                            wtype,
                            int(user_id),
                            int(author),
                            reason,
                            until=None,
                            channel=None,
                        )
                        count += 1

                        if count % update_interval == 0:
                            embed = discord.Embed(
                                description="Importing ModLog cases...",
                                color=discord.Color.orange(),
                            )
                            embed.set_thumbnail(url=LOADING)
                            embed.set_footer(text=f"{count} imported so far")
                            await msg.edit(embed=embed)  # Update progress every N cases
                    except PermissionError:
                        await ctx.send(
                            f"Failed to create case for User: {user_id} in guild: {guild.name}"
                        )
                        failed += 1
                        continue

            # ... (same as before)

        return count, failed

    @wtrans.command(name="movetocore")
    async def movetocore(self, ctx):
        """
        Import WarnSystem data to core modlog
        """
        warnsystem = self.bot.get_cog("WarnSystem")
        if not warnsystem:
            return await ctx.send(
                "WarnSystem is not loaded/installed. Please load it before importing"
            )
        embed = discord.Embed(
            description="Importing ModLog cases...", color=discord.Color.orange()
        )
        embed.set_thumbnail(url=LOADING)
        msg = await ctx.send(embed=embed)
        wsmodlogs = await warnsystem.data.custom("MODLOGS").all()
        async with ctx.typing():
            success, failed = await self.import_ws(ctx, msg, wsmodlogs)
            if success:
                res = f"Finished importing {success} cases!"
                if failed:
                    res += f"\nFailed to import {failed} cases!"
                embed = discord.Embed(description=res, color=discord.Color.green())
                await msg.edit(embed=embed)
            else:
                res = "No cases imported!"
                if failed:
                    res += f"\nFailed to import {failed} cases!"
                embed = discord.Embed(description=res, color=discord.Color.blue())
                await msg.edit(embed=embed)
