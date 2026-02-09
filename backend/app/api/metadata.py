from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import json
import os
import httpx

router = APIRouter()

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data"
)
QDRANT_URL = "http://localhost:6333"


def safe_path(base: str, filename: str) -> str:
    """Validate that resolved path stays within base directory."""
    base_path = Path(base).resolve()
    file_path = (base_path / filename).resolve()
    if not str(file_path).startswith(str(base_path)):
        raise ValueError(f"Path traversal detected: {filename}")
    return str(file_path)


class CollectionInfo(BaseModel):
    name: str
    points_count: int
    status: str


class SurahInfo(BaseModel):
    id: int
    name: str
    name_arabic: str
    transliteration: str
    type: str
    total_verses: int


class BookInfo(BaseModel):
    nr: int
    name: str
    chapters_count: int
    testament: str


class MetadataResponse(BaseModel):
    success: bool = True
    data: dict


_quran_cache: Optional[list[dict]] = None
_bible_cache: Optional[dict] = None


def _load_quran_data() -> list[dict]:
    global _quran_cache
    if _quran_cache is None:
        quran_path = safe_path(DATA_DIR, "quran_tr.json")
        if os.path.exists(quran_path):
            with open(quran_path, "r", encoding="utf-8") as f:
                _quran_cache = json.load(f)
        else:
            _quran_cache = []
    return _quran_cache


def _load_bible_data() -> dict:
    global _bible_cache
    if _bible_cache is None:
        bible_path = safe_path(DATA_DIR, "bible_kjva.json")
        if os.path.exists(bible_path):
            with open(bible_path, "r", encoding="utf-8") as f:
                _bible_cache = json.load(f)
        else:
            _bible_cache = {"books": []}
    return _bible_cache


def _get_testament(book_nr: int) -> str:
    OT_BOOKS = list(range(1, 40))
    NT_BOOKS = list(range(40, 67))

    if book_nr in OT_BOOKS:
        return "old_testament"
    elif book_nr in NT_BOOKS:
        return "new_testament"
    else:
        return "apocrypha"


@router.get("/collections")
async def get_collections():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{QDRANT_URL}/collections", timeout=5.0)
            if response.status_code != 200:
                raise HTTPException(status_code=503, detail="Qdrant unavailable")

            data = response.json()
            collections = data.get("result", {}).get("collections", [])

            result = []
            for col in collections:
                col_name = col.get("name", "")
                info_response = await client.get(
                    f"{QDRANT_URL}/collections/{col_name}", timeout=5.0
                )
                if info_response.status_code == 200:
                    col_data = info_response.json().get("result", {})
                    result.append(
                        CollectionInfo(
                            name=col_name,
                            points_count=col_data.get("points_count", 0),
                            status=col_data.get("status", "unknown"),
                        )
                    )

            return MetadataResponse(
                data={"collections": [c.model_dump() for c in result]}
            )

    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Qdrant connection failed")


@router.get("/quran/surahs")
async def get_quran_surahs():
    quran_data = _load_quran_data()

    surahs = [
        SurahInfo(
            id=surah["id"],
            name=surah.get("translation", ""),
            name_arabic=surah.get("name", ""),
            transliteration=surah.get("transliteration", ""),
            type=surah.get("type", ""),
            total_verses=surah.get("total_verses", 0),
        )
        for surah in quran_data
    ]

    return MetadataResponse(
        data={
            "surahs": [s.model_dump() for s in surahs],
            "total": len(surahs),
        }
    )


@router.get("/quran/surahs/{surah_id}")
async def get_surah_detail(surah_id: int):
    quran_data = _load_quran_data()

    surah = next((s for s in quran_data if s["id"] == surah_id), None)
    if not surah:
        raise HTTPException(status_code=404, detail=f"Surah {surah_id} not found")

    return MetadataResponse(
        data={
            "surah": {
                "id": surah["id"],
                "name": surah.get("translation", ""),
                "name_arabic": surah.get("name", ""),
                "transliteration": surah.get("transliteration", ""),
                "type": surah.get("type", ""),
                "total_verses": surah.get("total_verses", 0),
                "verses": surah.get("verses", []),
            }
        }
    )


@router.get("/bible/books")
async def get_bible_books(testament: Optional[str] = None):
    bible_data = _load_bible_data()

    books = []
    for book in bible_data.get("books", []):
        book_testament = _get_testament(book.get("nr", 0))

        if testament and book_testament != testament:
            continue

        chapters = book.get("chapters", [])
        books.append(
            BookInfo(
                nr=book.get("nr", 0),
                name=book.get("name", ""),
                chapters_count=len(chapters),
                testament=book_testament,
            )
        )

    return MetadataResponse(
        data={
            "books": [b.model_dump() for b in books],
            "total": len(books),
        }
    )


@router.get("/bible/books/{book_nr}")
async def get_book_detail(book_nr: int):
    bible_data = _load_bible_data()

    book = next(
        (b for b in bible_data.get("books", []) if b.get("nr") == book_nr), None
    )
    if not book:
        raise HTTPException(status_code=404, detail=f"Book {book_nr} not found")

    chapters_summary = []
    for chapter in book.get("chapters", []):
        chapters_summary.append(
            {
                "chapter": chapter.get("chapter", 0),
                "verses_count": len(chapter.get("verses", [])),
            }
        )

    return MetadataResponse(
        data={
            "book": {
                "nr": book.get("nr", 0),
                "name": book.get("name", ""),
                "testament": _get_testament(book.get("nr", 0)),
                "chapters": chapters_summary,
            }
        }
    )


@router.get("/bible/books/{book_nr}/chapters/{chapter_nr}")
async def get_chapter_verses(book_nr: int, chapter_nr: int):
    bible_data = _load_bible_data()

    book = next(
        (b for b in bible_data.get("books", []) if b.get("nr") == book_nr), None
    )
    if not book:
        raise HTTPException(status_code=404, detail=f"Book {book_nr} not found")

    chapter = next(
        (c for c in book.get("chapters", []) if c.get("chapter") == chapter_nr), None
    )
    if not chapter:
        raise HTTPException(status_code=404, detail=f"Chapter {chapter_nr} not found")

    return MetadataResponse(
        data={
            "book_name": book.get("name", ""),
            "chapter": chapter_nr,
            "verses": chapter.get("verses", []),
        }
    )


@router.get("/testaments")
async def get_testaments():
    return MetadataResponse(
        data={
            "testaments": [
                {
                    "id": "old_testament",
                    "name": "Old Testament",
                    "name_tr": "Eski Ahit",
                },
                {
                    "id": "new_testament",
                    "name": "New Testament",
                    "name_tr": "Yeni Ahit",
                },
                {"id": "apocrypha", "name": "Apocrypha", "name_tr": "Apokrifa"},
            ],
            "collections": {
                "quran": "quran_tr_diyanet",
                "old_testament": "bible_ot",
                "new_testament": "bible_nt",
                "apocrypha": "bible_apocrypha",
            },
        }
    )
