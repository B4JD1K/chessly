-- =====================================================
-- Chessly Database - Initial Setup
-- Run this script to create the complete database schema
-- =====================================================

-- Enable UUID extension (optional, for future use)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- ENUM TYPES
-- =====================================================

-- Lesson categories
CREATE TYPE lesson_category AS ENUM ('basics', 'tactics', 'openings', 'endgames');

-- Lesson levels
CREATE TYPE lesson_level AS ENUM ('beginner', 'intermediate', 'advanced');

-- Lesson status
CREATE TYPE lesson_status AS ENUM ('not_started', 'in_progress', 'completed');

-- =====================================================
-- USERS TABLE
-- =====================================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(500),
    rating INTEGER DEFAULT 1200,

    -- Streak tracking
    current_streak INTEGER DEFAULT 0,
    best_streak INTEGER DEFAULT 0,
    last_puzzle_date DATE,

    -- Stats for achievements
    puzzles_solved INTEGER DEFAULT 0,
    lessons_completed INTEGER DEFAULT 0,
    games_won INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ix_users_discord_id ON users(discord_id);

-- =====================================================
-- PUZZLES TABLE
-- =====================================================

CREATE TABLE puzzles (
    id SERIAL PRIMARY KEY,
    fen VARCHAR(100) NOT NULL,
    solution TEXT NOT NULL,  -- UCI moves separated by space
    rating INTEGER DEFAULT 1500,
    themes TEXT,  -- comma-separated themes
    source VARCHAR(50),  -- lichess, chess.com, etc.
    daily_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ix_puzzles_daily_date ON puzzles(daily_date);
CREATE INDEX ix_puzzles_source_daily_date ON puzzles(source, daily_date);

-- =====================================================
-- PUZZLE VARIANTS TABLE
-- =====================================================

CREATE TABLE puzzle_variants (
    id SERIAL PRIMARY KEY,
    puzzle_id INTEGER NOT NULL REFERENCES puzzles(id) ON DELETE CASCADE,
    move_sequence TEXT NOT NULL,  -- UCI moves to reach this position
    response_move VARCHAR(10) NOT NULL,  -- Correct response in UCI
    is_mainline BOOLEAN DEFAULT FALSE
);

-- =====================================================
-- USER PUZZLE PROGRESS TABLE
-- =====================================================

CREATE TABLE user_puzzle_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    puzzle_id INTEGER NOT NULL REFERENCES puzzles(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'in_progress',
    attempts INTEGER DEFAULT 0,
    current_move_index INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- =====================================================
-- GAME SESSIONS TABLE
-- =====================================================

CREATE TABLE game_sessions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(8) UNIQUE NOT NULL,

    -- Players
    white_player_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    black_player_id INTEGER REFERENCES users(id) ON DELETE SET NULL,

    -- Game state
    status VARCHAR(20) DEFAULT 'waiting',
    result VARCHAR(20),
    current_fen VARCHAR(100) DEFAULT 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',

    -- Time control
    time_control VARCHAR(20) DEFAULT 'blitz_5',
    white_time_remaining INTEGER DEFAULT 300,
    black_time_remaining INTEGER DEFAULT 300,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    last_move_at TIMESTAMPTZ
);

CREATE INDEX ix_game_sessions_code ON game_sessions(code);

-- =====================================================
-- GAME MOVES TABLE
-- =====================================================

CREATE TABLE game_moves (
    id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL REFERENCES game_sessions(id) ON DELETE CASCADE,
    move_number INTEGER NOT NULL,
    move_uci VARCHAR(10) NOT NULL,
    move_san VARCHAR(10) NOT NULL,
    fen_after VARCHAR(100) NOT NULL,
    time_spent INTEGER DEFAULT 0,  -- milliseconds
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- BOT GAMES TABLE
-- =====================================================

CREATE TABLE bot_games (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    player_color VARCHAR(10) DEFAULT 'white',

    -- Bot settings
    difficulty VARCHAR(20) DEFAULT 'medium',

    -- Game state
    status VARCHAR(20) DEFAULT 'active',
    result VARCHAR(20),
    current_fen VARCHAR(100) DEFAULT 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',

    -- Move history (space-separated UCI moves)
    moves TEXT DEFAULT '',

    -- PGN
    pgn TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ
);

-- =====================================================
-- LESSONS TABLE
-- =====================================================

CREATE TABLE lessons (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category lesson_category NOT NULL,
    level lesson_level NOT NULL DEFAULT 'beginner',
    order_index INTEGER NOT NULL DEFAULT 0,
    is_published BOOLEAN DEFAULT TRUE
);

-- =====================================================
-- LESSON STEPS TABLE
-- =====================================================

CREATE TABLE lesson_steps (
    id SERIAL PRIMARY KEY,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    order_index INTEGER NOT NULL,

    -- Content
    instruction TEXT NOT NULL,
    hint TEXT,

    -- Chess position
    fen VARCHAR(100) NOT NULL,
    expected_moves VARCHAR(500) NOT NULL DEFAULT '',  -- UCI moves, comma-separated

    -- Optional opponent response
    opponent_move VARCHAR(10),
    fen_after_opponent VARCHAR(100)
);

-- =====================================================
-- USER LESSON PROGRESS TABLE
-- =====================================================

CREATE TABLE user_lesson_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    status lesson_status NOT NULL DEFAULT 'not_started',
    current_step_index INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

-- =====================================================
-- ACHIEVEMENTS TABLE
-- =====================================================

CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    icon VARCHAR(50),
    event_type VARCHAR(50) NOT NULL,
    threshold INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    order_index INTEGER DEFAULT 0
);

CREATE INDEX ix_achievements_code ON achievements(code);

-- =====================================================
-- USER ACHIEVEMENTS TABLE
-- =====================================================

CREATE TABLE user_achievements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id INTEGER NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    unlocked_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id, achievement_id)
);

-- =====================================================
-- INITIAL ACHIEVEMENTS DATA
-- =====================================================

INSERT INTO achievements (code, name, description, icon, event_type, threshold, order_index) VALUES
-- Puzzle achievements
('FIRST_PUZZLE', 'Pierwszy puzzle', 'Rozwiąż swój pierwszy puzzle', '🧩', 'PUZZLE_SOLVED', 1, 1),
('PUZZLE_10', 'Amator puzzli', 'Rozwiąż 10 puzzli', '🎯', 'PUZZLE_SOLVED', 10, 2),
('PUZZLE_50', 'Mistrz puzzli', 'Rozwiąż 50 puzzli', '🏆', 'PUZZLE_SOLVED', 50, 3),
('PUZZLE_100', 'Legenda puzzli', 'Rozwiąż 100 puzzli', '👑', 'PUZZLE_SOLVED', 100, 4),

-- Streak achievements
('STREAK_3', 'Początek serii', 'Utrzymaj 3-dniową serię', '🔥', 'STREAK_DAY', 3, 10),
('STREAK_7', 'Tydzień praktyki', 'Utrzymaj 7-dniową serię', '⚡', 'STREAK_DAY', 7, 11),
('STREAK_30', 'Miesiąc wytrwałości', 'Utrzymaj 30-dniową serię', '💪', 'STREAK_DAY', 30, 12),

-- Lesson achievements
('FIRST_LESSON', 'Pierwsza lekcja', 'Ukończ swoją pierwszą lekcję', '📖', 'LESSON_COMPLETED', 1, 20),
('LESSON_5', 'Student', 'Ukończ 5 lekcji', '🎓', 'LESSON_COMPLETED', 5, 21),
('LESSON_ALL', 'Absolwent', 'Ukończ wszystkie lekcje', '🏅', 'LESSON_COMPLETED', 20, 22),

-- Game achievements
('FIRST_WIN', 'Pierwsze zwycięstwo', 'Wygraj swoją pierwszą grę', '🥇', 'GAME_WON', 1, 30),
('WIN_10', 'Zwycięzca', 'Wygraj 10 gier', '🏆', 'GAME_WON', 10, 31),
('WIN_50', 'Mistrz', 'Wygraj 50 gier', '👑', 'GAME_WON', 50, 32);

-- =====================================================
-- INITIAL LESSONS DATA
-- =====================================================

-- Lesson 1: Podstawy - Ruch pionem
INSERT INTO lessons (id, title, description, category, level, order_index) VALUES
(1, 'Ruch pionem', 'Naucz się jak poruszają się piony na szachownicy', 'basics', 'beginner', 1);

INSERT INTO lesson_steps (lesson_id, order_index, instruction, hint, fen, expected_moves) VALUES
(1, 0, 'Pion może ruszyć się o jedno pole do przodu. Przesuń piona z e2 na e3.', 'Kliknij na piona e2 i przeciągnij na e3', 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', 'e2e3'),
(1, 1, 'Z pozycji startowej pion może ruszyć się o dwa pola. Przesuń piona z d2 na d4.', 'Pion na swoim pierwszym ruchu może przejść dwa pola', '8/8/8/8/8/4P3/PPPP1PPP/8 w - - 0 1', 'd2d4'),
(1, 2, 'Piony biją na skos. Zbij czarnego piona pionem e4.', 'Pion bije na skos, nie prosto', '8/8/8/3p4/4P3/8/8/8 w - - 0 1', 'e4d5');

-- Lesson 2: Podstawy - Ruch wieżą
INSERT INTO lessons (id, title, description, category, level, order_index) VALUES
(2, 'Ruch wieżą', 'Naucz się jak porusza się wieża', 'basics', 'beginner', 2);

INSERT INTO lesson_steps (lesson_id, order_index, instruction, hint, fen, expected_moves) VALUES
(2, 0, 'Wieża porusza się po liniach prostych - w pionie i poziomie. Przesuń wieżę z a1 na a8.', 'Wieża może przejść przez całą planszę w linii prostej', 'r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1', 'a1a8'),
(2, 1, 'Wieża może też poruszać się poziomo. Przesuń wieżę z h1 na a1.', 'Ruch poziomy przez całą szachownicę', '8/8/8/8/8/8/8/4K2R w K - 0 1', 'h1a1');

-- Lesson 3: Taktyki - Widełki
INSERT INTO lessons (id, title, description, category, level, order_index) VALUES
(3, 'Widełki', 'Naucz się atakować dwie figury jednocześnie', 'tactics', 'beginner', 1);

INSERT INTO lesson_steps (lesson_id, order_index, instruction, hint, fen, expected_moves) VALUES
(3, 0, 'Skoczek może zaatakować dwie figury naraz. Znajdź ruch skoczkiem, który atakuje króla i wieżę.', 'Szukaj pola, z którego skoczek zaatakuje obie figury', 'r3k3/8/8/8/8/8/8/4K1N1 w - - 0 1', 'g1f3,g1e2'),
(3, 1, 'Wykonaj widełki hetmanem - zaatakuj króla i wieżę jednocześnie.', 'Hetman łączy ruchy wieży i gońca', '4k3/8/8/8/8/8/r7/4K2Q w - - 0 1', 'h1a1');
