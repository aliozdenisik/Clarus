#!/usr/bin/env python3
"""
Bible Ultimate RAG Test Suite - Comprehensive 30 Query Evaluation

Tests the Ultimate RAG Pipeline against the English KJVA Bible collection
with comprehensive, in-depth queries covering both Old and New Testaments.

Each query has expected verse references researched from web sources.
"""

import asyncio
import sys
import time
from dataclasses import dataclass
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add parent directory to path
sys.path.insert(0, '.')

console = Console()

@dataclass
class TestQuery:
    """Test query with expected results"""
    id: int
    query: str
    category: str
    expected_books: List[str]  # Expected books to find
    expected_verses: List[str]  # Expected verse references (e.g., "John 3:16")
    description: str


# 30 Comprehensive Bible Test Queries with Expected Answers
TEST_QUERIES = [
    # === LOVE & RELATIONSHIPS (1-5) ===
    TestQuery(
        id=1,
        query="What does the Bible teach about God's unconditional love for humanity and how it was demonstrated through the sacrifice of His Son?",
        category="Love",
        expected_books=["John", "Romans", "1 John"],
        expected_verses=["John 3:16", "Romans 5:8", "Romans 8:38-39", "1 John 4:9-10"],
        description="God's love demonstrated through Christ"
    ),
    TestQuery(
        id=2,
        query="How does Paul describe the characteristics and nature of true love in his letter to the Corinthians?",
        category="Love",
        expected_books=["1 Corinthians"],
        expected_verses=["1 Corinthians 13:4-7", "1 Corinthians 13:13"],
        description="Love chapter - 1 Corinthians 13"
    ),
    TestQuery(
        id=3,
        query="What commandment did Jesus give about loving one another and how should disciples demonstrate this love?",
        category="Love",
        expected_books=["John", "Matthew", "Mark"],
        expected_verses=["John 13:34-35", "Matthew 22:37-40", "Mark 12:30-31"],
        description="New commandment to love"
    ),
    TestQuery(
        id=4,
        query="What does the Bible say about perfect love casting out fear and how does fear relate to punishment?",
        category="Love",
        expected_books=["1 John"],
        expected_verses=["1 John 4:18"],
        description="Perfect love casts out fear"
    ),
    TestQuery(
        id=5,
        query="How should we love the Lord our God according to Deuteronomy and what does this involve?",
        category="Love",
        expected_books=["Deuteronomy", "Matthew", "Mark"],
        expected_verses=["Deuteronomy 6:5", "Matthew 22:37"],
        description="Greatest commandment"
    ),
    
    # === FAITH & BELIEF (6-10) ===
    TestQuery(
        id=6,
        query="What is the biblical definition of faith according to the book of Hebrews and how is it described as the substance of things hoped for?",
        category="Faith",
        expected_books=["Hebrews"],
        expected_verses=["Hebrews 11:1", "Hebrews 11:6"],
        description="Definition of faith"
    ),
    TestQuery(
        id=7,
        query="How are we saved by grace through faith according to Paul's letter to the Ephesians?",
        category="Faith",
        expected_books=["Ephesians"],
        expected_verses=["Ephesians 2:8-9"],
        description="Salvation by grace through faith"
    ),
    TestQuery(
        id=8,
        query="What did Jesus teach about having faith to move mountains and receiving what you pray for?",
        category="Faith",
        expected_books=["Mark", "Matthew"],
        expected_verses=["Mark 11:22-24", "Matthew 17:20", "Matthew 21:21"],
        description="Faith to move mountains"
    ),
    TestQuery(
        id=9,
        query="What does Paul mean when he says we walk by faith and not by sight?",
        category="Faith",
        expected_books=["2 Corinthians"],
        expected_verses=["2 Corinthians 5:7"],
        description="Walking by faith"
    ),
    TestQuery(
        id=10,
        query="How does faith come according to Paul's letter to the Romans and what is its relationship to hearing the word?",
        category="Faith",
        expected_books=["Romans"],
        expected_verses=["Romans 10:17"],
        description="Faith comes by hearing"
    ),
    
    # === SALVATION & REDEMPTION (11-15) ===
    TestQuery(
        id=11,
        query="What must a person do to be saved according to Paul's teaching about confessing with the mouth and believing in the heart?",
        category="Salvation",
        expected_books=["Romans"],
        expected_verses=["Romans 10:9-10", "Romans 10:13"],
        description="Confess and believe"
    ),
    TestQuery(
        id=12,
        query="What did Jesus say about being the way, the truth, and the life, and about coming to the Father?",
        category="Salvation",
        expected_books=["John"],
        expected_verses=["John 14:6"],
        description="Jesus is the way"
    ),
    TestQuery(
        id=13,
        query="What does Acts teach about salvation being found in no other name except Jesus Christ?",
        category="Salvation",
        expected_books=["Acts"],
        expected_verses=["Acts 4:12"],
        description="No other name"
    ),
    TestQuery(
        id=14,
        query="How does Titus describe salvation as not by works of righteousness but by God's mercy?",
        category="Salvation",
        expected_books=["Titus"],
        expected_verses=["Titus 3:5"],
        description="Not by works"
    ),
    TestQuery(
        id=15,
        query="What does John 3:16 teach about God's love, giving His Son, and receiving eternal life through belief?",
        category="Salvation",
        expected_books=["John"],
        expected_verses=["John 3:16", "John 3:17-18"],
        description="John 3:16 - most famous verse"
    ),
    
    # === FORGIVENESS (16-18) ===
    TestQuery(
        id=16,
        query="What does Jesus teach about forgiving others so that the Father will forgive our trespasses?",
        category="Forgiveness",
        expected_books=["Matthew", "Mark"],
        expected_verses=["Matthew 6:14-15", "Mark 11:25-26"],
        description="Forgive to be forgiven"
    ),
    TestQuery(
        id=17,
        query="How does Ephesians instruct us to be kind and forgiving to one another as God forgave us?",
        category="Forgiveness",
        expected_books=["Ephesians", "Colossians"],
        expected_verses=["Ephesians 4:32", "Colossians 3:13"],
        description="Forgive as God forgave"
    ),
    TestQuery(
        id=18,
        query="What does 1 John teach about confessing our sins and God being faithful to forgive and cleanse us?",
        category="Forgiveness",
        expected_books=["1 John"],
        expected_verses=["1 John 1:9"],
        description="Confess sins"
    ),
    
    # === JESUS' TEACHINGS & PARABLES (19-22) ===
    TestQuery(
        id=19,
        query="What are the Beatitudes that Jesus taught in the Sermon on the Mount about who is blessed?",
        category="Teachings",
        expected_books=["Matthew"],
        expected_verses=["Matthew 5:3-12"],
        description="Beatitudes"
    ),
    TestQuery(
        id=20,
        query="What did Jesus teach in the Lord's Prayer about how we should pray to our Father in heaven?",
        category="Teachings",
        expected_books=["Matthew", "Luke"],
        expected_verses=["Matthew 6:9-13", "Luke 11:2-4"],
        description="Lord's Prayer"
    ),
    TestQuery(
        id=21,
        query="What is the parable of the prodigal son about the father welcoming back his wayward child?",
        category="Parables",
        expected_books=["Luke"],
        expected_verses=["Luke 15:11-32"],
        description="Prodigal Son"
    ),
    TestQuery(
        id=22,
        query="What is the parable of the good Samaritan about loving your neighbor and showing mercy?",
        category="Parables",
        expected_books=["Luke"],
        expected_verses=["Luke 10:25-37"],
        description="Good Samaritan"
    ),
    
    # === MIRACLES OF JESUS (23-24) ===
    TestQuery(
        id=23,
        query="How did Jesus feed five thousand people with only five loaves of bread and two fish?",
        category="Miracles",
        expected_books=["Matthew", "Mark", "Luke", "John"],
        expected_verses=["Matthew 14:15-21", "Mark 6:31-44", "Luke 9:10-17", "John 6:5-14"],
        description="Feeding the 5000"
    ),
    TestQuery(
        id=24,
        query="How did Jesus raise Lazarus from the dead after he had been in the tomb for four days?",
        category="Miracles",
        expected_books=["John"],
        expected_verses=["John 11:1-44", "John 11:25-26"],
        description="Raising Lazarus"
    ),
    
    # === OLD TESTAMENT (25-27) ===
    TestQuery(
        id=25,
        query="How did God create the heavens and the earth in the beginning according to Genesis?",
        category="Creation",
        expected_books=["Genesis"],
        expected_verses=["Genesis 1:1", "Genesis 1:1-31", "Genesis 2:1-3"],
        description="Creation account"
    ),
    TestQuery(
        id=26,
        query="What are the Ten Commandments that God gave to Moses on Mount Sinai?",
        category="Law",
        expected_books=["Exodus", "Deuteronomy"],
        expected_verses=["Exodus 20:1-17", "Deuteronomy 5:6-21"],
        description="Ten Commandments"
    ),
    TestQuery(
        id=27,
        query="What does Psalm 23 say about the Lord being my shepherd and providing for all my needs?",
        category="Psalms",
        expected_books=["Psalms"],
        expected_verses=["Psalm 23:1-6"],
        description="Psalm 23 - The Lord is my shepherd"
    ),
    
    # === HOPE & ENCOURAGEMENT (28-29) ===
    TestQuery(
        id=28,
        query="What does Isaiah say about those who wait upon the Lord renewing their strength and mounting up with wings like eagles?",
        category="Hope",
        expected_books=["Isaiah"],
        expected_verses=["Isaiah 40:31"],
        description="Wings like eagles"
    ),
    TestQuery(
        id=29,
        query="What does Jeremiah say about God's plans to give us hope and a future, not to harm us?",
        category="Hope",
        expected_books=["Jeremiah"],
        expected_verses=["Jeremiah 29:11"],
        description="Plans for hope and future"
    ),
    
    # === REVELATION & END TIMES (30) ===
    TestQuery(
        id=30,
        query="What does Revelation say about God making all things new and wiping away every tear with no more death or sorrow?",
        category="Revelation",
        expected_books=["Revelation"],
        expected_verses=["Revelation 21:1-4", "Revelation 21:5"],
        description="New heaven and new earth"
    ),
]


def evaluate_result(result, expected_books: List[str], expected_verses: List[str]) -> dict:
    """Evaluate a single search result against expected values"""
    # Get reference from result
    ref = ""
    if hasattr(result, 'reference'):
        ref = result.reference
    elif hasattr(result, 'payload') and 'reference' in result.payload:
        ref = result.payload['reference']
    elif isinstance(result, dict):
        ref = result.get('reference', '')
    
    # Check if reference matches expected books
    book_match = any(book.lower() in ref.lower() for book in expected_books)
    
    # Check if reference matches expected verses (partial match)
    verse_match = any(
        verse.lower().replace(" ", "") in ref.lower().replace(" ", "") or
        ref.lower().replace(" ", "") in verse.lower().replace(" ", "")
        for verse in expected_verses
    )
    
    return {
        "reference": ref,
        "book_match": book_match,
        "verse_match": verse_match,
        "score": getattr(result, 'score', 0) if hasattr(result, 'score') else result.get('score', 0)
    }


async def run_tests():
    """Run all test queries and evaluate results"""
    from src.ultimate_rag import UltimateRAG
    
    console.print("\n[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]       Bible Ultimate RAG Test Suite - 30 Queries              [/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]\n")
    
    # Initialize RAG
    console.print("[dim]Initializing Ultimate RAG Pipeline...[/dim]")
    rag = UltimateRAG(verbose=False)
    
    results_summary = []
    total_book_matches = 0
    total_verse_matches = 0
    total_queries = len(TEST_QUERIES)
    
    start_time = time.time()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Testing...", total=total_queries)
        
        for test in TEST_QUERIES:
            progress.update(task, description=f"[cyan]Query {test.id}/30:[/cyan] {test.category}")
            
            try:
                # Run search
                search_results = rag.search_bible(test.query, translation="kjva", top_k=5)
                
                # Evaluate results
                query_book_match = False
                query_verse_match = False
                top_refs = []
                
                for i, res in enumerate(search_results[:5]):
                    eval_result = evaluate_result(res, test.expected_books, test.expected_verses)
                    top_refs.append(eval_result["reference"])
                    
                    if eval_result["book_match"]:
                        query_book_match = True
                    if eval_result["verse_match"]:
                        query_verse_match = True
                
                if query_book_match:
                    total_book_matches += 1
                if query_verse_match:
                    total_verse_matches += 1
                
                results_summary.append({
                    "id": test.id,
                    "category": test.category,
                    "description": test.description,
                    "expected": test.expected_verses[:2],  # First 2 expected
                    "found": top_refs[:3],  # Top 3 found
                    "book_match": "✅" if query_book_match else "❌",
                    "verse_match": "✅" if query_verse_match else "❌",
                })
                
            except Exception as e:
                console.print(f"[red]Error on query {test.id}: {e}[/red]")
                results_summary.append({
                    "id": test.id,
                    "category": test.category,
                    "description": test.description,
                    "expected": test.expected_verses[:2],
                    "found": ["ERROR"],
                    "book_match": "❌",
                    "verse_match": "❌",
                })
            
            progress.advance(task)
    
    elapsed_time = time.time() - start_time
    
    # Print results table
    console.print("\n[bold]═══════════════════════════════════════════════════════════════[/bold]")
    console.print("[bold]                         TEST RESULTS                          [/bold]")
    console.print("[bold]═══════════════════════════════════════════════════════════════[/bold]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", width=3)
    table.add_column("Category", width=12)
    table.add_column("Description", width=25)
    table.add_column("Expected", width=20)
    table.add_column("Found (Top 3)", width=30)
    table.add_column("Book", width=5)
    table.add_column("Verse", width=5)
    
    for r in results_summary:
        table.add_row(
            str(r["id"]),
            r["category"],
            r["description"][:24],
            ", ".join(r["expected"])[:19],
            ", ".join(r["found"])[:29],
            r["book_match"],
            r["verse_match"]
        )
    
    console.print(table)
    
    # Print summary
    console.print("\n[bold]═══════════════════════════════════════════════════════════════[/bold]")
    console.print("[bold]                         SUMMARY                               [/bold]")
    console.print("[bold]═══════════════════════════════════════════════════════════════[/bold]\n")
    
    book_accuracy = (total_book_matches / total_queries) * 100
    verse_accuracy = (total_verse_matches / total_queries) * 100
    
    console.print(f"[cyan]Total Queries:[/cyan] {total_queries}")
    console.print(f"[cyan]Total Time:[/cyan] {elapsed_time:.2f} seconds")
    console.print(f"[cyan]Average Time per Query:[/cyan] {elapsed_time/total_queries:.2f} seconds")
    console.print()
    console.print(f"[green]Book Match Accuracy:[/green] {total_book_matches}/{total_queries} ({book_accuracy:.1f}%)")
    console.print(f"[green]Verse Match Accuracy:[/green] {total_verse_matches}/{total_queries} ({verse_accuracy:.1f}%)")
    
    # Score interpretation
    if verse_accuracy >= 80:
        console.print("\n[bold green]✅ EXCELLENT: System performs very well![/bold green]")
    elif verse_accuracy >= 60:
        console.print("\n[bold yellow]⚠️ GOOD: System performs reasonably well[/bold yellow]")
    elif verse_accuracy >= 40:
        console.print("\n[bold orange3]⚠️ FAIR: System needs improvement[/bold orange3]")
    else:
        console.print("\n[bold red]❌ POOR: System needs significant improvement[/bold red]")
    
    return {
        "total_queries": total_queries,
        "book_matches": total_book_matches,
        "verse_matches": total_verse_matches,
        "book_accuracy": book_accuracy,
        "verse_accuracy": verse_accuracy,
        "elapsed_time": elapsed_time,
        "results": results_summary
    }


if __name__ == "__main__":
    console.print("[bold]Starting Bible Ultimate RAG Test Suite...[/bold]\n")
    results = asyncio.run(run_tests())
