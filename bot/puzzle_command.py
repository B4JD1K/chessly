import discord
from discord import app_commands
from discord.ext import commands

from config import config
from api_client import api_client
from board_renderer import get_board_file


class SolveButton(discord.ui.View):
    def __init__(self, puzzle_url: str):
        super().__init__(timeout=None)
        self.add_item(
            discord.ui.Button(
                label="Solve Puzzle",
                style=discord.ButtonStyle.link,
                url=puzzle_url,
                emoji="♟️",
            )
        )


class PuzzleCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="puzzle", description="Get today's daily chess puzzle")
    async def puzzle(self, interaction: discord.Interaction):
        """Display the daily puzzle with a board image and solve button."""
        await interaction.response.defer()

        # Sync user with backend
        avatar_url = None
        if interaction.user.avatar:
            avatar_url = interaction.user.avatar.url

        await api_client.sync_user(
            discord_id=str(interaction.user.id),
            username=interaction.user.display_name,
            avatar_url=avatar_url,
        )

        # Fetch daily puzzle
        puzzle = await api_client.get_daily_puzzle()

        if not puzzle:
            await interaction.followup.send(
                embed=discord.Embed(
                    title="No Puzzle Available",
                    description="There's no puzzle available for today. Check back later!",
                    color=discord.Color.orange(),
                ),
                ephemeral=True,
            )
            return

        # Fetch user streak
        streak = await api_client.get_user_streak(str(interaction.user.id))

        # Generate board image
        flipped = puzzle.player_color == "black"
        board_image = get_board_file(puzzle.fen, flipped=flipped)

        # Create embed
        color_to_move = "White" if puzzle.player_color == "white" else "Black"
        themes_str = ", ".join(puzzle.themes) if puzzle.themes else "Tactics"

        embed = discord.Embed(
            title="Daily Chess Puzzle",
            description=f"**{color_to_move} to move**\n\nFind the best move!",
            color=discord.Color.green(),
        )

        embed.add_field(name="Rating", value=str(puzzle.rating), inline=True)
        embed.add_field(name="Themes", value=themes_str, inline=True)

        if streak:
            streak_text = f"🔥 {streak.current_streak}"
            if streak.puzzle_solved_today:
                streak_text += " (Solved today!)"
            embed.add_field(name="Your Streak", value=streak_text, inline=True)

        embed.set_image(url="attachment://board.png")
        embed.set_footer(text="Chessly - Daily Chess Puzzles")

        # Create solve button
        puzzle_url = f"{config.FRONTEND_URL}/puzzle/daily"
        view = SolveButton(puzzle_url)

        # Send response
        file = discord.File(board_image, filename="board.png")
        await interaction.followup.send(embed=embed, file=file, view=view)

    @app_commands.command(name="streak", description="Check your puzzle solving streak")
    async def streak(self, interaction: discord.Interaction):
        """Display user's current streak."""
        await interaction.response.defer(ephemeral=True)

        streak = await api_client.get_user_streak(str(interaction.user.id))

        if not streak:
            await interaction.followup.send(
                embed=discord.Embed(
                    title="No Streak Data",
                    description="You haven't solved any puzzles yet. Use `/puzzle` to get started!",
                    color=discord.Color.blue(),
                ),
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="Your Puzzle Streak",
            color=discord.Color.orange() if streak.current_streak > 0 else discord.Color.greyple(),
        )

        embed.add_field(
            name="Current Streak",
            value=f"🔥 {streak.current_streak} day{'s' if streak.current_streak != 1 else ''}",
            inline=True,
        )
        embed.add_field(
            name="Best Streak",
            value=f"🏆 {streak.best_streak} day{'s' if streak.best_streak != 1 else ''}",
            inline=True,
        )

        status = "✅ Solved today!" if streak.puzzle_solved_today else "❌ Not solved yet"
        embed.add_field(name="Today's Puzzle", value=status, inline=False)

        if not streak.puzzle_solved_today:
            embed.set_footer(text="Use /puzzle to keep your streak alive!")

        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(PuzzleCog(bot))
