## 🆕 NOWE ELEMENTY DODANE DO PROJEKTU

### 1️⃣ System lekcji (Learning Path)

**Nowy filar aplikacji obok puzzli i gier.**

#### Co to jest

* Ustrukturyzowany proces nauki szachów
* Lekcje prowadzone **krok po kroku**
* Każdy krok = mini-zadanie na planszy

#### Kategorie lekcji

* **Podstawy**

  * figury i ich ruchy
  * bicie
  * szach / mat / pat
* **Taktyki**

  * widełki
  * związanie
  * odkryty atak
  * mat na ostatniej linii
* **Otwarcia** (light)

  * idee, nie warianty
* **Końcówki** (bardzo podstawowe)

#### Struktura lekcji

* lekcja → wiele kroków (steps)
* każdy krok:

  * FEN startowy
  * instrukcja tekstowa
  * oczekiwany ruch lub zestaw ruchów
* przejście do następnego kroku **dopiero po poprawnym ruchu**

---

### 2️⃣ Lekcje są INTERAKTYWNE (ważne)

Zmiana myślenia:

* ❌ nie „czytaj i kliknij dalej”
* ✅ **zrób ruch na planszy**

Technicznie:

* używa dokładnie tego samego silnika walidacji co puzzle
* backend decyduje, czy ruch był poprawny

---

### 3️⃣ Achievementy (Osiągnięcia)

**Nowy system meta-progresu.**

#### Jak działają

* oparte o **zdarzenia**, nie o ręczne sprawdzanie
* backend emituje eventy typu:

  * `PUZZLE_SOLVED`
  * `LESSON_COMPLETED`
  * `STREAK_DAY`
  * `FIRST_CHECKMATE`

#### Przykładowe achievementy

* „Pierwszy mat”
* „3-dniowy streak”
* „Ukończono 1 lekcję”
* „10 poprawnych puzzli”

#### Co ważne

* achievementy są **niezależne** od puzzli i lekcji
* można je łatwo rozszerzać bez ruszania logiki gry

---

### 4️⃣ Discord + Lekcje

Nowa interakcja z Discordem:

* nowa komenda:

  ```
  /learn
  ```
* bot:

  * pokazuje embed z lekcją dnia
  * linkuje do web app
* Discord staje się:

  * przypominaczem
  * hubem edukacyjnym
  * motywatorem (achievementy)

---

### 5️⃣ Nowe modele logiczne (konceptualnie)

Doszły **nowe byty domenowe**:

* Lesson
* LessonStep
* UserLessonProgress
* Achievement
* UserAchievement

Nie zmieniają istniejących puzzli – **rozszerzają system**.

---

### 6️⃣ Zmiana roadmapy (logiczna, nie rewolucja)

Nowy etap pomiędzy „Web MVP” a „Discord”:

* **System achievementów**
* **Widok lekcji**
* **Event system**

To:

* nie blokuje MVP puzzli
* można wdrażać iteracyjnie

---

### 7️⃣ Co się NIE zmieniło (ważne)

Żeby było jasno:

❌ brak wizualnego buildera
❌ brak rankingu
❌ brak timera
❌ brak multiplayer w MVP
❌ brak Discord Activity na start

To wszystko nadal **po MVP**.
