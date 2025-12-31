#!/usr/bin/env python3
"""Analyze failed Bible queries to understand why they didn't match expected books."""
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.table import Table
from src.query_enhancer import QueryEnhancer
from src.ultimate_rag import UltimateRAG

console = Console()

# Failed queries from test
FAILED_QUERIES = [
    {
        "turkish": "Süleyman'ın bilgeliği iki kadın bebek",
        "expected_book": "1 Kings",
        "expected_ref": "1 Kings 3:16-28",
        "got": ["Ezekiel", "1 Samuel", "Ezra"]
    },
    {
        "turkish": "Daniel aslan çukurunda",
        "expected_book": "Daniel",
        "expected_ref": "Daniel 6",
        "got": ["Bel and the Dragon"]
    },
    {
        "turkish": "Kutsal Ruh'un meyvesi sevgi sevinç",
        "expected_book": "Galatians",
        "expected_ref": "Galatians 5:22",
        "got": ["Ephesians", "2 Corinthians", "Sirach"]
    },
    {
        "turkish": "Ne ekersen onu biçersin",
        "expected_book": "Galatians",
        "expected_ref": "Galatians 6:7",
        "got": ["Proverbs", "Obadiah", "John"]
    },
    {
        "turkish": "Mesih'te ne Yahudi ne Grek",
        "expected_book": "Galatians",
        "expected_ref": "Galatians 3:28",
        "got": ["1 Corinthians"]
    },
]

def analyze_failures():
    console.print("\n[bold magenta]🔍 Analyzing Failed Bible Queries[/bold magenta]\n")
    
    enhancer = QueryEnhancer()
    rag = UltimateRAG(verbose=False)
    
    for i, q in enumerate(FAILED_QUERIES, 1):
        console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
        console.print(f"[bold]Query {i}: {q['turkish']}[/bold]")
        console.print(f"[dim]Expected: {q['expected_book']} ({q['expected_ref']})[/dim]")
        console.print(f"[yellow]Got: {q['got']}[/yellow]")
        
        # Step 1: Check translation
        translated = enhancer.translate_for_bible(q['turkish'])
        console.print(f"\n[green]Translation:[/green] {translated}")
        
        # Step 2: Search with translation
        results = rag.search_bible(q['turkish'], translation="kjva", top_k=10)
        
        # Display results
        console.print(f"\n[blue]Search Results (top 10):[/blue]")
        table = Table(show_lines=False)
        table.add_column("#", width=3)
        table.add_column("Book", width=20)
        table.add_column("Ref", width=10)
        table.add_column("Score", width=8)
        table.add_column("Text Snippet", width=50)
        
        found_expected = False
        for j, r in enumerate(results, 1):
            is_expected = r.book_name == q['expected_book']
            if is_expected:
                found_expected = True
            style = "green bold" if is_expected else "white"
            table.add_row(
                str(j),
                f"[{style}]{r.book_name}[/{style}]",
                f"{r.chapter}:{r.verse}",
                f"{r.score:.3f}",
                r.text[:50] + "..."
            )
        
        console.print(table)
        
        if not found_expected:
            console.print(f"\n[red]❌ Expected book '{q['expected_book']}' not in top 10 results[/red]")
        else:
            console.print(f"\n[green]✓ Found expected book in results[/green]")

if __name__ == "__main__":
    analyze_failures()
