from dataclasses import dataclass
from typing import Optional


@dataclass
class ChildProfile:
    id: int
    name: str
    age: int
    created_at: str


@dataclass
class WordList:
    id: int
    name: str
    created_at: str


@dataclass
class Word:
    id: int
    word_list_id: int
    word: str
    difficulty: str


@dataclass
class Session:
    id: int
    child_id: int
    word_list_id: int
    started_at: str
    completed_at: Optional[str] = None


@dataclass
class WordAttempt:
    id: int
    session_id: int
    word_id: int
    attempts: int
    correct: bool
    hints_used: list[str]