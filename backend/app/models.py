from datetime import datetime
from sqlalchemy import (
    String,
    Integer,
    DateTime,
    ForeignKey,
    Text,
    Boolean,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    google_id: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    query_count_today: Mapped[int] = mapped_column(Integer, default=0)
    last_query_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    search_history: Mapped[list["SearchHistory"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    preferences: Mapped[Optional["UserPreferences"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class SearchHistory(Base):
    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    search_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    result_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    user: Mapped["User"] = relationship(back_populates="search_history")


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), unique=True, nullable=False
    )

    theme: Mapped[str] = mapped_column(String(20), default="system")
    language: Mapped[str] = mapped_column(String(10), default="tr")
    default_search_source: Mapped[str] = mapped_column(String(20), default="quran")
    default_bible_testament: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )
    results_per_page: Mapped[int] = mapped_column(Integer, default=10)
    enable_streaming: Mapped[bool] = mapped_column(Boolean, default=True)
    enable_multi_agent: Mapped[bool] = mapped_column(Boolean, default=True)
    custom_settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user: Mapped["User"] = relationship(back_populates="preferences")


# ---------------------------------------------------------------------------
# Quran Morphology Tables (qm_*)
# ---------------------------------------------------------------------------


class QMSurah(Base):
    __tablename__ = "qm_surahs"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=False
    )  # 1-114, NOT auto-increment
    name_arabic: Mapped[str] = mapped_column(String(100), nullable=False)
    name_translit: Mapped[str] = mapped_column(String(100), nullable=False)
    name_english: Mapped[str] = mapped_column(String(100), nullable=False)
    revelation_type: Mapped[str] = mapped_column(String(20), nullable=False)
    total_verses: Mapped[int] = mapped_column(Integer, nullable=False)

    ayahs: Mapped[list["QMAyah"]] = relationship(
        back_populates="surah", cascade="all, delete-orphan"
    )


class QMAyah(Base):
    __tablename__ = "qm_ayahs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    surah_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("qm_surahs.id"), nullable=False
    )
    ayah_number: Mapped[int] = mapped_column(Integer, nullable=False)
    text_uthmani: Mapped[str] = mapped_column(Text, nullable=False)
    text_clean: Mapped[str] = mapped_column(Text, nullable=False)

    surah: Mapped["QMSurah"] = relationship(back_populates="ayahs")
    words: Mapped[list["QMWord"]] = relationship(
        back_populates="ayah", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("surah_id", "ayah_number", name="uq_qm_ayah_surah_ayah"),
    )


class QMWord(Base):
    __tablename__ = "qm_words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ayah_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("qm_ayahs.id"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    word_index: Mapped[int] = mapped_column(Integer, nullable=False)
    token: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    token_clean: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    root: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    root_buckwalter: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    lemma: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pos_tag: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    features: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    ayah: Mapped["QMAyah"] = relationship(back_populates="words")


# ---------------------------------------------------------------------------
# Bible Morphology Tables (bm_*)
# ---------------------------------------------------------------------------


class BMBook(Base):
    __tablename__ = "bm_books"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=False
    )  # book order number, NOT auto-increment
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_hebrew: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    name_english: Mapped[str] = mapped_column(String(100), nullable=False)
    testament: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    total_chapters: Mapped[int] = mapped_column(Integer, nullable=False)
    total_verses: Mapped[int] = mapped_column(Integer, nullable=False)
    book_order: Mapped[int] = mapped_column(Integer, nullable=False)

    verses: Mapped[list["BMVerse"]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )


class BMVerse(Base):
    __tablename__ = "bm_verses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("bm_books.id"), nullable=False
    )
    chapter: Mapped[int] = mapped_column(Integer, nullable=False)
    verse: Mapped[int] = mapped_column(Integer, nullable=False)
    text_original: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    text_english: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    text_turkish: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reference: Mapped[str] = mapped_column(String(50), nullable=False)

    book: Mapped["BMBook"] = relationship(back_populates="verses")
    words: Mapped[list["BMWord"]] = relationship(
        back_populates="verse", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("book_id", "chapter", "verse", name="uq_bm_verse_book_ch_v"),
    )


class BMWord(Base):
    __tablename__ = "bm_words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    verse_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("bm_verses.id"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    word: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    word_clean: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    lemma: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    root: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    strong_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    morph_tag: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pos_tag: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    transliteration: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    language: Mapped[str] = mapped_column(String(20), nullable=False, default="hebrew")
    original_lemma: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    verse: Mapped["BMVerse"] = relationship(back_populates="words")

    __table_args__ = (
        UniqueConstraint("verse_id", "position", name="uq_bm_word_verse_pos"),
    )


class BMStrongs(Base):
    __tablename__ = "bm_strongs"

    number: Mapped[str] = mapped_column(String(10), primary_key=True)
    original_word: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    transliteration: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    definition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(20), nullable=False)
