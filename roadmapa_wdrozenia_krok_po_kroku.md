# 🧭 Roadmapa wdrożenia projektu (krok po kroku)

Ten dokument opisuje **kolejność implementacji całego projektu** – od zera do pełnoprawnej platformy szachowej.

---

## ETAP 0 – Przygotowanie

### Cele
- jasny podział odpowiedzialności
- brak przepisywania kodu w przyszłości

### Kroki
1. Wybór repozytorium (monorepo lub dwa repo)
2. Konfiguracja środowiska (Docker opcjonalnie)
3. Wybór bazy danych (PostgreSQL)

---

## ETAP 1 – Fundament szachowy (core engine)

### Cele
- jeden silnik logiki szachów dla wszystkiego

### Kroki
1. Integracja `python-chess`
2. Obsługa FEN
3. Walidacja ruchów
4. Generowanie nowego FEN po ruchu

---

## ETAP 2 – Puzzle

### Cele
- grywalne daily puzzle

### Kroki
1. Model puzzla (FEN startowy)
2. Drzewo wariantów ruchów
3. Walidacja poprawności ruchu
4. Status: in_progress / solved / failed

---

## ETAP 3 – Lekcje

### Cele
- proces nauki krok po kroku

### Kroki
1. Kategorie lekcji
2. Lekcja → kroki
3. Instrukcje tekstowe
4. Walidacja ruchów w kroku

---

## ETAP 4 – Achievementy

### Cele
- retencja i progres użytkownika

### Kroki
1. System zdarzeń (events)
2. Warunki odblokowania
3. Zapisywanie osiągnięć

---

## ETAP 5 – Web App (PWA)

### Cele
- grywalny frontend

### Kroki
1. Next.js + React
2. Szachownica (drag & drop)
3. Widok puzzli
4. Widok lekcji
5. PWA install

---

## ETAP 6 – Discord

### Cele
- dystrybucja i community

### Kroki
1. Bot Discord
2. /puzzle
3. /learn
4. Embed + link

---

## ETAP 7 – Gra

### Cele
- interakcja społeczna

### Kroki
1. Gra z botem
2. Gra z użytkownikiem
3. Zapisy partii

---

## ETAP 8 – Discord Activity

### Cele
- pełna gra w Discordzie

### Kroki
1. Integracja SDK Discord
2. Tryb Activity
3. Testy
4. Publikacja
