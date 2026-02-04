import discord
from discord import app_commands
from discord.ext import commands

from config import config
from api_client import api_client

CATEGORY_LABELS = {
    "basics": {"name": "Podstawy", "icon": "📘"},
    "tactics": {"name": "Taktyki", "icon": "⚔️"},
    "openings": {"name": "Otwarcia", "icon": "🚀"},
    "endgames": {"name": "Końcówki", "icon": "👑"},
}

LEVEL_LABELS = {
    "beginner": "Początkujący",
    "intermediate": "Średniozaawansowany",
    "advanced": "Zaawansowany",
}


class LearnButton(discord.ui.View):
    def __init__(self, learn_url: str, lesson_url: str = None):
        super().__init__(timeout=None)
        self.add_item(
            discord.ui.Button(
                label="Przeglądaj lekcje",
                style=discord.ButtonStyle.link,
                url=learn_url,
                emoji="📚",
            )
        )
        if lesson_url:
            self.add_item(
                discord.ui.Button(
                    label="Rozpocznij lekcję",
                    style=discord.ButtonStyle.link,
                    url=lesson_url,
                    emoji="▶️",
                )
            )


class LearnCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="learn", description="Ucz się szachów krok po kroku")
    async def learn(self, interaction: discord.Interaction):
        """Display recommended lesson and learning progress."""
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

        # Fetch recommended lesson
        recommended = await api_client.get_recommended_lesson(str(interaction.user.id))

        # Fetch category progress
        progress = await api_client.get_category_progress(str(interaction.user.id))

        # Create embed
        embed = discord.Embed(
            title="📚 Nauka szachów",
            description="Ucz się szachów poprzez interaktywne lekcje. Każdy krok to ruch na planszy!",
            color=discord.Color.blue(),
        )

        # Add progress fields
        if progress:
            progress_text = ""
            total_completed = 0
            total_lessons = 0

            for cat in progress:
                label = CATEGORY_LABELS.get(cat.category, {"name": cat.category, "icon": "📖"})
                completed = cat.completed_lessons
                total = cat.total_lessons
                total_completed += completed
                total_lessons += total

                if total > 0:
                    percent = int((completed / total) * 100)
                    bar = "█" * (percent // 10) + "░" * (10 - percent // 10)
                    progress_text += f"{label['icon']} **{label['name']}**: {completed}/{total} `{bar}`\n"

            if progress_text:
                embed.add_field(
                    name="Twój postęp",
                    value=progress_text,
                    inline=False,
                )

            if total_lessons > 0:
                overall_percent = int((total_completed / total_lessons) * 100)
                embed.add_field(
                    name="Ogółem",
                    value=f"Ukończono **{total_completed}** z **{total_lessons}** lekcji ({overall_percent}%)",
                    inline=False,
                )

        # Add recommended lesson
        lesson_url = None
        if recommended:
            cat_label = CATEGORY_LABELS.get(
                recommended.category, {"name": recommended.category, "icon": "📖"}
            )
            level_label = LEVEL_LABELS.get(recommended.level, recommended.level)

            embed.add_field(
                name="🎯 Rekomendowana lekcja",
                value=(
                    f"**{recommended.title}**\n"
                    f"{cat_label['icon']} {cat_label['name']} • {level_label}\n"
                    f"{recommended.steps_count} kroków"
                ),
                inline=False,
            )
            lesson_url = f"{config.FRONTEND_URL}/learn/{recommended.id}"
        else:
            embed.add_field(
                name="🎉 Gratulacje!",
                value="Ukończyłeś wszystkie dostępne lekcje!",
                inline=False,
            )

        embed.set_footer(text="Chessly - Interaktywna nauka szachów")

        # Create buttons
        learn_url = f"{config.FRONTEND_URL}/learn"
        view = LearnButton(learn_url, lesson_url)

        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="stats", description="Sprawdź swoje statystyki")
    async def stats(self, interaction: discord.Interaction):
        """Display user's stats and achievements progress."""
        await interaction.response.defer(ephemeral=True)

        stats = await api_client.get_user_stats(str(interaction.user.id))

        if not stats:
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Brak danych",
                    description="Nie znaleziono twoich statystyk. Zacznij od rozwiązania puzzla lub lekcji!",
                    color=discord.Color.orange(),
                ),
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"📊 Statystyki - {interaction.user.display_name}",
            color=discord.Color.purple(),
        )

        embed.add_field(
            name="🎯 Puzzle",
            value=f"Rozwiązane: **{stats.puzzles_solved}**",
            inline=True,
        )
        embed.add_field(
            name="📚 Lekcje",
            value=f"Ukończone: **{stats.lessons_completed}**",
            inline=True,
        )
        embed.add_field(
            name="⚔️ Gry",
            value=f"Wygrane: **{stats.games_won}**",
            inline=True,
        )
        embed.add_field(
            name="🔥 Streak",
            value=f"Aktualny: **{stats.current_streak}** dni\nNajlepszy: **{stats.best_streak}** dni",
            inline=False,
        )

        profile_url = f"{config.FRONTEND_URL}/profile"
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="Zobacz profil i osiągnięcia",
                style=discord.ButtonStyle.link,
                url=profile_url,
                emoji="🏆",
            )
        )

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(LearnCog(bot))
