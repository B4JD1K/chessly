import discord
from discord import app_commands
from discord.ext import commands

from config import config
from puzzle_command import PuzzleCog
from learn_command import LearnCog


class ChesslyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.add_cog(PuzzleCog(self))
        await self.add_cog(LearnCog(self))
        await self.tree.sync()
        print(f"Synced slash commands")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print(f"Connected to {len(self.guilds)} guilds")


def main():
    if not config.DISCORD_BOT_TOKEN:
        print("Error: DISCORD_BOT_TOKEN not set in environment")
        return

    bot = ChesslyBot()
    bot.run(config.DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    main()
