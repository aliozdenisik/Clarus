#!/usr/bin/env python3
# ruff: noqa: E402
# Archive test script mutates sys.path before local imports.
"""
Bible Ultimate RAG Test Suite - Comprehensive 30 Query Evaluation (TURKISH QUERIES)

Tests the Ultimate RAG Pipeline against the English KJVA Bible collection
with comprehensive, in-depth TURKISH queries that will be translated to English.

This tests the full pipeline including:
- Turkish to English translation (via query_enhancer.translate_for_bible)
- Query enhancement
- Multi-query generation
- Semantic search
- Cross-encoder reranking

Each query has expected verse references researched from web sources.
"""

import asyncio
import sys
import time
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add parent directory to path
sys.path.insert(0, ".")

console = Console()


@dataclass
class TestQuery:
    """Test query with expected results"""

    id: int
    query: str  # Turkish query
    category: str
    expected_books: List[str]  # Expected books to find
    expected_verses: List[str]  # Expected verse references (e.g., "John 3:16")
    description: str


# 30 Comprehensive Bible Test Queries in TURKISH with Expected Answers
TEST_QUERIES = [
    # === SEVGİ (1-5) ===
    TestQuery(
        id=1,
        query="Tanrı'nın insanlığa koşulsuz sevgisi ve bunu Oğlu'nun kurbanıyla nasıl gösterdiği hakkında İncil ne öğretiyor?",
        category="Sevgi",
        expected_books=["John", "Romans", "1 John"],
        expected_verses=["John 3:16", "Romans 5:8", "Romans 8:38-39", "1 John 4:9-10"],
        description="Tanrı'nın Mesih'le gösterilen sevgisi",
    ),
    TestQuery(
        id=2,
        query="Pavlus Korintlilere mektubunda gerçek sevginin özelliklerini ve doğasını nasıl tanımlıyor?",
        category="Sevgi",
        expected_books=["1 Corinthians"],
        expected_verses=["1 Corinthians 13:4-7", "1 Corinthians 13:13"],
        description="Sevgi bölümü - 1. Korintliler 13",
    ),
    TestQuery(
        id=3,
        query="İsa birbirini sevme konusunda hangi emri verdi ve öğrenciler bu sevgiyi nasıl göstermeli?",
        category="Sevgi",
        expected_books=["John", "Matthew", "Mark"],
        expected_verses=["John 13:34-35", "Matthew 22:37-40", "Mark 12:30-31"],
        description="Birbirini sevme emri",
    ),
    TestQuery(
        id=4,
        query="İncil mükemmel sevginin korkuyu kovması hakkında ne diyor?",
        category="Sevgi",
        expected_books=["1 John"],
        expected_verses=["1 John 4:18"],
        description="Mükemmel sevgi korkuyu kovar",
    ),
    TestQuery(
        id=5,
        query="Tanrımız Rabbi tüm yüreğinle, tüm canınla ve tüm gücünle seveceksin emri nereden geliyor?",
        category="Sevgi",
        expected_books=["Deuteronomy", "Matthew", "Mark"],
        expected_verses=["Deuteronomy 6:5", "Matthew 22:37"],
        description="En büyük emir",
    ),
    # === İMAN (6-10) ===
    TestQuery(
        id=6,
        query="İbraniler kitabına göre imanın tanımı nedir ve umut edilen şeylerin özü nasıl açıklanıyor?",
        category="İman",
        expected_books=["Hebrews"],
        expected_verses=["Hebrews 11:1", "Hebrews 11:6"],
        description="İmanın tanımı",
    ),
    TestQuery(
        id=7,
        query="Pavlus'un Efeslilere mektubuna göre iman aracılığıyla lütufla nasıl kurtuluruz?",
        category="İman",
        expected_books=["Ephesians"],
        expected_verses=["Ephesians 2:8-9"],
        description="Lütufla iman yoluyla kurtuluş",
    ),
    TestQuery(
        id=8,
        query="İsa dağları hareket ettirecek iman ve dua hakkında ne öğretti?",
        category="İman",
        expected_books=["Mark", "Matthew"],
        expected_verses=["Mark 11:22-24", "Matthew 17:20", "Matthew 21:21"],
        description="Dağları hareket ettiren iman",
    ),
    TestQuery(
        id=9,
        query="Görünene değil imana göre yürümek ne anlama geliyor?",
        category="İman",
        expected_books=["2 Corinthians"],
        expected_verses=["2 Corinthians 5:7"],
        description="İmanla yürümek",
    ),
    TestQuery(
        id=10,
        query="Romalılara göre iman işitmekten gelir ve işitmek Tanrı'nın sözüyle olur ifadesi ne anlama geliyor?",
        category="İman",
        expected_books=["Romans"],
        expected_verses=["Romans 10:17"],
        description="İman işitmekten gelir",
    ),
    # === KURTULUŞ (11-15) ===
    TestQuery(
        id=11,
        query="Kurtulmak için ağzınla Rab İsa'yı itiraf etmek ve yüreğinle iman etmek hakkında Pavlus ne öğretiyor?",
        category="Kurtuluş",
        expected_books=["Romans"],
        expected_verses=["Romans 10:9-10", "Romans 10:13"],
        description="İtiraf et ve iman et",
    ),
    TestQuery(
        id=12,
        query="İsa yol, gerçek ve yaşam benim, Baba'ya ancak benim aracılığımla gelinir dedi. Bu hangi ayette?",
        category="Kurtuluş",
        expected_books=["John"],
        expected_verses=["John 14:6"],
        description="İsa yoldur",
    ),
    TestQuery(
        id=13,
        query="Kurtuluş başka hiç kimsede yoktur, insanlara kurtuluş için verilmiş başka bir ad yoktur ayeti nerede geçiyor?",
        category="Kurtuluş",
        expected_books=["Acts"],
        expected_verses=["Acts 4:12"],
        description="Başka bir isim yok",
    ),
    TestQuery(
        id=14,
        query="Titus kurtuluşun doğruluk işlerimizle değil Tanrı'nın merhametiyle olduğunu nasıl açıklıyor?",
        category="Kurtuluş",
        expected_books=["Titus"],
        expected_verses=["Titus 3:5"],
        description="İşlerle değil",
    ),
    TestQuery(
        id=15,
        query="Tanrı dünyayı o kadar çok sevdi ki biricik Oğlunu verdi ayeti hangi kitapta geçiyor?",
        category="Kurtuluş",
        expected_books=["John"],
        expected_verses=["John 3:16", "John 3:17-18"],
        description="Yuhanna 3:16 - en ünlü ayet",
    ),
    # === BAĞIŞLAMA (16-18) ===
    TestQuery(
        id=16,
        query="Başkalarını bağışlarsanız gökteki Babanız da sizi bağışlar öğretisi nerede geçiyor?",
        category="Bağışlama",
        expected_books=["Matthew", "Mark"],
        expected_verses=["Matthew 6:14-15", "Mark 11:25-26"],
        description="Bağışlamak için bağışla",
    ),
    TestQuery(
        id=17,
        query="Efesliler birbirinize şefkatli ve bağışlayıcı olun ayeti hakkında ne diyor?",
        category="Bağışlama",
        expected_books=["Ephesians", "Colossians"],
        expected_verses=["Ephesians 4:32", "Colossians 3:13"],
        description="Tanrı bağışladığı gibi bağışla",
    ),
    TestQuery(
        id=18,
        query="Günahlarımızı itiraf edersek Tanrı güvenilir ve adildir bizi bağışlar ayeti nerede?",
        category="Bağışlama",
        expected_books=["1 John"],
        expected_verses=["1 John 1:9"],
        description="Günahları itiraf et",
    ),
    # === İSA'NIN ÖĞRETİLERİ VE MESELLER (19-22) ===
    TestQuery(
        id=19,
        query="Dağdaki Vaaz'da İsa'nın öğrettiği ne mutlu sözleri Beatitudes nelerdir?",
        category="Öğretiler",
        expected_books=["Matthew"],
        expected_verses=["Matthew 5:3-12"],
        description="Ne mutlular (Beatitudes)",
    ),
    TestQuery(
        id=20,
        query="Rabbimizin Duası veya Baba Duası göklerdeki Babamız diye başlayan dua hangi bölümde?",
        category="Öğretiler",
        expected_books=["Matthew", "Luke"],
        expected_verses=["Matthew 6:9-13", "Luke 11:2-4"],
        description="Rabbin Duası",
    ),
    TestQuery(
        id=21,
        query="Savurgan oğul veya kayıp oğul meseli babanın geri dönen oğlunu karşılaması hangi bölümde?",
        category="Meseller",
        expected_books=["Luke"],
        expected_verses=["Luke 15:11-32"],
        description="Savurgan Oğul",
    ),
    TestQuery(
        id=22,
        query="İyi Samiriyeli meseli komşunu sev ve merhamet göster öğretisi nerede anlatılıyor?",
        category="Meseller",
        expected_books=["Luke"],
        expected_verses=["Luke 10:25-37"],
        description="İyi Samiriyeli",
    ),
    # === İSA'NIN MUCİZELERİ (23-24) ===
    TestQuery(
        id=23,
        query="İsa beş ekmek ve iki balıkla beş bin kişiyi nasıl doyurdu bu mucize nerede anlatılıyor?",
        category="Mucizeler",
        expected_books=["Matthew", "Mark", "Luke", "John"],
        expected_verses=[
            "Matthew 14:15-21",
            "Mark 6:31-44",
            "Luke 9:10-17",
            "John 6:5-14",
        ],
        description="5000 kişiyi doyurma",
    ),
    TestQuery(
        id=24,
        query="İsa Lazar'ı dört gündür mezarda olmasına rağmen nasıl diriltti?",
        category="Mucizeler",
        expected_books=["John"],
        expected_verses=["John 11:1-44", "John 11:25-26"],
        description="Lazar'ın dirilişi",
    ),
    # === ESKİ AHİT (25-27) ===
    TestQuery(
        id=25,
        query="Başlangıçta Tanrı gökleri ve yeri yarattı yaratılış hikayesi Tekvin'de nasıl anlatılıyor?",
        category="Yaratılış",
        expected_books=["Genesis"],
        expected_verses=["Genesis 1:1", "Genesis 1:1-31", "Genesis 2:1-3"],
        description="Yaratılış öyküsü",
    ),
    TestQuery(
        id=26,
        query="Tanrı'nın Musa'ya Sina Dağı'nda verdiği On Emir nelerdir?",
        category="Yasa",
        expected_books=["Exodus", "Deuteronomy"],
        expected_verses=["Exodus 20:1-17", "Deuteronomy 5:6-21"],
        description="On Emir",
    ),
    TestQuery(
        id=27,
        query="Rab çobanımdır eksikliğim olmaz Mezmur 23 neler söylüyor?",
        category="Mezmurlar",
        expected_books=["Psalms"],
        expected_verses=["Psalm 23:1-6"],
        description="Mezmur 23 - Rab çobanım",
    ),
    # === UMUT VE CESARET (28-29) ===
    TestQuery(
        id=28,
        query="Rabbe güvenenlerin gücü yenilenir kartallar gibi kanat açarlar ayeti İşaya'da nerede?",
        category="Umut",
        expected_books=["Isaiah"],
        expected_verses=["Isaiah 40:31"],
        description="Kartallar gibi kanatlanmak",
    ),
    TestQuery(
        id=29,
        query="Sizin için düşündüğüm tasarılar size zarar vermek değil umut ve gelecek vermek içindir ayeti Yeremya'da nerede?",
        category="Umut",
        expected_books=["Jeremiah"],
        expected_verses=["Jeremiah 29:11"],
        description="Umut ve gelecek planları",
    ),
    # === VAHİY VE SON ZAMANLAR (30) ===
    TestQuery(
        id=30,
        query="Vahiy kitabında Tanrı her şeyi yeni yapıyorum ve gözyaşlarını silecek ölüm olmayacak ayetleri nerede?",
        category="Vahiy",
        expected_books=["Revelation"],
        expected_verses=["Revelation 21:1-4", "Revelation 21:5"],
        description="Yeni gök ve yeni yer",
    ),
]


def evaluate_result(
    result, expected_books: List[str], expected_verses: List[str]
) -> dict:
    """Evaluate a single search result against expected values"""
    # Get reference from result - try multiple attribute names
    ref = ""
    if (
        hasattr(result, "book_name")
        and hasattr(result, "chapter")
        and hasattr(result, "verse")
    ):
        ref = f"{result.book_name} {result.chapter}:{result.verse}"
    elif hasattr(result, "reference"):
        ref = result.reference
    elif hasattr(result, "payload") and "reference" in result.payload:
        ref = result.payload["reference"]
    elif isinstance(result, dict):
        ref = result.get("reference", "")

    # Check if reference matches expected books
    book_match = any(book.lower() in ref.lower() for book in expected_books)

    # Check if reference matches expected verses (partial match)
    verse_match = any(
        verse.lower().replace(" ", "") in ref.lower().replace(" ", "")
        or ref.lower().replace(" ", "") in verse.lower().replace(" ", "")
        for verse in expected_verses
    )

    return {
        "reference": ref,
        "book_match": book_match,
        "verse_match": verse_match,
        "score": getattr(result, "score", 0)
        if hasattr(result, "score")
        else result.get("score", 0),
    }


async def run_tests():
    """Run all test queries and evaluate results"""
    from src.ultimate_rag import UltimateRAG

    console.print(
        "\n[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]"
    )
    console.print(
        "[bold cyan]   İncil Ultimate RAG Test Paketi - 30 TÜRKÇE Sorgu           [/bold cyan]"
    )
    console.print(
        "[bold cyan]   (Sorgular otomatik olarak İngilizce'ye çevrilecek)         [/bold cyan]"
    )
    console.print(
        "[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]\n"
    )

    # Initialize RAG
    console.print("[dim]Ultimate RAG Pipeline başlatılıyor...[/dim]")
    rag = UltimateRAG(verbose=False)

    results_summary = []
    total_book_matches = 0
    total_verse_matches = 0
    total_queries = len(TEST_QUERIES)

    start_time = time.time()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Test ediliyor...", total=total_queries)

        for test in TEST_QUERIES:
            progress.update(
                task, description=f"[cyan]Sorgu {test.id}/30:[/cyan] {test.category}"
            )

            try:
                # Run search - Turkish query will be translated to English
                search_results = await rag.search_bible(
                    test.query, translation="kjva", top_k=5
                )

                # Evaluate results
                query_book_match = False
                query_verse_match = False
                top_refs = []

                for i, res in enumerate(search_results[:5]):
                    eval_result = evaluate_result(
                        res, test.expected_books, test.expected_verses
                    )
                    top_refs.append(eval_result["reference"])

                    if eval_result["book_match"]:
                        query_book_match = True
                    if eval_result["verse_match"]:
                        query_verse_match = True

                if query_book_match:
                    total_book_matches += 1
                if query_verse_match:
                    total_verse_matches += 1

                results_summary.append(
                    {
                        "id": test.id,
                        "category": test.category,
                        "description": test.description,
                        "expected": test.expected_verses[:2],  # First 2 expected
                        "found": top_refs[:3],  # Top 3 found
                        "book_match": "✅" if query_book_match else "❌",
                        "verse_match": "✅" if query_verse_match else "❌",
                    }
                )

            except Exception as e:
                console.print(f"[red]Sorgu {test.id} hatası: {e}[/red]")
                results_summary.append(
                    {
                        "id": test.id,
                        "category": test.category,
                        "description": test.description,
                        "expected": test.expected_verses[:2],
                        "found": ["HATA"],
                        "book_match": "❌",
                        "verse_match": "❌",
                    }
                )

            progress.advance(task)

    elapsed_time = time.time() - start_time

    # Print results table
    console.print(
        "\n[bold]═══════════════════════════════════════════════════════════════[/bold]"
    )
    console.print(
        "[bold]                         TEST SONUÇLARI                        [/bold]"
    )
    console.print(
        "[bold]═══════════════════════════════════════════════════════════════[/bold]\n"
    )

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", width=3)
    table.add_column("Kategori", width=12)
    table.add_column("Açıklama", width=25)
    table.add_column("Beklenen", width=20)
    table.add_column("Bulunan (İlk 3)", width=30)
    table.add_column("Kitap", width=5)
    table.add_column("Ayet", width=5)

    for r in results_summary:
        table.add_row(
            str(r["id"]),
            r["category"],
            r["description"][:24],
            ", ".join(r["expected"])[:19],
            ", ".join(r["found"])[:29],
            r["book_match"],
            r["verse_match"],
        )

    console.print(table)

    # Print summary
    console.print(
        "\n[bold]═══════════════════════════════════════════════════════════════[/bold]"
    )
    console.print(
        "[bold]                           ÖZET                                [/bold]"
    )
    console.print(
        "[bold]═══════════════════════════════════════════════════════════════[/bold]\n"
    )

    book_accuracy = (total_book_matches / total_queries) * 100
    verse_accuracy = (total_verse_matches / total_queries) * 100

    console.print(f"[cyan]Toplam Sorgu:[/cyan] {total_queries}")
    console.print(f"[cyan]Toplam Süre:[/cyan] {elapsed_time:.2f} saniye")
    console.print(
        f"[cyan]Ortalama Sorgu Süresi:[/cyan] {elapsed_time / total_queries:.2f} saniye"
    )
    console.print()
    console.print(
        f"[green]Kitap Eşleşme Doğruluğu:[/green] {total_book_matches}/{total_queries} ({book_accuracy:.1f}%)"
    )
    console.print(
        f"[green]Ayet Eşleşme Doğruluğu:[/green] {total_verse_matches}/{total_queries} ({verse_accuracy:.1f}%)"
    )

    # Score interpretation
    if verse_accuracy >= 80:
        console.print(
            "\n[bold green]✅ MÜKEMMEL: Sistem çok iyi performans gösteriyor![/bold green]"
        )
    elif verse_accuracy >= 60:
        console.print(
            "\n[bold yellow]⚠️ İYİ: Sistem makul düzeyde performans gösteriyor[/bold yellow]"
        )
    elif verse_accuracy >= 40:
        console.print(
            "\n[bold orange3]⚠️ ORTA: Sistem iyileştirme gerektiriyor[/bold orange3]"
        )
    else:
        console.print(
            "\n[bold red]❌ DÜŞÜK: Sistem önemli iyileştirme gerektiriyor[/bold red]"
        )

    return {
        "total_queries": total_queries,
        "book_matches": total_book_matches,
        "verse_matches": total_verse_matches,
        "book_accuracy": book_accuracy,
        "verse_accuracy": verse_accuracy,
        "elapsed_time": elapsed_time,
        "results": results_summary,
    }


if __name__ == "__main__":
    console.print("[bold]İncil Ultimate RAG Test Paketi Başlatılıyor...[/bold]\n")
    console.print(
        "[dim]NOT: Tüm sorgular Türkçe olarak girilecek ve sistem tarafından[/dim]"
    )
    console.print("[dim]      otomatik olarak İngilizce'ye çevrilecektir.[/dim]\n")
    results = asyncio.run(run_tests())
