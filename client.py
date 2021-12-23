# This file contains the client along with most events.

from help_command import CustomHelpCommand
from asyncio import sleep
from itertools import cycle
from os import environ

import discord
from animation import Wait
from chalk import Chalk
from discord.ext import commands
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_actionrow, create_button
from discord_together import DiscordTogether
from dotenv import load_dotenv

load_dotenv()


# The strings that animate before Sonicbot is ready
starting_steps = [
    "Starting Sonicbot   ",
    "Starting Sonicbot.  ",
    "Starting Sonicbot.. ",
    "Starting Sonicbot...",
]


class Client(commands.AutoShardedBot):
    def __init__(self):
        # "Starting Sonicbot..." animation
        self.starting = Wait(animation=starting_steps)
        self.starting.start()

        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True

        # Initialise AutoShardedBot
        super().__init__(
            command_prefix=["$ ", "$"],
            case_insensitive=True,
            intents=intents,
            owner_ids=[535347480733286410],
            allowed_mentions=discord.AllowedMentions(everyone=False),
        )

        """
        The line below makes the help command case insensitive so that you can run 'help fun' or 'help Fun'.
        """
        self._BotBase__cogs = commands.core._CaseInsensitiveDict()

    colour = 0xFF7000

    async def on_ready(self):
        self.starting.stop()
        green = Chalk("green")
        print(green(f"{self.user.name} is now ready"), end=None)

        # Storing all the buttons needed
        support_btn = create_button(
            label="Support Server",
            style=ButtonStyle.URL,
            emoji=self.get_emoji(907550097368301578),
            url="https://discord.gg/NeZvXk5wh5",
        )
        help_buttons = create_actionrow(
            *[
                create_button(
                    label="Command list",
                    style=ButtonStyle.URL,
                    emoji=self.get_emoji(907549965444849675),
                    url="https://sonicbot.vercel.app/commands",
                ),
                support_btn,
                create_button(
                    style=ButtonStyle.URL,
                    label="Add me",
                    emoji=self.get_emoji(907549597105278976),
                    url="https://dsc.gg/thesonicbot",
                ),
            ]
        )
        self.help_command = CustomHelpCommand(help_buttons)

        self.info_btns = create_actionrow(
            *[
                create_button(
                    style=ButtonStyle.URL,
                    label="Add me",
                    emoji=self.get_emoji(907549597105278976),
                    url="https://dsc.gg/thesonicbot",
                ),
                create_button(
                    style=ButtonStyle.URL,
                    label="Website",
                    emoji=self.get_emoji(907550015063461898),
                    url="https://sonicbot.vercel.app/",
                ),
            ]
        )
        self.error_channel = await self.fetch_channel(922755294252105730)
        self.error_btns = create_actionrow(
            *[
                create_button(
                    style=ButtonStyle.URL,
                    url=f"https://sonicbot.vercel.app/commands",
                    label="Command list",
                    emoji=self.get_emoji(907549965444849675),
                ),
                support_btn,
            ]
        )

        self.loop.create_task(self.change_status())

        self.dt = await DiscordTogether(environ["TOKEN"])

    # Send prefix when mentioned
    async def on_message(self, message):
        if (
            message.content == f"<@!{self.user.id}>"
            or message.content == f"<@{self.user.id}>"
        ):
            await message.channel.send(
                "My prefix is `$`. You can add a space after it, but it's optional."
            )
        else:
            await self.process_commands(message)

    # Changing status
    async def change_status(self):
        statuses = cycle(
            [
                "$help | You can run my commands in DMs too!",
                "$help | sonicbot.vercel.app",
            ]
        )

        while not self.is_closed():
            await self.change_presence(activity=discord.Game(name=next(statuses)))
            await sleep(10)

    # Store message details when it is deleted

    sniped_messages = {}
    esniped_messages = {}

    def sniped_message_to_dict(self, message):
        return {
            "content": message.content,
            "author": str(message.author),
            "author_avatar": message.author.avatar_url,
            "timestamp": message.created_at,
            "attachments": [
                {"url": a.url, "filename": a.filename} for a in message.attachments
            ],
        }

    async def on_message_delete(self, message):
        if not message.guild:
            return

        try:
            # Update the guild's dict with the sniped message
            self.sniped_messages[message.guild.id].update(
                {message.channel.id: self.sniped_message_to_dict(message)}
            )
        except KeyError:
            # Creates a new dict for the guild if it isn't stored
            self.sniped_messages[message.guild.id] = {
                message.channel.id: self.sniped_message_to_dict(message)
            }

    async def on_message_edit(self, before, after):
        if not before.guild:
            return

        try:
            self.esniped_messages[before.guild.id].update(
                {before.channel.id: self.sniped_message_to_dict(before)}
            )
        except KeyError:
            self.esniped_messages[before.guild.id] = {
                before.channel.id: self.sniped_message_to_dict(before)
            }
