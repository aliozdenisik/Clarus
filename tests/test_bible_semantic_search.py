
import sys
import time
from pathlib import Path
from rich.console import Console
from rich.table import Table

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from src.search import BibleSemanticChunkSearcher

console = Console()

def run_semantic_search_tests():
    console.print("\n[bold blue]Running 30 Semantic Search Queries on Bible Chunks[/bold blue]\n")
    
    # Initialize searcher
    try:
        searcher = BibleSemanticChunkSearcher(translation="kjva")
        if not searcher.collection_exists():
            console.print("[red]Collection 'bible_kjva_semantic_chunks' does not exist![/red]")
            console.print("Run 'python main.py build-bible-semantic-chunks --translation kjva' first.")
            return
    except Exception as e:
        console.print(f"[red]Error initializing searcher: {e}[/red]")
        return

    queries = [
        "In the beginning God created heaven and earth",
        "faith without works is dead",
        "The Lord is my shepherd",
        "For God so loved the world",
        "I am the way the truth and the life",
        "The fruit of the Spirit is love joy peace",
        "Love is patient love is kind",
        "The armor of God",
        "Blessed are the poor in spirit",
        "The valley of the shadow of death",
        "Moses parting the Red Sea",
        "David and Goliath",
        "Noah's ark and the flood",
        "The ten commandments",
        "The sermon on the mount",
        "The prodigal son",
        "The good samaritan",
        "The resurrection of Jesus",
        "The betrayal by Judas",
        "Pentecost and the Holy Spirit",
        "The conversion of Paul",
        "The revelation of John",
        "The fall of Jericho",
        "Daniel in the lion's den",
        "Jonah and the whale",
        "The wisdom of Solomon",
        "The patience of Job",
        "The prophecy of Isaiah about the messiah",
        "The baptism of Jesus",
        "The transfiguration"
    ]

    table = Table(title="Semantic Search Test Results", show_lines=True)
    table.add_column("#", style="dim", width=3)
    table.add_column("Query", style="cyan", width=30)
    table.add_column("Top Result Reference", style="green", width=25)
    table.add_column("Score", style="magenta", width=8)
    table.add_column("Verses", style="yellow", width=6)
    table.add_column("Snippet", style="white")

    start_time = time.time()
    
    for i, query in enumerate(queries, 1):
        try:
            results = searcher.search(query, limit=1)
            
            if results:
                top = results[0]
                verse_range = f"{top.start_verse}-{top.end_verse}"
                ref = f"{top.book_name} {top.chapter}:{verse_range}"
                snippet = top.text[:50].replace("\n", " ") + "..."
                table.add_row(
                    str(i), 
                    query, 
                    ref, 
                    f"{top.score:.3f}", 
                    str(top.verse_count), 
                    snippet
                )
            else:
                table.add_row(str(i), query, "[red]No results[/red]", "-", "-", "-")
                
        except Exception as e:
            table.add_row(str(i), query, f"[red]Error: {e}[/red]", "-", "-", "-")

    duration = time.time() - start_time
    console.print(table)
    console.print(f"\n[dim]Completed 30 queries in {duration:.2f} seconds ({duration/30:.2f}s/query)[/dim]")

if __name__ == "__main__":
    run_semantic_search_tests()
