from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class LessonCategory(str, enum.Enum):
    BASICS = "basics"           # Podstawy - figury, ruchy, bicie
    TACTICS = "tactics"         # Taktyki - widełki, związanie, odkryty atak
    OPENINGS = "openings"       # Otwarcia - zasady, kontrola centrum
    ENDGAMES = "endgames"       # Końcówki - król+pion, opozycja


class LessonLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(SQLEnum(LessonCategory), nullable=False)
    level = Column(SQLEnum(LessonLevel), nullable=False, default=LessonLevel.BEGINNER)
    order_index = Column(Integer, nullable=False, default=0)  # Kolejność w kategorii
    is_published = Column(Boolean, default=True)

    # Relationships
    steps = relationship("LessonStep", back_populates="lesson", order_by="LessonStep.order_index")


class LessonStep(Base):
    __tablename__ = "lesson_steps"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    order_index = Column(Integer, nullable=False)  # Kolejność kroków w lekcji

    # Treść kroku
    instruction = Column(Text, nullable=False)  # Instrukcja tekstowa dla użytkownika
    hint = Column(Text, nullable=True)  # Opcjonalna podpowiedź

    # Pozycja szachowa
    fen = Column(String(100), nullable=False)  # Pozycja startowa

    # Oczekiwane ruchy (JSON array lub comma-separated)
    # Może być wiele poprawnych ruchów, np. "e4,d4" lub ["e4", "d4"]
    expected_moves = Column(String(500), nullable=False)  # Ruchy w notacji UCI

    # Czy pokazać ruch przeciwnika po poprawnym ruchu gracza
    opponent_move = Column(String(10), nullable=True)  # Opcjonalny ruch przeciwnika (UCI)
    fen_after_opponent = Column(String(100), nullable=True)  # FEN po ruchu przeciwnika

    # Relationships
    lesson = relationship("Lesson", back_populates="steps")
