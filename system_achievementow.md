# 🏆 System achievementów

Dokument opisuje **mechanizm osiągnięć** w aplikacji.

---

## Cele

- motywacja
- retencja
- feedback progresu

---

## Architektura

Achievementy są:
- pasywne
- event-driven
- niezależne od UI

---

## Eventy

Przykładowe:
- USER_LOGIN
- PUZZLE_SOLVED
- PUZZLE_FAILED
- LESSON_COMPLETED
- STREAK_DAY
- FIRST_CHECKMATE

---

## Achievement

Zawiera:
- kod
- nazwę
- opis
- ikonę
- warunek

---

## Przykłady

- FIRST_PUZZLE_SOLVED
- STREAK_3
- COMPLETE_FIRST_LESSON
- TEN_TACTICS_SOLVED

---

## Odblokowanie

1. Event
2. Sprawdzenie warunków
3. Zapis do bazy
4. (Opcjonalnie) powiadomienie Discord

