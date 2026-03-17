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


import sys
import time
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from dotenv import load_dotenv

load_dotenv()

console = Console()


def print_banner():
    console.print(Panel.fit(
        "[bold cyan]AI Blog Writer[/bold cyan] — Advanced Agentic Blog System\n"
        "[dim]Async LangGraph DAG  •  LangSmith Tracing  •  LLM-as-Judge Eval[/dim]",
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
        "evaluation": None,             # set by evaluator node
        "errors": [],                   # accumulated errors
    }


async def run_pipeline(inputs: dict):
    """Run the AI Blog Writer LangGraph pipeline asynchronously."""
    from graph import ai_blog_writer_graph

    console.print("\n[bold cyan]Starting AI Blog Writer Pipeline...[/bold cyan]\n")
    console.print("[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]")

    start_time = time.time()

    try:
        # Get concurrency limit from env
        import os
        max_concurrency = int(os.getenv("MAX_CONCURRENCY", 3))

        # Execute the graph asynchronously
        final_state = await ai_blog_writer_graph.ainvoke(
            inputs,
            config={
                "recursion_limit": 50,
                "max_concurrency": max_concurrency
            }
        )

        elapsed = time.time() - start_time
        console.print(f"\n[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]")
        console.print(f"[bold green]Pipeline completed in {elapsed:.1f}s[/bold green]")

        # Show final blog preview
        final_blog = final_state.get("final_blog")
        if final_blog:
            console.print(f"\n[bold]Blog Preview (first 500 chars):[/bold]")
            console.print(Panel(
                final_blog.full_content[:500] + "...",
                border_style="green",
                title=f"[green]{final_blog.title}[/green]"
            ))
            
            # Show Evaluation
            eval_data = final_state.get("evaluation")
            if eval_data:
                eval_style = "green" if eval_data.is_pass else "yellow"
                console.print(Panel(
                    f"[bold]Score:[/bold] {eval_data.score}/10\n"
                    f"[bold]Reasoning:[/bold] {eval_data.reasoning}\n"
                    f"[bold]Suggestions:[/bold] {', '.join(eval_data.suggestions) if eval_data.suggestions else 'None'}",
                    title=f"[{eval_style}]Editor's Evaluation[/{eval_style}]",
                    border_style=eval_style
                ))

            console.print(f"\n[bold green]✅ Full blog saved to:[/bold green] output/{inputs['topic'].lower().replace(' ', '_')[:50]}.md")
        else:
            console.print("[red]❌ No blog was generated. Check your API keys.[/red]")

        return final_state

    except Exception as e:
        console.print(f"\n[bold red]Pipeline failed: {e}[/bold red]")
        raise


async def main():
    print_banner()

    # Check .env exists
    import os
    if not os.path.exists(".env"):
        console.print("\n[bold red]⚠  .env file not found![/bold red]")
        sys.exit(1)

    # Get inputs
    inputs = get_user_input()

    if not Confirm.ask("[cyan]Start generating?[/cyan]", default=True):
        console.print("Cancelled.")
        sys.exit(0)

    await run_pipeline(inputs)


if __name__ == "__main__":
    asyncio.run(main())
