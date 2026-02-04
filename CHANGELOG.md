# Changelog

Wszystkie istotne zmiany w projekcie będą dokumentowane w tym pliku.

Format oparty na [Keep a Changelog](https://keepachangelog.com/pl/1.0.0/),
projekt stosuje [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.7.0] - 2026-02-04

### Added - Etap 7: System lekcji i achievementów

#### Backend
- **System lekcji (Learning Path):**
  - Model `Lesson` - lekcje z kategoriami i poziomami trudności
    - Kategorie: basics, tactics, openings, endgames
    - Poziomy: beginner, intermediate, advanced
  - Model `LessonStep` - kroki lekcji z FEN i oczekiwanymi ruchami
  - Model `UserLessonProgress` - postęp użytkownika w lekcjach
  - `LessonService` - logika walidacji ruchów i postępu
  - Router `/lessons` z endpointami:
    - `GET /lessons` - lista lekcji
    - `GET /lessons/with-progress` - lekcje z postępem użytkownika
    - `GET /lessons/category-progress` - postęp w kategoriach
    - `GET /lessons/recommended` - rekomendowana lekcja
    - `GET /lessons/{id}` - szczegóły lekcji ze krokami
    - `POST /lessons/{id}/start` - rozpoczęcie lekcji
    - `POST /lessons/{id}/validate-move` - walidacja ruchu
  - 6 przykładowych lekcji z krokami

- **System achievementów:**
  - Model `Achievement` - definicje osiągnięć
  - Model `UserAchievement` - odblokowane osiągnięcia użytkownika
  - `EventService` - event-driven system zdarzeń
    - Eventy: PUZZLE_SOLVED, LESSON_COMPLETED, STREAK_DAY, GAME_WON, CHECKMATE_DELIVERED
  - `AchievementService` - sprawdzanie i odblokowywanie achievementów
  - Router `/achievements` z endpointami:
    - `GET /achievements` - lista achievementów
    - `GET /achievements/user/{discord_id}` - achievementy użytkownika
    - `GET /achievements/user/{discord_id}/stats` - statystyki
  - 13 domyślnych achievementów

- Rozszerzenie modelu `User`:
  - `puzzles_solved`, `lessons_completed`, `games_won` - liczniki dla achievementów
- Migracja `005_add_lessons_and_achievements.py`
- Wersja API: 0.7.0

#### Frontend
- **Strony lekcji:**
  - `/learn` - lista lekcji z postępem i kategoriami
  - `/learn/[id]` - strona pojedynczej lekcji
- **Komponent `LessonBoard`:**
  - Interaktywna szachownica dla lekcji
  - Instrukcje krok po kroku
  - Walidacja ruchów przez backend
  - Podpowiedzi (hint)
  - Pasek postępu
- **Strona profilu:**
  - `/profile` - profil użytkownika
  - Statystyki: puzzle, lekcje, gry, streak
  - Lista achievementów (odblokowane i zablokowane)
- Rozszerzony `api.ts`:
  - Typy i endpointy dla lekcji
  - Typy i endpointy dla achievementów
- Zaktualizowany `Header`:
  - Link "Nauka"
  - Dropdown menu z profilem i osiągnięciami
- Zaktualizowana strona `/activity`:
  - Link do nauki
  - Link do profilu

#### Discord Bot
- Nowa komenda `/learn`:
  - Wyświetla postęp w kategoriach
  - Rekomendowana lekcja
  - Przyciski do aplikacji web
- Nowa komenda `/stats`:
  - Statystyki użytkownika
  - Link do profilu i osiągnięć
- Rozszerzony `api_client.py`:
  - `get_recommended_lesson()`
  - `get_category_progress()`
  - `get_user_stats()`

---

## [0.6.0] - 2026-02-04

### Added - Etap 6: Discord Activity

#### Backend
- Router `/auth` z endpointami do Discord Activity:
  - `POST /auth/discord/activity` - wymiana kodu OAuth2 na access token
- Aktualizacja `config.py` z ustawieniami Discord OAuth2:
  - `discord_client_id`
  - `discord_client_secret`
  - `discord_redirect_uri`
- Rozszerzenie CORS o domeny Discord (`discord.com`, `*.discordsays.com`)
- Wersja API: 0.4.0

#### Frontend
- Integracja `@discord/embedded-app-sdk` (v1.4.0)
- Biblioteka `lib/discord.ts`:
  - `isRunningInDiscord()` - wykrywanie trybu Discord Activity
  - `getDiscordSdk()` - inicjalizacja SDK
  - `initializeDiscordSdk()` - pełna autoryzacja z backendem
  - `setDiscordActivity()` - ustawianie statusu aktywności
- Context `DiscordProvider` (`contexts/discord-context.tsx`):
  - Stan autoryzacji Discord
  - Informacje o użytkowniku
  - Hook `useDiscord()`
- Komponent `ActivityLayout`:
  - Warunkowe ukrywanie Header w Discord
  - Loading state przy inicjalizacji SDK
  - Obsługa błędów połączenia
- Strona `/activity` - główne menu Discord Activity:
  - Puzzle dnia
  - Gra z botem
  - Gra z innym graczem
  - Status: wkrótce - Ranking
- Zaktualizowany hook `useUser`:
  - Obsługa autoryzacji z Discord Activity
  - Kompatybilność z NextAuth i Discord SDK
- Zaktualizowane pliki `.env.example`:
  - `NEXT_PUBLIC_DISCORD_CLIENT_ID`
  - `NEXT_PUBLIC_DISCORD_SDK_MOCK`
  - `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET` (backend)

---

## [0.5.0] - 2026-02-04

### Added - Etap 5: Gra z botem (Stockfish)

#### Backend
- `StockfishService` - integracja z silnikiem Stockfish
  - Konfigurowane poziomy trudności (beginner → master)
  - Mapowanie ELO: 800 → 2800
  - Ustawienia Skill Level, depth, time limit
- Model `BotGame` - gry przeciwko botowi
  - Przechowywanie historii ruchów
  - Generowanie PGN
  - Status i wynik gry
- `BotGameService` - logika gier z botem
  - Tworzenie gry z wyborem koloru
  - Walidacja ruchów gracza
  - Automatyczne odpowiedzi bota
  - Wykrywanie końca gry (mat, pat, remis)
- Router `/bot-games` z endpointami:
  - `GET /bot-games/difficulties` - lista poziomów trudności
  - `POST /bot-games` - utworzenie gry
  - `GET /bot-games/{id}` - pobranie stanu gry
  - `POST /bot-games/{id}/move` - wykonanie ruchu
  - `POST /bot-games/{id}/resign` - poddanie się
  - `GET /bot-games/{id}/pgn` - eksport PGN
  - `GET /bot-games/user/{discord_id}/history` - historia gier
- Migracja `004_add_bot_games.py`

#### Frontend
- Strona `/play/bot` - wybór ustawień gry z botem
  - Wybór poziomu trudności (6 poziomów)
  - Wybór koloru (białe/czarne)
- Strona `/play/bot/[id]` - gra przeciwko botowi
- Komponent `BotGameBoard` - szachownica do gry z botem
  - Wskaźnik "Bot is thinking..."
  - Przycisk poddania się
  - Pobieranie PGN po zakończeniu gry
- Zaktualizowana strona `/play` z dwoma opcjami:
  - Gra ze znajomym
  - Gra z botem

---

## [0.4.0] - 2026-02-04

### Added - Etap 4: Multiplayer (gra przez link)

#### Backend
- Model `GameSession` - sesje gier multiplayer
  - Kod gry (8 znaków) do udostępniania
  - Status: waiting, active, completed, abandoned
  - Kontrola czasu (bullet, blitz, rapid)
  - Śledzenie pozostałego czasu dla obu graczy
- Model `GameMove` - historia ruchów w partii
- `ConnectionManager` - zarządzanie połączeniami WebSocket
- `GameService` - logika tworzenia/dołączania do gier, walidacji ruchów
- Router `/games` z endpointami:
  - `POST /games` - utworzenie nowej gry
  - `GET /games/{code}` - pobranie stanu gry
  - `POST /games/{code}/join` - dołączenie do gry
  - `POST /games/{code}/move` - wykonanie ruchu
  - `POST /games/{code}/resign` - poddanie się
  - `WS /games/{code}/ws` - WebSocket dla synchronizacji w czasie rzeczywistym
- Migracja `003_add_multiplayer_games.py`

#### Frontend
- Strona `/play` - lobby do tworzenia gier
  - Wybór kontroli czasu
  - Tworzenie gry i generowanie linku
- Strona `/play/[code]` - strona gry
- Komponent `WaitingRoom` - oczekiwanie na przeciwnika
  - Kopiowanie linku do udostępnienia
  - WebSocket do wykrywania dołączenia przeciwnika
- Komponent `GameBoard` - szachownica multiplayer
  - Synchronizacja ruchów przez WebSocket
  - Wyświetlanie informacji o graczach
  - Obsługa poddania się
- Komponent `ChessClock` - zegar szachowy
  - Odliczanie czasu
  - Wizualne ostrzeżenia (low time, critical time)
  - Wykrywanie timeout
- Link "Play" w nagłówku

---

## [0.3.0] - 2026-02-03

### Added - Etap 3: Discord Bot

#### Bot (`bot/`)
- Struktura bota discord.py (`main.py`, `config.py`)
- Klient API do komunikacji z backendem (`api_client.py`)
- Generator obrazów szachownicy z FEN (`board_renderer.py`)
  - Wykorzystuje python-chess + cairosvg
  - Renderuje PNG 400x400 z pozycji
- Komenda `/puzzle`:
  - Pobiera dzienny puzzle z API
  - Wyświetla embed z obrazem szachownicy
  - Pokazuje rating, tematy, streak użytkownika
  - Przycisk "Solve Puzzle" linkujący do aplikacji web
- Komenda `/streak`:
  - Wyświetla aktualny i najlepszy streak użytkownika
  - Informuje czy dzisiejszy puzzle został rozwiązany
- Automatyczna synchronizacja użytkownika z backendem

---

## [0.2.0] - 2026-02-03

### Added - Etap 2: Web MVP

#### Frontend
- Discord OAuth z NextAuth.js (`/api/auth/[...nextauth]`)
- Strona logowania z Discord (`/login`)
- Komponenty shadcn/ui (Button, Card, Avatar)
- Interaktywna szachownica (`PuzzleBoard`) z react-chessboard
- Strona dziennego puzzla (`/puzzle/daily`)
- System streak z wyświetlaniem w nagłówku
- Hook `useUser` do zarządzania sesją i streak
- Rozszerzony API client o endpointy user/streak

#### Backend
- Model `UserPuzzleProgress` do śledzenia postępu
- Pola streak w modelu `User` (current_streak, best_streak, last_puzzle_date)
- Serwis `UserService` z logiką streak
- Router `/users` z endpointami:
  - `POST /users/sync` - synchronizacja z Discord
  - `GET /users/{discord_id}/streak` - pobranie streak
  - `POST /users/{discord_id}/puzzles/{puzzle_id}/complete` - ukończenie puzzla
- Migracja `002_add_streak_tracking.py`

---

## [0.1.0] - 2026-02-03

### Added - Etap 1: Fundamenty

#### Backend
- Struktura projektu FastAPI (`backend/app/`)
- Konfiguracja środowiskowa (`config.py`) z obsługą Neon.tech
- Połączenie SQLAlchemy 2.0 z PostgreSQL (`database.py`)
- Modele danych:
  - `User` - użytkownik
  - `Puzzle` - puzzle szachowy
  - `PuzzleVariant` - warianty rozwiązań
- Schematy Pydantic (`PuzzleResponse`, `MoveRequest`, `MoveResponse`)
- Serwis `PuzzleService` z walidacją ruchów (python-chess)
- Router `/puzzles` z endpointami:
  - `GET /puzzles/daily` - dzienny puzzle
  - `GET /puzzles/{id}` - puzzle po ID
  - `POST /puzzles/{id}/validate-move` - walidacja ruchu
- Konfiguracja Alembic z migracją `001_initial_tables.py`
- Endpoint `/health` do sprawdzania statusu

#### Frontend
- Inicjalizacja Next.js 14 z App Router
- Konfiguracja Tailwind CSS
- API client (`lib/api.ts`)
- Podstawowy layout i strona główna

---

## [0.0.1] - 2026-02-03

### Added

- Inicjalizacja projektu
- Specyfikacja projektu (`SPECIFICATION.md`)
- Changelog (`CHANGELOG.md`)
- Konfiguracja `.gitignore`

---

[Unreleased]: https://github.com/user/chessly/compare/v0.7.0...HEAD
[0.7.0]: https://github.com/user/chessly/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/user/chessly/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/user/chessly/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/user/chessly/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/user/chessly/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/user/chessly/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/user/chessly/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/user/chessly/releases/tag/v0.0.1
