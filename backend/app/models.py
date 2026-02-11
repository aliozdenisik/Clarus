from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users_legacy"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    query_count_today: Mapped[int] = mapped_column(Integer, default=0)
    last_query_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Legacy relationships removed — SearchHistory and UserPreferences now reference Better Auth user table


class SearchHistory(Base):
    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("user.id"), nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    search_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    result_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    auth_user: Mapped["BetterAuthUser"] = relationship(viewonly=True)


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("user.id"), unique=True, nullable=False)

    theme: Mapped[str] = mapped_column(String(20), default="system")
    language: Mapped[str] = mapped_column(String(10), default="tr")
    default_search_source: Mapped[str] = mapped_column(String(20), default="quran")
    default_bible_testament: Mapped[str | None] = mapped_column(String(20), nullable=True)
    results_per_page: Mapped[int] = mapped_column(Integer, default=10)
    enable_streaming: Mapped[bool] = mapped_column(Boolean, default=True)
    enable_multi_agent: Mapped[bool] = mapped_column(Boolean, default=True)
    custom_settings: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    auth_user: Mapped["BetterAuthUser"] = relationship(viewonly=True)


# ---------------------------------------------------------------------------
# Quran Morphology Tables (qm_*)
# ---------------------------------------------------------------------------


class QMSurah(Base):
    __tablename__ = "qm_surahs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)  # 1-114, NOT auto-increment
    name_arabic: Mapped[str] = mapped_column(String(100), nullable=False)
    name_translit: Mapped[str] = mapped_column(String(100), nullable=False)
    name_english: Mapped[str] = mapped_column(String(100), nullable=False)
    revelation_type: Mapped[str] = mapped_column(String(20), nullable=False)
    total_verses: Mapped[int] = mapped_column(Integer, nullable=False)

    ayahs: Mapped[list["QMAyah"]] = relationship(back_populates="surah", cascade="all, delete-orphan")


class QMAyah(Base):
    __tablename__ = "qm_ayahs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    surah_id: Mapped[int] = mapped_column(Integer, ForeignKey("qm_surahs.id"), nullable=False)
    ayah_number: Mapped[int] = mapped_column(Integer, nullable=False)
    text_uthmani: Mapped[str] = mapped_column(Text, nullable=False)
    text_clean: Mapped[str] = mapped_column(Text, nullable=False)

    surah: Mapped["QMSurah"] = relationship(back_populates="ayahs")
    words: Mapped[list["QMWord"]] = relationship(back_populates="ayah", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("surah_id", "ayah_number", name="uq_qm_ayah_surah_ayah"),)


class QMWord(Base):
    __tablename__ = "qm_words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ayah_id: Mapped[int] = mapped_column(Integer, ForeignKey("qm_ayahs.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    word_index: Mapped[int] = mapped_column(Integer, nullable=False)
    token: Mapped[str | None] = mapped_column(String(100), nullable=True)
    token_clean: Mapped[str | None] = mapped_column(String(100), nullable=True)
    root: Mapped[str | None] = mapped_column(String(20), nullable=True)
    root_buckwalter: Mapped[str | None] = mapped_column(String(20), nullable=True)
    lemma: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pos_tag: Mapped[str | None] = mapped_column(String(20), nullable=True)
    features: Mapped[str | None] = mapped_column(Text, nullable=True)

    ayah: Mapped["QMAyah"] = relationship(back_populates="words")


class QMRootEtymology(Base):
    __tablename__ = "qm_root_etymologies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    root: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    root_buckwalter: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    definition_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    definition_tr: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_tr: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    semantic_field: Mapped[str | None] = mapped_column(String(100), nullable=True)
    morphological_forms: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    related_roots: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    quran_frequency: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    lane_match_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    lane_volume: Mapped[int | None] = mapped_column(Integer, nullable=True)
    confidence: Mapped[str] = mapped_column(String(20), nullable=False, default="low")
    tr_translation_source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tr_translation_confidence: Mapped[float | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LaneLexiconEntry(Base):
    __tablename__ = "lane_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    root: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    broot: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    word: Mapped[str | None] = mapped_column(Text, nullable=True)
    bword: Mapped[str | None] = mapped_column(Text, nullable=True)
    xml: Mapped[str | None] = mapped_column(Text, nullable=True)
    page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    headword: Mapped[str | None] = mapped_column(Text, nullable=True)
    itype: Mapped[str | None] = mapped_column(String(50), nullable=True)


class LaneLexiconRoot(Base):
    __tablename__ = "lane_roots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    word: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    bword: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    letter: Mapped[str | None] = mapped_column(String(20), nullable=True)
    bletter: Mapped[str | None] = mapped_column(String(20), nullable=True)
    page: Mapped[int | None] = mapped_column(Integer, nullable=True)


# ---------------------------------------------------------------------------
# Bible Morphology Tables (bm_*)
# ---------------------------------------------------------------------------


class BMBook(Base):
    __tablename__ = "bm_books"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=False
    )  # book order number, NOT auto-increment
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_hebrew: Mapped[str | None] = mapped_column(String(100), nullable=True)
    name_english: Mapped[str] = mapped_column(String(100), nullable=False)
    testament: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    total_chapters: Mapped[int] = mapped_column(Integer, nullable=False)
    total_verses: Mapped[int] = mapped_column(Integer, nullable=False)
    book_order: Mapped[int] = mapped_column(Integer, nullable=False)

    verses: Mapped[list["BMVerse"]] = relationship(back_populates="book", cascade="all, delete-orphan")


class BMVerse(Base):
    __tablename__ = "bm_verses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey("bm_books.id"), nullable=False)
    chapter: Mapped[int] = mapped_column(Integer, nullable=False)
    verse: Mapped[int] = mapped_column(Integer, nullable=False)
    text_original: Mapped[str | None] = mapped_column(Text, nullable=True)
    text_english: Mapped[str | None] = mapped_column(Text, nullable=True)
    text_turkish: Mapped[str | None] = mapped_column(Text, nullable=True)
    reference: Mapped[str] = mapped_column(String(50), nullable=False)

    book: Mapped["BMBook"] = relationship(back_populates="verses")
    words: Mapped[list["BMWord"]] = relationship(back_populates="verse", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("book_id", "chapter", "verse", name="uq_bm_verse_book_ch_v"),)


class BMWord(Base):
    __tablename__ = "bm_words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    verse_id: Mapped[int] = mapped_column(Integer, ForeignKey("bm_verses.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    word: Mapped[str | None] = mapped_column(String(200), nullable=True)
    word_clean: Mapped[str | None] = mapped_column(String(200), nullable=True)
    lemma: Mapped[str | None] = mapped_column(String(100), nullable=True)
    root: Mapped[str | None] = mapped_column(String(50), nullable=True)
    strong_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    morph_tag: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pos_tag: Mapped[str | None] = mapped_column(String(20), nullable=True)
    transliteration: Mapped[str | None] = mapped_column(String(200), nullable=True)
    language: Mapped[str] = mapped_column(String(20), nullable=False, default="hebrew")
    original_lemma: Mapped[str | None] = mapped_column(String(100), nullable=True)

    verse: Mapped["BMVerse"] = relationship(back_populates="words")

    __table_args__ = (UniqueConstraint("verse_id", "position", name="uq_bm_word_verse_pos"),)


class BMStrongs(Base):
    __tablename__ = "bm_strongs"

    number: Mapped[str] = mapped_column(String(10), primary_key=True)
    original_word: Mapped[str | None] = mapped_column(String(100), nullable=True)
    transliteration: Mapped[str | None] = mapped_column(String(100), nullable=True)
    definition: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(20), nullable=False)


class BMVerseMapping(Base):
    __tablename__ = "bm_verse_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mt_reference: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    lxx_reference: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    mt_book_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("bm_books.id"), nullable=True)
    lxx_book_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("bm_books.id"), nullable=True)
    mapping_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    mt_book: Mapped[Optional["BMBook"]] = relationship(foreign_keys=[mt_book_id], viewonly=True)
    lxx_book: Mapped[Optional["BMBook"]] = relationship(foreign_keys=[lxx_book_id], viewonly=True)


# ---------------------------------------------------------------------------
# Better Auth Integration Tables (READ-ONLY)
# ---------------------------------------------------------------------------


class BetterAuthUser(Base):
    """Better Auth user table — camelCase columns mapped to snake_case attributes."""

    __tablename__ = "user"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    email_verified: Mapped[bool] = mapped_column("emailVerified", Boolean, default=False)
    image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime, nullable=False)


class BetterAuthSession(Base):
    """Better Auth session table — camelCase columns mapped to snake_case attributes."""

    __tablename__ = "session"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    user_id: Mapped[str] = mapped_column("userId", String(255), ForeignKey("user.id"), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column("expiresAt", DateTime, nullable=False)
    ip_address: Mapped[str | None] = mapped_column("ipAddress", String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column("userAgent", String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime, nullable=False)


class UserStats(Base):
    __tablename__ = "user_stats"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("user.id"), nullable=False, unique=True, index=True)
    query_count_today: Mapped[int] = mapped_column(Integer, default=0)
    last_query_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    api_key: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True, index=True)
    api_key_created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
