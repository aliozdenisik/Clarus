#!/usr/bin/env python3
"""
Multi-Agent Flow Test

Tests how queries flow through the 4 specialist agents:
- OldTestamentAgent
- NewTestamentAgent  
- ApocryphaAgent
- QuranAgent

And how SummaryAgent synthesizes their outputs.
"""
import sys
import os
import time
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def test_multi_agent_flow():
    """Test multi-agent query processing flow."""
    from src.comparative_rag import ComparativeRAG
    
    console.print("\n[bold cyan]═══ MULTI-AGENT FLOW TEST ═══[/bold cyan]\n")
    
    # Initialize RAG
    rag = ComparativeRAG(
        enable_multi_query=True,  # Use multi-query for better accuracy
        verbose=True
    )
    
    # Test query
    test_query = "Sabır ve tahammül hakkında kutsal kitaplar ne diyor?"
    
    console.print(f"[bold]Test Query:[/bold] {test_query}\n")
    
    # Time the entire process
    total_start = time.time()
    
    # Step 1: Run search_all to get raw search results
    console.print("[yellow]Step 1: Running search_all() with 4 testament collections[/yellow]")
    search_start = time.time()
    search_result = rag.search_all(test_query)
    search_time = time.time() - search_start
    
    # Step 2: Show search results distribution
    console.print(f"\n[yellow]Step 2: Search Results Distribution (Per Testament)[/yellow]")
    
    search_table = Table(title="Search Results by Testament")
    search_table.add_column("Collection", style="cyan")
    search_table.add_column("Count", justify="right")
    search_table.add_column("Agent")
    
    search_table.add_row("quran_tr", str(len(search_result.quran)), "QuranAgent")
    search_table.add_row("bible_ot", str(len(search_result.ot)), "OldTestamentAgent")
    search_table.add_row("bible_nt", str(len(search_result.nt)), "NewTestamentAgent")
    search_table.add_row("bible_apocrypha", str(len(search_result.apocrypha)), "ApocryphaAgent")
    search_table.add_row("TOTAL", str(search_result.total_verses), "-")
    
    console.print(search_table)
    console.print(f"Search completed in {search_time:.2f}s")
    
    # Step 3: Direct to agents (no more splitting needed!)
    console.print(f"\n[yellow]Step 3: Results Ready for Agents (No Split Needed)[/yellow]")
    
    split_table = Table(title="Verses Directly Available Per Agent")
    split_table.add_column("Agent", style="cyan")
    split_table.add_column("Collection", style="dim")
    split_table.add_column("Verse Count", justify="right")
    
    split_table.add_row("OldTestamentAgent", "bible_ot", str(len(search_result.ot)))
    split_table.add_row("NewTestamentAgent", "bible_nt", str(len(search_result.nt)))
    split_table.add_row("ApocryphaAgent", "bible_apocrypha", str(len(search_result.apocrypha)))
    split_table.add_row("QuranAgent", "quran_tr", str(len(search_result.quran)))
    
    console.print(split_table)
    
    # Step 4: Run multi-agent generation
    console.print(f"\n[yellow]Step 4: Running 4 Specialist Agents + Summary Agent[/yellow]")
    gen_start = time.time()
    
    answer = rag.multi_agent_generator.generate(
        query=test_query,
        quran_verses=search_result.quran,
        ot_verses=search_result.ot,
        nt_verses=search_result.nt,
        apocrypha_verses=search_result.apocrypha
    )
    gen_time = time.time() - gen_start
    
    total_time = time.time() - total_start
    
    # Step 5: Show agent outputs
    console.print(f"\n[bold green]═══ AGENT OUTPUTS ═══[/bold green]\n")
    
    # OT Agent
    if answer.old_testament_commentary:
        console.print(Panel(
            answer.old_testament_commentary,
            title="[bold]OldTestamentAgent (Eski Ahit)[/bold]",
            border_style="blue"
        ))
        console.print(f"Citations: {answer.citations.get('old_testament', [])}\n")
    else:
        console.print("[dim]OldTestamentAgent: No verses found[/dim]\n")
    
    # NT Agent
    if answer.new_testament_commentary:
        console.print(Panel(
            answer.new_testament_commentary,
            title="[bold]NewTestamentAgent (Yeni Ahit)[/bold]",
            border_style="green"
        ))
        console.print(f"Citations: {answer.citations.get('new_testament', [])}\n")
    else:
        console.print("[dim]NewTestamentAgent: No verses found[/dim]\n")
    
    # Apocrypha Agent
    if answer.apocrypha_commentary:
        console.print(Panel(
            answer.apocrypha_commentary,
            title="[bold]ApocryphaAgent (Apokrifa)[/bold]",
            border_style="yellow"
        ))
        console.print(f"Citations: {answer.citations.get('apocrypha', [])}\n")
    else:
        console.print("[dim]ApocryphaAgent: No verses found[/dim]\n")
    
    # Quran Agent
    if answer.quran_commentary:
        console.print(Panel(
            answer.quran_commentary,
            title="[bold]QuranAgent (Kuran)[/bold]",
            border_style="magenta"
        ))
        console.print(f"Citations: {answer.citations.get('quran', [])}\n")
    else:
        console.print("[dim]QuranAgent: No verses found[/dim]\n")
    
    # Summary Agent
    if answer.synthesis:
        console.print(Panel(
            answer.synthesis,
            title="[bold]SummaryAgent (Karşılaştırmalı Sentez)[/bold]",
            border_style="cyan"
        ))
    
    # Final stats
    console.print(f"\n[bold cyan]═══ PERFORMANCE METRICS ═══[/bold cyan]")
    
    metrics_table = Table()
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", justify="right")
    
    metrics_table.add_row("Search Time", f"{search_time:.2f}s")
    metrics_table.add_row("Agent Generation Time", f"{gen_time:.2f}s")
    metrics_table.add_row("Total Time", f"{total_time:.2f}s")
    metrics_table.add_row("Overall Confidence", f"{answer.confidence:.0%}")
    
    total_citations = sum(len(c) for c in answer.citations.values())
    metrics_table.add_row("Total Citations", str(total_citations))
    
    console.print(metrics_table)
    
    # Save results to file
    results = {
        "query": test_query,
        "search_stats": {
            "quran": len(search_result.quran),
            "old_testament": len(search_result.ot),
            "new_testament": len(search_result.nt),
            "apocrypha": len(search_result.apocrypha),
            "total": search_result.total_verses
        },
        "agent_input": {
            "old_testament": len(search_result.ot),
            "new_testament": len(search_result.nt),
            "apocrypha": len(search_result.apocrypha),
            "quran": len(search_result.quran)
        },
        "agent_output": {
            "old_testament": {
                "has_commentary": bool(answer.old_testament_commentary),
                "commentary_length": len(answer.old_testament_commentary),
                "citations": answer.citations.get("old_testament", [])
            },
            "new_testament": {
                "has_commentary": bool(answer.new_testament_commentary),
                "commentary_length": len(answer.new_testament_commentary),
                "citations": answer.citations.get("new_testament", [])
            },
            "apocrypha": {
                "has_commentary": bool(answer.apocrypha_commentary),
                "commentary_length": len(answer.apocrypha_commentary),
                "citations": answer.citations.get("apocrypha", [])
            },
            "quran": {
                "has_commentary": bool(answer.quran_commentary),
                "commentary_length": len(answer.quran_commentary),
                "citations": answer.citations.get("quran", [])
            }
        },
        "synthesis_length": len(answer.synthesis),
        "confidence": answer.confidence,
        "timing": {
            "search_time_s": search_time,
            "generation_time_s": gen_time,
            "total_time_s": total_time
        }
    }
    
    output_path = Path(__file__).parent / "multi_agent_test_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    console.print(f"\n[green]Results saved to {output_path}[/green]")
    
    return answer


if __name__ == "__main__":
    test_multi_agent_flow()
