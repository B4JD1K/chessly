const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const WS_BASE_URL = API_BASE_URL.replace("http", "ws");

export interface PuzzleResponse {
  id: number;
  fen: string;
  rating: number;
  themes: string[];
  player_color: "white" | "black";
}

export interface MoveRequest {
  move: string;
  move_index: number;
}

export interface MoveResponse {
  correct: boolean;
  is_complete: boolean;
  opponent_move: string | null;
  message: string | null;
}

export interface UserResponse {
  id: number;
  discord_id: string;
  username: string;
  avatar_url: string | null;
  rating: number;
  current_streak: number;
  best_streak: number;
  last_puzzle_date: string | null;
}

export interface StreakResponse {
  current_streak: number;
  best_streak: number;
  last_puzzle_date: string | null;
  puzzle_solved_today: boolean;
}

export interface UserCreate {
  discord_id: string;
  username: string;
  avatar_url?: string | null;
}

// Game types
export type TimeControl = "bullet_1" | "bullet_2" | "blitz_3" | "blitz_5" | "rapid_10" | "rapid_15";
export type GameStatus = "waiting" | "active" | "completed" | "abandoned";
export type GameResult = "white_win" | "black_win" | "draw" | "abandoned";

export interface PlayerInfo {
  id: number;
  username: string;
  avatar_url: string | null;
}

export interface GameResponse {
  id: number;
  code: string;
  status: GameStatus;
  result: GameResult | null;
  current_fen: string;
  time_control: TimeControl;
  white_time_remaining: number;
  black_time_remaining: number;
  white_player: PlayerInfo | null;
  black_player: PlayerInfo | null;
  is_white_turn: boolean;
  move_count: number;
  created_at: string;
  started_at: string | null;
}

export interface GameMoveResponse {
  valid: boolean;
  move_san: string | null;
  fen_after: string | null;
  game_over: boolean;
  result: GameResult | null;
  message: string | null;
}

export const TIME_CONTROL_LABELS: Record<TimeControl, string> = {
  bullet_1: "1+0 Bullet",
  bullet_2: "2+1 Bullet",
  blitz_3: "3+0 Blitz",
  blitz_5: "5+0 Blitz",
  rapid_10: "10+0 Rapid",
  rapid_15: "15+10 Rapid",
};

// Puzzle endpoints
export async function getDailyPuzzle(): Promise<PuzzleResponse> {
  const response = await fetch(`${API_BASE_URL}/puzzles/daily`);
  if (!response.ok) {
    throw new Error("Failed to fetch daily puzzle");
  }
  return response.json();
}

export async function getPuzzle(puzzleId: number): Promise<PuzzleResponse> {
  const response = await fetch(`${API_BASE_URL}/puzzles/${puzzleId}`);
  if (!response.ok) {
    throw new Error("Failed to fetch puzzle");
  }
  return response.json();
}

export async function validateMove(
  puzzleId: number,
  move: string,
  moveIndex: number
): Promise<MoveResponse> {
  const response = await fetch(`${API_BASE_URL}/puzzles/${puzzleId}/validate-move`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      move,
      move_index: moveIndex,
    } as MoveRequest),
  });
  if (!response.ok) {
    throw new Error("Failed to validate move");
  }
  return response.json();
}

// User endpoints
export async function syncUser(userData: UserCreate): Promise<UserResponse> {
  const response = await fetch(`${API_BASE_URL}/users/sync`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(userData),
  });
  if (!response.ok) {
    throw new Error("Failed to sync user");
  }
  return response.json();
}

export async function getStreak(discordId: string): Promise<StreakResponse> {
  const response = await fetch(`${API_BASE_URL}/users/${discordId}/streak`);
  if (!response.ok) {
    throw new Error("Failed to fetch streak");
  }
  return response.json();
}

export async function completePuzzle(
  discordId: string,
  puzzleId: number,
  success: boolean = true
): Promise<StreakResponse> {
  const response = await fetch(
    `${API_BASE_URL}/users/${discordId}/puzzles/${puzzleId}/complete?success=${success}`,
    { method: "POST" }
  );
  if (!response.ok) {
    throw new Error("Failed to complete puzzle");
  }
  return response.json();
}

// Game endpoints
export async function createGame(
  discordId: string,
  timeControl: TimeControl = "blitz_5"
): Promise<GameResponse> {
  const response = await fetch(`${API_BASE_URL}/games?discord_id=${discordId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ time_control: timeControl }),
  });
  if (!response.ok) {
    throw new Error("Failed to create game");
  }
  return response.json();
}

export async function getGame(code: string): Promise<GameResponse> {
  const response = await fetch(`${API_BASE_URL}/games/${code}`);
  if (!response.ok) {
    throw new Error("Failed to fetch game");
  }
  return response.json();
}

export async function joinGame(code: string, discordId: string): Promise<GameResponse> {
  const response = await fetch(`${API_BASE_URL}/games/${code}/join?discord_id=${discordId}`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("Failed to join game");
  }
  return response.json();
}

export async function resignGame(code: string, discordId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/games/${code}/resign?discord_id=${discordId}`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("Failed to resign");
  }
}

export function getGameWebSocketUrl(code: string, discordId: string): string {
  return `${WS_BASE_URL}/games/${code}/ws?discord_id=${discordId}`;
}

// Bot game types
export type BotDifficulty = "beginner" | "easy" | "medium" | "hard" | "expert" | "master";

export interface BotGameResponse {
  id: number;
  difficulty: BotDifficulty;
  player_color: "white" | "black";
  status: "active" | "completed";
  result: GameResult | null;
  current_fen: string;
  moves: string[];
  move_count: number;
  is_player_turn: boolean;
  created_at: string;
  ended_at: string | null;
}

export interface BotMoveResponse {
  valid: boolean;
  player_move_san: string | null;
  bot_move_uci: string | null;
  bot_move_san: string | null;
  fen_after: string | null;
  game_over: boolean;
  result: GameResult | null;
  message: string | null;
}

export const BOT_DIFFICULTY_LABELS: Record<BotDifficulty, { name: string; elo: number }> = {
  beginner: { name: "Beginner", elo: 800 },
  easy: { name: "Easy", elo: 1000 },
  medium: { name: "Medium", elo: 1400 },
  hard: { name: "Hard", elo: 1800 },
  expert: { name: "Expert", elo: 2200 },
  master: { name: "Master", elo: 2800 },
};

// Bot game endpoints
export async function createBotGame(
  discordId: string,
  difficulty: BotDifficulty = "medium",
  playerColor: "white" | "black" = "white"
): Promise<BotGameResponse> {
  const response = await fetch(`${API_BASE_URL}/bot-games?discord_id=${discordId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ difficulty, player_color: playerColor }),
  });
  if (!response.ok) {
    throw new Error("Failed to create bot game");
  }
  return response.json();
}

export async function getBotGame(gameId: number): Promise<BotGameResponse> {
  const response = await fetch(`${API_BASE_URL}/bot-games/${gameId}`);
  if (!response.ok) {
    throw new Error("Failed to fetch bot game");
  }
  return response.json();
}

export async function makeBotMove(
  gameId: number,
  move: string,
  discordId: string
): Promise<BotMoveResponse> {
  const response = await fetch(`${API_BASE_URL}/bot-games/${gameId}/move?discord_id=${discordId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ move }),
  });
  if (!response.ok) {
    throw new Error("Failed to make move");
  }
  return response.json();
}

export async function resignBotGame(gameId: number, discordId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/bot-games/${gameId}/resign?discord_id=${discordId}`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("Failed to resign");
  }
}

export async function getBotGamePGN(gameId: number): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/bot-games/${gameId}/pgn`);
  if (!response.ok) {
    throw new Error("Failed to fetch PGN");
  }
  return response.text();
}

// Lesson types
export type LessonCategory = "basics" | "tactics" | "openings" | "endgames";
export type LessonLevel = "beginner" | "intermediate" | "advanced";
export type LessonStatus = "not_started" | "in_progress" | "completed";

export interface LessonStepResponse {
  id: number;
  order_index: number;
  instruction: string;
  hint: string | null;
  fen: string;
}

export interface LessonResponse {
  id: number;
  title: string;
  description: string | null;
  category: LessonCategory;
  level: LessonLevel;
  order_index: number;
  steps_count: number;
}

export interface LessonDetailResponse {
  id: number;
  title: string;
  description: string | null;
  category: LessonCategory;
  level: LessonLevel;
  steps: LessonStepResponse[];
}

export interface LessonProgressResponse {
  lesson_id: number;
  status: LessonStatus;
  current_step_index: number;
  total_steps: number;
  started_at: string | null;
  completed_at: string | null;
}

export interface LessonWithProgressResponse {
  lesson: LessonResponse;
  progress: LessonProgressResponse | null;
}

export interface ValidateLessonMoveResponse {
  correct: boolean;
  is_step_complete: boolean;
  is_lesson_complete: boolean;
  next_step_index: number | null;
  opponent_move: string | null;
  fen_after: string | null;
  message: string | null;
}

export interface CategoryProgressResponse {
  category: LessonCategory;
  total_lessons: number;
  completed_lessons: number;
  in_progress_lessons: number;
}

export const LESSON_CATEGORY_LABELS: Record<LessonCategory, { name: string; icon: string }> = {
  basics: { name: "Podstawy", icon: "📘" },
  tactics: { name: "Taktyki", icon: "⚔️" },
  openings: { name: "Otwarcia", icon: "🚀" },
  endgames: { name: "Końcówki", icon: "👑" },
};

export const LESSON_LEVEL_LABELS: Record<LessonLevel, string> = {
  beginner: "Początkujący",
  intermediate: "Średniozaawansowany",
  advanced: "Zaawansowany",
};

// Lesson endpoints
export async function getLessons(category?: LessonCategory): Promise<LessonResponse[]> {
  const url = category
    ? `${API_BASE_URL}/lessons?category=${category}`
    : `${API_BASE_URL}/lessons`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("Failed to fetch lessons");
  }
  return response.json();
}

export async function getLessonsWithProgress(
  discordId: string,
  category?: LessonCategory
): Promise<LessonWithProgressResponse[]> {
  const url = category
    ? `${API_BASE_URL}/lessons/with-progress?discord_id=${discordId}&category=${category}`
    : `${API_BASE_URL}/lessons/with-progress?discord_id=${discordId}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("Failed to fetch lessons with progress");
  }
  return response.json();
}

export async function getLesson(lessonId: number): Promise<LessonDetailResponse> {
  const response = await fetch(`${API_BASE_URL}/lessons/${lessonId}`);
  if (!response.ok) {
    throw new Error("Failed to fetch lesson");
  }
  return response.json();
}

export async function getLessonProgress(
  lessonId: number,
  discordId: string
): Promise<LessonProgressResponse> {
  const response = await fetch(
    `${API_BASE_URL}/lessons/${lessonId}/progress?discord_id=${discordId}`
  );
  if (!response.ok) {
    throw new Error("Failed to fetch lesson progress");
  }
  return response.json();
}

export async function startLesson(
  lessonId: number,
  discordId: string
): Promise<LessonProgressResponse> {
  const response = await fetch(
    `${API_BASE_URL}/lessons/${lessonId}/start?discord_id=${discordId}`,
    { method: "POST" }
  );
  if (!response.ok) {
    throw new Error("Failed to start lesson");
  }
  return response.json();
}

export async function validateLessonMove(
  lessonId: number,
  move: string,
  discordId: string
): Promise<ValidateLessonMoveResponse> {
  const response = await fetch(
    `${API_BASE_URL}/lessons/${lessonId}/validate-move?discord_id=${discordId}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ move }),
    }
  );
  if (!response.ok) {
    throw new Error("Failed to validate move");
  }
  return response.json();
}

export async function getCategoryProgress(
  discordId: string
): Promise<CategoryProgressResponse[]> {
  const response = await fetch(
    `${API_BASE_URL}/lessons/category-progress?discord_id=${discordId}`
  );
  if (!response.ok) {
    throw new Error("Failed to fetch category progress");
  }
  return response.json();
}

export async function getRecommendedLesson(
  discordId: string
): Promise<LessonResponse | null> {
  const response = await fetch(
    `${API_BASE_URL}/lessons/recommended?discord_id=${discordId}`
  );
  if (!response.ok) {
    throw new Error("Failed to fetch recommended lesson");
  }
  const data = await response.json();
  return data || null;
}

// Achievement types
export interface AchievementResponse {
  id: number;
  code: string;
  name: string;
  description: string;
  icon: string | null;
  threshold: number;
}

export interface UserAchievementResponse {
  achievement: AchievementResponse;
  unlocked_at: string;
}

export interface UserAchievementsListResponse {
  unlocked: UserAchievementResponse[];
  locked: AchievementResponse[];
  total_unlocked: number;
  total_available: number;
}

export interface UserStatsResponse {
  puzzles_solved: number;
  lessons_completed: number;
  games_won: number;
  current_streak: number;
  best_streak: number;
}

// Achievement endpoints
export async function getAllAchievements(): Promise<AchievementResponse[]> {
  const response = await fetch(`${API_BASE_URL}/achievements`);
  if (!response.ok) {
    throw new Error("Failed to fetch achievements");
  }
  return response.json();
}

export async function getUserAchievements(
  discordId: string
): Promise<UserAchievementsListResponse> {
  const response = await fetch(`${API_BASE_URL}/achievements/user/${discordId}`);
  if (!response.ok) {
    throw new Error("Failed to fetch user achievements");
  }
  return response.json();
}

export async function getUserStats(discordId: string): Promise<UserStatsResponse> {
  const response = await fetch(`${API_BASE_URL}/achievements/user/${discordId}/stats`);
  if (!response.ok) {
    throw new Error("Failed to fetch user stats");
  }
  return response.json();
}
