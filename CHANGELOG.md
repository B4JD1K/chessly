# Changelog

Wszystkie istotne zmiany w projekcie Chessly.

## [Unreleased]

### Added
- Wiele daily puzzli z różnych źródeł (Lichess, Chess.com)
- GitHub Actions workflow do automatycznego pobierania puzzli (`.github/workflows/fetch-puzzles.yml`)
- Skrypty migracji SQL:
  - `backend/migrations/001_initial_setup.sql` - pełna konfiguracja bazy
  - `backend/migrations/002_add_puzzle_source.sql` - migracja dla istniejącej bazy

### Changed

#### Backend
- `backend/app/models/puzzle.py`:
  - Dodano pole `source: Mapped[str | None]` do śledzenia pochodzenia puzzla
  - Usunięto `unique=True` z `daily_date` (pozwala na wiele puzzli dziennie)
- `backend/app/schemas/puzzle.py`:
  - Dodano `source: str | None` do `PuzzleResponse`
- `backend/app/services/puzzle_service.py`:
  - Dodano metodę `get_daily_puzzles()` zwracającą listę puzzli
  - Zachowano `get_daily_puzzle()` dla kompatybilności wstecznej
- `backend/app/routers/puzzles.py`:
  - Zmieniono endpoint `GET /puzzles/daily` - zwraca `list[PuzzleResponse]`
- `backend/scripts/fetch_puzzles.py`:
  - Przepisano skrypt do pobierania z wielu źródeł (Lichess, Chess.com)
  - Dodano argumenty `--days` i `--date`
  - Dodano walidację duplikatów (source + date)

#### Frontend
- `frontend/src/lib/api.ts`:
  - Zmieniono `getDailyPuzzle()` na `getDailyPuzzles()` zwracającą tablicę
  - Dodano pole `source` do interfejsu `PuzzleResponse`
- `frontend/src/app/puzzle/daily/page.tsx`:
  - Obsługa wielu puzzli z przełączaniem między źródłami
  - Przyciski nawigacji (Lichess / Chess.com)
  - Wskaźnik ukończenia dla każdego puzzla (zielona kropka)
  - Osobny komunikat "All puzzles solved!" gdy wszystkie rozwiązane

## [0.8.0] - 2026-02-04

### Added
- Skrypt `fetch_puzzles.py` do pobierania puzzli z Lichess i Chess.com

### Fixed
- Naprawiono duplikat linku "Profil" w menu nawigacji
- Przeniesiono overlay "Bot is thinking" do sekcji statusu (zamiast środka planszy)

## [0.7.0] - 2026-02-04

### Fixed
- Zarejestrowano handler eventów achievementów w `main.py`
- Poprawiono logikę `player_color` w odpowiedzi puzzla (było odwrócone)
- Dodano symlink dla ścieżki Stockfish na Debian (`/usr/games/stockfish` → `/usr/bin/stockfish`)

## [0.6.0] - 2026-02-04

### Fixed
- Naprawiono błędy TypeScript w `bot-game-board.tsx` (async onPieceDrop)
- Naprawiono błędy zamknięcia (closure) dla `discordId` w komponentach React
- Przeniesiono `authOptions` do `lib/auth.ts` (kompatybilność z Next.js App Router)
- Rozwiązano circular import poprzez przeniesienie `BotDifficulty` do `app/enums.py`
- Obniżono wersję pytest do 7.4.4 (kompatybilność z pytest-asyncio)

## [0.5.0] - 2026-02-04

### Added
- Dockerfile dla deploymentu na Render
- Wsparcie dla Stockfish w kontenerze Docker
- Konfiguracja CORS dla produkcji

### Security
- Usunięto hardcoded secrets z plików `.env.example`

## [0.4.0] - 2026-02-03

### Added
- Etap 7: System lekcji i achievementów
- Tabele: lessons, lesson_steps, user_lesson_progress, achievements, user_achievements
- Endpointy API dla lekcji i achievementów
- Frontend: strony lekcji z interaktywną szachownicą

## [0.3.0] - 2026-02-02

### Added
- Etap 6: Discord Activity
- Integracja z Discord Embedded App SDK
- Wsparcie dla uruchamiania jako Discord Activity

## [0.2.0] - 2026-02-01

### Added
- Etap 5: Gra z botem (Stockfish)
- Różne poziomy trudności bota
- Historia ruchów i eksport PGN

## [0.1.0] - 2026-01-31

### Added
- Etap 4: Multiplayer (gra przez link)
- WebSocket dla gier w czasie rzeczywistym
- Kontrola czasu (bullet, blitz, rapid)
- System puzzli dziennych
- Streak tracking
- Discord OAuth authentication
