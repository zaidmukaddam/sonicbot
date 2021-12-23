"This is the file to run. It contains the commands to warn/ban users from Sonicbot and background tasks."

import os

import discord
import topgg
import dotenv
from discord.ext import commands, tasks
from discord_slash import SlashCommand

from client import Client
from utils import cluster

bans = cluster["sonicbot"]["bans"]

dotenv.load_dotenv()

client = Client()
slash = SlashCommand(
    client, sync_commands=True, delete_from_unused_guilds=True, sync_on_cog_reload=True
)

# Command to message a user from Sonicbot
@client.command(hidden=True)
@commands.is_owner()
async def messageuser(ctx, id: int, *, message):
    if id in client.owner_ids:
        return await ctx.send("You can't send messages to an owner through Sonicbot.")
    try:
        user: discord.User = client.get_user(id)

        embed = discord.Embed(
            title="My developers have sent you a message!",
            colour=client.colour,
        )

        embed.add_field(name="Message", value=message)

        await user.send(embed=embed)
        await ctx.send(f"✅ Messaged user `{user.name}` with this embed.", embed=embed)

    except Exception as e:
        await ctx.send(f"❌ **Error:**\n\n{e}")


# Command to ban a user from submitting suggestions
@client.command(hidden=True, aliases=["suggestionban", "suggestionblock"])
@commands.is_owner()
async def block(ctx, id: int, *, reason):
    if id in client.owner_ids:
        return await ctx.send("You can't block an owner.")

    bans.insert_one({"_id": id})

    try:
        user: discord.User = client.get_user(id)

        embed = discord.Embed(
            title="You've been blocked from sending suggestions!",
            colour=0xFF0000,
            description=f"You've been banned from submitting suggestions as we have noticed that you are spamming them.",
        )
        embed.add_field(name="Reason", value=reason, inline=False)

        await user.send(embed=embed)
        await ctx.send(f"✅ Blocked user `{user.name}` with this embed:", embed=embed)

    except Exception as e:
        await ctx.send(f"❌ **Error:**\n\n{e}")
    except discord.Forbidden:
        await ctx.send(f"{user.name} has DMs disabled, but they have been blocked.")

if __name__ == "__main__":
    # Loop through py files in cogs directory and load them
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            client.load_extension(f"cogs.{file[:-3]}")

    # Load Jishaku
    client.load_extension("jishaku")

    client.run(os.environ["TOKEN"])
