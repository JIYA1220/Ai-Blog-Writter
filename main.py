# main.py
# ============================================================
# AI Blog Writer — Main Entry Point
# Run this from PyCharm or terminal:
#   python main.py
# ============================================================

import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from dotenv import load_dotenv

load_dotenv()

console = Console()


def print_banner():
    console.print(Panel.fit(
        "[bold cyan]AI Blog Writer[/bold cyan] — Production-Grade Agentic Blog System\n"
        "[dim]LangGraph DAG  •  OpenRouter  •  Tavily Retrieval  •  Pydantic Validation[/dim]",
        border_style="cyan"
    ))


def get_user_input() -> dict:
    """Collect blog generation parameters from the user."""
    console.print("\n[bold]Configure your blog:[/bold]\n")

    topic = Prompt.ask(
        "[cyan]Blog Topic[/cyan]",
        default="The Rise of Agentic AI Systems in 2025"
    )

    audience = Prompt.ask(
        "[cyan]Target Audience[/cyan]",
        default="tech-curious professionals"
    )

    tone_options = {
        "1": "informative and engaging",
        "2": "conversational and friendly",
        "3": "technical and precise",
        "4": "bold and opinionated"
    }

    console.print("\n[dim]Tone options:[/dim]")
    for k, v in tone_options.items():
        console.print(f"  [yellow]{k}[/yellow]. {v}")

    tone_choice = Prompt.ask("[cyan]Choose tone[/cyan]", choices=["1", "2", "3", "4"], default="1")
    tone = tone_options[tone_choice]

    return {
        "topic": topic,
        "target_audience": audience,
        "tone": tone,
        "needs_retrieval": False,       # set by router node
        "retrieval_results": None,      # set by retriever node
        "blog_plan": None,              # set by planner node
        "written_sections": [],         # populated by parallel writers
        "final_blog": None,             # set by reducer node
        "errors": [],                   # accumulated errors
    }


def run_pipeline(inputs: dict):
    """Run the AI Blog Writer LangGraph pipeline."""
    from graph import ai_blog_writer_graph

    console.print("\n[bold cyan]Starting AI Blog Writer Pipeline...[/bold cyan]\n")
    console.print("[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]")

    start_time = time.time()

    try:
        # Get concurrency limit from env
        import os
        max_concurrency = int(os.getenv("MAX_CONCURRENCY", 3))

        # Execute the graph
        final_state = ai_blog_writer_graph.invoke(
            inputs,
            config={
                "recursion_limit": 50,
                "max_concurrency": max_concurrency
            }
        )

        elapsed = time.time() - start_time
        console.print(f"\n[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]")
        console.print(f"[bold green]Pipeline completed in {elapsed:.1f}s[/bold green]")

        # Print errors if any
        errors = final_state.get("errors", [])
        if errors:
            console.print(f"\n[yellow]⚠  {len(errors)} non-fatal warning(s):[/yellow]")
            for e in errors:
                console.print(f"   [dim]{e}[/dim]")

        # Show final blog preview
        final_blog = final_state.get("final_blog")
        if final_blog:
            console.print(f"\n[bold]Blog Preview (first 500 chars):[/bold]")
            console.print(Panel(
                final_blog.full_content[:500] + "...",
                border_style="green",
                title=f"[green]{final_blog.title}[/green]"
            ))
            console.print(f"\n[bold green]✅ Full blog saved to:[/bold green] output/{inputs['topic'].lower().replace(' ', '_')[:50]}.md")
        else:
            console.print("[red]❌ No blog was generated. Check your API keys.[/red]")

        return final_state

    except Exception as e:
        console.print(f"\n[bold red]Pipeline failed: {e}[/bold red]")
        console.print("\n[dim]Common fixes:[/dim]")
        console.print("  • Check your OPENROUTER_API_KEY in .env")
        console.print("  • Make sure you copied .env.example → .env")
        console.print("  • Try a free model: meta-llama/llama-3.1-8b-instruct:free")
        raise


def main():
    print_banner()

    # Check .env exists
    import os
    if not os.path.exists(".env"):
        console.print("\n[bold red]⚠  .env file not found![/bold red]")
        console.print("Copy .env.example to .env and fill in your API keys:")
        console.print("  [cyan]cp .env.example .env[/cyan]")
        sys.exit(1)

    # Get inputs
    inputs = get_user_input()

    console.print(f"\n[dim]Topic: {inputs['topic']}[/dim]")
    console.print(f"[dim]Audience: {inputs['target_audience']}[/dim]")
    console.print(f"[dim]Tone: {inputs['tone']}[/dim]\n")

    if not Confirm.ask("[cyan]Start generating?[/cyan]", default=True):
        console.print("Cancelled.")
        sys.exit(0)

    run_pipeline(inputs)


if __name__ == "__main__":
    main()
