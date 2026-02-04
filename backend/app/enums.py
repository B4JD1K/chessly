from enum import Enum


class BotDifficulty(str, Enum):
    BEGINNER = "beginner"      # ~800 ELO
    EASY = "easy"              # ~1000 ELO
    MEDIUM = "medium"          # ~1400 ELO
    HARD = "hard"              # ~1800 ELO
    EXPERT = "expert"          # ~2200 ELO
    MASTER = "master"          # ~2500+ ELO
