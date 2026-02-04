# Chess Puzzles & Play – Specyfikacja projektu

## 1. Wizja projektu

Celem projektu jest stworzenie aplikacji webowej (PWA) zintegrowanej z Discordem, która umożliwia:

* rozwiązywanie zadań szachowych (daily puzzles, taktyka, mat w X),
* grę z innym użytkownikiem lub botem,
* zapisywanie partii i ruchów,
* wykorzystanie Discorda jako systemu logowania, notyfikacji i (docelowo) platformy do uruchamiania gry jako Discord Activity.

Projekt **nie konkuruje bezpośrednio** z Lichess/Chess.com, lecz czerpie z ich UX – skupia się na:

* prostocie,
* puzzle-first,
* integracji społecznościowej przez Discord.

---

## 2. Zakres funkcjonalny (MVP + roadmapa)

### 2.1 MVP (pierwsza wersja produkcyjna)

#### Aplikacja Web (PWA)

* logowanie przez Discord OAuth2
* daily puzzle (1 dziennie na użytkownika)
* obsługa zadań typu:
  * mate in 1 / 2 / 3
  * wymuszona sekwencja szachów
* obsługa **wielu poprawnych odpowiedzi przeciwnika** (drzewo wariantów)
* interaktywna szachownica (drag & drop)
* walidacja ruchów
* informacja zwrotna (dobry/zły ruch)
* streak dzienny
* zapis postępu użytkownika

#### Discord Bot

* komenda `/puzzle`
* embed z:
  * miniaturą planszy
  * opisem zadania
  * przyciskiem/linkiem „Rozwiąż w aplikacji"
* identyfikacja użytkownika (Discord ID)

---

### 2.2 Funkcje po MVP (Roadmapa)

#### Gra

* gra z botem (Stockfish, różne poziomy)
* gra z innym użytkownikiem:
  * zaproszenie do poczekalni (link)
  * realtime (WebSocket)
* zapis partii (PGN)
* replay partii

#### Społeczność

* czat w trakcie gry
* znajomi
* historia gier

#### Discord

* Discord Activity (embedded app)
* uruchamianie gry bezpośrednio z Discorda
* wspólne oglądanie partii

---

## 3. Architektura systemu

```
[ Discord Bot ]
  └── Slash commands
  └── Embeds + linki

[ Frontend – Next.js (PWA) ]
  ├── React
  ├── chessboard UI
  ├── OAuth Discord
  ├── Gameplay / Puzzles
  └── WebSocket (później)

[ Backend – FastAPI ]
  ├── Auth
  ├── Puzzle engine
  ├── Game engine
  ├── Stockfish integration
  └── API + WS

[ Database ]
  └── PostgreSQL
```

---

## 4. Stack technologiczny

### Frontend

* **Next.js (App Router)**
* React
* `react-chessboard`
* `chess.js`
* `next-pwa`
* Tailwind / MUI / Mantine / ShadCN

### Backend

* **FastAPI (Python)**
* `python-chess`
* Stockfish (local / docker)
* SQLAlchemy 2.0
* Alembic (migracje)

### Database

* PostgreSQL

### Realtime (po MVP)

* WebSocket (FastAPI)
* Redis (opcjonalnie – kolejki, matchmaking)

---

## 5. Model danych

### users

| Pole       | Typ       | Opis                  |
|------------|-----------|-----------------------|
| id         | UUID      | klucz główny          |
| discord_id | string    | ID użytkownika Discord|
| username   | string    | nazwa użytkownika     |
| avatar     | string    | URL avatara           |
| created_at | timestamp | data utworzenia       |

### puzzles

| Pole         | Typ       | Opis                        |
|--------------|-----------|-----------------------------|
| id           | UUID      | klucz główny                |
| date         | date      | data (nullable – daily)     |
| fen_start    | string    | pozycja startowa FEN        |
| side_to_move | string    | strona do ruchu (w/b)       |
| goal         | string    | cel (mate_in_2, tactic, etc)|

### puzzle_variants

Umożliwia wiele poprawnych odpowiedzi przeciwnika.

| Pole           | Typ     | Opis                          |
|----------------|---------|-------------------------------|
| id             | UUID    | klucz główny                  |
| puzzle_id      | UUID    | FK do puzzles                 |
| parent_move_id | UUID    | FK do parent (nullable)       |
| move_san       | string  | ruch w notacji SAN            |
| fen_after      | string  | pozycja po ruchu              |
| is_correct     | boolean | czy ruch gracza jest poprawny |

### user_puzzle_progress

| Pole                 | Typ     | Opis                          |
|----------------------|---------|-------------------------------|
| user_id              | UUID    | FK do users                   |
| puzzle_id            | UUID    | FK do puzzles                 |
| status               | string  | in_progress / solved / failed |
| current_variant_node | UUID    | aktualny węzeł w drzewie      |
| attempts             | integer | liczba prób                   |

### games (po MVP)

| Pole            | Typ       | Opis                  |
|-----------------|-----------|-----------------------|
| id              | UUID      | klucz główny          |
| player_white_id | UUID      | FK do users           |
| player_black_id | UUID      | FK do users           |
| pgn             | text      | zapis partii PGN      |
| result          | string    | wynik partii          |
| created_at      | timestamp | data utworzenia       |

---

## 6. Puzzle z wieloma wariantami

Puzzle jest **drzewem ruchów**, a nie jedną linią.

Przykład:

```
Qh7+
 ├── Kf8 → Qf7#
 ├── Kg8 → Qh8#
 └── Kxh7 → Ng5#
```

**Backend:**
* przechowuje drzewo wariantów
* sprawdza, czy ruch użytkownika istnieje w aktualnym węźle

**Frontend:**
* nie zna pełnej odpowiedzi
* tylko wysyła ruchy do walidacji

---

## 7. Builder puzzli

### MVP (admin-only)

* wklejenie:
  * FEN
  * sekwencji ruchów (PGN / SAN)
* backend generuje drzewo wariantów

### Po MVP

* wizualny builder
* import z PGN
* import z Lichess study

---

## 8. PWA + Discord Activity

### PWA

* instalowalna aplikacja
* offline shell
* push notifications (daily puzzle)

### Discord Activity

* Discord Activity = iframe z aplikacją
* auth przez Discord SDK
* jedna codebase z dwoma trybami:
  * tryb „web / PWA"
  * tryb „Discord Activity"

---

## 9. Plan realizacji

### ETAP 1 – Fundamenty

* repo mono (frontend + backend)
* FastAPI + Postgres
* model puzzli
* endpoint walidacji ruchu

### ETAP 2 – Web MVP

* Next.js + chessboard
* Discord OAuth
* daily puzzle view
* streak

### ETAP 3 – Discord Bot

* `/puzzle`
* embed + link

### ETAP 4 – Multiplayer (gra przez link)

* **WebSocket server** (FastAPI WebSocket)
* model danych dla sesji gry:
  * `game_sessions` - aktywne pokoje
  * `game_moves` - historia ruchów
* **flow gry:**
  1. Gracz A tworzy pokój → otrzymuje unikalny link (np. `/play/abc123`)
  2. Gracz B otwiera link → dołącza do pokoju
  3. Synchronizacja ruchów przez WebSocket
  4. Zapis zakończonej partii do `games`
* **UI:**
  * strona oczekiwania na przeciwnika
  * szachownica z timerem
  * chat w grze (opcjonalnie)
* kontrola czasu (bullet/blitz/rapid)

### ETAP 5 – Gra z botem

* integracja Stockfish (subprocess lub Docker)
* wybór poziomu trudności (ELO 800-2800)
* zapisy partii (PGN)

### ETAP 6 – Discord Activity

* integracja `@discord/embedded-app-sdk`
* wykrywanie trybu Discord Activity (iframe)
* autoryzacja OAuth2 przez Discord SDK
* backend endpoint do wymiany kodu na token
* dedykowana strona `/activity` z menu gier
* adaptacja UI (brak Header, ciemny motyw)
* context `DiscordProvider` do zarządzania stanem
* kompatybilność z istniejącą autoryzacją NextAuth

---

## 10. Struktura plików - Etap 6

```
backend/
├── app/
│   ├── config.py                 ✓ Discord OAuth settings
│   ├── main.py                   ✓ CORS dla Discord, router auth
│   └── routers/
│       └── auth.py               ✓ POST /auth/discord/activity

frontend/
├── src/
│   ├── lib/
│   │   └── discord.ts            ✓ Discord SDK utilities
│   ├── contexts/
│   │   └── discord-context.tsx   ✓ DiscordProvider, useDiscord
│   ├── components/
│   │   ├── providers.tsx         ✓ + DiscordProvider
│   │   └── activity-layout.tsx   ✓ Warunkowy layout
│   ├── hooks/
│   │   └── use-user.ts           ✓ Obsługa Discord Activity auth
│   └── app/
│       ├── layout.tsx            ✓ + ActivityLayout
│       └── activity/
│           └── page.tsx          ✓ Menu Discord Activity
```

---

## 11. Konfiguracja Discord Activity

### Wymagane zmienne środowiskowe

Backend (`.env`):
```
DISCORD_CLIENT_ID=your-app-client-id
DISCORD_CLIENT_SECRET=your-app-client-secret
DISCORD_REDIRECT_URI=http://localhost:3000
```

Frontend (`.env.local`):
```
NEXT_PUBLIC_DISCORD_CLIENT_ID=your-app-client-id
NEXT_PUBLIC_DISCORD_SDK_MOCK=false
```

### Rejestracja w Discord Developer Portal

1. Przejdź do https://discord.com/developers/applications
2. Wybierz aplikację Chessly (lub utwórz nową)
3. W zakładce "Activities" włącz "Enable Activities"
4. Ustaw "Activity URL" na adres produkcyjny aplikacji
5. Dodaj "Redirect URLs" w OAuth2: `https://your-domain.com`
6. Skopiuj Client ID i Client Secret

---

## 12. Struktura plików - Etap 7

```
backend/
├── app/
│   ├── models/
│   │   ├── lesson.py                ✓ Lesson, LessonStep
│   │   ├── user_lesson_progress.py  ✓ UserLessonProgress
│   │   └── achievement.py           ✓ Achievement, UserAchievement
│   ├── schemas/
│   │   ├── lesson.py                ✓ LessonResponse, ValidateMoveResponse
│   │   └── achievement.py           ✓ AchievementResponse
│   ├── services/
│   │   ├── event_service.py         ✓ EventService (event-driven)
│   │   ├── achievement_service.py   ✓ AchievementService
│   │   └── lesson_service.py        ✓ LessonService
│   └── routers/
│       ├── lessons.py               ✓ /lessons endpoints
│       └── achievements.py          ✓ /achievements endpoints
└── alembic/versions/
    └── 005_add_lessons_and_achievements.py  ✓

frontend/
├── src/
│   ├── app/
│   │   ├── learn/
│   │   │   ├── page.tsx             ✓ Lista lekcji
│   │   │   └── [id]/page.tsx        ✓ Strona lekcji
│   │   └── profile/
│   │       └── page.tsx             ✓ Profil i achievementy
│   └── components/
│       └── lesson-board.tsx         ✓ Szachownica dla lekcji

bot/
├── learn_command.py                 ✓ /learn, /stats
└── api_client.py                    ✓ + lesson/achievement endpoints
```

---

## 13. Podsumowanie projektu Chessly

```
┌──────┬────────┬──────────────────────────────────────────────┐
│ Etap │ Status │                     Opis                     │
├──────┼────────┼──────────────────────────────────────────────┤
│ 1    │ ✓      │ Fundamenty (FastAPI, SQLAlchemy, Next.js)    │
├──────┼────────┼──────────────────────────────────────────────┤
│ 2    │ ✓      │ Web MVP (Discord OAuth, puzzles, streak)     │
├──────┼────────┼──────────────────────────────────────────────┤
│ 3    │ ✓      │ Discord Bot (/puzzle, /streak)               │
├──────┼────────┼──────────────────────────────────────────────┤
│ 4    │ ✓      │ Multiplayer (WebSocket, timer, link sharing) │
├──────┼────────┼──────────────────────────────────────────────┤
│ 5    │ ✓      │ Gra z botem (Stockfish, PGN export)          │
├──────┼────────┼──────────────────────────────────────────────┤
│ 6    │ ✓      │ Discord Activity (embedded app)              │
├──────┼────────┼──────────────────────────────────────────────┤
│ 7    │ ✓      │ Lekcje i Achievementy                        │
└──────┴────────┴──────────────────────────────────────────────┘
```
