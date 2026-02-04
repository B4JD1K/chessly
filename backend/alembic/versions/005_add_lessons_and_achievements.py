"""Add lessons and achievements

Revision ID: 005
Revises: 004
Create Date: 2026-02-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Lessons table
    op.create_table(
        'lessons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.Enum('basics', 'tactics', 'openings', 'endgames', name='lessoncategory'), nullable=False),
        sa.Column('level', sa.Enum('beginner', 'intermediate', 'advanced', name='lessonlevel'), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_published', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_lessons_id', 'lessons', ['id'])
    op.create_index('ix_lessons_category', 'lessons', ['category'])

    # Lesson steps table
    op.create_table(
        'lesson_steps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('instruction', sa.Text(), nullable=False),
        sa.Column('hint', sa.Text(), nullable=True),
        sa.Column('fen', sa.String(100), nullable=False),
        sa.Column('expected_moves', sa.String(500), nullable=False),
        sa.Column('opponent_move', sa.String(10), nullable=True),
        sa.Column('fen_after_opponent', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_lesson_steps_id', 'lesson_steps', ['id'])
    op.create_index('ix_lesson_steps_lesson_id', 'lesson_steps', ['lesson_id'])

    # User lesson progress table
    op.create_table(
        'user_lesson_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('not_started', 'in_progress', 'completed', name='lessonstatus'), nullable=False, server_default='not_started'),
        sa.Column('current_step_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_lesson_progress_id', 'user_lesson_progress', ['id'])
    op.create_index('ix_user_lesson_progress_user_lesson', 'user_lesson_progress', ['user_id', 'lesson_id'], unique=True)

    # Achievements table
    op.create_table(
        'achievements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('threshold', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('order_index', sa.Integer(), server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_achievements_id', 'achievements', ['id'])
    op.create_index('ix_achievements_code', 'achievements', ['code'], unique=True)

    # User achievements table
    op.create_table(
        'user_achievements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('achievement_id', sa.Integer(), nullable=False),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['achievement_id'], ['achievements.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_achievements_id', 'user_achievements', ['id'])
    op.create_index('ix_user_achievements_user_achievement', 'user_achievements', ['user_id', 'achievement_id'], unique=True)

    # Add stats columns to users table
    op.add_column('users', sa.Column('puzzles_solved', sa.Integer(), server_default='0', nullable=False))
    op.add_column('users', sa.Column('lessons_completed', sa.Integer(), server_default='0', nullable=False))
    op.add_column('users', sa.Column('games_won', sa.Integer(), server_default='0', nullable=False))

    # Insert default achievements
    op.execute("""
        INSERT INTO achievements (code, name, description, icon, event_type, threshold, order_index) VALUES
        ('FIRST_PUZZLE_SOLVED', 'First Steps', 'Solve your first puzzle', '🎯', 'PUZZLE_SOLVED', 1, 1),
        ('PUZZLES_10', 'Puzzle Enthusiast', 'Solve 10 puzzles', '🧩', 'PUZZLE_SOLVED', 10, 2),
        ('PUZZLES_50', 'Puzzle Master', 'Solve 50 puzzles', '🏆', 'PUZZLE_SOLVED', 50, 3),
        ('PUZZLES_100', 'Puzzle Legend', 'Solve 100 puzzles', '👑', 'PUZZLE_SOLVED', 100, 4),
        ('STREAK_3', 'Getting Started', 'Achieve a 3-day streak', '🔥', 'STREAK_DAY', 3, 10),
        ('STREAK_7', 'Week Warrior', 'Achieve a 7-day streak', '💪', 'STREAK_DAY', 7, 11),
        ('STREAK_30', 'Monthly Master', 'Achieve a 30-day streak', '🌟', 'STREAK_DAY', 30, 12),
        ('FIRST_LESSON', 'Eager Learner', 'Complete your first lesson', '📚', 'LESSON_COMPLETED', 1, 20),
        ('LESSONS_5', 'Studious', 'Complete 5 lessons', '🎓', 'LESSON_COMPLETED', 5, 21),
        ('LESSONS_ALL_BASICS', 'Basics Mastered', 'Complete all basics lessons', '✅', 'CATEGORY_COMPLETED_BASICS', 1, 22),
        ('FIRST_WIN', 'Victorious', 'Win your first game', '⚔️', 'GAME_WON', 1, 30),
        ('WINS_10', 'Competitor', 'Win 10 games', '🥇', 'GAME_WON', 10, 31),
        ('FIRST_CHECKMATE', 'Checkmate!', 'Deliver your first checkmate', '♔', 'CHECKMATE_DELIVERED', 1, 40)
    """)

    # Insert sample lessons - Basics category
    op.execute("""
        INSERT INTO lessons (id, title, description, category, level, order_index, is_published) VALUES
        (1, 'Ruch wieży', 'Naucz się jak porusza się wieża', 'basics', 'beginner', 1, true),
        (2, 'Ruch gońca', 'Naucz się jak porusza się goniec', 'basics', 'beginner', 2, true),
        (3, 'Ruch hetmana', 'Naucz się jak porusza się hetman', 'basics', 'beginner', 3, true),
        (4, 'Szach i mat', 'Podstawy szacha i mata', 'basics', 'beginner', 4, true),
        (5, 'Widełki', 'Atak na dwie figury jednocześnie', 'tactics', 'beginner', 1, true),
        (6, 'Mat na ostatniej linii', 'Klasyczny wzorzec matowy', 'tactics', 'intermediate', 2, true)
    """)

    # Insert lesson steps
    op.execute("""
        INSERT INTO lesson_steps (id, lesson_id, order_index, instruction, hint, fen, expected_moves, opponent_move, fen_after_opponent) VALUES
        -- Lesson 1: Ruch wieży
        (1, 1, 0, 'Wieża porusza się poziomo i pionowo. Przesuń wieżę na pole e8, aby dać szacha.', 'Wieża może ruszyć się wzdłuż całej kolumny lub wiersza.', '4k3/8/8/8/8/8/8/R3K3 w Q - 0 1', 'a1e1,a1a8', NULL, NULL),
        (2, 1, 1, 'Świetnie! Teraz przesuń wieżę, aby zaatakować króla.', NULL, '4k3/8/8/8/8/8/8/4RK2 w - - 0 1', 'e1e8', NULL, NULL),

        -- Lesson 2: Ruch gońca
        (3, 2, 0, 'Goniec porusza się po przekątnych. Przesuń gońca, aby zaatakować wieżę.', 'Goniec może ruszyć się tylko po polach tego samego koloru.', '4k3/8/8/3r4/8/8/8/B3K3 w - - 0 1', 'a1e5,a1d4', NULL, NULL),
        (4, 2, 1, 'Dobrze! Goniec atakuje wieżę. Teraz zbij ją.', NULL, '4k3/8/4B3/3r4/8/8/8/4K3 w - - 0 1', 'e5d4', NULL, NULL),

        -- Lesson 3: Ruch hetmana
        (5, 3, 0, 'Hetman łączy ruchy wieży i gońca. Daj szacha hetmanem.', 'Hetman może ruszyć się w dowolnym kierunku.', '4k3/8/8/8/8/8/8/Q3K3 w - - 0 1', 'a1a8,a1e5', NULL, NULL),
        (6, 3, 1, 'Świetnie! Teraz daj mata hetmanem.', NULL, 'Q3k3/8/8/8/8/8/8/4K3 w - - 0 1', 'a8e8,a8f8', NULL, NULL),

        -- Lesson 4: Szach i mat
        (7, 4, 0, 'Szach to atak na króla. Daj szacha wieżą.', NULL, '4k3/8/8/8/8/8/4R3/4K3 w - - 0 1', 'e2e8', 'e8f7', '4k3/5K2/8/8/8/8/8/4K3 w - - 0 1'),
        (8, 4, 1, 'Król uciekł. Teraz daj mata - król nie może uciec ani zablokować.', 'Użyj wieży, aby dać mata na ostatniej linii.', '8/5k2/8/8/8/8/4R3/4K3 w - - 0 1', 'e2e7,e2f2', NULL, NULL),

        -- Lesson 5: Widełki
        (9, 5, 0, 'Widełki to atak na dwie figury jednocześnie. Zaatakuj skoczkiem króla i wieżę.', 'Skoczek skacze w kształcie litery L.', '4k3/8/8/8/3N4/8/8/4K2r w - - 0 1', 'd4f5,d4e6', NULL, NULL),
        (10, 5, 1, 'Świetnie! Teraz zbij wieżę, bo król musi uciekać.', NULL, '4k3/8/5N2/8/8/8/8/4K2r w - - 0 1', 'f5h1', NULL, NULL),

        -- Lesson 6: Mat na ostatniej linii
        (11, 6, 0, 'Król jest uwięziony na ostatniej linii. Daj mata wieżą.', 'Wieża daje mata, bo król nie może uciec - blokują go własne piony.', '6k1/5ppp/8/8/8/8/8/R3K3 w Q - 0 1', 'a1a8', NULL, NULL),
        (12, 6, 1, 'Doskonale! To klasyczny mat na ostatniej linii.', NULL, 'R5k1/5ppp/8/8/8/8/8/4K3 w - - 0 1', NULL, NULL, NULL)
    """)


def downgrade() -> None:
    op.drop_table('user_achievements')
    op.drop_table('achievements')
    op.drop_table('user_lesson_progress')
    op.drop_table('lesson_steps')
    op.drop_table('lessons')

    op.drop_column('users', 'puzzles_solved')
    op.drop_column('users', 'lessons_completed')
    op.drop_column('users', 'games_won')

    op.execute("DROP TYPE IF EXISTS lessoncategory")
    op.execute("DROP TYPE IF EXISTS lessonlevel")
    op.execute("DROP TYPE IF EXISTS lessonstatus")
